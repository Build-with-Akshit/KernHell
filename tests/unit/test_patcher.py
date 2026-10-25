"""Unit tests for the Surgical AST/CST Patcher."""

from __future__ import annotations

from pathlib import Path
import pytest

from kernhell.core.exceptions import SelectorNotFoundInASTError
from kernhell.core.models import SelectorFix, SelectorStrategy
from kernhell.patcher.patcher import SurgicalPatcher
from kernhell.utils.file_utils import read_file


def test_patcher_preserves_comments_and_formatting() -> None:
    patcher = SurgicalPatcher()

    original_code = '''"""Module docstring."""

# Critical test setup comment
def test_order_flow(page):
    # Step 1: navigate to store
    page.goto("https://example.com")

    # Step 2: click the purchase action (needs to be healed)
    page.click("#buy-now")  # inline comment here

    # Final assertion
    assert page.is_visible(".success")
'''

    patched = patcher.apply_patch(
        source_code=original_code,
        old_selector="#buy-now",
        new_selector="#purchase-btn",
        target_line=9,
    )

    # Replaced selector
    assert '"#purchase-btn"' in patched or "'#purchase-btn'" in patched
    assert "#buy-now" not in patched

    # Comments MUST be 100% preserved!
    assert "# Critical test setup comment" in patched
    assert "# Step 1: navigate to store" in patched
    assert "# Step 2: click the purchase action (needs to be healed)" in patched
    assert "# inline comment here" in patched
    assert '"""Module docstring."""' in patched


def test_patcher_file_workflow_with_backup(tmp_path: Path) -> None:
    patcher = SurgicalPatcher()
    test_file = tmp_path / "test_checkout.py"
    test_file.write_text('page.click("#old-btn")\n', encoding="utf-8")

    fix = SelectorFix(
        old_selector="#old-btn",
        new_selector="#new-btn",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.9,
    )

    patcher.patch_test_file(test_file, fix, line_number=1, create_backup=True)

    # Target file is mutated
    assert read_file(test_file).strip() == 'page.click("#new-btn")'

    # Backup file exists and has original content
    backup_file = test_file.with_suffix(test_file.suffix + ".kernhell.bak")
    assert backup_file.is_file()
    assert read_file(backup_file).strip() == 'page.click("#old-btn")'


def test_patcher_raises_when_selector_not_found() -> None:
    patcher = SurgicalPatcher()
    code = 'page.click("#other-button")\n'

    with pytest.raises(SelectorNotFoundInASTError):
        patcher.apply_patch(
            source_code=code,
            old_selector="#completely-missing-selector",
            new_selector="#replacement",
        )


def test_patcher_typescript_file_workflow(tmp_path: Path) -> None:
    patcher = SurgicalPatcher()
    ts_file = tmp_path / "checkout.spec.ts"
    ts_code = """import { test, expect } from '@playwright/test';

// Step 1: Open store
test('checkout', async ({ page }: { page: any }) => {
  // Step 2: Click checkout
  await page.click('#old-checkout-btn');
});
"""
    ts_file.write_text(ts_code, encoding="utf-8")

    fix = SelectorFix(
        old_selector="#old-checkout-btn",
        new_selector="#new-checkout-btn",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.95,
    )

    patched = patcher.patch_test_file(ts_file, fix, line_number=6, create_backup=True)

    assert "#new-checkout-btn" in patched
    assert "#old-checkout-btn" not in patched
    assert "// Step 1: Open store" in patched
    assert "// Step 2: Click checkout" in patched
    assert "async ({ page }: { page: any })" in patched

