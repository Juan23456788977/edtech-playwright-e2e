import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    try:
        print("1. Logging in to omega...")
        page.goto('https://omega.akdemia.com/login')
        page.fill('#email_login', 'jcortez@akdemia.com')
        page.fill('#password_login', 'akdemia#2026*')
        page.click('input[type="submit"]')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        if "confirm_role" in page.url:
            print("On select role page. Submitting form...")
            page.evaluate('''
            document.getElementById('selected-instance-type').value = 'Employee';
            document.getElementById('selected-instance-id').value = '17548';
            document.getElementById('select-role-form').submit();
            ''')
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        # Navigate to Cobros
        print("Navigating to Cobros...")
        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        school_name = ""
        try:
            school_name = page.locator("#school-name p").inner_text().strip()
        except Exception:
            pass

        if "Prueba" not in school_name:
            print("Changing school in Cobros...")
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

        # Go to register payment
        print("Navigating to register payment page...")
        page.click('#register_payment')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Search for a student
        print("Searching for 'Prueba'...")
        page.fill('#fill-student-info', 'Prueba')
        time.sleep(1)
        page.press('#fill-student-info', 'Enter')
        
        print("Waiting for search results...")
        time.sleep(5)
        
        # Click the first Representative (Representante Prueba, id 46816)
        print("Clicking representative link...")
        page.click('a.js-guardian[id="46816"]')
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        
        print("URL at account status page:", page.url)
        page.screenshot(path="cobros_account_status.png")
        
        # Save HTML
        html_content = page.content()
        with open('account_status.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Account status HTML saved.")

    except Exception as e:
        print("Error during exploration:", e)
        page.screenshot(path="account_status_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
