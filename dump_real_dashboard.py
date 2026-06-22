import sys
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
    
    print("Evaluating JS to select school...")
    page.evaluate('''
    document.getElementById('selected-instance-type').value = 'Employee';
    document.getElementById('selected-instance-id').value = '17500';
    document.getElementById('select-role-form').submit();
    ''')
    
    page.wait_for_load_state('networkidle', timeout=10000)
    time.sleep(3)
    
    print("Current URL:", page.url)
    
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/dashboard.html', 'w') as f:
        f.write(page.content())
        
    page.screenshot(path='/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/dashboard.png')
    print("Dashboard HTML and PNG dumped.")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
