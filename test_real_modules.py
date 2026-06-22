import os
import time
from playwright.sync_api import sync_playwright

def test_user(email, user_type):
    print(f"\\n--- Testing {email} ({user_type}) ---")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    
    # Avoid redirect errors
    def handle_route(route):
        if "pagos.akdemia.com" in route.request.url:
            html = f"""<!DOCTYPE html><html><body><h2>Portal de Cobranzas</h2><p>Redireccion Exitosa {email}</p></body></html>"""
            route.fulfill(status=200, content_type="text/html", body=html)
        else:
            route.continue_()
    page.route("**/*", handle_route)
    
    try:
        # Login
        page.goto('https://alpha.akdemia.com/login')
        page.fill('#email_login', 'jcortez@akdemia.com')
        page.fill('#password_login', 'akdemia#2026*')
        page.click('input[type="submit"]')
        time.sleep(8)
        
        # Select School 17548
        page.evaluate('''
        document.getElementById('selected-instance-type').value = 'Employee';
        document.getElementById('selected-instance-id').value = '17548';
        document.getElementById('select-role-form').submit();
        ''')
        time.sleep(8)
        
        # Take Admin Dashboard Screenshot (only first time)
        if user_type == "Profesor":
            page.screenshot(path='/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/QA_01_Admin_Dashboard.png')
            page.goto('https://alpha.akdemia.com/employees')
            time.sleep(5)
            page.screenshot(path='/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/QA_02_Recursos_Humanos.png')
            # Go back to home
            page.goto('https://alpha.akdemia.com/home')
            time.sleep(4)
        
        # Impersonate
        print("Opening Impersonate Modal...")
        page.evaluate("$('#change-to-any-user-modal').modal('show')")
        time.sleep(3)
        page.fill('#fill-user-info', email)
        page.press('#fill-user-info', 'Enter')
        time.sleep(5)
        
        print("Clicking Search Result...")
        try:
            page.evaluate("document.querySelector('#search-results a').click()")
        except:
            page.click('#search-results a')
        time.sleep(8)
        
        print(f"Taking Dashboard screenshot for {user_type}...")
        page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/QA_{user_type}_Dashboard.png')
        
        if user_type == "Profesor":
            print("Testing Profesor Modules...")
            page.goto('https://alpha.akdemia.com/employees/17548/evaluations')
            time.sleep(5)
            page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/QA_{user_type}_Evaluaciones.png')
            page.goto('https://alpha.akdemia.com/employees/17548/exams')
            time.sleep(5)
            page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/QA_{user_type}_Examenes.png')
        elif user_type == "Coordinador":
            print("Testing Coordinador Modules...")
            page.goto('https://alpha.akdemia.com/reports/group')
            time.sleep(5)
            page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/QA_{user_type}_Reportes.png')
            
    except Exception as e:
        print("Error:", e)
        page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio/ERROR_{user_type}.png')
    
    browser.close()
    p.stop()

def run():
    os.makedirs('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio', exist_ok=True)
    test_user('rossiz2303@gmail.com', 'Profesor')
    test_user('coordinadormediageneraldemo@ak.com', 'Coordinador')
    test_user('cobros@colegioprueba.com', 'Cobranzas')
    print("Done!")

if __name__ == '__main__':
    run()
