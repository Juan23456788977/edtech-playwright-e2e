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
    
    print("Opening change role modal...")
    page.evaluate('''() => {
        let el = document.querySelector('a[href="#change-role-modal"], [data-target="#change-role-modal"], [data-toggle="modal"][href*="change"]');
        if(el) el.click();
    }''')
    time.sleep(2)
    page.screenshot(path="omega_modal_open.png")
    
    # Dump body to check modal HTML
    body = page.evaluate("document.body.innerHTML")
    with open('omega_body_modal.html', 'w') as f:
        f.write(body)
        
    # Let's search for the target schools in the modal's list if already loaded, or filter them
    for school_query in ["Italo Angelo di Marta", "Mas Luz", "Kalil Gibran"]:
        print(f"Searching for '{school_query}' in change role list...")
        page.fill('#fill-school', school_query)
        time.sleep(2)
        items = page.evaluate('''() => {
            let list = document.querySelectorAll('ul#change-role li a');
            return Array.from(list).map(a => a.innerText.trim());
        }''')
        print(f"Results for '{school_query}':", items)

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
