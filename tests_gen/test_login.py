from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        # page.goto("http://localhost:3000/Login")
        
        try:
        # page.goto("http://localhost:3000", timeout=30000)
            page.goto("http://localhost:3000", timeout=30000)
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        # Verify page loaded
        try:
        # page.wait_for_selector("h1", has_text="Welcome Back")
            page.wait_for_selector("h1", has_text="Welcome Back")
        except Exception as e:
            print(f"Failed to find welcome back text: {e}")
            browser.close()
            return

        # Interact with email input
        email_input = page.query_selector("[data-testid='email-input']")
        if email_input:
        # email_input.fill("test@example.com")
            email_input.fill("test@example.com")
        else:
            print("Failed to find email input")
            browser.close()
            return

        # Interact with password input
        password_input = page.query_selector("[data-testid='password-input']")
        if password_input:
        # password_input.fill("password123")
            password_input.fill("password123")
        else:
            print("Failed to find password input")
            browser.close()
            return

        # Interact with sign in button
        sign_in_button = page.query_selector("#login-btn")
        # sign_in_button.click()
        if sign_in_button:
            sign_in_button.click()
        else:
            print("Failed to find sign in button")
            browser.close()
            return

        # Verify forgot password link
        forgot_password_link = page.query_selector("text='Forgot Password?'")
        # forgot_password_link.click()
        if forgot_password_link:
            forgot_password_link.click()
        # page.wait_for_load_state("networkidle")
            page.wait_for_load_state("networkidle")
        else:
            print("Failed to find forgot password link")
            browser.close()
            return

        # Verify forgot password page loaded
        try:
        # page.wait_for_selector("h1")
            page.wait_for_selector("h1")
        except Exception as e:
            print(f"Failed to find forgot password page: {e}")
            browser.close()
            return

        time.sleep(5)  # wait for 5 seconds before closing the browser
        browser.close()

if __name__ == "__main__":
    run()
