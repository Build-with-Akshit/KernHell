"""
Demo test with an intentionally broken selector.
Run: kernhell heal demo_tests/test_broken.py
"""
from playwright.sync_api import sync_playwright


def test_google_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to Google
        page.goto("https://www.google.com")

        # This selector is INTENTIONALLY WRONG - KernHell should fix it
        page.fill("#search-box-that-doesnt-exist", "KernHell self healing")

        # Click a button that doesn't exist
        page.click("#wrong-submit-button")

        browser.close()


if __name__ == "__main__":
    test_google_search()
