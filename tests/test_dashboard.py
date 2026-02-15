from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
        # page.goto("http://localhost:3000/dashboard")
            page.goto("http://localhost:3000/dashboard", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Failed to navigate to http://localhost:3000/dashboard: {e}")
            browser.close()
            return

        # Verify Dashboard link
        dashboard_link = page.query_selector('text="Dashboard"')
        assert dashboard_link is not None

        # Verify Trends link
        trends_link = page.query_selector('text="Trends"')
        assert trends_link is not None

        # Verify Water Quality link
        water_quality_link = page.query_selector('text="Water Quality"')
        assert water_quality_link is not None

        # Verify Village Map link
        village_map_link = page.query_selector('text="Village Map"')
        assert village_map_link is not None

        # Verify Data Entry link
        data_entry_link = page.query_selector('text="Data Entry"')
        assert data_entry_link is not None

        # Verify Education link
        education_link = page.query_selector('text="Education"')
        assert education_link is not None

        # Click on Trends link
        trends_link = page.query_selector('text="Trends"')
        trends_link.click()
        page.wait_for_load_state("networkidle")

        # Click on Water Quality link
        # page.goto("http://localhost:3000/dashboard")
        # page.wait_for_load_state("networkidle")
        water_quality_link = page.query_selector('text="Water Quality"')
        water_quality_link.click()
        page.wait_for_load_state("networkidle")

        # Click on Village Map link
        # page.goto("http://localhost:3000/dashboard")
        # page.wait_for_load_state("networkidle")
        village_map_link = page.query_selector('text="Village Map"')
        village_map_link.click()
        page.wait_for_load_state("networkidle")

        # Click on Data Entry link
        # page.goto("http://localhost:3000/dashboard")
        # page.wait_for_load_state("networkidle")
        data_entry_link = page.query_selector('text="Data Entry"')
        data_entry_link.click()
        page.wait_for_load_state("networkidle")

        # Click on Education link
        # page.goto("http://localhost:3000/dashboard")
        # page.wait_for_load_state("networkidle")
        education_link = page.query_selector('text="Education"')
        education_link.click()
        page.wait_for_load_state("networkidle")

        browser.close()

if __name__ == "__main__":
    run()
