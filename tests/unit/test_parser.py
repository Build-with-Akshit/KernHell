"""Unit tests for the Playwright error output parser."""

from __future__ import annotations

from pathlib import Path

from kernhell.core.models import ErrorType, SelectorType
from kernhell.scanner.parser import (
    classify_selector,
    parse_playwright_errors,
)


def test_classify_selector() -> None:
    assert classify_selector("#buy-now") == SelectorType.CSS
    assert classify_selector(".btn.btn-primary") == SelectorType.CSS
    assert classify_selector("button[type='submit']") == SelectorType.CSS
    assert classify_selector("//button[@id='buy-now']") == SelectorType.XPATH
    assert classify_selector("(//div//a)[1]") == SelectorType.XPATH
    assert classify_selector("text=Place Your Order") == SelectorType.TEXT
    assert classify_selector("role=button") == SelectorType.ROLE
    assert classify_selector("data-testid=order-btn") == SelectorType.TEST_ID
    assert classify_selector("[data-testid='submit']") == SelectorType.TEST_ID


def test_parse_playwright_timeout_error(
    sample_pytest_timeout_error: str,
    sample_test_path: Path,
) -> None:
    failures = parse_playwright_errors(sample_pytest_timeout_error, sample_test_path)

    assert len(failures) == 1
    f = failures[0]

    assert f.broken_selector == "#buy-now"
    assert f.selector_type == SelectorType.CSS
    assert f.error_type == ErrorType.TIMEOUT
    assert f.line_number == 15
    assert f.test_file == sample_test_path
    assert "page.click" in f.surrounding_code or "#buy-now" in f.surrounding_code


def test_parse_playwright_role_selector(sample_test_path: Path) -> None:
    output = """
    E playwright._impl._errors.TimeoutError: Page.get_by_role: Timeout 5000ms exceeded.
    E Call log:
    E   - waiting for page.get_by_role("button", name="Purchase Now")
    tests/fixtures/sample_test.py:20: TimeoutError
    """
    failures = parse_playwright_errors(output, sample_test_path)

    assert len(failures) == 1
    assert "get_by_role" in failures[0].broken_selector
    assert failures[0].selector_type == SelectorType.ROLE
    assert failures[0].line_number == 20


def test_parse_playwright_strict_mode(sample_test_path: Path) -> None:
    output = """
    E playwright._impl._errors.Error: strict mode violation: locator("button") resolved to 3 elements:
    E   1) <button id="one">First</button>
    E   2) <button id="two">Second</button>
    tests/fixtures/sample_test.py:10: Error
    """
    failures = parse_playwright_errors(output, sample_test_path)

    assert len(failures) == 1
    assert failures[0].broken_selector == "button"
    assert failures[0].error_type == ErrorType.STRICT_MODE
    assert failures[0].line_number == 10


def test_parse_clean_output_returns_empty(sample_test_path: Path) -> None:
    clean_output = """
    ============================= test session starts =============================
    collected 1 item
    tests/fixtures/sample_test.py .                                          [100%]
    ============================== 1 passed in 1.20s ==============================
    """
    failures = parse_playwright_errors(clean_output, sample_test_path)
    assert len(failures) == 0


def test_parse_playwright_typescript_output(tmp_path: Path) -> None:
    ts_file = tmp_path / "checkout.spec.ts"
    ts_file.write_text("import { test } from '@playwright/test';\ntest('checkout', async ({ page }) => {\n  await page.click('#checkout-btn');\n});\n", encoding="utf-8")

    ts_output = """
    Running 1 test using 1 worker
    1) [chromium] › checkout.spec.ts:3:9 › checkout ──────────────────────────────────────────────
       Error: locator.click: Timeout 5000ms exceeded.
       Call log:
         - waiting for locator('#checkout-btn')
       
          1 | import { test } from '@playwright/test';
          2 | test('checkout', async ({ page }) => {
        > 3 |   await page.click('#checkout-btn');
            |              ^
          4 | });

          at checkout.spec.ts:3:14
    """
    failures = parse_playwright_errors(ts_output, ts_file)
    assert len(failures) == 1
    assert failures[0].broken_selector == "#checkout-btn"
    assert failures[0].selector_type == SelectorType.CSS
    assert failures[0].line_number == 3


def test_parse_playwright_typescript_get_by_test_id(tmp_path: Path) -> None:
    ts_file = tmp_path / "cart.spec.ts"
    ts_file.write_text("await page.getByTestId('cart-btn').click();\n", encoding="utf-8")

    ts_output = """
    1) [chromium] › cart.spec.ts:1:9 › cart
       Error: locator.click: Timeout 5000ms exceeded.
       Call log:
         - waiting for getByTestId('cart-btn')
       > 1 | await page.getByTestId('cart-btn').click();
       at cart.spec.ts:1:12
    """
    failures = parse_playwright_errors(ts_output, ts_file)
    assert len(failures) == 1
    assert "getByTestId" in failures[0].broken_selector
    assert failures[0].selector_type == SelectorType.TEST_ID
    assert failures[0].line_number == 1


def test_parse_playwright_typescript_expect_codeframe(tmp_path: Path) -> None:
    ts_file = tmp_path / "expect.spec.ts"
    ts_file.write_text("// comment\nawait expect(page.locator('#status')).toBeVisible();\n", encoding="utf-8")

    ts_output = """
    1) [chromium] › expect.spec.ts:2:9 › status
       Error: Timed out 5000ms waiting for expect(locator).toBeVisible()
       Call log:
         - waiting for locator('#status')
       > 2 | await expect(page.locator('#status')).toBeVisible();
       at expect.spec.ts:2:15
    """
    failures = parse_playwright_errors(ts_output, ts_file)
    assert len(failures) == 1
    assert failures[0].broken_selector == "#status"
    assert failures[0].line_number == 2


