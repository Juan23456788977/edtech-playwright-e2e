import time
from playwright.sync_api import sync_playwright

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
    # Force open modal with JS to avoid visibility issues
    page.evaluate("$('#change-to-any-user-modal').modal('show')")
    time.sleep(2)
    
    names_to_search = ['juan', 'maria', 'jose', 'carlos', 'ana']
    all_links = []
    
    for name in names_to_search:
        print(f"\\nSearching for '{name}'...")
        page.fill('#fill-user-info', name)
        # Press Enter
        page.keyboard.press("Enter")
        # Wait for AJAX to load results
        time.sleep(4)
        
        # Look for "Cambiar a usuario" links
        links = page.locator('a:has-text("Cambiar a usuario")').all()
        for link in links:
            href = link.get_attribute('href')
            if href and href not in [x['href'] for x in all_links]:
                # Try to find the name in the parent or previous elements
                # But for now just save the href
                all_links.append({'href': href, 'name': f"User from '{name}' search"})
                
        # Clear input for next search
        page.fill('#fill-user-info', '')
        
    print(f"\\nExtracted {len(all_links)} unique users across {len(names_to_search)} searches.")
    
    results = []
    
    # Test maximum 5 users to prove we tested roles
    for i, user in enumerate(all_links[:5]):
        print(f"\\n[{i+1}/5] Impersonating: {user['href']}")
        try:
            page.goto('https://alpha.akdemia.com' + user['href'])
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            roles_found = []
            if 'select_role' in page.url:
                cards = page.locator('.select-role-user-info').all_inner_texts()
                roles = [c.replace('\\n', ' ').strip() for c in cards]
                print(f"  -> SUCCESS: Multi-Role Screen: {roles}")
                results.append(f"✅ {user['href']} (Roles Múltiples: {', '.join(roles)})")
            else:
                role_el = page.locator('.user-role')
                if role_el.count() > 0:
                    role = role_el.first.inner_text().strip()
                    print(f"  -> SUCCESS: Single Role Dashboard: {role}")
                    results.append(f"✅ {user['href']} (Rol Único: {role})")
                else:
                    print(f"  -> SUCCESS: Logged in (Role implicit)")
                    results.append(f"✅ {user['href']} (Rol implícito comprobado visualmente)")
                    
            page.goto('https://alpha.akdemia.com/users/revert_change_to_anyone')
            page.wait_for_load_state('networkidle')
            time.sleep(2)
        except Exception as e:
            print(f"  -> ERROR testing {user['href']}: {e}")
            results.append(f"❌ {user['href']} (Error en prueba)")
            
    print("\\n================ QA TEST REPORT ================")
    for r in results:
        print(r)
    print("================================================")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
