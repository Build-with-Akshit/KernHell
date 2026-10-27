"""End-to-end integration tests for the KernHell healing pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import NoFailuresDetectedError
from kernhell.core.models import FailureContext, SelectorType
from kernhell.core.orchestrator import HealingOrchestrator
from kernhell.utils.file_utils import read_file, write_file


def test_end_to_end_healing_and_caching_cycle(
    tmp_path: Path,
    sample_dom_renamed_html: str,
) -> None:
    # 1. Setup isolated test environment
    test_file = tmp_path / "test_checkout.py"
    original_code = '''# Test checkout flow
def test_checkout(page):
    page.goto("https://example.com/checkout")
    # Intent: complete checkout
    page.click("#buy-now")  # Target selector to heal
    assert page.is_visible(".success")
'''
    write_file(test_file, original_code)

    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path / "cache")
    cfg.cache.similarity_threshold = 0.88
    cfg.healing.dry_run = False

    orchestrator = HealingOrchestrator(cfg)

    # 2. Mock initial failure
    mock_failure = FailureContext(
        test_file=test_file,
        line_number=5,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout 5000ms exceeded waiting for locator('#buy-now')",
        live_dom=sample_dom_renamed_html,
        page_url="https://example.com/checkout",
        surrounding_code='page.click("#buy-now")',
    )

    # First run: Scanner detects failure on first execution, then passes during verification
    orchestrator.scanner.run = MagicMock(side_effect=[
        [mock_failure],                     # Initial run finds failure
        NoFailuresDetectedError("Passed!"), # Verification run passes!
    ])

    # 3. Execute First Healing Run (Hits AI Pipeline -> Stores in Cache)
    report1 = orchestrator.heal(test_file, dry_run=False)

    assert report1.total_failures == 1
    assert report1.healed_count == 1
    assert report1.cache_hits == 0
    assert report1.llm_calls == 1

    # Check file was mutated surgically
    patched_code = read_file(test_file)
    assert "#buy-now" not in patched_code
    assert "# Target selector to heal" in patched_code  # Comments preserved!
    assert ("#purchase-btn" in patched_code or "complete-order-btn" in patched_code or "Place Your Order" in patched_code or "Complete Order" in patched_code)

    # 4. Re-inject broken selector to test Semantic Vector Cache instant hit
    write_file(test_file, original_code)

    # Second run: Scanner finds broken selector, verification passes
    orchestrator.scanner.run = MagicMock(side_effect=[
        [mock_failure],
        NoFailuresDetectedError("Passed!"),
    ])

    report2 = orchestrator.heal(test_file, dry_run=False)

    # Must hit Semantic Cache (ZERO LLM calls!)
    assert report2.total_failures == 1
    assert report2.healed_count == 1
    assert report2.cache_hits == 1
    assert report2.llm_calls == 0
    assert report2.results[0].from_cache is True
