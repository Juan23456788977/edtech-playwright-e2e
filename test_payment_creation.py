import os
import time
import random
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    # Enable dialog handling in case of alerts
    page.on("dialog", lambda dialog: print(f"Dialog encountered: {dialog.message} ({dialog.type})") or dialog.accept())

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
        else:
            print("Already on dashboard. Changing role via modal...")
            page.click('a[href="#change-role-modal"]')
            time.sleep(2)
            page.click('input[name="role"][value="employee"]', force=True)
            time.sleep(1)
            page.fill('#fill-school', 'Colegio Prueba Akdemia')
            time.sleep(1)
            page.click('.dropdown-toggle')
            time.sleep(2)
            page.locator('#change-role li').filter(has_text='Colegio Prueba Akdemia').first.click()
            time.sleep(2)
            page.click('#change-role-button')
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        # Navigate to Cobros
        print("Navigating to Cobros...")
        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Change school if needed
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

        # Navigate to representative 226283's account status
        url = "https://cobros.akdemia.com/services_students/account_status?person_id=226283"
        print(f"Navigating to representative 226283...")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Check first enabled invoice checkbox
        print("Checking first enabled checkbox...")
        checkbox = page.locator('.js-check-invoice:not([disabled])').first
        checkbox.check()
        time.sleep(2)

        # Click Pagar button to load details form
        print("Clicking Pagar button...")
        page.click('.js-button-assign')
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        print("URL at details form:", page.url)

        # Clear any existing local storage warning or locks if any
        page.evaluate("localStorage.removeItem('payment_documents_page_open')")

        # Click on "Transferencia" payment method button
        print("Selecting 'Transferencia' payment method...")
        page.click('a.add_nested_fields[data-association="wire_transfers"]')
        time.sleep(2)

        # Generate a unique reference number
        ref_num = str(random.randint(100000, 999999))
        print(f"Filling payment details with Reference: {ref_num}")

        # Fill in the fields
        page.fill('input[name*="[original_amount_cents]"]', '6073900')
        page.select_option('select[name*="[origin_bank_id]"]', '15') # Banco Mercantil
        page.fill('input[name*="[customer_identifier]"]', '26516123165121')
        page.select_option('select[name*="[school_bank_account_id]"]', '308') # Banco Mercantil
        page.fill('input[name*="[reference]"]', ref_num)
        page.fill('input[name*="[concept]"]', f'E2E Payment E-{ref_num}')
        
        # Create a dummy voucher file to upload
        dummy_file = "dummy_voucher.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a dummy payment voucher for automated E2E testing.")
        
        # Attach the file
        print("Uploading dummy voucher...")
        page.locator('input[name*="[voucher]"]').set_input_files(dummy_file)
        time.sleep(1)

        # Take a screenshot before clicking Pay
        page.screenshot(path="payment_details_filled.png")

        # Click Pagar button at the bottom of the details form
        print("Submitting payment document...")
        page.click('.actions button.js-button-assign')
        time.sleep(8)
        page.wait_for_load_state('networkidle')
        
        print("URL after submitting payment:", page.url)
        page.screenshot(path="payment_submitted_result.png")
        
        # Save HTML for verification
        with open("payment_submitted.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Saved payment_submitted.html")
        
        # Write the reference number to a file so other scripts can access it
        with open("last_payment_ref.txt", "w") as f:
            f.write(ref_num)

    except Exception as e:
        print("Error during execution:", e)
        page.screenshot(path="creation_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
