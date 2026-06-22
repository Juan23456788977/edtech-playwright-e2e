import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    try:
        print("Logging in...")
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

        # Navigate to Cobros
        print("Navigating to Cobros...")
        page.goto('https://cobros.akdemia.com/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        school_name = ""
        try:
            school_name = page.locator("#school-name p").inner_text().strip()
        except Exception:
            pass

        if "Prueba" not in school_name:
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

        print("Navigating to Reportes...")
        page.goto('https://cobros.akdemia.com/reports/new')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        # Print all options of report_information
        options = page.evaluate('''() => {
            let select = document.querySelector('select[name="report[report_information]"]');
            return Array.from(select.options).map(o => ({text: o.text, value: o.value}));
        }''')
        print("\nAll Available Report Options:")
        for opt in options:
            print(f"  - [{opt['value']}] {opt['text']}")

        # Select option 22
        print("\nSelecting R006 (value 22)...")
        page.select_option('select[name="report[report_information]"]', '22')
        time.sleep(3)

        # Print all visible input/select elements
        elements = page.evaluate('''() => {
            let fields = [];
            document.querySelectorAll('input, select').forEach(el => {
                let is_visible = el.offsetWidth > 0 && el.offsetHeight > 0;
                if (is_visible && el.name !== 'utf8' && el.name !== 'authenticity_token') {
                    let opts = [];
                    if (el.tagName === 'SELECT') {
                        opts = Array.from(el.options).map(o => ({text: o.text, value: o.value}));
                    }
                    fields.push({
                        tag: el.tagName,
                        name: el.name,
                        id: el.id,
                        value: el.value,
                        options: opts
                    });
                }
            });
            return fields;
        }''')

        print("\n--- Visible Fields after Selecting R006 ---")
        for el in elements:
            print(f"{el['tag']} name='{el['name']}' id='{el['id']}' value='{el['value']}'")
            if el['options']:
                print("  Options:")
                for opt in el['options']:
                    print(f"    - [{opt['value']}] {opt['text']}")

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
