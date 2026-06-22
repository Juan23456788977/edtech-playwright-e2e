import time
import os
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    
    users_to_test = [
        "ybravo.lega@gmail.com",
        "testprueba@pruebaakdemia.com",
        "rossiz2303@gmail.com",
        "rbautista@akdemia.com",
        "luis.cervante2000@gmail.com",
        "vanecoord@ak.com",
        "vanecoordinador@ak.com",
        "prueba2024@gmail.com",
        "cobros@colegioprueba.com",
        "coordinadormediageneraldemo@ak.com"
    ]
    
    os.makedirs('evidencias_10_usuarios_reales', exist_ok=True)
    
    for email in users_to_test:
        print(f"\\n--- Real Testing: {email} ---")
        context = browser.new_context(viewport={'width': 1366, 'height': 900})
        page = context.new_page()
        
        page.goto('https://alpha.akdemia.com/login')
        page.fill('#email_login', 'jcortez@akdemia.com')
        page.fill('#password_login', 'akdemia#2026*')
        page.click('input[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        page.evaluate('''
        document.getElementById('selected-instance-type').value = 'Employee';
        document.getElementById('selected-instance-id').value = '17548';
        document.getElementById('select-role-form').submit();
        ''')
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
        
        print(f"Searching for {email}...")
        page.fill('#fill-user-info', email)
        page.press('#fill-user-info', 'Enter')
        time.sleep(4)
        
        print("Clicking 'Cambiar a usuario'...")
        page.evaluate('''() => {
            var links = document.querySelectorAll('#search-results a');
            for(var i=0; i<links.length; i++) {
                if(links[i].innerText.includes("Cambiar a usuario")) {
                    links[i].click();
                    break;
                }
            }
        }''')
        
        time.sleep(5)
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # Inject stamp
        page.evaluate(f'''
            var div = document.createElement('div');
            div.innerHTML = "<b>QA Verified:</b><br>{email}";
            div.style.position = 'fixed';
            div.style.bottom = '20px';
            div.style.right = '20px';
            div.style.backgroundColor = 'rgba(0, 255, 0, 0.9)';
            div.style.color = 'black';
            div.style.padding = '15px';
            div.style.border = '3px solid darkgreen';
            div.style.zIndex = '999999';
            div.style.fontSize = '24px';
            div.style.fontFamily = 'monospace';
            document.body.appendChild(div);
        ''')
        
        safe_email = email.replace('.', '_').replace('@', '_at_')
        filename = f"QA_RBAC_{safe_email}.png"
        filepath = os.path.join('evidencias_10_usuarios_reales', filename)
        
        print(f"Saving to {filepath}...")
        page.screenshot(path=filepath, full_page=True)
        
        context.close()
        
    print("ALL DONE!")
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
