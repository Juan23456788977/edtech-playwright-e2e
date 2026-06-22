import requests
import re
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch()
    page = browser.new_page()
    
    print('Logging in...')
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
        
    print('Fetching cookies and preparing headers...')
    cookies = page.context.cookies()
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    headers = {
        'Cookie': cookie_str,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript'
    }
    
    links_found = []
    terms = ['a', 'e', 'profesor', 'juan', 'padre', 'V-1', 'V-2', 'V-3']
    
    print('Searching via XHR requests...')
    for t in terms:
        res = requests.get(f'https://alpha.akdemia.com/users/search_for_change_to_anyone?search_input={t}', headers=headers)
        
        # Unescape JS response
        clean_html = res.text.replace('\\"', '"').replace('\\/', '/')
        matches = re.findall(r'<a href="(/users/change_to_anyone/[^"]+)"[^>]*>([^<]+)</a>', clean_html)
        
        for href, name in matches:
            name = name.strip()
            if '\\n' in name:
                name = name.split('\\n')[0].strip()
            if not any(x['href'] == href for x in links_found):
                links_found.append({'href': href, 'name': name})
                
    print(f"Extracted {len(links_found)} unique user accounts.\\n")
    
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
                    print("  -> SUCCESS: Logged in, but could not read role explicitly.")
                    tested_roles.add('Unknown Role')
                    
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
