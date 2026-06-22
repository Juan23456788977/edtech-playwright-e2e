import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 900})
    
    print("Logging in...")
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("Selecting school...")
    page.evaluate('''
    document.getElementById('selected-instance-type').value = 'Employee';
    document.getElementById('selected-instance-id').value = '17548';
    document.getElementById('select-role-form').submit();
    ''')
    time.sleep(5)

    email = 'rossiz2303@gmail.com'
    print(f"Opening modal for {email}...")
    page.evaluate('''
        var modal = document.getElementById('change-to-any-user-modal');
        if(modal) {
            modal.classList.add('show', 'in');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
        }
    ''')
    time.sleep(1)

    page.fill('#fill-user-info', email)
    page.press('#fill-user-info', 'Enter')
    time.sleep(4)

    html_before = page.evaluate('document.querySelector(".user-name") ? document.querySelector(".user-name").innerText : "No name"')
    print(f"Name BEFORE click: {html_before}")

    print("Clicking search result...")
    page.evaluate('''
        var a = document.querySelector('#search-results a');
        if(a) {
            a.click();
        }
    ''')
    time.sleep(10)
    
    html_after = page.evaluate('document.querySelector(".user-name") ? document.querySelector(".user-name").innerText : "No name"')
    print(f"Name AFTER click: {html_after}")

    sidebar_items = page.evaluate('''
        Array.from(document.querySelectorAll('.sidebar-menu > li > a')).map(a => a.innerText.trim().replace(/\\n/g, ' ')).filter(t => t.length > 0)
    ''')
    print("Sidebar items rendered:")
    for item in sidebar_items:
        print(" -", item)
        
    page.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
