import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://edge.akdemia.com'
    print("1. Logging in to edge.akdemia.com...")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("Logged in, current URL:", page.url)
    
    print("Navigating to cobros-edge reports page...")
    page.goto('https://cobros-edge.akdemia.com/reports/new')
    page.wait_for_load_state('networkidle')
    time.sleep(5)
    print("URL at edge reports page:", page.url)
    page.screenshot(path="cobros_edge_reports.png")
    
    # Extract select options
    options = page.evaluate('''() => {
        let select = document.querySelector('select[name="report[report_information]"]');
        if (!select) select = document.querySelector('select');
        if (!select) return [];
        return Array.from(select.options).map(o => ({text: o.text, value: o.value}));
    }''')
    print("Edge Report options:")
    for o in options:
        print(f"Value: {o['value']} - Text: {o['text']}")
        
    # Save body
    body = page.evaluate("document.body.innerHTML")
    with open('edge_cobros_reports_body.html', 'w') as f:
        f.write(body)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
