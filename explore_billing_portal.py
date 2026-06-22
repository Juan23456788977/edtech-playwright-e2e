import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    # Using a context to keep cookies/session
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://alpha.akdemia.com'
    print("1. Logging in to alpha.akdemia.com...")
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
    
    print("Navigating to cobros-alpha.akdemia.com...")
    page.goto('https://cobros-alpha.akdemia.com/')
    page.wait_for_load_state('networkidle')
    time.sleep(5)
    print("Billing portal URL:", page.url)
    page.screenshot(path="billing_home.png")
    
    # Get all links in the billing portal to find the reports section
    links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText.trim(), href: a.href}));
    }''')
    print("Links found on Billing home:")
    for l in links:
        print(l)
        
    # Let's save the billing home HTML
    billing_html = page.evaluate("document.body.innerHTML")
    with open('billing_home.html', 'w') as f:
        f.write(billing_html)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
