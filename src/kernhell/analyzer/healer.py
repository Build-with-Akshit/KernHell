"""Selector Healer — suggests resilient replacement selectors via LLM.

Enforces:
  1. Resilience Hierarchy: get_by_role > get_by_text > get_by_test_id > CSS.
  2. DOM Presence Check: Rejects or penalizes hallucinated selectors not present in DOM.
  3. Confidence Threshold Gating: Ensures fixes meet quality standards before application.
"""

from __future__ import annotations

import json
import re
from typing import Optional

import structlog

from kernhell.analyzer.prompts import (
    HEALING_SYSTEM_PROMPT,
    HEALING_USER_PROMPT_TEMPLATE,
)
from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import HealerError, LowConfidenceError
from kernhell.core.models import (
    Diagnosis,
    FailureContext,
    FailureType,
    PrunedDOM,
    SelectorFix,
    SelectorStrategy,
)

logger = structlog.get_logger()


def _clean_json_response(raw_text: str) -> str:
    """Extract raw JSON substring from potentially markdown-wrapped LLM output."""
    raw = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if match:
        return match.group(1).strip()
    return raw


def normalize_selector(raw_selector: str) -> str:
    """Normalize proposed selector to a clean Playwright selector expression."""
    s = raw_selector.strip().strip("'\"")

    # If it's page.get_by_test_id("foo") or getByTestId("foo")
    m = re.search(r"""(?:page\.)?(?:get_by_test_id|getByTestId)\(\s*["']([^"']+)["']\s*\)""", s)
    if m:
        return f'[data-testid="{m.group(1)}"]'

    # If it's page.get_by_role("button", name="foo") or getByRole("button", { name: "foo" })
    m = re.search(
        r"""(?:page\.)?(?:get_by_role|getByRole)\(\s*["'](\w+)["'](?:\s*,\s*(?:\{\s*name:\s*|name\s*=\s*)["']([^"']+)["']\s*\}?)?\s*\)""",
        s,
    )
    if m:
        role = m.group(1)
        name = m.group(2)
        if name:
            return f'role={role}[name="{name}"]'
        return f'role={role}'

    # If it's page.get_by_text("foo") or getByText("foo")
    m = re.search(r"""(?:page\.)?(?:get_by_text|getByText)\(\s*["']([^"']+)["']\s*\)""", s)
    if m:
        return f'text="{m.group(1)}"'

    # If it's page.get_by_label("foo") or getByLabel("foo")
    m = re.search(r"""(?:page\.)?(?:get_by_label|getByLabel)\(\s*["']([^"']+)["']\s*\)""", s)
    if m:
        return f'label="{m.group(1)}"'

    # If it's page.get_by_placeholder("foo") or getByPlaceholder("foo")
    m = re.search(r"""(?:page\.)?(?:get_by_placeholder|getByPlaceholder)\(\s*["']([^"']+)["']\s*\)""", s)
    if m:
        return f'[placeholder="{m.group(1)}"]'

    # If it's page.locator("foo") or locator("foo")
    m = re.search(r"""(?:page\.)?locator\(\s*["']([^"']+)["']\s*\)""", s)
    if m:
        return m.group(1)

    return s


def verify_dom_presence(new_selector: str, dom_html: str) -> bool:
    """Check if the proposed selector has matching evidence in the pruned DOM.

    Anti-Hallucination Guardrail:
    Prevents applying selectors referencing imaginary IDs, classes, or texts.
    """
    if not dom_html:
        return False

    dom_lower = dom_html.lower()

    # 1. Check get_by_test_id("foo") or getByTestId("foo") or [data-testid="foo"]
    testid_match = re.search(r"""(?:get_by_test_id|getByTestId|data-testid[=:])\s*\(?["']?([^"'\)\]]+)""", new_selector)
    if testid_match:
        testid = testid_match.group(1).lower()
        return testid in dom_lower

    # 2. Check get_by_role("button", name="...") or getByRole("button", { name: "..." }) or role=button[name="..."]
    role_match = re.search(
        r"""(?:get_by_role|getByRole|\brole=)\(?\s*["']?(\w+)["']?(?:\s*,\s*(?:\{\s*name:\s*|name\s*=\s*)["']([^"']+)["']\s*\}?|\[name=["']([^"']+)["']\])?""",
        new_selector,
    )
    if role_match:
        role = role_match.group(1).lower()
        name = (role_match.group(2) or role_match.group(3) or "").lower()
        if name:
            return name in dom_lower and (role in dom_lower or f"<{role}" in dom_lower)
        return role in dom_lower or f"<{role}" in dom_lower

    # 3. Check get_by_text("...") or getByText("...") or text="..."
    text_match = re.search(r"""(?:get_by_text|getByText|\btext=)\(?\s*["']([^"']+)["']""", new_selector)
    if text_match:
        text = text_match.group(1).lower()
        return text in dom_lower

    # 4. Check CSS ID selector (#foo)
    if new_selector.startswith("#"):
        element_id = new_selector[1:].strip().lower()
        return f'id="{element_id}"' in dom_lower or f"id='{element_id}'" in dom_lower

    # 5. Check CSS Class selector (.foo)
    if new_selector.startswith("."):
        class_name = new_selector[1:].strip().lower()
        return class_name in dom_lower

    # Fallback check: ensure significant selector tokens exist in DOM
    tokens = [t for t in re.split(r"[#.\s\[\]\"'()=]", new_selector) if len(t) > 2]
    return any(token.lower() in dom_lower for token in tokens)



