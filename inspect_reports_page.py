import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
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

        print("2. Navigating to Reportes...")
        page.goto('https://cobros.akdemia.com/reports/new')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Print select element name and its options
        selects = page.locator('select')
        count = selects.count()
        print(f"Total select elements: {count}")
        for i in range(count):
            sel = selects.nth(i)
            sel_name = sel.get_attribute('name')
            sel_id = sel.get_attribute('id')
            print(f"Select {i}: name='{sel_name}', id='{sel_id}'")
            
            # Print options
            options = sel.locator('option')
            opt_count = options.count()
            print(f"  Total options: {opt_count}")
            for j in range(opt_count):
                opt = options.nth(j)
                val = opt.get_attribute('value')
                text = opt.inner_text().strip()
                print(f"    Option {j}: value='{val}', text='{text}'")

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == "__main__":
    run()
