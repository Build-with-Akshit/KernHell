from playwright.sync_api import sync_playwright
import time

def run():
    print("Opening Page...")
    # Simulate a Playwright Timeout
    # raise Exception("TimeoutError: Waiting for selector '#made_up_id'")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.example.com")
        try:
            page.wait_for_selector("#existing_id", timeout=5000)
            print("Selector found")
        except Exception as e:
            print(f"Error: {e}")
        browser.close()

if __name__ == "__main__":
    run()
