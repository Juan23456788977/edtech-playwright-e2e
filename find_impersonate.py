import sys
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=8000)
    
    # Try to find the impersonate button text
    try:
        # Get all text in the body to see what it says
        body_text = page.locator('body').inner_text()
        print("BODY TEXT SNIPPET:")
        print(body_text[:1000])
        
        # Click the impersonate button (text usually contains "Cambiar a cualquier usuario")
        impersonate_btn = page.locator("text='Cambiar a cualquier usuario'")
        if impersonate_btn.is_visible():
            impersonate_btn.click()
            page.wait_for_timeout(2000) # wait for modal
            print("Modal HTML:")
            print(page.locator('.modal, .dialog, [role="dialog"]').inner_html())
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
