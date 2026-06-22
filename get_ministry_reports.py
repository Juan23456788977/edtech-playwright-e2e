import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://edge.akdemia.com'
    print("1. Logging in...")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("Current URL:", page.url)
    page.screenshot(path="edge_after_login.png")
    
    # Click change role
    print("Opening change role modal...")
    page.evaluate('''() => {
        let el = document.querySelector('a[href="#change-role-modal"]');
        if(el) el.click();
    }''')
    time.sleep(2)
    page.screenshot(path="edge_modal.png")
    
    print("Typing school name...")
    page.fill('#fill-school', 'Colegio Demo Satisfacción')
    time.sleep(2)
    page.screenshot(path="edge_modal_typed.png")
    
    # Try clicking the dropdown item
    clicked = page.evaluate('''() => {
        let items = Array.from(document.querySelectorAll('ul#change-role li'));
        let target = items.find(li => li.innerText.includes('Colegio Demo Satisfacción'));
        if (target) {
            target.click();
            return true;
        }
        return false;
    }''')
    
    if clicked:
        print("Clicked school in dropdown.")
    else:
        print("Could not find school in dropdown. Let's try pressing Enter.")
        page.press('#fill-school', 'Enter')
    
    time.sleep(1)
    
    print("Clicking Cambiar...")
    page.evaluate('''() => {
        let btn = document.querySelector('#change-role-button');
        if(btn && !btn.classList.contains('disabled')) {
            btn.click();
        }
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    print("URL after changing school:", page.url)
    page.screenshot(path="edge_after_school_change.png")
    
    # Click on Reportes
    print("Navigating to Reportes...")
    page.evaluate('''() => {
        let links = Array.from(document.querySelectorAll('a'));
        let reportesLink = links.find(l => l.innerText.trim() === 'Reportes');
        if(reportesLink) reportesLink.click();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("URL at Reportes:", page.url)
    page.screenshot(path="edge_reportes_demo.png")
    
    # Dump HTML of Reportes page
    html = page.evaluate("document.body.innerHTML")
    with open('reportes_demo.html', 'w') as f:
        f.write(html)
        
    reports = page.evaluate('''() => {
        let sections = Array.from(document.querySelectorAll('h3, h4, h5, div.title, .separator-heading'));
        let ministrySection = sections.find(s => s.innerText.toLowerCase().includes('ministerio'));
        if (!ministrySection) return "Ministry section not found";
        
        let container = ministrySection.closest('.col-md-6') || ministrySection.parentElement;
        return container.innerText;
    }''')
    
    print("Reports found directly:", reports)
    
    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
