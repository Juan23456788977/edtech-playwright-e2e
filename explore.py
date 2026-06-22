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
    page.wait_for_load_state('networkidle')
    
    # Try to find a user search page or list
    page.goto('https://alpha.akdemia.com/users')
    page.wait_for_load_state('networkidle')
    print("USERS URL:", page.url)
    
    # Try to find the billing configuration page
    page.goto('https://alpha.akdemia.com/billing')
    page.wait_for_load_state('networkidle')
    print("BILLING URL:", page.url)
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
