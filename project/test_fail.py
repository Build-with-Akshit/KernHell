from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

# 
#
        # print("Opening Google...")
        # print("Opening Google...")
        page.goto("https://www.google.com")

# 
#
#
        # search_input = page.query_selector("input[name='q']")
        
# 
#
        # print("Waiting for search input to be visible...")
        # print("Waiting for search input to be visible...")
        # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] search_input = page.query_selector("input[name='q']")
        # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] page.wait_for_selector("input[name='q']", state="visible")
        # [KERNHELL-FIX-OLD] page.wait_for_selector("input[name='q']", timeout=60000)
        # page.wait_for_selector("input[name='q']", timeout=30000)
        page.wait_for_selector("input[name='q']", state="visible")

# 
#
        # print("Trying to search for something...")
        # print("Trying to search for something...")
        # [KERNHELL-FIX-OLD] search_input = page.query_selector("input[name='q']")
        page.fill("input[name='q']", "Playwright")
        # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] print("Trying to click the button...")
        # print("Trying to click the search button...")
        # print("Trying to click the button...")
        # print("Trying to click the button...")
        # page.click("input[name='btnK']")
        page.click("input[name='btnK']")
        page.wait_for_timeout(5000)

# 
#
#
        # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # Error: Yeh ID exist nahi karti
        # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] # [KERNHELL-FIX-OLD] page.click("#made_up_button_id_123")
        
# 
#
#
#
#
#
#
#
        # print("Success!")
        # print("Success!")
        # page.wait_for_timeout(5000)  # wait for 5 seconds
        # page.wait_for_timeout(5000)  # wait for 5 seconds
        # page.wait_for_timeout(5000)

# 
        browser.close()

if __name__ == "__main__":
    run()
