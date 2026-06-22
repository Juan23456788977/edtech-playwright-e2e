import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://omega.akdemia.com'
    print(f"Navigating to {BASE_URL}/login")
    response = page.goto(f'{BASE_URL}/login')
    if not response or not response.ok:
        print(f"Failed to reach {BASE_URL}")
        return
        
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    # Change school
    print("Changing school...")
    page.evaluate('''() => {
        let el = document.querySelector('a[href="#change-role-modal"]');
        if(el) el.click();
    }''')
    time.sleep(1)
    
    page.fill('#fill-school', 'Colegio Demo Satisfacción')
    try:
        page.wait_for_selector('ul#change-role li', timeout=5000)
    except:
        pass
    time.sleep(2)
    
    page.evaluate('''() => {
        let items = Array.from(document.querySelectorAll('ul#change-role li a'));
        let target = items.find(a => a.innerText.includes('Colegio Demo Satisfacción'));
        if (target) target.click();
    }''')
    time.sleep(1)
    
    page.evaluate('''() => {
        let btn = document.querySelector('#change-role-button');
        if(btn) btn.click();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    page.screenshot(path='omega_dashboard.png')
    
    print("Extracting sidebar modules...")
    modules = page.evaluate('''() => {
        let result = [];
        // The sidebar is usually a ul inside a nav or aside. Let's grab all links that look like sidebar items.
        // Assuming there's a sidebar container
        let sidebar = document.querySelector('.sidebar') || document.querySelector('#sidebar-left') || document.querySelector('ul.nav');
        if (!sidebar) {
            // fallback: get all links that might be in the left column
            return Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText.trim(), href: a.href })).filter(a => a.text.length > 0);
        }
        let links = sidebar.querySelectorAll('a');
        links.forEach(l => {
            if (l.innerText.trim()) {
                result.push({ text: l.innerText.trim(), href: l.href });
            }
        });
        return result;
    }''')
    
    print("MODULES:")
    seen = set()
    for m in modules:
        if m['text'] not in seen:
            print(f"- {m['text']}: {m['href']}")
            seen.add(m['text'])
            
    with open("omega_sidebar.html", "w") as f:
        f.write(page.evaluate("document.body.innerHTML"))
            
    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
