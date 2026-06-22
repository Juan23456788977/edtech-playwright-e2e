import os
import time
import random
from playwright.sync_api import sync_playwright

def run_variant(amount_to_type, voucher_filename, use_png_bytes=False):
    print(f"\n--- Testing variant: Amount={amount_to_type}, Voucher={voucher_filename} ---")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    # Capture dialogs
    dialogs = []
    def handle_dialog(dialog):
        print(f"  [Dialog] {dialog.message} ({dialog.type})")
        dialogs.append(dialog.message)
        dialog.accept()
    page.on("dialog", handle_dialog)

    try:
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

        school_name = page.locator("#school-name p").inner_text().strip()
        if "Prueba" not in school_name:
            page.click('#change-role')
            time.sleep(2)
            page.locator('input[type="radio"]').first.click(force=True)
            time.sleep(2)
            page.locator('#selected_school').click()
            page.locator('#selected_school').type('Colegio Prueba Akdemia', delay=100)
            time.sleep(3)
            page.locator('#school_role_list a').filter(has_text='Colegio Prueba Akdemia').first.click(force=True)
            time.sleep(2)
            page.click('#change_role_button', force=True)
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        # Go to representative 226283
        page.goto("https://cobros.akdemia.com/services_students/account_status?person_id=226283")
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Check first enabled checkbox
        checkbox = page.locator('.js-check-invoice:not([disabled])').first
        checkbox.check(force=True)
        time.sleep(2)

        page.click('.js-button-assign', force=True)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        page.evaluate("localStorage.removeItem('payment_documents_page_open')")

        # Select Transferencia
        page.click('a.add_nested_fields[data-association="wire_transfers"]')
        time.sleep(2)

        amount_selector = 'input[name*="[original_amount_cents]"]'
        page.locator(amount_selector).fill('')
        page.locator(amount_selector).type(amount_to_type, delay=100)
        time.sleep(1)

        # Fill other fields
        ref_num = str(random.randint(100000, 999999))
        page.select_option('select[name*="[origin_bank_id]"]', '15') # Banco Mercantil
        page.fill('input[name*="[customer_identifier]"]', '26516123165121')
        page.select_option('select[name*="[school_bank_account_id]"]', '308') # Banco Mercantil
        page.fill('input[name*="[reference]"]', ref_num)
        page.fill('input[name*="[concept]"]', f'Variant Test Ref {ref_num}')

        # Prepare voucher file
        if use_png_bytes:
            png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
            with open(voucher_filename, "wb") as f:
                f.write(png_bytes)
        else:
            with open(voucher_filename, "w") as f:
                f.write("Dummy test voucher content")

        page.locator('input[name*="[voucher]"]').set_input_files(voucher_filename)
        time.sleep(2)

        # Submit
        print("  Submitting form...")
        page.click('.actions button.js-button-assign')
        time.sleep(8)
        page.wait_for_load_state('networkidle')

        print("  Redirected URL:", page.url)
        if "show_details_payment" in page.url:
            print("  ✅ SUCCESS!")
            return True
        else:
            print("  ❌ FAILED!")
            # Print any alert messages
            alerts = page.locator('.alert, .error, .has-error, .help-block, .invalid-feedback')
            for i in range(alerts.count()):
                print(f"    Alert {i}: {alerts.nth(i).inner_text().strip()}")
            return False
    except Exception as e:
        print("  Error:", e)
        return False
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    # Test variant 1: Exact amount with PNG
    success1 = run_variant('6073,90', 'dummy_voucher.png', use_png_bytes=True)
    if success1:
        print("Variant 1 succeeded. No need to test others.")
        exit(0)

    # Test variant 2: Exact amount with TXT
    success2 = run_variant('6073,90', 'dummy_voucher.txt', use_png_bytes=False)
    if success2:
        print("Variant 2 succeeded. No need to test others.")
        exit(0)

    # Test variant 3: Surplus amount with TXT
    success3 = run_variant('6073900', 'dummy_voucher.txt', use_png_bytes=False)
    if success3:
        print("Variant 3 succeeded.")
        exit(0)
