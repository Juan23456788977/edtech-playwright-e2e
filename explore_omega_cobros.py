import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://omega.akdemia.com'
    print("1. Logging in to omega.akdemia.com...")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("Current URL:", page.url)
    page.screenshot(path="omega_after_login.png")
    
    # Save select role page HTML if present
    select_role_html = page.evaluate("document.body.innerHTML")
    with open('omega_select_role.html', 'w') as f:
        f.write(select_role_html)
        
    # Let's check the options in the school dropdown/grid on Omega
    schools = page.evaluate('''() => {
        let options = Array.from(document.querySelectorAll('.role-option, select option'));
        return options.map(o => {
            let strong = o.querySelector('strong');
            return {
                text: strong ? strong.innerText : o.text || o.innerText,
                id: o.getAttribute ? o.getAttribute('data-instance-id') || o.value : o.value
            };
        });
    }''')
    print("Schools found on Omega:")
    for s in schools:
        if any(name in s['text'] for name in ["Marta", "Luz", "Gibran", "Angelo"]):
            print(s)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
