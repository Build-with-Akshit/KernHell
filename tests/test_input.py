from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # page = browser.new_page()
        context = browser.new_context()
        page = context.new_page()
        
        try:
        # page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
            page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
        # page.goto("http://localhost:3000/input")
        # page.wait_for_load_state("networkidle")
        # page.wait_for_load_state("networkidle", timeout=30000)
        except Exception as e:
            print(f"Failed to navigate to http://localhost:3000/input: {e}")
            browser.close()
            return

        # Verify page loaded
        assert page.title() == "React App"

        # Interact with elements
        dashboard_link = page.query_selector("text='Dashboard'")
        trends_link = page.query_selector("text='Trends'")
        water_quality_link = page.query_selector("text='Water Quality'")
        village_map_link = page.query_selector("text='Village Map'")
        data_entry_link = page.query_selector("text='Data Entry'")
        education_link = page.query_selector("text='Education'")

        assert dashboard_link is not None
        assert trends_link is not None
        assert water_quality_link is not None
        assert village_map_link is not None
        assert data_entry_link is not None
        assert education_link is not None

        # Click on links
        # with page.expect_navigation():
        with page.expect_navigation(wait_until="networkidle"):
        # dashboard_link.click()
            dashboard_link.click()
        # page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/dashboard"

        page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
        # page.goto("http://localhost:3000/input")
        # page.wait_for_load_state("networkidle")
        # page.wait_for_load_state("networkidle", timeout=30000)
        # with page.expect_navigation():
        with page.expect_navigation(wait_until="networkidle"):
        # trends_link.click()
            trends_link.click()
        # page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/trends"

        page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
        # page.goto("http://localhost:3000/input")
        # page.wait_for_load_state("networkidle")
        # page.wait_for_load_state("networkidle", timeout=30000)
        # with page.expect_navigation():
        with page.expect_navigation(wait_until="networkidle"):
        # water_quality_link.click()
            water_quality_link.click()
        # page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/water"

        page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
        # page.goto("http://localhost:3000/input")
        # page.wait_for_load_state("networkidle")
        # page.wait_for_load_state("networkidle", timeout=30000)
        # with page.expect_navigation():
        with page.expect_navigation(wait_until="networkidle"):
        # village_map_link.click()
            village_map_link.click()
        # page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/map"

        page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
        # page.goto("http://localhost:3000/input")
        # page.wait_for_load_state("networkidle")
        # page.wait_for_load_state("networkidle", timeout=30000)
        # with page.expect_navigation():
        with page.expect_navigation(wait_until="networkidle"):
        # data_entry_link.click()
            data_entry_link.click()
        # page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/input"

        page.goto("http://localhost:3000/input", wait_until="networkidle", timeout=30000)
        # page.goto("http://localhost:3000/input")
        # page.wait_for_load_state("networkidle")
        # page.wait_for_load_state("networkidle", timeout=30000)
        # with page.expect_navigation():
        with page.expect_navigation(wait_until="networkidle"):
        # education_link.click()
            education_link.click()
        # page.wait_for_load_state("networkidle")
        assert page.url == "http://localhost:3000/education"

        browser.close()

if __name__ == "__main__":
    run()
