import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://alpha.akdemia.com'
    print("1. Logging in...")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("Selecting school 17508...")
    page.locator('div.role-option[data-instance-id="17508"]').click()
    time.sleep(1)
    with page.expect_navigation():
        page.evaluate("document.getElementById('select-role-form').submit()")
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("Navigating to cobros reports page...")
    page.goto('https://cobros-alpha.akdemia.com/reports/new')
    page.wait_for_load_state('networkidle')
    time.sleep(4)
    print("URL at reports page:", page.url)
    page.screenshot(path="cobros_reports.png")
    
    # Extract select options
    options = page.evaluate('''() => {
        let select = document.querySelector('select[name="report[report_information]"]');
        if (!select) select = document.querySelector('select');
        if (!select) return [];
        return Array.from(select.options).map(o => ({text: o.text, value: o.value}));
    }''')
    print("Report options:")
    for o in options:
        print(f"Value: {o['value']} - Text: {o['text']}")
        
    # Let's save the HTML body
    rep_html = page.evaluate("document.body.innerHTML")
    with open('cobros_reports_body.html', 'w') as f:
        f.write(rep_html)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
