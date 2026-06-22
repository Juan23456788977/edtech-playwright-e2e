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
    page.locator('div.role-option[data-instance-id="17508"]').click()
    time.sleep(1)
    
    with page.expect_navigation():
        page.evaluate("document.getElementById('select-role-form').submit()")
        
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    print("Logged in, URL is:", page.url)
    page.screenshot(path="after_role_select.png")
    
    # Check menu items or dump dashboard HTML
    dash_html = page.evaluate("document.body.innerHTML")
    with open('dashboard_after_role.html', 'w') as f:
        f.write(dash_html)
        
    # Find links related to Cobros/Facturación/Reportes
    links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText.trim(), href: a.href}));
    }''')
    print("Links found on dashboard:")
    for l in links:
        if any(w in l['text'].lower() or w in l['href'].lower() for w in ["report", "cobro", "pago", "factur"]):
            print(l)

    # Let's try navigating to /reports/new
    print("Navigating to /reports/new ...")
    page.goto(f'{BASE_URL}/reports/new')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    print("URL at /reports/new:", page.url)
    
    options = page.evaluate('''() => {
        let select = document.querySelector('select');
        if (!select) return [];
        return Array.from(select.options).map(o => ({text: o.text, value: o.value}));
    }''')
    print("Report options found:", options)
    
    # Dump reports page content to file
    rep_html = page.evaluate("document.body.innerHTML")
    with open('reports_page_body.html', 'w') as f:
        f.write(rep_html)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
