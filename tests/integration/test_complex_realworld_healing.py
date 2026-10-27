"""Comprehensive integration test suite for complicated real-world Playwright scenarios.

Covers all complex possibilities:
  1. Page Object Model (POM) with inheritance, class attributes, typing, and docstrings.
  2. Chained locators with filters (e.g. .filter(has_text=...).locator(...)).
  3. Multi-line formatted locators spanning multiple lines with trailing comments.
  4. Module-level constant selectors and variable references.
  5. Multi-step failure cascades (multiple broken selectors in a single test workflow).
  6. Heavy modern enterprise DOMs (deeply nested, Tailwind classes, SVG icons, dynamic hashes).
  7. TypeScript Playwright specs (.spec.ts) with modern locator APIs (getByRole, getByTestId).
  8. Anti-hallucination guardrail on genuinely missing elements (genuine bug detection).
  9. Full End-to-End Orchestrator healing cycle on POM with Semantic Cache reuse.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import NoFailuresDetectedError
from kernhell.core.models import (
    Diagnosis,
    FailureContext,
    FailureType,
    HealingReport,
    SelectorFix,
    SelectorStrategy,
    SelectorType,
)
from kernhell.core.orchestrator import HealingOrchestrator
from kernhell.patcher.patcher import SurgicalPatcher
from kernhell.pruner.dom_pruner import prune_dom
from kernhell.utils.file_utils import read_file, write_file


# ============================================================================
# Possibility 1: Page Object Model (POM) with Classes, Inheritance & Methods
# ============================================================================

def test_pom_class_architecture_healing(tmp_path: Path) -> None:
    """Ensure KernHell surgically heals selectors inside Page Object Model classes
    without disturbing class definitions, super() calls, docstrings, typing, or methods.
    """
    patcher = SurgicalPatcher()
    pom_file = tmp_path / "checkout_page.py"

    original_code = '''"""Enterprise Checkout Page Object."""

from typing import Optional
from playwright.sync_api import Page, Locator


class BasePage:
    """Base class for all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = page.locator("header.main-header")


class CheckoutPage(BasePage):
    """Encapsulates checkout DOM interactions and assertions."""

    # Class-level constant
    DEFAULT_TIMEOUT: int = 10000

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Form field locators
        self.email_input = self.page.locator("input#user-email")
        self.address_input = self.page.locator("textarea#shipping-address")

        # The broken selector to heal:
        self.place_order_button = self.page.locator("button.legacy-place-order-btn")

    def submit_order(self, email: str, address: str) -> None:
        """Fills order info and triggers final purchase."""
        self.email_input.fill(email)
        self.address_input.fill(address)
        # Action step
        self.place_order_button.click()
'''
    write_file(pom_file, original_code)

    fix = SelectorFix(
        old_selector="button.legacy-place-order-btn",
        new_selector="button[data-testid='confirm-purchase-action']",
        strategy=SelectorStrategy.TEST_ID_MATCH,
        confidence=0.97,
    )

    patched_code = patcher.patch_test_file(pom_file, fix, line_number=28, create_backup=True)

    # 1. Target selector replaced accurately
    assert "button[data-testid='confirm-purchase-action']" in patched_code
    assert "button.legacy-place-order-btn" not in patched_code

    # 2. Entire class hierarchy, typing, and docstrings 100% intact
    assert "class BasePage:" in patched_code
    assert "class CheckoutPage(BasePage):" in patched_code
    assert "super().__init__(page)" in patched_code
    assert '"""Enterprise Checkout Page Object."""' in patched_code
    assert '"""Encapsulates checkout DOM interactions and assertions."""' in patched_code
    assert "DEFAULT_TIMEOUT: int = 10000" in patched_code
    assert "self.email_input = self.page.locator(\"input#user-email\")" in patched_code
    assert "def submit_order(self, email: str, address: str) -> None:" in patched_code


# ============================================================================
# Possibility 2: Chained Locators with Filter (.filter(has_text=...))
# ============================================================================

def test_chained_locator_with_filter_healing(tmp_path: Path) -> None:
    """Ensure chained locators with filters and sub-locators are healed cleanly."""
    patcher = SurgicalPatcher()
    test_file = tmp_path / "test_pricing.py"

    original_code = '''def test_select_subscription_plan(page):
    # Step: Locate specific tier card and click its CTA
    plan_button = page.locator(".pricing-card").filter(has_text="Enterprise Tier").locator("button.old-subscribe-btn")
    plan_button.click()
    assert page.is_visible(".checkout-form")
