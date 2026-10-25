"""Healing orchestrator — coordinates the full self-healing pipeline.

Pipeline Flow:
  1. Scan test file for selector failures.
  2. Prune live DOM snapshot.
  3. Query Semantic Vector Cache (zero latency, zero LLM cost).
  4. On Cache Miss:
     a. AI Failure Diagnosis (RENAME vs MISSING vs STRUCTURAL).
     b. Anti-Hallucination Guardrail: Skip genuine MISSING bugs.
     c. AI Resilient Selector Generation (with DOM presence check).
  5. Surgical AST/CST Patching (preserves comments, indentation, formatting).
  6. Test Verification (re-runs test to confirm fix; reverts on failure).
  7. Store verified fix in Semantic Memory for future instant reuse.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import structlog

from kernhell.analyzer.analyzer import FailureAnalyzer
from kernhell.analyzer.healer import SelectorHealer
from kernhell.cache.cache_manager import CacheManager
from kernhell.core.config import KernHellConfig, load_config
from kernhell.core.exceptions import (
    HealerError,
    LowConfidenceError,
    NoFailuresDetectedError,
    ScannerError,
)
from kernhell.core.models import (
    Diagnosis,
    FailureContext,
    FailureType,
    HealingReport,
    HealingResult,
    PrunedDOM,
    SelectorFix,
)
from kernhell.patcher.patcher import SurgicalPatcher
from kernhell.patcher.verifier import TestVerifier
from kernhell.pruner.dom_pruner import prune_dom
from kernhell.scanner.runner import ScannerRunner

logger = structlog.get_logger()


class HealingOrchestrator:
    """Coordinates failure scanning, context capture, DOM pruning, and healing."""

    def __init__(self, config: Optional[KernHellConfig] = None) -> None:
        self.config = config or load_config()
        self.scanner = ScannerRunner(self.config)
        self.cache = CacheManager(self.config)
        self.analyzer = FailureAnalyzer(self.config)
        self.healer = SelectorHealer(self.config)
        self.patcher = SurgicalPatcher()
        self.verifier = TestVerifier(self.config)

    def scan(self, test_file: Path) -> list[tuple[FailureContext, Optional[PrunedDOM]]]:
        """Scan a test file for failures and capture pruned DOMs without modifying files."""
        logger.info("orchestrator.scan.start", test_file=str(test_file))
        failures = self.scanner.run(test_file)

        results: list[tuple[FailureContext, Optional[PrunedDOM]]] = []
        for failure in failures:
            pruned: Optional[PrunedDOM] = None
            if failure.live_dom:
                pruned = prune_dom(failure.live_dom)
            results.append((failure, pruned))

        logger.info("orchestrator.scan.complete", failures_count=len(results))
        return results

    def heal(self, test_file: Path, dry_run: Optional[bool] = None) -> HealingReport:
        """Run the autonomous self-healing pipeline for a test file."""
        start_time = time.perf_counter()
        is_dry_run = self.config.healing.dry_run if dry_run is None else dry_run

        logger.info(
            "orchestrator.heal.start",
            test_file=str(test_file),
            dry_run=is_dry_run,
        )

        report = HealingReport(test_file=test_file)

        try:
            scan_results = self.scan(test_file)
        except NoFailuresDetectedError as exc:
            logger.info("orchestrator.no_failures", message=str(exc))
            report.duration_ms = int((time.perf_counter() - start_time) * 1000)
            return report
        except ScannerError as exc:
            logger.error("orchestrator.scan_failed", error=str(exc))
            raise

        # Limit heals per file to prevent runaway modification
        max_heals = self.config.healing.max_heals_per_file
        if len(scan_results) > max_heals:
            logger.warning(
                "orchestrator.exceeded_max_heals",
                failures=len(scan_results),
                max_allowed=max_heals,
            )

        for failure, pruned in scan_results[:max_heals]:
            result = self._heal_single_failure(
                test_file=test_file,
                failure=failure,
                pruned_dom=pruned,
                dry_run=is_dry_run,
            )
            report.results.append(result)

        report.duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "orchestrator.heal.complete",
            test_file=str(test_file),
            total=report.total_failures,
            healed=report.healed_count,
            skipped=report.skipped_count,
            from_cache=report.cache_hits,
            duration_ms=report.duration_ms,
        )
        return report

    def _heal_single_failure(
        self,
        test_file: Path,
        failure: FailureContext,
        pruned_dom: Optional[PrunedDOM],
        dry_run: bool,
    ) -> HealingResult:
        """Execute the healing decision tree for a single broken selector."""
        # 1. Check Semantic Vector Cache
        cached_fix, score = self.cache.lookup(
            broken_selector=failure.broken_selector,
            context=failure.surrounding_code,
            page_url=failure.page_url,
        )

        if cached_fix is not None:
            logger.info(
                "orchestrator.cache_hit_applying",
                selector=failure.broken_selector,
                score=score,
            )
            applied_fix = SelectorFix(
                old_selector=failure.broken_selector,
                new_selector=cached_fix.new_selector,
                strategy=cached_fix.strategy,
                confidence=score,
                reasoning=f"Matched semantic cache fix (similarity {score:.2f})",
                verified=cached_fix.verified,
            )
            if not dry_run:
                try:
                    self.patcher.patch_test_file(
                        test_file=test_file,
                        fix=applied_fix,
                        line_number=failure.line_number,
                    )
                    verified = self.verifier.verify(test_file, applied_fix)
                    if verified:
                        return HealingResult(
                            failure=failure,
                            pruned_dom=pruned_dom,
                            fix=applied_fix,
                            from_cache=True,
                        )
                    else:
                        logger.warning(
                            "orchestrator.cache_fix_verification_failed.proceeding_to_ai",
                            selector=failure.broken_selector,
                        )
                except Exception as exc:
                    logger.warning(
                        "orchestrator.cache_fix_patch_failed.proceeding_to_ai",
                        error=str(exc),
                    )
            else:
                applied_fix.verified = True
                return HealingResult(
                    failure=failure,
                    pruned_dom=pruned_dom,
                    fix=applied_fix,
                    from_cache=True,
                )

        # 2. AI Failure Diagnosis
        try:
            diagnosis = self.analyzer.diagnose(failure, pruned_dom)
        except Exception as exc:
            logger.error("orchestrator.diagnosis_failed", error=str(exc))
            return HealingResult(
                failure=failure,
                pruned_dom=pruned_dom,
                skipped=True,
                skip_reason=f"Diagnosis failed: {exc}",
            )

        # 3. Anti-Hallucination Guardrail: Never heal genuine MISSING bugs
        if diagnosis.failure_type == FailureType.MISSING:
            logger.info(
                "orchestrator.skip_missing",
                selector=failure.broken_selector,
                explanation=diagnosis.explanation,
            )
            return HealingResult(
                failure=failure,
                pruned_dom=pruned_dom,
                diagnosis=diagnosis,
                skipped=True,
                skip_reason=f"Potential real bug: element is genuinely MISSING ({diagnosis.explanation})",
            )

        # 4. Generate Resilient Replacement Selector
        try:
            fix = self.healer.suggest_fix(failure, diagnosis, pruned_dom)
        except LowConfidenceError as exc:
            logger.warning("orchestrator.low_confidence", error=str(exc))
            return HealingResult(
                failure=failure,
                pruned_dom=pruned_dom,
                diagnosis=diagnosis,
                skipped=True,
                skip_reason=str(exc),
            )
        except HealerError as exc:
            logger.warning("orchestrator.healer_error", error=str(exc))
            return HealingResult(
                failure=failure,
                pruned_dom=pruned_dom,
                diagnosis=diagnosis,
                skipped=True,
                skip_reason=str(exc),
            )

        # 5. Surgical AST/CST Patching & Verification
        if not dry_run:
            self.patcher.patch_test_file(
                test_file=test_file,
                fix=fix,
                line_number=failure.line_number,
            )
            verified = self.verifier.verify(test_file, fix)
            if verified:
                # 6. Store in Semantic Memory
                self.cache.store(
                    broken_selector=failure.broken_selector,
                    fix=fix,
                    context=failure.surrounding_code,
                    page_url=failure.page_url,
                    test_file=str(test_file),
                )
        else:
            # In dry-run mode, simulate successful verification preview
            fix.verified = True

        return HealingResult(
            failure=failure,
            pruned_dom=pruned_dom,
            diagnosis=diagnosis,
            fix=fix,
            from_cache=False,
        )
