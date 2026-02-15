from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify page loaded
            # Verify page loaded
        # assert page.title() == ""
            assert page.title() != ""

        # Interact with elements
            # Interact with elements
        # page.click("text='Dashboard'")
            page.click("text='Dashboard'")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # assert page.url == "http://localhost:3000/dashboard"
            assert page.url == "http://localhost:3000/dashboard"

        # page.click("text='Trends'")
            page.click("text='Trends'")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # assert page.url == "http://localhost:3000/trends"
            assert page.url == "http://localhost:3000/trends"

        # page.click("text='Water Quality'")
            page.click("text='Water Quality'")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # assert page.url == "http://localhost:3000/water"
            assert page.url == "http://localhost:3000/water"

        # page.click("text='Village Map'")
            page.click("text='Village Map'")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # assert page.url == "http://localhost:3000/map"
            assert page.url == "http://localhost:3000/map"

        # page.click("text='Data Entry'")
            page.click("text='Data Entry'")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # assert page.url == "http://localhost:3000/input"
            assert page.url == "http://localhost:3000/input"

        # page.click("text='Education'")
            page.click("text='Education'")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # assert page.url == "http://localhost:3000/education"
            assert page.url == "http://localhost:3000/education"

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
        # browser.close()
            browser.close()

if __name__ == "__main__":
    run()
