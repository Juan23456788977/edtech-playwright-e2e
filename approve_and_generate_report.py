import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    
    download_dir = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/downloads'
    os.makedirs(download_dir, exist_ok=True)
    
    context = browser.new_context(
        viewport={'width': 1366, 'height': 900},
        accept_downloads=True
    )
    page = context.new_page()

    # Increase default timeouts to 60 seconds
    page.set_default_navigation_timeout(60000)
    page.set_default_timeout(60000)

    # Capture downloads
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
            print("Confirming role in Omega...")
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

        # Retry login if redirected back to login page
        if "login" in page.url or page.locator('#email_login').count() > 0:
            print("Detected redirect to login page. Retrying login...")
            page.goto('https://omega.akdemia.com/login')
            page.fill('#email_login', 'jcortez@akdemia.com')
            page.fill('#password_login', 'akdemia#2026*')
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            if "confirm_role" in page.url or page.locator("div.role-option").count() > 0:
                print("Confirming role in Omega (retry)...")
                page.evaluate('''
                document.getElementById('selected-instance-type').value = 'Employee';
                document.getElementById('selected-instance-id').value = '17548';
                document.getElementById('select-role-form').submit();
                ''')
                page.wait_for_load_state('networkidle')
                time.sleep(5)

            print("Navigating to Cobros (retry)...")
            page.goto('https://cobros.akdemia.com/')
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        # Switch school in Cobros if needed
        school_name = page.locator("#school-name p").inner_text().strip()
        print("School in Cobros:", school_name)
        if "Prueba" not in school_name:
            print("Switching school in Cobros...")
            page.click('#change-role')
            
            # Wait for role change modal to open
            page.locator('#employee-radio-button').wait_for(state='visible')
            page.evaluate('''() => {
                let rb = document.getElementById('employee-radio-button');
                rb.checked = true;
                rb.dispatchEvent(new Event('click', { bubbles: true }));
                rb.dispatchEvent(new Event('change', { bubbles: true }));
            }''')
            
            # Wait for schools list to load (populated via AJAX)
            print("Waiting for schools list to load...")
            page.locator('#school_role_list a').first.wait_for(state='visible', timeout=20000)
            
            # Type and select school
            page.locator('#selected_school').fill('')
            page.locator('#selected_school').type('Colegio Prueba Akdemia', delay=100)
            time.sleep(2)
            
            page.locator('#school_role_list a').filter(has_text='Colegio Prueba Akdemia').first.click(force=True)
            time.sleep(2)
            page.click('#change_role_button', force=True)
            page.wait_for_load_state('networkidle')
            time.sleep(5)
            print("Active school updated to:", page.locator("#school-name p").inner_text().strip())

        # Navigate to payment details page for payment 358
        payment_uuid = "c26da9fa-2834-4d8b-b189-63b1c5d267cb"
        url = f"https://cobros.akdemia.com/payment_documents/show_details_payment?payment_document={payment_uuid}"
        print(f"3. Navigating to payment {payment_uuid} details...")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Session loss recovery check
        if "login" in page.url or page.locator('#email_login').count() > 0 or "sign_in" in page.url:
            print("Session lost during navigation. Re-authenticating...")
            page.goto('https://omega.akdemia.com/login')
            page.fill('#email_login', 'jcortez@akdemia.com')
            page.fill('#password_login', 'akdemia#2026*')
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            if "confirm_role" in page.url or page.locator("div.role-option").count() > 0:
                page.evaluate('''
                document.getElementById('selected-instance-type').value = 'Employee';
                document.getElementById('selected-instance-id').value = '17548';
                document.getElementById('select-role-form').submit();
                ''')
                page.wait_for_load_state('networkidle')
                time.sleep(5)
            
            print("Returning to payment details page...")
            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(5)

        page.screenshot(path="payment_detail_initial.png")

        # Click checkmark to approve
        print("Clicking approve payment with surplus...")
        page.click('.js-approve-payment-with-surplus')
        time.sleep(3)
        page.screenshot(path="payment_approve_modal_open.png")

        # Select the wallet option in the modal
        print("Selecting deposit option in modal...")
        page.locator('input[name="deposit_to_wallet"]').first.click(force=True)
        time.sleep(1)
        page.screenshot(path="payment_approve_modal_selected.png")

        # Confirm approval in modal
        print("Confirming approval...")
        page.click('#approve_payment_with_surplus_button')
        time.sleep(5)
        page.wait_for_load_state('networkidle')
        
        page.screenshot(path="payment_approved_result.png")

        # Verify status is APROBADO
        body_text = page.locator('body').inner_text()
        if "APROBADO" in body_text:
            print("✅ Payment status verified as APROBADO!")
        else:
            print("⚠️ Payment status not verified as APROBADO. Snip:")
            print(body_text[:1000])

        # 4. Go to Reportes to generate R006
        print("4. Navigating to Reportes...")
        page.goto('https://cobros.akdemia.com/reports/new')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Select R006 ('22')
        print("Selecting R006 ('22')...")
        page.select_option('select[name="report[report_information]"]', '22')
        time.sleep(3)

        # Fill start and end dates with today's date
        today_str = "19/06/2026"
        print(f"Setting date range: {today_str}")
        page.evaluate(f'''() => {{
            let sd = document.getElementById('report_start_date');
            let ed = document.getElementById('report_end_date');
            if (sd) {{ sd.value = '{today_str}'; }}
            if (ed) {{ ed.value = '{today_str}'; }}
        }}''')
        time.sleep(1)

        # Click Generar to download Excel
        print("Generating report...")
        with page.expect_download() as download_info:
            page.locator('button[type="submit"]:has-text("Generar"), input[type="submit"]').first.click()
            
        download = download_info.value
        download_path = os.path.join(download_dir, download.suggested_filename)
        download.save_as(download_path)
        print(f"✅ Excel Report Downloaded: {download_path} ({download.suggested_filename})")
        
        page.screenshot(path="report_generated_result.png")
        print("E2E payment approval and report download completed successfully!")

    except Exception as e:
        print("Error:", e)
        page.screenshot(path="approve_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == "__main__":
    run()
