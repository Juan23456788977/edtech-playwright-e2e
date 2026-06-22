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
    
    # Let's try to open the change role modal.
    # The school name in the header is a good candidate.
    # In the screenshot, it says "UFP Colegio Roraima" in the top right.
    # Let's find any element containing that text or try to find the modal toggle.
    print("Attempting to open the Cambio de Rol modal...")
    
    # We can execute JS to find the header dropdown
    opened = page.evaluate('''() => {
        // Find elements that might toggle the modal
        let els = Array.from(document.querySelectorAll('a, button, div.dropdown-toggle, li.dropdown-toggle'));
        let toggles = els.filter(el => el.innerText && el.innerText.includes('UFP Colegio Roraima'));
        if (toggles.length > 0) {
            toggles[0].click();
            return true;
        }
        
        // If not found by text, try finding the modal target
        let modalToggles = document.querySelectorAll('[data-target="#changeRoleModal"], [data-target="#change-role-modal"]');
        if (modalToggles.length > 0) {
            modalToggles[0].click();
            return true;
        }
        
        // Let's just try to manually show the modal if we know its ID, but we don't know the exact ID.
        // Let's look for any modal with 'Cambio de Rol'
        return false;
    }''')
    
    time.sleep(2)
    
    if not opened:
        print("Could not click the modal toggle. Let's dump header HTML.")
        header_html = page.evaluate("document.querySelector('header') ? document.querySelector('header').innerHTML : ''")
        with open('header_dump.html', 'w') as f:
            f.write(header_html)
        
        # Try to find modal directly
        modal_html = page.evaluate("document.querySelector('.modal') ? document.body.innerHTML : ''")
        with open('body_dump.html', 'w') as f:
            f.write(modal_html)
    else:
        print("Clicked something that looks like the school name. Waiting for modal...")
        time.sleep(2)
        
    page.screenshot(path="edge_modal_open.png")
    
    print("Extracting select options from modal...")
    # Find the select element in the modal
    options = page.evaluate('''() => {
        let selects = document.querySelectorAll('select');
        let res = [];
        selects.forEach(s => {
            let opts = Array.from(s.options).map(o => ({text: o.text, value: o.value}));
            res.push({id: s.id, name: s.name, options: opts});
        });
        return res;
    }''')
    print("Selects found:", options)
    
    target_value = None
    target_select_id = None
    for s in options:
        for opt in s['options']:
            if "Colegio Demo Satisfacción" in opt['text']:
                target_value = opt['value']
                target_select_id = s['id'] or s['name']
                break
                
    if target_value:
        print(f"Selecting {target_value} in {target_select_id}")
        if target_select_id:
            page.select_option(f"select[name='{target_select_id}']", target_value)
            page.select_option(f"select[id='{target_select_id}']", target_value)
        else:
            page.evaluate(f'''() => {{
                let selects = document.querySelectorAll('select');
                selects.forEach(s => {{
                    Array.from(s.options).forEach(o => {{
                        if(o.text.includes('Colegio Demo Satisfacción')) {{
                            s.value = o.value;
                            s.dispatchEvent(new Event('change'));
                        }}
                    }});
                }});
            }}''')
        
        time.sleep(1)
        # Click Cambiar
        page.evaluate('''() => {
            let btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
            let btn = btns.find(b => b.innerText.includes('Cambiar'));
            if(btn) btn.click();
        }''')
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        print("URL after changing school:", page.url)
        page.screenshot(path="edge_demo_school.png")
    else:
        print("Could not find 'Colegio Demo Satisfacción' in the dropdowns.")
        
    # Go to Reportes
    print("Navigating to Reportes...")
    page.evaluate('''() => {
        let links = Array.from(document.querySelectorAll('a'));
        let reportesLink = links.find(l => l.innerText.trim() === 'Reportes');
        if(reportesLink) reportesLink.click();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("URL at Reportes:", page.url)
    page.screenshot(path="edge_reportes.png")
    
    # Dump reportes HTML
    reportes_html = page.evaluate("document.body.innerHTML")
    with open('reportes_dump.html', 'w') as f:
        f.write(reportes_html)

    context.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
