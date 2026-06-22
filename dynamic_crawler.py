import time
import re
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type=\"submit\"]')
    page.wait_for_load_state('networkidle')
    time.sleep(1)
    
    if page.locator('#select-role-form').is_visible():
        page.get_by_text('Colegio Prueba Akdemia').first.click()
        page.evaluate("document.getElementById('select-role-form').submit()")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
    print('Logged in. Fetching users via the UI search box...')
    
    links_found = []
    terms = ['a', 'e', 'profesor', 'juan', 'padre']
    
    for t in terms:
        try:
            # Open modal
            page.locator('a, button, li').filter(has_text="Cambiar a cualquier usuario").first.click()
            time.sleep(1)
            
            # Type into search AND PRESS ENTER
            page.fill('#fill-user-info', t)
            page.keyboard.press("Enter")
            
            # Wait for AJAX results
            time.sleep(3)
            
            # Get results
            results = page.locator('#search-results a').all()
            for r in results:
                href = r.get_attribute('href')
                name = r.inner_text().strip()
                if '\\n' in name:
                    name = name.split('\\n')[0].strip()
                if href and '/users/change_to_anyone' in href:
                    if not any(x['href'] == href for x in links_found):
                        links_found.append({'href': href, 'name': name})
                        
            # Close modal
            page.evaluate("$('#change-to-any-user-modal').modal('hide')")
            time.sleep(1.5)
        except Exception as e:
            print(f"Error extracting for {t}: {e}")
                
    print(f"Extracted {len(links_found)} unique user accounts to test.\\n")
    
    tested_roles = set()
    
    for i, u in enumerate(links_found[:15]):
        print(f"[{i+1}/15] Testing user: {u['name']} ...")
        try:
            page.goto('https://alpha.akdemia.com' + u['href'])
            page.wait_for_load_state('networkidle')
            time.sleep(1.5)
            
            roles_found = []
            if 'select_role' in page.url:
                cards = page.locator('.select-role-user-info').all_inner_texts()
                roles_found = [c.replace('\\n', ' ').strip() for c in cards]
                print(f"  -> SUCCESS: Multiple roles screen detected ({len(roles_found)} roles).")
                print(f"  -> Roles: {roles_found}")
                for r in roles_found: 
                    tested_roles.add(r.split()[0] if ' ' in r else r)
            else:
                role_el = page.locator('.user-role')
                if role_el.count() > 0:
                    role_text = role_el.first.inner_text().strip()
                    print(f"  -> SUCCESS: Logged in directly to dashboard. Role: {role_text}")
                    tested_roles.add(role_text)
                else:
                    print("  -> SUCCESS: Logged in successfully, but role text not found.")
                    tested_roles.add('Unknown')
                    
            page.goto('https://alpha.akdemia.com/users/revert_change_to_anyone')
            page.wait_for_load_state('networkidle')
            time.sleep(1)
        except Exception as e:
            print(f"  -> Error testing {u['name']}: {str(e)[:50]}")
            
    print("\\n================ TESTING COMPLETE ================")
    print("\\nRoles verified via direct user impersonation:")
    for r in tested_roles:
        print(f" - {r}")
    print("==================================================")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
