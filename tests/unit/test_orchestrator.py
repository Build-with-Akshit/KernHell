"""Unit tests for the HealingOrchestrator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import NoFailuresDetectedError
from kernhell.core.models import FailureContext, SelectorType
from kernhell.core.orchestrator import HealingOrchestrator


def test_orchestrator_scan_with_failures(
    sample_test_path: Path,
    sample_dom_html: str,
) -> None:
    cfg = KernHellConfig()
    orchestrator = HealingOrchestrator(cfg)

    mock_failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout exceeded",
        live_dom=sample_dom_html,
    )

    orchestrator.scanner.run = MagicMock(return_value=[mock_failure])

    results = orchestrator.scan(sample_test_path)
    assert len(results) == 1
    failure, pruned = results[0]
    assert failure.broken_selector == "#buy-now"
    assert pruned is not None
    assert pruned.reduction_pct > 0.0
    assert "<script" not in pruned.html


def test_orchestrator_heal_report_generation(
    sample_test_path: Path,
    sample_dom_html: str,
) -> None:
    cfg = KernHellConfig()
    orchestrator = HealingOrchestrator(cfg)

    mock_failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout exceeded",
        live_dom=sample_dom_html,
    )
    orchestrator.scanner.run = MagicMock(return_value=[mock_failure])

    report = orchestrator.heal(sample_test_path)
    assert report.total_failures == 1
    assert report.skipped_count == 1
    assert report.duration_ms >= 0


def test_orchestrator_no_failures(sample_test_path: Path) -> None:
    cfg = KernHellConfig()
    orchestrator = HealingOrchestrator(cfg)
    orchestrator.scanner.run = MagicMock(side_effect=NoFailuresDetectedError("Clean test"))

    report = orchestrator.heal(sample_test_path)
    assert report.total_failures == 0
