"""Sample Playwright test file representing a standard checkout automation flow.

This test is intentionally designed to target `#buy-now`. When run against
the refactored DOM (`sample_dom_renamed.html`), it will fail with a selector timeout.
"""

from playwright.sync_api import Page, expect


def test_checkout_purchase_flow(page: Page) -> None:
    # Navigates to the checkout page
    page.goto("https://example.com/checkout")

    # Fill customer info
    page.fill("#email-input", "buyer@example.com")
    page.fill("#address-input", "123 Innovation Way")

    # Intentionally broken selector when refactored: #buy-now
    page.click("#buy-now")

    # Verification expectation
    expect(page.locator(".order-success")).to_be_visible()
