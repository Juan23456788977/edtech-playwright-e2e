import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://edge.akdemia.com'
    print(f"--- 1. Testing Bypass URL (Multiple Roles) on {BASE_URL} ---")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    print("Taking screenshot after login...")
    page.screenshot(path="edge_login_result.png")
    
    print(f"URL: {page.url}")

    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
