import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=5000)
    
    page.goto('https://alpha.akdemia.com/employees/17500/evaluations')
    page.wait_for_load_state('networkidle', timeout=5000)
    
    page.screenshot(path='/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias/QA_06_y_07_Control_Calificaciones.png')
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
