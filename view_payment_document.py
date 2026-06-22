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

        # Switch school in Cobros if needed
        school_name = page.locator("#school-name p").inner_text().strip()
        print("School in Cobros:", school_name)
        if "Prueba" not in school_name:
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

        for pid in ["357", "358"]:
            url = f"https://cobros.akdemia.com/payment_documents/{pid}"
            print(f"\n--- Checking Payment Document {pid} at {url} ---")
            page.goto(url)
            page.wait_for_load_state('networkidle')
            time.sleep(5)
            
            page.screenshot(path=f"payment_{pid}_detail.png", full_page=True)
            with open(f"payment_{pid}_detail.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print(f"Saved payment_{pid}_detail.html")
            
            body_text = page.locator('body').inner_text()
            print("Status:", "APROBADO" if "APROBADO" in body_text else "PENDIENTE" if "PENDIENTE" in body_text else "UNKNOWN")
            print("Representative:", "Prueba Prueba" if "Prueba Prueba" in body_text else "OTHER")
            
            # Look for reference and amount details
            print("Snippet of payment details:")
            lines = body_text.split('\n')
            for line in lines:
                if any(k in line.lower() for k in ["referencia", "monto", "estatus", "banco"]):
                    print("  >", line.strip())

    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == "__main__":
    run()
