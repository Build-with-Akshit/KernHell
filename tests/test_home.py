from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify Dashboard link
            # Verify Dashboard link
        # dashboard_link = page.query_selector("text='Dashboard'")
            dashboard_link = page.query_selector("text='Dashboard'")
        # assert dashboard_link is not None
            assert dashboard_link is not None
        # dashboard_link.click()
            dashboard_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify Trends link
            # Verify Trends link
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # trends_link = page.query_selector("text='Trends'")
            trends_link = page.query_selector("text='Trends'")
        # assert trends_link is not None
            assert trends_link is not None
        # trends_link.click()
            trends_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify Water Quality link
            # Verify Water Quality link
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # water_quality_link = page.query_selector("text='Water Quality'")
            water_quality_link = page.query_selector("text='Water Quality'")
        # assert water_quality_link is not None
            assert water_quality_link is not None
        # water_quality_link.click()
            water_quality_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify Village Map link
            # Verify Village Map link
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # village_map_link = page.query_selector("text='Village Map'")
            village_map_link = page.query_selector("text='Village Map'")
        # assert village_map_link is not None
            assert village_map_link is not None
        # village_map_link.click()
            village_map_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify Data Entry link
            # Verify Data Entry link
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # data_entry_link = page.query_selector("text='Data Entry'")
            data_entry_link = page.query_selector("text='Data Entry'")
        # assert data_entry_link is not None
            assert data_entry_link is not None
        # data_entry_link.click()
            data_entry_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

        # Verify Education link
            # Verify Education link
        # page.goto("http://localhost:3000/")
            page.goto("http://localhost:3000/")
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        # education_link = page.query_selector("text='Education'")
            education_link = page.query_selector("text='Education'")
        # assert education_link is not None
            assert education_link is not None
        # education_link.click()
            education_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")

# 
#
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
        # browser.close()
            browser.close()

if __name__ == "__main__":
    run()
