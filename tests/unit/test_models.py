"""Unit tests for core Pydantic data models."""

from __future__ import annotations

from pathlib import Path
import pytest
from pydantic import ValidationError

from kernhell.core.models import (
    Diagnosis,
    ErrorType,
    FailureContext,
    FailureType,
    HealingReport,
    HealingResult,
    PrunedDOM,
    SelectorFix,
    SelectorStrategy,
    SelectorType,
)


def test_failure_context_defaults() -> None:
    ctx = FailureContext(
        test_file=Path("tests/test_sample.py"),
        line_number=42,
        broken_selector="#btn-submit",
        error_message="Timeout exceeded",
    )
    assert ctx.selector_type == SelectorType.UNKNOWN
    assert ctx.error_type == ErrorType.TIMEOUT
    assert ctx.live_dom == ""
    assert ctx.screenshot_path is None
    assert ctx.timestamp is not None


def test_pruned_dom_reduction_calculation() -> None:
    p1 = PrunedDOM(html="<button>Hi</button>", original_size=1000, pruned_size=200)
    assert p1.reduction_pct == 80.0

    p_empty = PrunedDOM(html="", original_size=0, pruned_size=0)
    assert p_empty.reduction_pct == 0.0


def test_confidence_validation() -> None:
    # Valid confidence
    diag = Diagnosis(
        failure_type=FailureType.RENAME,
        explanation="Renamed selector",
        confidence=0.95,
    )
    assert diag.confidence == 0.95

    # Out of range confidence should fail validation
    with pytest.raises(ValidationError):
        Diagnosis(
            failure_type=FailureType.RENAME,
            explanation="Invalid confidence",
            confidence=1.5,
        )

    with pytest.raises(ValidationError):
        SelectorFix(
            old_selector="#old",
            new_selector="#new",
            confidence=-0.1,
        )


def test_healing_report_aggregations() -> None:
    test_path = Path("tests/test_sample.py")
    report = HealingReport(test_file=test_path)

    f1 = FailureContext(
        test_file=test_path,
        line_number=10,
        broken_selector="#old-1",
        error_message="Timeout",
    )
    fix1 = SelectorFix(
        old_selector="#old-1",
        new_selector="#new-1",
        strategy=SelectorStrategy.ROLE_MATCH,
        confidence=0.95,
        verified=True,
    )

    f2 = FailureContext(
        test_file=test_path,
        line_number=20,
        broken_selector="#old-2",
        error_message="Timeout",
    )

    r1 = HealingResult(failure=f1, fix=fix1, from_cache=True)
    r2 = HealingResult(failure=f2, skipped=True, skip_reason="Real missing bug")

    report.results = [r1, r2]

    assert report.total_failures == 2
    assert report.healed_count == 1
    assert report.skipped_count == 1
    assert report.cache_hits == 1
    assert report.llm_calls == 0
    assert report.verification_passed is True
