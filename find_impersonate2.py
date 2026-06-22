import time
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
    
    try:
        # Click the "U.E. Tulio Febres Cordero" school card
        page.locator("text='U.E. Tulio Febres Cordero'").click()
        page.wait_for_load_state('networkidle', timeout=8000)
        
        # Click the impersonate button
        impersonate_btn = page.locator("text='Cambiar a cualquier usuario'")
        if impersonate_btn.is_visible():
            print("Found impersonate button! Clicking it.")
            impersonate_btn.click()
            time.sleep(2) # wait for modal
            
            modal = page.locator('.modal.show, .modal[style*="display: block"]')
            print("Modal HTML:")
            print(modal.inner_html())
        else:
            print("Impersonate button NOT visible")
            print("Body snippets:", page.locator('body').inner_text()[:500])
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
