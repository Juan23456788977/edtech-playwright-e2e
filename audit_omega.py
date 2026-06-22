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
        print("Failed to reach omega.akdemia.com")
        return
        
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    # Change school
    print("Changing school to Colegio Prueba Akdemia...")
    page.evaluate('''() => {
        let el = document.querySelector('a[href="#change-role-modal"]');
        if(el) el.click();
    }''')
    time.sleep(1)
    
    page.fill('#fill-school', 'Colegio Prueba Akdemia')
    try:
        page.wait_for_selector('ul#change-role li', timeout=5000)
    except:
        pass
    time.sleep(2)
    
    page.evaluate('''() => {
        let items = Array.from(document.querySelectorAll('ul#change-role li a'));
        let target = items.find(a => a.innerText.includes('Colegio Prueba Akdemia'));
        if (target) target.click();
    }''')
    time.sleep(1)
    
    page.evaluate('''() => {
        let btn = document.querySelector('#change-role-button');
        if(btn) btn.click();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    page.screenshot(path='omega_prueba_dashboard.png')
    print("At dashboard, checking Secciones module...")
    
    # Go to Secciones
    page.goto(f'{BASE_URL}/batches')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    page.screenshot(path='omega_prueba_secciones.png')
    
    print("Checking how many clicks to create a new Section...")
    # Find the "New Section" or "Crear Sección" button
    new_btn = page.evaluate('''() => {
        let links = Array.from(document.querySelectorAll('a, button'));
        let btn = links.find(l => l.innerText.toLowerCase().includes('crear') || l.innerText.toLowerCase().includes('nueva'));
        if (btn) return {text: btn.innerText, href: btn.href || ''};
        return null;
    }''')
    print("New Section button:", new_btn)
    
    # Dump HTML to analyze the form
    with open("omega_secciones.html", "w") as f:
        f.write(page.evaluate("document.body.innerHTML"))

    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
