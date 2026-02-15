from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Browser launch (Headless=False taaki tum dekh sako)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

# 
        # print("🌍 Going to the Dynamic ID Playground...")
        print("Going to the Dynamic ID Playground...")
        # Yeh website har refresh par naye IDs banati hai
        page.goto("http://uitestingplayground.com/dynamicid")

# 
        # ❌ COMPLEX BUG:
        # Hum button par click karna chahte hain.
        # Humne Kal wali ID copy karke yahan likh di hai.
        # Lekin Aaj wahan nayi ID generate ho gayi hai.
        
# 
        # print("🕵️ Trying to click Button with Hardcoded ID...")
        print("Trying to click Button with Dynamic ID...")
        
# 
        # Yeh ID pakka fail hogi kyunki yeh Randomly Generated hai
        # AI ko samajhna padega ki "ID bekaar hai, Button ke Text se dhoondo"
        page.click("text=Button with Dynamic ID")
        print("Success!")
        # page.click("#75666756-3c7c-47e2-8700-64264629c158")
        
# 
        # print("✅ Success! Button Clicked.")
        browser.close()

if __name__ == "__main__":
    run()
