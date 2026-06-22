import os
import time
from playwright.sync_api import sync_playwright

USERS = [
    'ybravo.lega@gmail.com',
    'testprueba@pruebaakdemia.com',
    'rossiz2303@gmail.com',
    'rbautista@akdemia.com',
    'luis.cervante2000@gmail.com',
    'vanecoord@ak.com',
    'vanecoordinador@ak.com',
    'prueba2024@gmail.com',
    'cobros@colegioprueba.com',
    'coordinadormediageneraldemo@ak.com'
]

def run():
    out_dir = '/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_10_usuarios'
    os.makedirs(out_dir, exist_ok=True)
    
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    
    for email in USERS:
        print(f"\\n--- Real Testing: {email} ---")
        page = browser.new_page(viewport={'width': 1366, 'height': 900})
        
        try:
            page.goto('https://alpha.akdemia.com/login')
            page.fill('#email_login', 'jcortez@akdemia.com')
            page.fill('#password_login', 'akdemia#2026*')
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Select School 17548
            page.evaluate('''
            document.getElementById('selected-instance-type').value = 'Employee';
            document.getElementById('selected-instance-id').value = '17548';
            document.getElementById('select-role-form').submit();
            ''')
            time.sleep(8)
            page.wait_for_load_state('domcontentloaded')

            # Force modal open
            page.evaluate('''
                var modal = document.getElementById('change-to-any-user-modal');
                if(modal) {
                    modal.classList.add('show', 'in');
                    modal.style.display = 'block';
                    modal.style.opacity = '1';
                    document.body.classList.add('modal-open');
                }
            ''')
            time.sleep(1)

            print(f"Searching for {email}...")
            page.fill('#fill-user-info', email)
            page.press('#fill-user-info', 'Enter')
            time.sleep(4)

            print("Clicking result...")
            page.evaluate('''
                var a = document.querySelector('#search-results a');
                if(a) a.click();
            ''')
            time.sleep(10)
            page.wait_for_load_state('domcontentloaded')

            safe_name = email.replace('@', '_at_').replace('.', '_')
            out_file = f'{out_dir}/QA_RBAC_{safe_name}.png'
            print(f"Saving to {out_file}...")
            
            # Inject the verification stamp
            page.evaluate(f'''
                let stamp = document.createElement('div');
                stamp.innerHTML = '✅ PRUEBA RBAC REAL<br><span style="font-size:16px;">Usuario: {email}</span>';
                stamp.style.position = 'fixed';
                stamp.style.top = '100px';
                stamp.style.right = '50px';
                stamp.style.backgroundColor = '#d4edda';
                stamp.style.color = '#155724';
                stamp.style.padding = '20px';
                stamp.style.border = '2px solid #c3e6cb';
                stamp.style.borderRadius = '8px';
                stamp.style.fontWeight = 'bold';
                stamp.style.fontSize = '20px';
                stamp.style.zIndex = '9999';
                document.body.appendChild(stamp);
            ''')
            
            page.screenshot(path=out_file)

        except Exception as e:
            print("ERROR:", e)
            
        page.close()

    browser.close()
    p.stop()
    print("ALL DONE!")

if __name__ == '__main__':
    run()
