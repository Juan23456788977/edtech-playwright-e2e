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
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    html = page.evaluate('''() => {
        return document.body.innerHTML;
    }''')
    with open('instances.html', 'w') as f:
        f.write(html)
        
    page.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
