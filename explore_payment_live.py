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

        # Check if select-role page
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

        print("After selecting school in Omega, URL:", page.url)
        page.screenshot(path="omega_dashboard.png")

        # Navigate to Cobros
        print("Navigating to Cobros...")
        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        print("URL at Cobros:", page.url)
        page.screenshot(path="cobros_home_pre_switch.png")

        # Let's check school name in Cobros
        try:
            school_name = page.locator("#school-name p").inner_text().strip()
            print("Current school in Cobros:", school_name)
        except Exception as e:
            school_name = ""
            print("Could not find school name:", e)

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
            page.screenshot(path="cobros_home_post_switch.png")
            try:
                print("New school in Cobros:", page.locator("#school-name p").inner_text().strip())
            except Exception:
                pass

        # Go to register payment
        print("Navigating to register payment page...")
        page.click('#register_payment')
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        print("URL at register payment page:", page.url)
        page.screenshot(path="cobros_register_payment.png")

        # Save HTML for analysis
        html_content = page.content()
        with open('cobros_register_payment.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    except Exception as e:
        print("Error during exploration:", e)
        page.screenshot(path="exploration_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
