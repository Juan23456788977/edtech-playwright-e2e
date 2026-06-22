import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    def handle_response(response):
        if "payment_documents/invoices" in response.url:
            print(f"URL: {response.url}")
            print(f"Status: {response.status}")
            try:
                text = response.text()
                print(f"Response JS Body:\n{text}")
            except Exception as e:
                print(f"Error: {e}")
    page.on("response", handle_response)

    try:
        print("1. Logging in..." )
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

        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        school_name = ""
        try:
            school_name = page.locator("#school-name p").inner_text().strip()
        except Exception:
            pass

        if "Prueba" not in school_name:
            page.click('#change-role')
            time.sleep(2)
            page.click('input[type="radio"]', force=True)
            time.sleep(1)
            page.click('#selected_school')
            time.sleep(1)
            page.type('#selected_school', 'Colegio Prueba', delay=100)
            time.sleep(3)
            page.locator('.dropdown-menu li').filter(has_text='Colegio Prueba Akdemia').first.click()
            time.sleep(2)
            page.click('#change_role_button', force=True)
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        page.goto("https://cobros.akdemia.com/services_students/account_status?person_id=226283")
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        checkbox = page.locator('input.js-check-invoice').first
        checkbox.check(force=True)
        time.sleep(2)
        
        page.click('button.js-button-assign')
        time.sleep(5)

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
