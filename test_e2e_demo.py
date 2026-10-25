from playwright.sync_api import sync_playwright

def test_purchase():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Page par button ka id 'purchase-btn' hai
        page.set_content('<button id="purchase-btn" data-testid="order now">order now</button>')

        # Lekin test purana '[data-testid="complete-order-btn"]' dhundh raha hai
        page.click('[data-testid="order now"]')
        browser.close()
