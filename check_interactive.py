import os
import time
import random
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

        if "confirm_role" in page.url or page.locator("div.role-option").count() > 0:
            print("On select role page. Submitting form...")
            page.evaluate('''
            document.getElementById('selected-instance-type').value = 'Employee';
            document.getElementById('selected-instance-id').value = '17548';
            document.getElementById('select-role-form').submit();
            ''')
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        print("2. Navigating to Cobros...")
        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Switch school in Cobros
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

        # Navigate to representative 226283's account status
        url = "https://cobros.akdemia.com/services_students/account_status?person_id=226283"
        print(f"3. Navigating to representative 226283 account status...")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Take initial screenshot of the table
        page.screenshot(path="initial_table_state.png")

        # Let's find all checkboxes and print their state
        checkboxes = page.locator('input.js-check-invoice')
        count = checkboxes.count()
        print(f"Total checkboxes found: {count}")
        for i in range(count):
            cb = checkboxes.nth(i)
            val = cb.get_attribute('value')
            cb_id = cb.get_attribute('id')
            is_disabled = cb.is_disabled()
            is_checked = cb.is_checked()
            is_visible = cb.is_visible()
            print(f"Checkbox {i}: value={val}, id={cb_id}, disabled={is_disabled}, checked={is_checked}, visible={is_visible}")

        # Let's print the state of the "Pagar" button
        pagar_btn = page.locator('.js-button-assign')
        print(f"Pagar button count: {pagar_btn.count()}")
        if pagar_btn.count() > 0:
            classes = pagar_btn.first.get_attribute('class')
            text = pagar_btn.first.inner_text().strip()
            print(f"Pagar button details: class='{classes}', text='{text}'")

        # Let's inspect the first non-disabled checkbox and try to check/click it
        print("Trying to check/click checkboxes...")
        for i in range(count):
            cb = checkboxes.nth(i)
            is_disabled = cb.is_disabled()
            if not is_disabled:
                print(f"Attempting to check Checkbox {i} (value={cb.get_attribute('value')})...")
                # Let's try check()
                try:
                    cb.check(force=True)
                    print(f"Checkbox {i} checked via check(). Is checked? {cb.is_checked()}")
                except Exception as e:
                    print(f"Error checking via check(): {e}")
                
                # Let's also try evaluate-click to be sure if standard check didn't toggle it
                if not cb.is_checked():
                    print("Trying JS click...")
                    cb.evaluate("node => node.click()")
                    print(f"After JS click, is checked? {cb.is_checked()}")

                # Wait for any AJAX updates
                time.sleep(3)
                page.screenshot(path=f"after_checking_{i}.png")
                
                # Print updated Pagar button state
                classes = pagar_btn.first.get_attribute('class')
                text = pagar_btn.first.inner_text().strip()
                print(f"Updated Pagar button details: class='{classes}', text='{text}'")
                break

    except Exception as e:
        print("Error:", e)
        page.screenshot(path="interactive_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