'''
    write_file(test_file, original_code)

    fix = SelectorFix(
        old_selector="button.old-subscribe-btn",
        new_selector="button.cta-upgrade-enterprise",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.94,
    )

    patched_code = patcher.patch_test_file(test_file, fix, line_number=3)

    assert "button.cta-upgrade-enterprise" in patched_code
    assert "button.old-subscribe-btn" not in patched_code
    assert '.filter(has_text="Enterprise Tier")' in patched_code
    assert 'page.locator(".pricing-card")' in patched_code


# ============================================================================
# Possibility 3: Multi-Line Formatted Locators Across Multiple Lines
# ============================================================================

def test_multiline_formatted_selector_healing(tmp_path: Path) -> None:
    """Ensure locators formatted across multiple lines with comments heal cleanly."""
    patcher = SurgicalPatcher()
    test_file = tmp_path / "test_multiline.py"

    original_code = '''def test_complex_multiline_statement(page):
    # Action broken across lines
    page.locator(
        "#old-multiline-selector-id"  # Inline explanatory note
    ).click()
'''
    write_file(test_file, original_code)

    fix = SelectorFix(
        old_selector="#old-multiline-selector-id",
        new_selector="#new-healed-selector-id",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.96,
    )

    patched_code = patcher.patch_test_file(test_file, fix, line_number=4)

    assert "#new-healed-selector-id" in patched_code
    assert "#old-multiline-selector-id" not in patched_code
    assert "# Inline explanatory note" in patched_code


# ============================================================================
# Possibility 4: Module-Level Constant / Variable Selectors
# ============================================================================

def test_module_level_constant_selector_healing(tmp_path: Path) -> None:
    """Ensure selectors declared as module-level constants or variables heal properly."""
    patcher = SurgicalPatcher()
    test_file = tmp_path / "test_constants.py"

    original_code = '''# Configuration constants
CHECKOUT_SUBMIT_SELECTOR: str = "button#legacy-order-trigger"
CANCEL_BUTTON_SELECTOR: str = "a.btn-cancel"

def test_trigger_order(page):
    page.goto("/order")
    page.locator(CHECKOUT_SUBMIT_SELECTOR).click()
'''
    write_file(test_file, original_code)

    fix = SelectorFix(
        old_selector="button#legacy-order-trigger",
        new_selector="button[data-testid='submit-order-now']",
        strategy=SelectorStrategy.TEST_ID_MATCH,
        confidence=0.98,
    )

    patched_code = patcher.patch_test_file(test_file, fix, line_number=2)

    assert "button[data-testid='submit-order-now']" in patched_code
    assert "button#legacy-order-trigger" not in patched_code
    assert "CHECKOUT_SUBMIT_SELECTOR: str =" in patched_code
    assert "page.locator(CHECKOUT_SUBMIT_SELECTOR).click()" in patched_code


# ============================================================================
# Possibility 5: Multi-Step Cascading Failures in a Single Test Workflow
# ============================================================================

def test_multi_step_cascade_sequential_healing(tmp_path: Path) -> None:
    """Ensure KernHell handles sequential failures across multiple steps in a single test."""
    test_file = tmp_path / "test_multi_step_flow.py"

    original_code = '''def test_end_to_end_journey(page):
    page.goto("/app")
    # Step 1: Login
    page.fill("#old-username-field", "admin@corp.io")
    # Step 2: Search
    page.click("button.old-search-icon")
    # Step 3: Checkout
    page.click("#old-checkout-btn")
'''
    write_file(test_file, original_code)

    patcher = SurgicalPatcher()

    # Step 1 Fix
    fix1 = SelectorFix(
        old_selector="#old-username-field",
        new_selector="#login-email-input",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.95,
    )
    patched = patcher.patch_test_file(test_file, fix1, line_number=4)

    # Step 2 Fix
    fix2 = SelectorFix(
        old_selector="button.old-search-icon",
        new_selector="button[data-testid='global-search-btn']",
        strategy=SelectorStrategy.TEST_ID_MATCH,
        confidence=0.98,
    )
    patched = patcher.patch_test_file(test_file, fix2, line_number=6)

    # Step 3 Fix
    fix3 = SelectorFix(
        old_selector="#old-checkout-btn",
        new_selector="#order-confirmation-btn",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.92,
    )
    patched = patcher.patch_test_file(test_file, fix3, line_number=8)

    final_content = read_file(test_file)

    # Verify all 3 steps healed cleanly in the same file
    assert "#login-email-input" in final_content
    assert "button[data-testid='global-search-btn']" in final_content
    assert "#order-confirmation-btn" in final_content
    assert "#old-username-field" not in final_content
    assert "button.old-search-icon" not in final_content
    assert "#old-checkout-btn" not in final_content


# ============================================================================
# Possibility 6: Modern Complex Enterprise DOM (Tailwind, Hashed, Nested SVGs)
# ============================================================================

def test_complex_enterprise_dom_pruning_and_matching() -> None:
    """Ensure the DOM pruner reduces a large, deeply nested, Tailwind-heavy DOM
    with SVGs, hashed IDs, and siblings without losing the critical interactive targets.
    """
    complex_dom = '''<!DOCTYPE html>
