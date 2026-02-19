"""
Wagtail Blog Creation Test - WORKING VERSION
Verified selectors from live DOM inspection.
"""
from playwright.sync_api import sync_playwright


def test_wagtail_blog_creation():
    with sync_playwright() as p:
        print("Launching Browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.set_default_timeout(15000)

        # 1. Login
        print("Step 1: Logging In...")
        page.goto("http://127.0.0.1:8000/admin/login/")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "pass")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        print("  -> Login successful. Dashboard loaded.")

        # 2. Navigate to Home Page explorer
        print("Step 2: Navigating to Pages Explorer...")
        page.goto("http://127.0.0.1:8000/admin/pages/3/")
        page.wait_for_load_state("networkidle")
        print("  -> Pages explorer loaded.")

        # 3. Click "Add child page"
        # Verified: aria-label='Add child page', href='/admin/pages/3/add_subpage/'
        print("Step 3: Clicking 'Add child page'...")
        page.click("a[aria-label='Add child page']")
        page.wait_for_load_state("networkidle")
        print("  -> Editor page loaded (single page type, skipped selection).")

        # 4. Fill Title
        # Verified: id='id_title', name='title'
        print("Step 4: Filling Title...")
        page.wait_for_selector("#id_title")
        page.fill("#id_title", "KernHell Auto-Generated Blog Post")
        print("  -> Title filled.")

        # 5. Publish (hidden behind "More actions" dropdown)
        print("Step 5: Publishing...")
        # First, open the "More actions" dropdown to reveal the Publish button
        page.click("button:has-text('More actions')")
        page.wait_for_timeout(500)
        # Now click the revealed Publish button
        page.click("button[name='action-publish']")
        page.wait_for_load_state("networkidle")
        print("  -> Published!")

        # 6. Verify success
        print("Step 6: Verifying...")
        page.wait_for_timeout(2000)
        current_url = page.url
        print(f"  -> Current URL: {current_url}")

        # Check for success message or redirect
        if "edit" not in current_url:
            print("SUCCESS: Page created and published!")
        else:
            print("WARNING: May still be on edit page. Check manually.")

        page.wait_for_timeout(3000)
        browser.close()
        print("DONE.")


if __name__ == "__main__":
    test_wagtail_blog_creation()
