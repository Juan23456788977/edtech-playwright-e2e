import os
import time
from playwright.sync_api import sync_playwright

def check_school(p, school_id, school_name):
    print(f"\n--- Checking school {school_name} (ID: {school_id}) ---")
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://alpha.akdemia.com'
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    page.locator(f'div.role-option[data-instance-id="{school_id}"]').click()
    time.sleep(1)
    with page.expect_navigation():
        page.evaluate("document.getElementById('select-role-form').submit()")
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    page.goto('https://cobros-alpha.akdemia.com/reports/new')
    page.wait_for_load_state('networkidle')
    time.sleep(4)
    
    options = page.evaluate('''() => {
        let select = document.querySelector('select[name="report[report_information]"]');
        if (!select) select = document.querySelector('select');
        if (!select) return [];
        return Array.from(select.options).map(o => ({text: o.text, value: o.value}));
    }''')
    
    print(f"Report options for {school_name}:")
    for o in options:
        print(f"  Value: {o['value']} - Text: {o['text']}")
        
    browser.close()

def run():
    p = sync_playwright().start()
    check_school(p, "17579", "Colegio MÁS LUZ")
    check_school(p, "17597", "Colegio Kalil Gibran")
    p.stop()

if __name__ == '__main__':
    run()
