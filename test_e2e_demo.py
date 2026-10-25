from playwright.sync_api import sync_playwright

def test_purchase():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Page has refactored button: id='purchase-btn' and data-testid='complete-order-btn'
        page.set_content('<button id="purchase-btn" data-testid="complete-order-btn">Place Your Order</button>')

        # Broken selector that needs healing:
        page.click('[data-testid="complete-order-btn"]')
        browser.close()
