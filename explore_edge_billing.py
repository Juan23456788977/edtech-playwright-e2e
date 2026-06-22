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
    
    # Save select role page to search for schools on Edge
    role_html = page.evaluate("document.body.innerHTML")
    with open('edge_select_role.html', 'w') as f:
        f.write(role_html)
        
    # Let's find options containing the target schools
    schools = page.evaluate('''() => {
        let options = Array.from(document.querySelectorAll('.role-option'));
        return options.map(o => ({
            text: o.querySelector('strong') ? o.querySelector('strong').innerText : '',
            id: o.getAttribute('data-instance-id')
        }));
    }''')
    
    print("Schools found on Edge:")
    target_id = None
    for s in schools:
        if any(name in s['text'] for name in ["Marta", "Luz", "Gibran", "Angelo"]):
            print(s)
            if not target_id:
                target_id = s['id']
                
    if not target_id:
        # Fallback to the first one or Colegio Roraima (17498)
        print("No target school found, using Roraima (17498) as fallback to test billing reports dropdown")
        target_id = "17498"
        
    print(f"Selecting school ID: {target_id}")
    page.locator(f'div.role-option[data-instance-id="{target_id}"]').click()
    time.sleep(1)
    with page.expect_navigation():
        page.evaluate("document.getElementById('select-role-form').submit()")
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
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

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
