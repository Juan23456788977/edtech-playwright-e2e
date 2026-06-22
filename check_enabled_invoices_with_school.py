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
            page.locator('input[type="radio"]').first.click(force=True)
            time.sleep(2)
            
            page.locator('#selected_school').click()
            page.locator('#selected_school').fill('')
            page.locator('#selected_school').type('Colegio Prueba Akdemia', delay=100)
            time.sleep(3)
            
            page.locator('#school_role_list a').filter(has_text='Colegio Prueba Akdemia').first.click(force=True)
            time.sleep(2)
            
            page.click('#change_role_button', force=True)
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        url = "https://cobros.akdemia.com/services_students/account_status?person_id=226283"
        print(f"Navigating to representative 226283: {url}")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        checkboxes = page.locator('.js-check-invoice')
        enabled_checkboxes = page.locator('.js-check-invoice:not([disabled])')
        
        print(f"Total invoice checkboxes: {checkboxes.count()}")
        print(f"Enabled invoice checkboxes: {enabled_checkboxes.count()}")

        for i in range(checkboxes.count()):
            cb = checkboxes.nth(i)
            disabled = cb.get_attribute("disabled") is not None
            text = page.evaluate(f"node => node.closest('tr').innerText", cb)
            print(f"Checkbox {i}: disabled={disabled}, Row text: {text.strip().replace(chr(10), ' | ')}")

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
