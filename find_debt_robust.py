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

        # List of representative IDs to check
        rep_ids = ["46816", "226283", "254334", "254335", "254386", "288007", "304409"]
        
        for rid in rep_ids:
            url = f"https://cobros.akdemia.com/services_students/account_status?person_id={rid}"
            print(f"\nChecking representative {rid} at {url}...")
            page.goto(url)
            page.wait_for_load_state('load')
            time.sleep(4)
            print("Current URL:", page.url)
            
            if "login" in page.url:
                print("Error: Redirected to login page. Session lost!")
                page.screenshot(path="session_lost.png")
                break
                
            # Check if there is debt
            try:
                # Wait for loading overlay to disappear if any
                time.sleep(2)
                
                # Check the red-light element (Deuda)
                red_box = page.locator('.red-light')
                if red_box.count() > 0:
                    debt_text = red_box.locator('h6').inner_text().strip()
                    print(f"  Total Debt: {debt_text}")
                else:
                    debt_text = "N/A"
                    print("  Total Debt box (.red-light) not found")
                    
                # Let's count rows in table
                rows = page.locator('table.service-students-datatable tbody tr')
                rows_count = rows.count()
                print(f"  Table rows count: {rows_count}")
                
                first_row_text = ""
                if rows_count > 0:
                    first_row_text = rows.first.inner_text().strip()
                    print(f"  First row text: {first_row_text}")
                    
                if "Bs0,00" not in debt_text and "N/A" not in debt_text and rows_count > 0 and "No se encontraron" not in first_row_text:
                    print(f"  >>> FOUND REPRESENTATIVE WITH ACTIVE DEBT: {rid} ({debt_text}) <<<")
                    page.screenshot(path=f"debt_found_{rid}.png")
                    with open(f"account_status_{rid}.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    # Do not break, let's check all to find the best candidate
            except Exception as ex:
                print(f"  Error checking {rid}: {ex}")
                page.screenshot(path=f"error_{rid}.png")

    except Exception as e:
        print("Fatal error during exploration:", e)
        page.screenshot(path="fatal_error.png")
    finally:
        browser.close()
        p.stop()

if __name__ == '__main__':
    run()
