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

        if "confirm_role" in page.url or page.locator("div.role-option").count() > 0:
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
        print("Clicking change role link...")
        page.click('#change-role')
        time.sleep(2)
        
        # Click Employee radio
        print("Clicking radio button...")
        page.locator('input[type="radio"]').first.click(force=True)
        time.sleep(2)

        # Click dropdown button
        print("Clicking dropdown button...")
        page.click('#dropdownButton')
        time.sleep(2)

        # Print all schools in list
        schools = page.locator('#school_role_list a')
        count = schools.count()
        print(f"Total schools in dropdown: {count}")
        for i in range(count):
            print(f"School {i}: {schools.nth(i).inner_text().strip()}")

        # Click Colegio Prueba Akdemia
        print("Selecting Colegio Prueba Akdemia...")
        page.locator('#school_role_list a').filter(has_text='Colegio Prueba Akdemia').first.click(force=True)
        time.sleep(2)

        # Click Change button
        print("Clicking change button...")
        page.click('#change_role_button', force=True)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        print("Final school name:", page.locator("#school-name p").inner_text().strip())
        page.screenshot(path="school_switch_success.png")

    except Exception as e:
        print("Error:", e)
        page.screenshot(path="school_switch_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == "__main__":
    run()
