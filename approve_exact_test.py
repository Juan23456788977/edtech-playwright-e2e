import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    try:
        print("Logging in...")
        page.goto('https://omega.akdemia.com/login')
        page.fill('#email_login', 'jcortez@akdemia.com')
        page.fill('#password_login', 'akdemia#2026*')
        page.click('input[type="submit"]')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        if "confirm_role" in page.url:
            page.evaluate('''
            document.getElementById('selected-instance-type').value = 'Employee';
            document.getElementById('selected-instance-id').value = '17548';
            document.getElementById('select-role-form').submit();
            ''')
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        url = "https://cobros.akdemia.com/payment_documents/show_details_payment?payment_document=149a95fa-8b5c-48c9-9487-47753108a070"
        print(f"Navigating to payment details: {url}")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        print("Page URL before approval:", page.url)
        print("Initial status on page (contains 'APROBADO'?):", "APROBADO" in page.locator("body").inner_text())

        print("Clicking approval checkmark (.js-payment-approved)...")
        page.click('a.js-payment-approved')
        time.sleep(5)
        page.wait_for_load_state('networkidle')

        # Take a screenshot right after
        page.screenshot(path="approve_exact_direct.png")

        # Let's reload to see if status changes
        print("Reloading page to verify...")
        page.reload()
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        text = page.locator("body").inner_text()
        print("Status on page after reload (contains 'APROBADO'?):", "APROBADO" in text)
        if "APROBADO" in text:
            print("✅ Successfully approved!")
        else:
            print("❌ Status is still pending or not approved!")
            print("First 1000 chars of body text:")
            print(text[:1000])

        page.screenshot(path="approve_exact_reload.png")

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
