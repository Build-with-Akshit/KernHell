"""Healing orchestrator — coordinates the full self-healing pipeline.

In Weekend 1:
- Scans test file using ScannerRunner
- Prunes live DOM snapshots using DOMPruner
- Packages failure contexts and pruning stats into HealingReport
- Prepares extension points for Weekend 2 (Analyzer, Healer, Patcher, Verifier)
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import structlog

from kernhell.core.config import KernHellConfig, load_config
from kernhell.core.exceptions import NoFailuresDetectedError, ScannerError
from kernhell.core.models import (
    FailureContext,
    HealingReport,
    HealingResult,
    PrunedDOM,
)
from kernhell.pruner.dom_pruner import prune_dom
from kernhell.scanner.runner import ScannerRunner

logger = structlog.get_logger()


class HealingOrchestrator:
    """Coordinates failure scanning, context capture, DOM pruning, and healing."""

    def __init__(self, config: Optional[KernHellConfig] = None) -> None:
        self.config = config or load_config()
        self.scanner = ScannerRunner(self.config)

    def scan(self, test_file: Path) -> list[tuple[FailureContext, Optional[PrunedDOM]]]:
        """Scan a test file for failures and capture pruned DOMs without modifying files.

        Parameters
        ----------
        test_file : Path
            Path to the Playwright test file.

        Returns
        -------
        list[tuple[FailureContext, Optional[PrunedDOM]]]
            List of detected failures paired with their pruned DOM (if live DOM was captured).
        """
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
        """Run the self-healing pipeline for a test file.

        In Weekend 1, this runs detection + pruning and prepares the report skeleton.
        Weekend 2 will plug in LLM Analyzer, Healer, CST Patcher, and Verifier.
        """
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

        for failure, pruned in scan_results:
            result = HealingResult(
                failure=failure,
                pruned_dom=pruned,
                skipped=True,
                skip_reason="Weekend 1 engine active: detection & pruning complete; AI healing hooks available in Weekend 2.",
            )
            report.results.append(result)

        report.duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "orchestrator.heal.complete",
            test_file=str(test_file),
            failures=report.total_failures,
            duration_ms=report.duration_ms,
        )
        return report
