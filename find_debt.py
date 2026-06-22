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

        if "confirm_role" in page.url:
            print("On select role page. Submitting form...")
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

        # Representative IDs from search results
        rep_ids = ["46816", "226283", "254334", "254335", "254386", "288007", "304409"]
        
        for rid in rep_ids:
            url = f"https://cobros.akdemia.com/services_students/account_status?person_id={rid}"
            print(f"Checking representative {rid} at {url}...")
            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(4)
            
            # Check if there are debts
            # The red box contains the total debt
            debt_text = page.locator('.red-light h6').inner_text().strip()
            print(f"  Debt: {debt_text}")
            
            # Let's count rows in table
            rows_count = page.locator('table.service-students-datatable tbody tr').count()
            print(f"  Table rows count: {rows_count}")
            if rows_count > 0:
                first_row_text = page.locator('table.service-students-datatable tbody tr').first.inner_text()
                print(f"  First row text: {first_row_text.strip()}")
                
            if "Bs0,00" not in debt_text or rows_count > 1 or (rows_count == 1 and "No se encontraron" not in first_row_text):
                print(f"  >>> FOUND REPRESENTATIVE WITH DEBT: {rid} <<<")
                page.screenshot(path=f"debt_found_{rid}.png")
                # Save HTML
                with open(f"account_status_{rid}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                break

    except Exception as e:
        print("Error during exploration:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
