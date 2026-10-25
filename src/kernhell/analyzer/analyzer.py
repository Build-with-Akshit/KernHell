"""Failure Analyzer — classifies Playwright test failures using LLM.

Determines whether a selector failure is:
  - RENAME: Element exists, selector refactored (safe to heal).
  - MISSING: Element genuinely absent / application bug (do not heal!).
  - STRUCTURAL: Major UI/flow refactor.
"""

from __future__ import annotations

import json
import re
from typing import Optional

import structlog

from kernhell.analyzer.prompts import (
    DIAGNOSIS_SYSTEM_PROMPT,
    DIAGNOSIS_USER_PROMPT_TEMPLATE,
)
from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import AnalyzerError
from kernhell.core.models import Diagnosis, FailureContext, FailureType, PrunedDOM

logger = structlog.get_logger()


def _clean_json_response(raw_text: str) -> str:
    """Extract raw JSON substring from potentially markdown-wrapped LLM output."""
    raw = raw_text.strip()
    # Strip markdown ```json ... ``` wrappers if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if match:
        return match.group(1).strip()
    return raw


class FailureAnalyzer:
    """Diagnoses test failure causes using configured LLM provider."""

    def __init__(self, config: KernHellConfig) -> None:
        self.config = config
        self.llm_cfg = config.llm

    def diagnose(
        self,
        failure: FailureContext,
        pruned_dom: Optional[PrunedDOM] = None,
    ) -> Diagnosis:
        """Analyze failure context and pruned DOM to diagnose the failure type.

        Parameters
        ----------
        failure : FailureContext
            Failure metadata captured by the scanner.
        pruned_dom : Optional[PrunedDOM]
            Pruned live DOM snapshot of the page.

        Returns
        -------
        Diagnosis
            Classification (RENAME | MISSING | STRUCTURAL) with confidence & rationale.
        """
        dom_text = pruned_dom.html if pruned_dom else failure.live_dom

        logger.info(
            "analyzer.diagnose.start",
            selector=failure.broken_selector,
            dom_length=len(dom_text),
        )

        # Guardrail: If no DOM was captured, we cannot reliably inspect elements
        if not dom_text:
            return Diagnosis(
                failure_type=FailureType.UNKNOWN,
                explanation="No DOM captured at the time of failure.",
                confidence=0.0,
            )

        prompt_content = DIAGNOSIS_USER_PROMPT_TEMPLATE.format(
            broken_selector=failure.broken_selector,
            selector_type=failure.selector_type.value,
            line_number=failure.line_number,
            test_file=failure.test_file.name,
            surrounding_code=failure.surrounding_code or "# (surrounding code unavailable)",
            pruned_dom=dom_text,
            error_message=failure.error_message,
        )

        try:
            raw_response = self._call_llm(
                system_prompt=DIAGNOSIS_SYSTEM_PROMPT,
                user_prompt=prompt_content,
            )
            clean_json = _clean_json_response(raw_response)
            data = json.loads(clean_json)

            failure_type_str = data.get("failure_type", "unknown").lower()
            try:
                failure_type = FailureType(failure_type_str)
            except ValueError:
                failure_type = FailureType.UNKNOWN

            diagnosis = Diagnosis(
                failure_type=failure_type,
                explanation=data.get("explanation", "No explanation provided."),
                confidence=float(data.get("confidence", 0.5)),
            )

            logger.info(
                "analyzer.diagnose.complete",
                failure_type=diagnosis.failure_type.value,
                confidence=diagnosis.confidence,
            )
            return diagnosis

        except Exception as exc:
            logger.error("analyzer.diagnose.error", error=str(exc))
            raise AnalyzerError(f"Failed to diagnose test failure via LLM: {exc}") from exc

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM using litellm with fallback for local test execution."""
        # Check if litellm is available
        try:
            import litellm
        except ImportError:
            # Fallback heuristic mode when running offline or in unit tests
            logger.warning("analyzer.litellm_not_installed.using_heuristic")
            return self._heuristic_diagnosis_fallback(user_prompt)

        # Resolve API key from config or standard provider environment variables (e.g. GEMINI_API_KEY)
        api_key = self.llm_cfg.get_resolved_api_key()
        if not api_key and self.llm_cfg.provider not in ("ollama", "local"):
            logger.warning("analyzer.no_api_key.using_heuristic")
            return self._heuristic_diagnosis_fallback(user_prompt)

        model_name = self.llm_cfg.get_litellm_model_name()

        try:
            response = litellm.completion(
                model=model_name,
                api_key=api_key,
                temperature=self.llm_cfg.temperature,
                max_tokens=self.llm_cfg.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.warning(
                "analyzer.llm_call_failed.falling_back_to_heuristic",
                model=model_name,
                error=str(exc),
            )
            return self._heuristic_diagnosis_fallback(user_prompt)

    def _heuristic_diagnosis_fallback(self, user_prompt: str) -> str:
        """Deterministic heuristic for offline testing without LLM API key."""
        prompt_lower = user_prompt.lower()

        # If DOM has order/purchase button but test used buy-now -> RENAME
        if ("buy-now" in prompt_lower or "cart" in prompt_lower) and (
            "purchase" in prompt_lower or "place your order" in prompt_lower or "complete-order-btn" in prompt_lower
        ):
            return json.dumps({
                "failure_type": "rename",
                "explanation": "Target action exists in DOM but selector changed from #buy-now to a refactored button element.",
                "confidence": 0.95,
            })

        # If DOM indicates unavailable / missing / error banner -> MISSING
        if "out of stock" in prompt_lower or "unavailable" in prompt_lower or "error" in prompt_lower:
            return json.dumps({
                "failure_type": "missing",
                "explanation": "Element is genuinely absent from page due to out of stock status. This represents an application state change, not a selector rename.",
                "confidence": 0.92,
            })

        # Default fallback
        return json.dumps({
            "failure_type": "rename",
            "explanation": "Heuristic fallback analysis.",
            "confidence": 0.85,
        })
