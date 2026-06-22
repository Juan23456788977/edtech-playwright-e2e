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
    
    # We should be on the school selection page. Dump the HTML.
    html = page.content()
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/schools.html', 'w') as f:
        f.write(html)
        
    print("Schools HTML dumped.")
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
