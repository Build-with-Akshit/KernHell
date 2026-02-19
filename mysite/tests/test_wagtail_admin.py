"""
Wagtail CMS Admin Tests — KernHell Self-Healing Demo
=====================================================
Target: Wagtail CMS (17,000+ GitHub stars)
Used by: NASA, Google, NHS, Mozilla, MIT

10 Playwright tests:
    4 WORKING  (control group)
    6 BUGGY    (intentional failures — KernHell will fix these)

Bug Categories:
    - Wrong selector (CSS class/ID changed)
    - Wrong text content (menu renamed)
    - Missing interaction step (hover/dropdown)
    - Timing issue (no wait after navigation)
    - Wrong URL path
    - Stale element reference

Run:    pytest test_wagtail_admin.py -v
Heal:   kernhell heal test_wagtail_admin.py
"""

from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:8000"
ADMIN_URL = f"{BASE_URL}/admin/"
USERNAME = "admin"
PASSWORD = "pass"


# ===========================================================
#  HELPER: Reusable login (used by "logged_in" tests)
# ===========================================================

def _do_login(page: Page):
    page.goto(f"{ADMIN_URL}login/")
    page.fill("#id_username", USERNAME)
    page.fill("#id_password", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")


# ===========================================================
#  WORKING TESTS  (4 tests — these PASS out-of-the-box)
# ===========================================================

def test_01_admin_login_success(page: Page):
    """WORKING: Admin can login and reach dashboard."""
    page.goto(f"{ADMIN_URL}login/")
    page.fill("#id_username", USERNAME)
    page.fill("#id_password", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    # Dashboard URL stays /admin/
    expect(page).to_have_url(f"{ADMIN_URL}")


def test_02_invalid_login_shows_error(page: Page):
    """WORKING: Wrong credentials show an error message."""
    page.goto(f"{ADMIN_URL}login/")
    page.fill("#id_username", "hacker")
    page.fill("#id_password", "wrong")
    page.click("button[type='submit']")
    page.wait_for_timeout(1000)

    error = page.locator(".error-message, .help-block, .errorlist, .w-field__errors")
    expect(error.first).to_be_visible()


def test_03_navigate_to_pages_explorer(page: Page):
    """WORKING: Navigate to Pages section via direct URL."""
    _do_login(page)
    page.goto(f"{BASE_URL}/admin/pages/3/")
    page.wait_for_load_state("networkidle")

    # The explorer should show a table/listing
    listing = page.locator("table, .listing, tbody, .w-slim-header")
    expect(listing.first).to_be_visible()


def test_04_create_and_publish_page(page: Page):
    """WORKING: Full page creation workflow — login, add child, fill title, publish."""
    _do_login(page)

    # Navigate to Home page explorer
    page.goto(f"{BASE_URL}/admin/pages/3/")
    page.wait_for_load_state("networkidle")

    # Click "Add child page"
    page.click("a[aria-label='Add child page']")
    page.wait_for_load_state("networkidle")

    # Fill title
    page.wait_for_selector("#id_title")
    page.fill("#id_title", "Working Test Page")

    # Publish via dropdown
    page.click("button:has-text('More actions')")
    page.wait_for_timeout(300)
    page.click("button[name='action-publish']")
    page.wait_for_load_state("networkidle")

    # Should redirect back to explorer
    expect(page).not_to_have_url(f"{BASE_URL}/admin/pages/3/edit/")


# ===========================================================
#  BUGGY TESTS  (6 tests — KernHell will heal these)
# ===========================================================

def test_05_login_wrong_button_selector(page: Page):
    """BUG: Wrong login button selector.
    
    Real selector: button[type='submit']
    Broken with:   .submit-login-button  (does not exist)
    Fix type:      Selector correction
    """
    page.goto(f"{ADMIN_URL}login/")
    page.fill("#id_username", USERNAME)
    page.fill("#id_password", PASSWORD)

    # INTENTIONAL BUG: This class does not exist
    page.click(".submit-login-button")

    page.wait_for_timeout(1000)
    expect(page).to_have_url(f"{ADMIN_URL}")


def test_06_navigate_images_wrong_selector(page: Page):
    """BUG: Wrong sidebar navigation selector for Images.
    
    Real selector: a[href='/admin/images/'] or text=Images
    Broken with:   .nav-images-link  (old class, does not exist)
    Fix type:      Selector correction
    """
    _do_login(page)

    # INTENTIONAL BUG: Old CSS class that doesn't exist
    page.click(".nav-images-link")

    page.wait_for_timeout(1000)
    expect(page).to_have_url(f"{BASE_URL}/admin/images/")


def test_07_documents_timing_bug(page: Page):
    """BUG: Clicks sidebar before page fully loads (race condition).
    
    Missing: page.wait_for_load_state('networkidle') after login
    Fix type:      Add wait / timing fix
    """
    page.goto(f"{ADMIN_URL}login/")
    page.fill("#id_username", USERNAME)
    page.fill("#id_password", PASSWORD)
    page.click("button[type='submit']")

    # INTENTIONAL BUG: No wait! Sidebar may not be rendered yet
    page.click("text=Documents")

    page.wait_for_timeout(500)
    listing = page.locator(".listing, table, tbody")
    expect(listing.first).to_be_visible()


def test_08_search_wrong_field_id(page: Page):
    """BUG: Wrong search input selector.
    
    Real selector: input[type='search'] or input[name='q']
    Broken with:   #search-box-old  (ID does not exist)
    Fix type:      Selector correction
    """
    _do_login(page)

    # INTENTIONAL BUG: This ID doesn't exist
    search = page.locator("#search-box-old")
    search.fill("Welcome")
    search.press("Enter")

    page.wait_for_timeout(1000)


def test_09_click_renamed_menu_item(page: Page):
    """BUG: Menu item text changed between versions.
    
    Real text:   "Images"
    Broken with: "Media Library"  (old text that no longer exists)
    Fix type:      Text/semantic correction
    """
    _do_login(page)

    # INTENTIONAL BUG: "Media Library" was the old name; it's "Images" now
    page.click("text=Media Library")

    page.wait_for_timeout(1000)


def test_10_settings_wrong_class(page: Page):
    """BUG: Settings dropdown trigger class changed.
    
    Real trigger: Account icon / user menu
    Broken with:  .settings-dropdown-toggle  (class doesn't exist)
    Fix type:      Selector correction
    """
    _do_login(page)

    # INTENTIONAL BUG: Old class name
    page.click(".settings-dropdown-toggle")

    page.wait_for_timeout(500)
    dropdown = page.locator(".dropdown-menu, .w-dropdown, .tippy-content")
    expect(dropdown.first).to_be_visible()
