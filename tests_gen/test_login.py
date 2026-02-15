from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://localhost:3000/Login")
        page.wait_for_load_state("networkidle")

        # Verify page loaded
        page.wait_for_selector("h1", has_text="Welcome Back")

        # Interact with email input
        email_input = page.query_selector("[data-testid='email-input']")
        email_input.fill("test@example.com")

        # Interact with password input
        password_input = page.query_selector("[data-testid='password-input']")
        password_input.fill("password123")

        # Interact with sign in button
        sign_in_button = page.query_selector("#login-btn")
        sign_in_button.click()

        # Verify forgot password link
        forgot_password_link = page.query_selector("text='Forgot Password?'")
        forgot_password_link.click()
        page.wait_for_load_state("networkidle")

        # Verify forgot password page loaded
        page.wait_for_selector("h1")

        browser.close()

if __name__ == "__main__":
    run()