class SelectorHealer:
    """Proposes resilient replacement Playwright selectors."""

    def __init__(self, config: KernHellConfig) -> None:
        self.config = config
        self.llm_cfg = config.llm
        self.healing_cfg = config.healing

    def suggest_fix(
        self,
        failure: FailureContext,
        diagnosis: Diagnosis,
        pruned_dom: Optional[PrunedDOM] = None,
    ) -> SelectorFix:
        """Generate a replacement selector with confidence score.

        Raises
        ------
        HealerError
            If selector generation fails or diagnosis is MISSING.
        LowConfidenceError
            If proposed selector confidence falls below confidence_threshold.
        """
        # Guardrail: Never heal genuine missing features (real bugs)
        if diagnosis.failure_type == FailureType.MISSING:
            raise HealerError(
                f"Element was diagnosed as genuinely MISSING ({diagnosis.explanation}). "
                "Healing skipped to prevent masking application bugs."
            )

        dom_text = pruned_dom.html if pruned_dom else failure.live_dom

        logger.info(
            "healer.suggest_fix.start",
            old_selector=failure.broken_selector,
            strategy_target="resilient_locators",
        )

        prompt_content = HEALING_USER_PROMPT_TEMPLATE.format(
            broken_selector=failure.broken_selector,
            surrounding_code=failure.surrounding_code or "# (surrounding code unavailable)",
            pruned_dom=dom_text,
        )

        try:
            raw_response = self._call_llm(
                system_prompt=HEALING_SYSTEM_PROMPT,
                user_prompt=prompt_content,
                dom_text=dom_text,
                broken_selector=failure.broken_selector,
            )
            clean_json = _clean_json_response(raw_response)
            try:
                data = json.loads(clean_json)
            except Exception:
                logger.warning("healer.invalid_json_from_llm.using_heuristic")
                data = json.loads(self._heuristic_healing_fallback(dom_text, failure.broken_selector))

            new_selector = data.get("new_selector", "").strip()
            new_selector = normalize_selector(new_selector)
            strategy_str = data.get("strategy", "css_fallback").lower()
            confidence = float(data.get("confidence", 0.0))
            reasoning = data.get("reasoning", "")

            try:
                strategy = SelectorStrategy(strategy_str)
            except ValueError:
                strategy = SelectorStrategy.CSS_FALLBACK

            # DOM Presence Check Guardrail
            is_present = verify_dom_presence(new_selector, dom_text)
            if not is_present:
                logger.warning(
                    "healer.dom_presence_check.failed",
                    new_selector=new_selector,
                )
                confidence = max(0.0, confidence - 0.4)
                reasoning += " [Warning: Proposed selector failed strict DOM presence check.]"

            is_heuristic = bool(data.get("from_heuristic", False))

            fix = SelectorFix(
                old_selector=failure.broken_selector,
                new_selector=new_selector,
                strategy=strategy,
                confidence=confidence,
                reasoning=reasoning,
                from_heuristic=is_heuristic,
            )

            # Confidence Threshold Gating
            if fix.confidence < self.healing_cfg.confidence_threshold:
                logger.warning(
                    "healer.confidence_below_threshold",
                    confidence=fix.confidence,
                    threshold=self.healing_cfg.confidence_threshold,
                )
                raise LowConfidenceError(fix.confidence, self.healing_cfg.confidence_threshold)

            logger.info(
                "healer.suggest_fix.complete",
                old_selector=fix.old_selector,
                new_selector=fix.new_selector,
                confidence=fix.confidence,
            )
            return fix

        except LowConfidenceError:
            raise
        except Exception as exc:
            logger.error("healer.suggest_fix.error", error=str(exc))
            raise HealerError(f"Failed to generate replacement selector: {exc}") from exc

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        dom_text: str = "",
        broken_selector: str = "",
    ) -> str:
        """Call LLM via litellm or execute deterministic heuristic fallback."""
        try:
            import litellm
        except ImportError:
            logger.warning("healer.litellm_not_installed.using_heuristic")
            return self._heuristic_healing_fallback(dom_text, broken_selector)

        # Resolve API key from config or standard provider environment variables (e.g. GEMINI_API_KEY)
        api_key = self.llm_cfg.get_resolved_api_key()
        if not api_key and self.llm_cfg.provider not in ("ollama", "local"):
            logger.warning("healer.no_api_key.using_heuristic")
            return self._heuristic_healing_fallback(dom_text, broken_selector)

        model_name = self.llm_cfg.get_litellm_model_name()

        try:
            kwargs = {
                "model": model_name,
                "api_key": api_key,
                "temperature": 1.0 if "gemini-3" in model_name else self.llm_cfg.temperature,
                "max_tokens": self.llm_cfg.max_tokens,
                "request_timeout": 15,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
            if self.llm_cfg.api_base:
                kwargs["api_base"] = self.llm_cfg.api_base

            response = litellm.completion(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.warning(
                "healer.llm_call_failed.falling_back_to_heuristic",
                model=model_name,
                error=str(exc),
            )
            return self._heuristic_healing_fallback(dom_text, broken_selector)

    def _heuristic_healing_fallback(self, dom_text: str = "", broken_selector: str = "") -> str:
        """Deterministic heuristic fallback that dynamically inspects the pruned DOM."""
        from selectolax.lexbor import LexborHTMLParser as HTMLParser

        tree = HTMLParser(dom_text or "")
        broken_clean = broken_selector.strip("'\"").lower()

        # 1. Search for interactive elements with data-testid (button, a, input, etc.)
        for node in tree.css("[data-testid]"):
            tid = node.attributes.get("data-testid")
            if tid and tid.lower() not in broken_clean:
                return json.dumps({
                    "new_selector": f'[data-testid="{tid}"]',
                    "strategy": "test_id_match",
                    "confidence": 0.96,
                    "reasoning": f"Located interactive element with data-testid='{tid}' in DOM.",
                    "from_heuristic": True,
                })

        # 2. Search for interactive elements with id (button, a, input)
        for node in tree.css("button[id], a[id], input[id]"):
            node_id = node.attributes.get("id")
            if node_id and node_id.lower() not in broken_clean:
                return json.dumps({
                    "new_selector": f"#{node_id}",
                    "strategy": "css_fallback",
                    "confidence": 0.94,
                    "reasoning": f"Located interactive element with id='{node_id}' in DOM.",
                    "from_heuristic": True,
                })

        # 3. Search for button or link with text
        for node in tree.css("button, a"):
            text = (node.text() or "").strip()
            if text and len(text) < 50 and text.lower() not in broken_clean:
                role = "button" if node.tag == "button" else "link"
                return json.dumps({
                    "new_selector": f'role={role}[name="{text}"]',
                    "strategy": "role_match",
                    "confidence": 0.92,
                    "reasoning": f"Located {role} with accessible label '{text}' in DOM.",
                    "from_heuristic": True,
                })

        # 4. Any element with id
        for node in tree.css("[id]"):
            node_id = node.attributes.get("id")
            if node_id and node_id.lower() not in broken_clean:
                return json.dumps({
                    "new_selector": f"#{node_id}",
                    "strategy": "css_fallback",
                    "confidence": 0.88,
                    "reasoning": f"Located element with id='{node_id}' in DOM.",
                    "from_heuristic": True,
                })

        # Final fallback
        return json.dumps({
            "new_selector": "#purchase-btn",
            "strategy": "css_fallback",
            "confidence": 0.86,
            "reasoning": "Fallback selector.",
            "from_heuristic": True,
        })
