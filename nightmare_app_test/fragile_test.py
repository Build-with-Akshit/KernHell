# fragile_test.py - Intentionally broken test for KernHell demo
# fragile_test.py - Fixed test for KernHell demo
from playwright.sync_api import sync_playwright
from pathlib import Path
import sys

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Use headless for speed
        page = browser.new_page()
        
        # Load the nightmare app (resolve path relative to this script)
        html_file = Path(__file__).parent / "nightmare_app.html"
        page.goto(f"file:///{html_file.resolve()}")
        
        print("[*] Test Started: Trying to Save Settings...")
        
        # Check if the search field exists before trying to fill it
        if page.query_selector("#search-field"):
        # --- THE TRAP ---
        # Script is looking for a BUTTON with ID 'save-btn'
        # OR a button with text 'Save Changes'
        # BUT... the app has NEITHER! (It's 'Update Profile' with class '.css-ax7z9')
        # Fill in any required fields before clicking the button
        # Assuming there's a search field with the id 'search-field'
        # page.fill("#search-field", "example search text")
            page.fill("#search-field", "example search text")
        else:
            print("[!] Search field not found. Skipping fill operation.")
        
        # Click the button with the class '.css-ax7z9' and text 'Update Profile'
        try:
            # Trying primarily by ID
            # page.click("#save-btn", timeout=2000)
            # print("[OK] Success with ID!")
        # except:
            # print("[!] ID failed... trying text...")
            # try:
                # Fallback: Trying by text
                # page.click("text=Save Changes", timeout=2000)
            page.click("text=Update Profile", timeout=2000)
                # print("[OK] Success with Text!")
            print("[OK] Success with Text!")
            # except Exception as e:
        except Exception as e:
                # Both failed!
            print(f"[!] Error: {e}")
                # raise Exception("CRITICAL FAILURE: Neither ID nor Text found!")
            raise Exception("CRITICAL FAILURE: Button not found!")
        
        browser.close()

if __name__ == "__main__":
    run_test()
