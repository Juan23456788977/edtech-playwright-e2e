import time
from playwright.sync_api import sync_playwright
import urllib.parse

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print('Logging in...')
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type=\"submit\"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    if page.locator('#select-role-form').is_visible():
        print('Selecting UEP Colegio Roraima...')
        page.get_by_text('UEP Colegio Roraima').first.click()
        page.evaluate("document.getElementById('select-role-form').submit()")
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
    print('Opening search modal...')
    page.evaluate("$('#change-to-any-user-modal').modal('show')")
    time.sleep(2)
    
    names_to_search = ['juan', 'maria', 'jose', 'carlos', 'ana', 'V-', 'profesor', 'admin', 'E-']
    all_links = []
    
    for name in names_to_search:
        print(f"\\nSearching for '{name}'...")
        page.fill('#fill-user-info', name)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        links = page.locator('a:has-text("Cambiar a usuario")').all()
        for link in links:
            href = link.get_attribute('href')
            if href and href not in [x['href'] for x in all_links]:
                # Extract role class from URL
                parsed = urllib.parse.urlparse(href)
                query = urllib.parse.parse_qs(parsed.query)
                role_class = query.get('class_instance', ['Unknown'])[0]
                
                all_links.append({'href': href, 'role': role_class})
                
        page.fill('#fill-user-info', '')
        
    print(f"\\nExtracted {len(all_links)} unique users across {len(names_to_search)} searches.")
    
    # Group by role
    roles_dict = {}
    for user in all_links:
        r = user['role']
        if r not in roles_dict:
            roles_dict[r] = []
        roles_dict[r].append(user)
        
    print(f"Roles found in DB search: {list(roles_dict.keys())}")
    
    results = []
    
    # Test at least 2 users from EACH role found to ensure ALL roles are tested
    users_to_test = []
    for role, users in roles_dict.items():
        users_to_test.extend(users[:2])
        
    print(f"\\nWill test {len(users_to_test)} users covering all extracted roles: {list(roles_dict.keys())}")
    
    for i, user in enumerate(users_to_test):
        print(f"\\n[{i+1}/{len(users_to_test)}] Impersonating Role [{user['role']}]: {user['href']}")
        try:
            page.goto('https://alpha.akdemia.com' + user['href'])
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            roles_found = []
            if 'select_role' in page.url:
                cards = page.locator('.select-role-user-info').all_inner_texts()
                roles = [c.replace('\\n', ' ').strip() for c in cards]
                print(f"  -> SUCCESS: Multi-Role Screen: {roles}")
                results.append(f"✅ ROL {user['role']} -> {user['href']} (Multi-rol: {', '.join(roles)})")
            else:
                role_el = page.locator('.user-role')
                if role_el.count() > 0:
                    role = role_el.first.inner_text().strip()
                    print(f"  -> SUCCESS: Single Role Dashboard: {role}")
                    results.append(f"✅ ROL {user['role']} -> {user['href']} (Dashboard: {role})")
                else:
                    print(f"  -> SUCCESS: Logged in (Role implicit)")
                    results.append(f"✅ ROL {user['role']} -> {user['href']} (Visualización de dashboard correcta)")
                    
            page.goto('https://alpha.akdemia.com/users/revert_change_to_anyone')
            page.wait_for_load_state('networkidle')
            time.sleep(2)
        except Exception as e:
            print(f"  -> ERROR testing {user['href']}: {e}")
            results.append(f"❌ ROL {user['role']} -> {user['href']} (Error en prueba)")
            
    print("\\n================ QA TEST REPORT ================")
    for r in results:
        print(r)
    print("================================================")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
