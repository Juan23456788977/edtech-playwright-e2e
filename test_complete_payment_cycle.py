import os
import time
import random
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    
    # Setup download directory
    download_dir = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/downloads'
    os.makedirs(download_dir, exist_ok=True)
    
    context = browser.new_context(
        viewport={'width': 1366, 'height': 900},
        accept_downloads=True
    )
    page = context.new_page()

    # Capture all downloads
    downloads = []
    page.on('download', lambda d: downloads.append(d))

    # Enable dialog handling to accept alerts
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
        print("2. Navigating to Cobros...")
        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Change school if needed
        school_name = ""
        try:
            school_name = page.locator("#school-name p").inner_text().strip()
            print("School name in Cobros:", school_name)
        except Exception:
            pass

        if "Prueba" not in school_name:
            print("Changing school in Cobros...")
            page.click('#change-role')
            time.sleep(2)
            # Click Employee radio button
            page.locator('input[type="radio"]').first.click(force=True)
            time.sleep(2)
            
            # Type school name to trigger keyup
            page.locator('#selected_school').click()
            page.locator('#selected_school').fill('')
            page.locator('#selected_school').type('Colegio Prueba Akdemia', delay=100)
            time.sleep(3)
            
            # Select the option from school list
            page.locator('#school_role_list a').filter(has_text='Colegio Prueba Akdemia').first.click(force=True)
            time.sleep(2)
            
            # Click Change button
            page.click('#change_role_button', force=True)
            page.wait_for_load_state('networkidle')
            time.sleep(5)
            print("After school switch in Cobros, URL:", page.url)

        # Navigate to representative 226283's account status
        url = "https://cobros.akdemia.com/services_students/account_status?person_id=226283"
        print(f"3. Navigating to representative 226283 account status...")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Check for session loss and re-login if necessary
        if "login" in page.url or page.locator('#email_login').count() > 0 or "sign_in" in page.url:
            print("Session lost during navigation. Re-authenticating...")
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
            
            # Go back to representative account status
            print("Returning to representative account status page...")
            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        # Check first enabled invoice checkbox
        print("Checking first enabled checkbox...")
        checkbox = page.locator('.js-check-invoice:not([disabled])').first
        checkbox.check(force=True)
        time.sleep(1)
        if not checkbox.is_checked():
            print("Force-checking via JS...")
            checkbox.evaluate("node => { node.checked = true; node.dispatchEvent(new Event('change', { bubbles: true })); }")
        time.sleep(2)

        # Clear any existing local storage warning or locks if any
        page.evaluate("localStorage.removeItem('payment_documents_page_open')")

        # Click Pagar button to load details form
        print("Clicking Pagar button...")
        page.click('.js-button-assign', force=True)
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        print("URL at details form:", page.url)

        # Parse amount pending in cents dynamically from page
        pending_text = page.locator('#remaining_amount_value').inner_text().strip()
        print(f"Pending amount displayed: {pending_text}")
        amount_cents = "".join(c for c in pending_text if c.isdigit())
        print(f"Parsed amount in cents: {amount_cents}")

        # Click on "Transferencia" payment method button
        print("Selecting 'Transferencia' payment method...")
        page.click('a.add_nested_fields[data-association="wire_transfers"]')
        time.sleep(2)

        # Generate a unique reference number
        ref_num = str(random.randint(100000, 999999))
        print(f"Filling payment details with Reference: {ref_num}")

        # Fill in the fields
        page.fill('input[name*="[original_amount_cents]"]', amount_cents)
        page.select_option('select[name*="[origin_bank_id]"]', '15') # Banco Mercantil
        page.fill('input[name*="[customer_identifier]"]', '26516123165121')
        page.select_option('select[name*="[school_bank_account_id]"]', '308') # Banco Mercantil
        page.fill('input[name*="[reference]"]', ref_num)
        page.fill('input[name*="[concept]"]', f'E2E Payment E-{ref_num}')
        
        # Create a valid 1x1 pixel PNG binary file to satisfy validation
        dummy_file = "dummy_voucher.png"
        png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(dummy_file, "wb") as f:
            f.write(png_bytes)
        
        # Attach the file
        print("Uploading dummy voucher...")
        page.locator('input[name*="[voucher]"]').set_input_files(dummy_file)
        time.sleep(1)

        # Take a screenshot before clicking Pay
        page.screenshot(path="payment_details_filled.png")

        # Click Pagar button at the bottom of the details form
        print("4. Submitting payment document...")
        page.click('.actions button.js-button-assign')
        time.sleep(8)
        page.wait_for_load_state('networkidle')
        print("URL after submitting payment:", page.url)
        page.screenshot(path="payment_submitted_result.png")
        
        # Verify we are on show_details_payment
        if "show_details_payment" in page.url:
            print("Successfully redirected to payment details. Approving payment...")
            
            # Click checkmark to approve
            page.click('a.js-approve-payment-with-surplus')
            time.sleep(2)
            
            # Confirm approval in modal
            print("Confirming approval in modal...")
            page.click('#approve_payment_with_surplus_button')
            time.sleep(5)
            page.wait_for_load_state('networkidle')
            print("Payment approved. URL:", page.url)
            page.screenshot(path="payment_approved_result.png")
            
            # Verify status is APROBADO
            status_text = page.locator('body').inner_text()
            if "APROBADO" in status_text:
                print("✅ Payment status verified as APROBADO!")
            else:
                print("⚠️ Payment status not found or not APROBADO, current body snippet:")
                print(status_text[:500])
        else:
            print("❌ Failed to reach show_details_payment page!")
            page.screenshot(path="payment_submitted_error_full.png", full_page=True)
            alerts = page.locator('.alert, .error, .has-error, .help-block, .invalid-feedback')
            alert_count = alerts.count()
            print(f"Number of error/alert elements: {alert_count}")
            for i in range(alert_count):
                print(f"Alert/Error {i}: {alerts.nth(i).inner_text().strip()}")
            body_text = page.locator('body').inner_text()
            print("\n--- Snippets of body text containing common error/alert terms ---")
            for line in body_text.split('\n'):
                line_l = line.lower()
                if any(term in line_l for term in ["error", "debe", "obligatorio", "inválido", "invalido", "no puede", "blank"]):
                    print("  >", line.strip())
            return

        # 5. Go to Reportes to generate R006
        print("5. Navigating to Reportes...")
        page.goto('https://cobros.akdemia.com/reports/new')
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        print("URL at Reportes:", page.url)

        # Select R006 ('22')
        print("Selecting R006 ('22')...")
        page.select_option('select[name="report[report_information]"]', '22')
        time.sleep(3)
        page.screenshot(path="report_r006_selected.png")

        # Fill start and end dates with today's date
        today_str = "19/06/2026"
        print(f"Setting report date range: {today_str} - {today_str}")
        page.evaluate(f'''() => {{
            let sd = document.getElementById('report_start_date');
            let ed = document.getElementById('report_end_date');
            if (sd) {{ sd.value = '{today_str}'; }}
            if (ed) {{ ed.value = '{today_str}'; }}
        }}''')
        time.sleep(1)

        # Select Mercantil in bank filter if it exists
        bank_select = page.locator('select[name="report[bank]"]')
        if bank_select.count() > 0:
            print("Selecting Mercantil in bank filter...")
            bank_select.select_option('mercantil')
            time.sleep(1)

        # Click Generar to download Excel
        print("Generating report...")
        with page.expect_download() as download_info:
            page.locator('button[type="submit"]:has-text("Generar"), input[type="submit"]').first.click()
            
        download = download_info.value
        download_path = os.path.join(download_dir, download.suggested_filename)
        download.save_as(download_path)
        print(f"✅ Excel Report Downloaded: {download_path} ({download.suggested_filename})")
        
        # Take a final screenshot
        page.screenshot(path="report_generated_result.png")
        print("E2E Payment Cycle completed successfully!")

    except Exception as e:
        print("Error during execution:", e)
        page.screenshot(path="cycle_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
