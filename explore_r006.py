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
    
    print("Current URL after login:", page.url)
    page.screenshot(path="login_result.png")
    
    # Dump body to see options
    body_html = page.evaluate("document.body.innerHTML")
    with open('select_role_body.html', 'w') as f:
        f.write(body_html)
        
    # Let's find options containing the schools
    schools = page.evaluate('''() => {
        let options = Array.from(document.querySelectorAll('select option'));
        return options.map(o => ({text: o.text, value: o.value}));
    }''')
    print("Schools found in dropdown:")
    for s in schools:
        if any(name in s['text'] for name in ["Marta", "Luz", "Gibran", "Angelo"]):
            print(s)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
