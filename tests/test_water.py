from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
        # page.goto("http://localhost:3000/water")
            page.goto("http://localhost:3000/water", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        # Verify page loaded
        assert page.title() == "Water"

        # Interact with elements
        page.click("text='Dashboard'")
        page.wait_for_load_state("networkidle")
        assert page.title() == "Dashboard"

        # page.goto("http://localhost:3000/water")
        page.goto("http://localhost:3000/water", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")

        page.click("text='Trends'")
        page.wait_for_load_state("networkidle")
        assert page.title() == "Trends"

        # page.goto("http://localhost:3000/water")
        page.goto("http://localhost:3000/water", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")

        page.click("text='Water Quality'")
        page.wait_for_load_state("networkidle")
        assert page.title() == "Water"

        # page.goto("http://localhost:3000/water")
        page.goto("http://localhost:3000/water", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")

        page.click("text='Village Map'")
        page.wait_for_load_state("networkidle")
        assert page.title() == "Map"

        # page.goto("http://localhost:3000/water")
        page.goto("http://localhost:3000/water", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")

        page.click("text='Data Entry'")
        page.wait_for_load_state("networkidle")
        assert page.title() == "Input"

        # page.goto("http://localhost:3000/water")
        page.goto("http://localhost:3000/water", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")

        page.click("text='Education'")
        page.wait_for_load_state("networkidle")
        assert page.title() == "Education"

        browser.close()

if __name__ == "__main__":
    run()
