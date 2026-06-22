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
    
    print("Selecting school: UNIDAD EDUCATIVA COLEGIO ITALO VENEZOLANO ANGELO DE MARTA (ID: 17508)")
    page.evaluate('''() => {
        document.getElementById('selected-instance-type').value = 'Employee';
        document.getElementById('selected-instance-id').value = '17508';
        document.getElementById('select-role-form').submit();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    print("Logged in, URL is:", page.url)
    
    # Try navigating to /reports/new
    print("Navigating to /reports/new ...")
    page.goto(f'{BASE_URL}/reports/new')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    print("URL at /reports/new:", page.url)
    page.screenshot(path="reports_page_angelo.png")
    
    # Check if there is a dropdown for report selection
    options = page.evaluate('''() => {
        let select = document.querySelector('select[name*="report_information"]');
        if (!select) select = document.querySelector('select');
        if (!select) return [];
        return Array.from(select.options).map(o => ({text: o.text, value: o.value}));
    }''')
    print("Report options found:", options)
    
    # Let's check for billing portal links
    billing_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).filter(a => a.href.includes('cobros') || a.innerText.includes('Factur') || a.innerText.includes('Pago')).map(a => ({text: a.innerText, href: a.href}));
    }''')
    print("Billing / Cobros links found:", billing_links)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
