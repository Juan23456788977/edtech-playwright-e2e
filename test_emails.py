import sys
from playwright.sync_api import sync_playwright

def run():
    emails = ["pagos@akdemia.com", "contable@akdemia.com", "representante@akdemia.com", "deuda@akdemia.com", "moroso@akdemia.com", "admin_pagos@akdemia.com", "finanzas@akdemia.com"]
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    
    for email in emails:
        page = browser.new_page()
        try:
            page.goto('https://alpha.akdemia.com/login')
            page.fill('#email_login', email)
            page.fill('#password_login', 'akdemia#2026*')
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle', timeout=5000)
            print(f"[{email}] -> {page.url}")
        except Exception as e:
            print(f"[{email}] -> Error: {e}")
        page.close()
        
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
