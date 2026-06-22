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

        # Navigate to representative 226283
        url = "https://cobros.akdemia.com/services_students/account_status?person_id=226283"
        print(f"Navigating to representative 226283 account status...")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Check first enabled checkbox
        print("Checking first enabled checkbox...")
        checkbox = page.locator('.js-check-invoice:not([disabled])').first
        checkbox.check(force=True)
        time.sleep(2)

        # Click Pagar
        print("Clicking Pagar button...")
        page.click('.js-button-assign', force=True)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        page.evaluate("localStorage.removeItem('payment_documents_page_open')")

        # Click Transferencia
        print("Selecting 'Transferencia'...")
        page.click('a.add_nested_fields[data-association="wire_transfers"]')
        time.sleep(2)

        amount_selector = 'input[name*="[original_amount_cents]"]'

        # Test 1: type '607390'
        page.locator(amount_selector).fill('')
        page.locator(amount_selector).type('607390', delay=100)
        time.sleep(1)
        val1 = page.input_value(amount_selector)
        print("Value after typing '607390':", val1)

        # Test 2: type '6073900'
        page.locator(amount_selector).fill('')
        page.locator(amount_selector).type('6073900', delay=100)
        time.sleep(1)
        val2 = page.input_value(amount_selector)
        print("Value after typing '6073900':", val2)

        # Test 3: type '6073,90'
        page.locator(amount_selector).fill('')
        page.locator(amount_selector).type('6073,90', delay=100)
        time.sleep(1)
        val3 = page.input_value(amount_selector)
        print("Value after typing '6073,90':", val3)

        # Test 4: type '6073.90'
        page.locator(amount_selector).fill('')
        page.locator(amount_selector).type('6073.90', delay=100)
        time.sleep(1)
        val4 = page.input_value(amount_selector)
        print("Value after typing '6073.90':", val4)

    except Exception as e:
        print("Error during execution:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
