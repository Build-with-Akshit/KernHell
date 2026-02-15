from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # page.goto("http://localhost:3000/trends")
        try:
        # page.goto("http://localhost:3000/trends", wait_until="networkidle")
            page.goto("http://localhost:3000/trends", wait_until="networkidle", timeout=30000)
        # page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Error navigating to trends page: {e}")
            browser.close()
            return

        time.sleep(2)

        # Verify Trends page loads
        assert page.url == "http://localhost:3000/trends"

        # Verify navigation links
        dashboard_link = page.query_selector('text="Dashboard"')
        trends_link = page.query_selector('text="Trends"')
        water_quality_link = page.query_selector('text="Water Quality"')
        village_map_link = page.query_selector('text="Village Map"')
        data_entry_link = page.query_selector('text="Data Entry"')
        education_link = page.query_selector('text="Education"')

        assert dashboard_link is not None
        assert trends_link is not None
        assert water_quality_link is not None
        assert village_map_link is not None
        assert data_entry_link is not None
        assert education_link is not None

        # Interact with navigation links
        trends_link.click()
        page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/trends"

        dashboard_link = page.query_selector('text="Dashboard"')
        dashboard_link.click()
        page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/dashboard"

        # page.goto("http://localhost:3000/trends")
        page.goto("http://localhost:3000/trends", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        time.sleep(2)

        water_quality_link = page.query_selector('text="Water Quality"')
        water_quality_link.click()
        page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/water"

        # page.goto("http://localhost:3000/trends")
        page.goto("http://localhost:3000/trends", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        time.sleep(2)

        village_map_link = page.query_selector('text="Village Map"')
        village_map_link.click()
        page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/map"

        # page.goto("http://localhost:3000/trends")
        page.goto("http://localhost:3000/trends", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        time.sleep(2)

        data_entry_link = page.query_selector('text="Data Entry"')
        data_entry_link.click()
        page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/input"

        # page.goto("http://localhost:3000/trends")
        page.goto("http://localhost:3000/trends", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        time.sleep(2)

        education_link = page.query_selector('text="Education"')
        education_link.click()
        page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/education"

        browser.close()

if __name__ == "__main__":
    run()