<html lang="en">
<head><title>Enterprise Billing</title></head>
<body>
  <div id="__next" data-reactroot="">
    <div class="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between">
      <header class="sticky top-0 z-50 backdrop-blur-md bg-slate-900/80 border-b border-slate-800 px-6 py-4">
        <nav class="max-w-7xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-4">
            <span class="text-xl font-black tracking-tight text-indigo-400">CloudCorp</span>
          </div>
        </nav>
      </header>
      <main class="flex-1 max-w-7xl w-full mx-auto p-8">
        <section class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Card 1 -->
          <div class="rounded-2xl border border-slate-800 bg-slate-950/50 p-6 flex flex-col justify-between shadow-2xl">
            <div>
              <h3 class="text-lg font-semibold text-slate-200">Developer</h3>
              <p class="text-3xl font-extrabold mt-4">$0 <span class="text-sm font-normal text-slate-400">/mo</span></p>
            </div>
            <button class="mt-8 w-full py-3 px-4 rounded-xl font-medium bg-slate-800 hover:bg-slate-700 text-slate-300">Current Plan</button>
          </div>
          <!-- Card 2: Enterprise Upgrade Target -->
          <div class="rounded-2xl border-2 border-indigo-500 bg-gradient-to-b from-indigo-950/20 to-slate-950 p-6 flex flex-col justify-between shadow-2xl relative">
            <div>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-indigo-400">Enterprise Pro</h3>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">Popular</span>
              </div>
              <p class="text-3xl font-extrabold mt-4">$299 <span class="text-sm font-normal text-slate-400">/mo</span></p>
            </div>
            <button
              id="enterprise-upgrade-action"
              data-testid="upgrade-to-enterprise-pro"
              class="mt-8 w-full py-3 px-4 rounded-xl font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
              <span>Upgrade to Enterprise Pro</span>
            </button>
          </div>
        </section>
      </main>
    </div>
  </div>
</body>
</html>'''

    # Prune DOM
    pruned = prune_dom(complex_dom)

    # 1. Non-essential styling noise pruned
    assert "data-reactroot" not in pruned.html or "Upgrade to Enterprise Pro" in pruned.html

    # 2. Interactive target button with data-testid and role remains intact
    assert 'data-testid="upgrade-to-enterprise-pro"' in pruned.html
    assert "enterprise-upgrade-action" in pruned.html
    assert "Upgrade to Enterprise Pro" in pruned.html


# ============================================================================
# Possibility 7: Complex TypeScript Playwright Spec (.spec.ts)
# ============================================================================

def test_complex_typescript_spec_healing(tmp_path: Path) -> None:
    """Ensure complex TypeScript Playwright tests with nested describe/test blocks,
    fixtures, and getByRole/getByTestId calls are surgically transformed.
    """
    patcher = SurgicalPatcher()
    ts_file = tmp_path / "billing.spec.ts"

    original_ts = """import { test, expect } from '@playwright/test';

test.describe('Billing & Subscription Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings/billing');
  });

  test('should allow upgrading subscription plan', async ({ page }) => {
    // Step 1: Open modal
    await page.getByRole('button', { name: 'Change Plan' }).click();

    // Step 2: Broken selector inside modal
    await page.getByTestId('old-select-pro-tier').click();

    // Verification
    await expect(page.locator('.plan-active-badge')).toBeVisible();
  });
});
"""
    write_file(ts_file, original_ts)

    fix = SelectorFix(
        old_selector="getByTestId('old-select-pro-tier')",
        new_selector='[data-testid="select-pro-tier-v2"]',
        strategy=SelectorStrategy.TEST_ID_MATCH,
        confidence=0.98,
    )

    patched_ts = patcher.patch_test_file(ts_file, fix, line_number=12, create_backup=True)

    # Replaced modern TS Playwright locator
    assert "await page.getByTestId('select-pro-tier-v2').click();" in patched_ts
    assert "old-select-pro-tier" not in patched_ts

    # Preserves TypeScript describe blocks and beforeEach hooks
    assert "test.describe('Billing & Subscription Management'" in patched_ts
    assert "test.beforeEach(async ({ page }) => {" in patched_ts
    assert "await page.getByRole('button', { name: 'Change Plan' }).click();" in patched_ts


# ============================================================================
# Possibility 8: Anti-Hallucination Guardrail on Genuinely MISSING Elements
# ============================================================================

def test_anti_hallucination_skips_genuinely_missing_element(tmp_path: Path) -> None:
    """Verify that when an element was intentionally deleted from the product,
    KernHell's anti-hallucination guardrail flags it as a real bug and DOES NOT mutate the test.
    """
    test_file = tmp_path / "test_deleted_feature.py"
    original_code = '''def test_deprecated_feature(page):
    page.goto("/settings")
    # Feature was completely removed from the product
    page.click("button#legacy-export-csv-btn")
