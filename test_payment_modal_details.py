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
        print("Logged in, URL:", page.url)

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
        print("URL at Cobros:", page.url)

        # Check school name in Cobros
        school_name = ""
        try:
            school_name = page.locator("#school-name p").inner_text().strip()
            print("Current school in Cobros:", school_name)
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
            print("After school switch in Cobros, URL:", page.url)

        # Navigate to representative 226283's account status
        url = "https://cobros.akdemia.com/services_students/account_status?person_id=226283"
        print(f"Navigating to representative 226283 at {url}...")
        page.goto(url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        print("URL at account status:", page.url)
        
        # Verify debt total exists
        red_box = page.locator('.red-light')
        if red_box.count() > 0:
            print("Deuda total text:", red_box.locator('h6').inner_text().strip())

        # Click the first enabled invoice checkbox
        print("Checking first enabled checkbox...")
        checkbox = page.locator('.js-check-invoice:not([disabled])').first
        checkbox.check()
        time.sleep(2)
        
        page.screenshot(path="payment_step1_checked.png")

        # Click the Pagar button (.js-button-assign)
        print("Clicking Pagar button...")
        page.click('.js-button-assign')
        time.sleep(5)
        page.wait_for_load_state('networkidle')
        print("URL after Pagar click:", page.url)
        page.screenshot(path="payment_step2_details_form.png")

        # Save HTML for analysis of the details form fields
        with open("payment_details_form.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Saved payment_details_form.html")

    except Exception as e:
        print("Error during execution:", e)
        page.screenshot(path="details_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
