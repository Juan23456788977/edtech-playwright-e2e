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
        try:
            page.wait_for_url(lambda u: "confirm_role" in u or "dashboard" in u or "omega" in u, timeout=15000)
        except Exception:
            pass
        time.sleep(3)

        if "confirm_role" in page.url or page.locator("div.role-option").count() > 0:
            page.evaluate('''
            document.getElementById('selected-instance-type').value = 'Employee';
            document.getElementById('selected-instance-id').value = '17548';
            document.getElementById('select-role-form').submit();
            ''')
            try:
                page.wait_for_url(lambda u: "dashboard" in u, timeout=15000)
            except Exception:
                pass
            time.sleep(5)

        url = "https://cobros.akdemia.com/payment_documents/show_details_payment?payment_document=149a95fa-8b5c-48c9-9487-47753108a070"
        print(f"Navigating to payment details: {url}")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        print("Page URL:", page.url)
        
        # Dump links/buttons text and classes
        elements = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a, button')).map(el => ({
                tag: el.tagName,
                text: (el.innerText || '').trim(),
                id: el.id,
                className: el.className,
                href: el.href || ''
            })).filter(el => el.text || el.id || el.className);
        }''')
        
        print("\n--- Interactive Elements on Details Page ---")
        for el in elements:
            print(f"{el['tag']}: text='{el['text']}' id='{el['id']}' class='{el['className']}' href='{el['href']}'")

        # Take screenshot
        page.screenshot(path="inspect_details_exact.png")
        print("\nScreenshot saved to inspect_details_exact.png")

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