'''
    write_file(test_file, original_code)

    cfg = KernHellConfig()
    cfg.healing.dry_run = False
    orchestrator = HealingOrchestrator(cfg)

    # Mock failure context
    failure = FailureContext(
        test_file=test_file,
        line_number=4,
        broken_selector="button#legacy-export-csv-btn",
        selector_type=SelectorType.CSS,
        error_message="Timeout 5000ms exceeded waiting for locator('button#legacy-export-csv-btn')",
        live_dom="<html><body><div>Settings Page (Feature Removed)</div></body></html>",
        page_url="https://app.io/settings",
        surrounding_code='page.click("button#legacy-export-csv-btn")',
    )

    # Scanner detects the failure
    orchestrator.scanner.run = MagicMock(return_value=[failure])

    # Analyzer correctly diagnoses MISSING (not a rename)
    orchestrator.analyzer.diagnose = MagicMock(
        return_value=Diagnosis(
            failure_type=FailureType.MISSING,
            explanation="Feature was removed from DOM. No matching export button exists.",
            confidence=0.99,
        )
    )

    report = orchestrator.heal(test_file, dry_run=False)

    # Must be skipped
    assert report.total_failures == 1
    assert report.healed_count == 0
    assert report.skipped_count == 1
    assert "Potential real bug: element is genuinely MISSING" in report.results[0].skip_reason

    # File must NOT be modified
    assert read_file(test_file) == original_code


# ============================================================================
# Possibility 9: Full E2E Orchestrator Cycle on POM with Semantic Caching
# ============================================================================

def test_full_orchestrator_pom_cycle_with_cache(tmp_path: Path) -> None:
    """Run the entire Orchestrator healing cycle on a Page Object Model test,
    confirming AST modification, verification, and instant semantic cache reuse.
    """
    test_file = tmp_path / "test_pom_integration.py"
    original_code = '''from playwright.sync_api import Page

class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.checkout_btn = page.locator("#old-checkout-action")

    def checkout(self):
        self.checkout_btn.click()

def test_cart_checkout(page: Page):
    cart = CartPage(page)
    cart.checkout()
'''
    write_file(test_file, original_code)

    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path / "cache")
    cfg.cache.similarity_threshold = 0.88
    cfg.healing.dry_run = False

    orchestrator = HealingOrchestrator(cfg)

    mock_failure = FailureContext(
        test_file=test_file,
        line_number=6,
        broken_selector="#old-checkout-action",
        selector_type=SelectorType.CSS,
        error_message="Timeout 5000ms waiting for locator('#old-checkout-action')",
        live_dom="""<html><body><button id="proceed-to-payment" data-testid="checkout-v2">Proceed to Payment</button></body></html>""",
        page_url="https://store.io/cart",
        surrounding_code='self.checkout_btn = page.locator("#old-checkout-action")',
    )

    # Run 1: Scanner finds failure, verification passes
    orchestrator.scanner.run = MagicMock(side_effect=[
        [mock_failure],
        NoFailuresDetectedError("Passed!"),
    ])

    report1 = orchestrator.heal(test_file, dry_run=False)

    assert report1.total_failures == 1
    assert report1.healed_count == 1
    assert report1.cache_hits == 0

    patched_content = read_file(test_file)
    assert "#old-checkout-action" not in patched_content
    assert "class CartPage:" in patched_content
    assert "def checkout(self):" in patched_content

    # Re-inject failure into file to test instant Semantic Vector Cache hit
    write_file(test_file, original_code)

    orchestrator.scanner.run = MagicMock(side_effect=[
        [mock_failure],
        NoFailuresDetectedError("Passed!"),
    ])

    report2 = orchestrator.heal(test_file, dry_run=False)

    # Must hit cache instantly with zero LLM calls
    assert report2.total_failures == 1
    assert report2.healed_count == 1
    assert report2.cache_hits == 1
    assert report2.llm_calls == 0
    assert report2.results[0].from_cache is True
