"""Unit tests for the SelectorHealer."""

from __future__ import annotations

from pathlib import Path
import pytest

from kernhell.analyzer.healer import SelectorHealer, verify_dom_presence
from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import HealerError, LowConfidenceError
from kernhell.core.models import (
    Diagnosis,
    FailureContext,
    FailureType,
    PrunedDOM,
    SelectorStrategy,
    SelectorType,
)


def test_verify_dom_presence_with_existing_elements(sample_dom_renamed_html: str) -> None:
    # 1. ID selector
    assert verify_dom_presence("#purchase-btn", sample_dom_renamed_html) is True

    # 2. Test ID selector
    assert verify_dom_presence("page.get_by_test_id('complete-order-btn')", sample_dom_renamed_html) is True

    # 3. Role + Name selector
    assert verify_dom_presence("page.get_by_role('button', name='Place Your Order')", sample_dom_renamed_html) is True

    # 4. Text selector
    assert verify_dom_presence("page.get_by_text('Place Your Order')", sample_dom_renamed_html) is True


def test_verify_dom_presence_rejects_hallucinations(sample_dom_renamed_html: str) -> None:
    # Non-existent ID
    assert verify_dom_presence("#nonexistent-imaginary-button-12345", sample_dom_renamed_html) is False

    # Non-existent test ID
    assert verify_dom_presence("page.get_by_test_id('phantom-element')", sample_dom_renamed_html) is False

    # Non-existent text
    assert verify_dom_presence("page.get_by_text('Click to win 1000000 dollars')", sample_dom_renamed_html) is False


def test_suggest_fix_skips_missing_bugs(sample_test_path: Path, sample_dom_missing_html: str) -> None:
    cfg = KernHellConfig()
    healer = SelectorHealer(cfg)

    failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        error_message="Timeout",
    )
    diagnosis = Diagnosis(
        failure_type=FailureType.MISSING,
        explanation="Element is absent from DOM due to out of stock condition.",
        confidence=0.92,
    )
    pruned = PrunedDOM(html=sample_dom_missing_html, original_size=100, pruned_size=100)

    # Must raise HealerError to refuse healing genuine bugs
    with pytest.raises(HealerError, match="MISSING"):
        healer.suggest_fix(failure, diagnosis, pruned)


def test_suggest_fix_generates_resilient_selector(sample_test_path: Path, sample_dom_renamed_html: str) -> None:
    cfg = KernHellConfig()
    healer = SelectorHealer(cfg)

    failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout 5000ms exceeded",
        live_dom=sample_dom_renamed_html,
        surrounding_code='page.click("#buy-now")',
    )
    diagnosis = Diagnosis(
        failure_type=FailureType.RENAME,
        explanation="Renamed to purchase-btn",
        confidence=0.95,
    )
    pruned = PrunedDOM(html=sample_dom_renamed_html, original_size=1000, pruned_size=500)

    fix = healer.suggest_fix(failure, diagnosis, pruned)

    assert fix.old_selector == "#buy-now"
    assert fix.confidence >= 0.85
    assert (
        "purchase-btn" in fix.new_selector
        or "complete-order-btn" in fix.new_selector
        or "Place Your Order" in fix.new_selector
    )
