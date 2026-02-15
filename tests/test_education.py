from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
        # page.goto("http://localhost:3000/education")
            page.goto("http://localhost:3000/education", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Failed to navigate to http://localhost:3000/education: {str(e)}")
            browser.close()
            return

        # Verify page loaded
        assert page.title() == "Education"

        # Interact with elements
        dashboard_link = page.query_selector("text='Dashboard'")
        trends_link = page.query_selector("text='Trends'")
        water_quality_link = page.query_selector("text='Water Quality'")
        village_map_link = page.query_selector("text='Village Map'")
        data_entry_link = page.query_selector("text='Data Entry'")
        education_link = page.query_selector("text='Education'")

        # Verify links are visible
        assert dashboard_link.is_visible()
        assert trends_link.is_visible()
        assert water_quality_link.is_visible()
        assert village_map_link.is_visible()
        assert data_entry_link.is_visible()
        assert education_link.is_visible()

        # Click on links
        dashboard_link.click()
        page.wait_for_load_state("networkidle")
        assert page.title() == "Dashboard"

        # page.goto("http://localhost:3000/education")
        page.goto("http://localhost:3000/education", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        trends_link.click()
        page.wait_for_load_state("networkidle")
        assert page.title() == "Trends"

        # page.goto("http://localhost:3000/education")
        page.goto("http://localhost:3000/education", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        water_quality_link.click()
        page.wait_for_load_state("networkidle")
        assert page.title() == "Water Quality"

        # page.goto("http://localhost:3000/education")
        page.goto("http://localhost:3000/education", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        village_map_link.click()
        page.wait_for_load_state("networkidle")
        assert page.title() == "Village Map"

        # page.goto("http://localhost:3000/education")
        page.goto("http://localhost:3000/education", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        data_entry_link.click()
        page.wait_for_load_state("networkidle")
        assert page.title() == "Data Entry"

        # page.goto("http://localhost:3000/education")
        page.goto("http://localhost:3000/education", wait_until="networkidle")
        # page.wait_for_load_state("networkidle")
        education_link.click()
        page.wait_for_load_state("networkidle")
        assert page.title() == "Education"

        browser.close()

if __name__ == "__main__":
    run()
