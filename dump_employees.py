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
    
    # Click the school using a more robust selector
    page.click('.card:has-text("U.E. Tulio Febres Cordero")')
    page.wait_for_load_state('networkidle', timeout=8000)
    
    # Go to employees page
    page.goto('https://alpha.akdemia.com/employees')
    page.wait_for_load_state('networkidle', timeout=8000)
    
    # Take screenshot
    page.screenshot(path='/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/employees_page.png')
    
    # Save HTML
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/employees.html', 'w') as f:
        f.write(page.content())
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
