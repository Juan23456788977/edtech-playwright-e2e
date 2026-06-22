import os
import time
import random
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 1200})
    page = context.new_page()

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

        # Navigate to Cobros
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

        # Check first enabled invoice checkbox
        print("Checking first enabled checkbox...")
        checkbox = page.locator('.js-check-invoice:not([disabled])').first
        checkbox.check(force=True)
        time.sleep(1)
        if not checkbox.is_checked():
            checkbox.evaluate("node => { node.checked = true; node.dispatchEvent(new Event('change', { bubbles: true })); }")
        time.sleep(2)

        # Click Pagar button to load details form
        print("Clicking Pagar button...")
        page.click('.js-button-assign', force=True)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Clear any local storage locks
        page.evaluate("localStorage.removeItem('payment_documents_page_open')")

        # Parse amount pending in cents
        pending_text = page.locator('#remaining_amount_value').inner_text().strip()
        print(f"Pending amount displayed: {pending_text}")
        amount_cents = "".join(c for c in pending_text if c.isdigit())

        # Click on "Transferencia" payment method
        print("Selecting 'Transferencia' payment method...")
        page.click('a.add_nested_fields[data-association="wire_transfers"]')
        time.sleep(2)

        # Fill fields using visible container
        ref_num = str(random.randint(100000, 999999))
        print(f"Filling payment details with Reference: {ref_num}")
        
        visible_fields = page.locator('.fields:visible').last
        
        # We use evaluate to safely set the inputmask value for amount
        visible_fields.locator('input[name*="[original_amount_cents]"]').evaluate(f'(el) => $(el).inputmask("setvalue", {amount_cents} / 100)')
        
        visible_fields.locator('select[name*="[origin_bank_id]"]').select_option('15') # Banco Mercantil
        visible_fields.locator('input[name*="[customer_identifier]"]').fill('V12345678')
        visible_fields.locator('select[name*="[school_bank_account_id]"]').select_option('308') # Banco Mercantil
        visible_fields.locator('input[name*="[reference]"]').fill(ref_num)
        visible_fields.locator('input[name*="[concept]"]').fill(f'E2E Payment E-{ref_num}')
        
        # Attach the file
        dummy_file = "dummy_voucher.png"
        print("Uploading dummy voucher...")
        visible_fields.locator('input[name*="[voucher]"]').set_input_files(dummy_file)
        time.sleep(1)

        # Intercept POST request to see what is sent
        def handle_request(route, request):
            if request.method == "POST" and "payment_documents" in request.url:
                print(f"\\n--- POST payload to {request.url} ---")
                print(request.post_data)
                print("---------------------------------------\\n")
            route.continue_()
            
        page.route("**/*", handle_request)

        # Dump HTML before submitting
        html_content = page.content()
        with open("payment_details_form.html", "w") as f:
            f.write(html_content)

        # Click Pagar button at the bottom of the details form
        print("4. Submitting payment document...")
        page.click('.actions button.js-button-assign')
        time.sleep(8)
        page.wait_for_load_state('networkidle')
        print("URL after submitting payment:", page.url)
        
        # Take full page screenshot of the result
        page.screenshot(path="payment_submitted_full.png", full_page=True)
        
        # Find and print any alert or validation errors
        alerts = page.locator('.alert, .error, .has-error, .help-block, .invalid-feedback')
        alert_count = alerts.count()
        print(f"Number of error/alert elements: {alert_count}")
        for i in range(alert_count):
            print(f"Alert/Error {i}: {alerts.nth(i).inner_text().strip()}")

        # Print all text that looks like a validation message (e.g. text containing "error" or "debe" or "obligatorio")
        body_text = page.locator('body').inner_text()
        print("\n--- Snippets of body text containing common error/alert terms ---")
        for line in body_text.split('\n'):
            line_l = line.lower()
            if any(term in line_l for term in ["error", "debe", "obligatorio", "inválido", "invalido", "no puede", "blank"]):
                print("  >", line.strip())

    except Exception as e:
        print("Error during execution:", e)
        page.screenshot(path="debug_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
