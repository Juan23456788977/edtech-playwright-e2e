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
    page.wait_for_load_state('networkidle', timeout=5000)
    
    page.goto('https://alpha.akdemia.com/users')
    page.wait_for_load_state('networkidle', timeout=5000)
    
    html = page.content()
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/users.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    # Also check the modal "#fill-user-info" mentioned in the subagent prompt
    try:
        page.goto('https://alpha.akdemia.com/home') # or wherever
        page.wait_for_load_state('networkidle')
        # We can also dump this html
        with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/home.html', 'w', encoding='utf-8') as f:
            f.write(page.content())
    except:
        pass
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
