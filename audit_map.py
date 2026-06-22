import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    BASE_URL = 'https://omega.akdemia.com'
    print(f"=== MAPA DE MÓDULOS AKDEMIA ===\n")
    
    # Login
    print("1. Login...")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    # Change to Colegio Prueba Akdemia
    page.click('a[href="#change-role-modal"]')
    time.sleep(2)
    page.click('input[name="role"][value="employee"]', force=True)
    time.sleep(2)
    page.fill('#fill-school', 'Colegio Prueba Akdemia')
    time.sleep(1)
    page.click('.dropdown-toggle')
    time.sleep(2)
    page.locator('#change-role li').filter(has_text='Colegio Prueba Akdemia').first.click()
    time.sleep(2)
    page.click('#change-role-button')
    page.wait_for_load_state('networkidle')
    time.sleep(4)
    
    # === MÓDULO ESCOLAR (omega.akdemia.com) ===
    print("\n=== MÓDULO ESCOLAR (omega.akdemia.com) ===")
    
    # Get all sidebar links
    school_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href,
            id: a.id,
            classes: a.className
        })).filter(l => l.href && l.text && !l.href.includes('javascript'));
    }''')
    
    print("\nLinks del dashboard escolar:")
    seen = set()
    for l in school_links:
        key = l['href']
        if key not in seen and 'akdemia.com' in key:
            seen.add(key)
            print(f"  [{l['id'] or '-'}] {l['text'][:60]} -> {l['href']}")
    
    # Take screenshot of main dashboard
    ss1 = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/audit_school_dashboard.png'
    page.screenshot(path=ss1, full_page=True)
    
    # Navigate to each main section and collect sub-links
    sections_to_visit = []
    for l in school_links:
        if l['href'].startswith('https://omega.akdemia.com/') and l['href'] != 'https://omega.akdemia.com/' and l['text']:
            sections_to_visit.append(l)
    
    # Visit key sections
    visited = set()
    for section in sections_to_visit[:20]:
        if section['href'] in visited:
            continue
        visited.add(section['href'])
        try:
            page.goto(section['href'], timeout=10000)
            page.wait_for_load_state('networkidle')
            time.sleep(1)
            
            # Get page title and sub-links
            title = page.evaluate('() => document.querySelector("h1, h2, .page-title, .content-header")?.innerText?.trim() || document.title')
            sub_links = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.sidebar a, .nav a, .menu a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.href
                })).filter(l => l.text && l.href);
            }''')
            
            print(f"\n  📁 {section['text'][:40]} ({section['href']})")
            print(f"     Title: {title[:80]}")
            if sub_links:
                seen_sub = set()
                for sl in sub_links[:10]:
                    if sl['href'] not in seen_sub:
                        seen_sub.add(sl['href'])
                        print(f"       - {sl['text'][:50]} -> {sl['href']}")
        except:
            pass
    
    # === MÓDULO COBRANZAS (cobros.akdemia.com) ===
    print("\n\n=== MÓDULO COBRANZAS (cobros.akdemia.com) ===")
    
    page.goto('https://cobros.akdemia.com/')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # Change school in cobros
    page.click('#change-role')
    time.sleep(2)
    page.click('input[type="radio"]', force=True)
    time.sleep(1)
    page.click('#selected_school')
    time.sleep(1)
    page.type('#selected_school', 'Colegio Prueba', delay=100)
    time.sleep(3)
    page.locator('.dropdown-menu li').filter(has_text='Colegio Prueba Akdemia').first.click()
    time.sleep(2)
    page.click('#change_role_button', force=True)
    page.wait_for_load_state('networkidle')
    time.sleep(4)
    
    # Get all cobros links
    cobros_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href,
            id: a.id
        })).filter(l => l.href && l.text && !l.href.includes('javascript'));
    }''')
    
    print("\nLinks del módulo de cobranzas:")
    seen_cobros = set()
    for l in cobros_links:
        key = l['href']
        if key not in seen_cobros and 'cobros' in key:
            seen_cobros.add(key)
            print(f"  [{l['id'] or '-'}] {l['text'][:60]} -> {l['href']}")
    
    ss2 = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/audit_cobros_dashboard.png'
    page.screenshot(path=ss2, full_page=True)
    
    # Visit each cobros section
    visited_cobros = set()
    for section in cobros_links:
        if 'cobros.akdemia.com' in section['href'] and section['href'] not in visited_cobros:
            visited_cobros.add(section['href'])
            try:
                page.goto(section['href'], timeout=10000)
                page.wait_for_load_state('networkidle')
                time.sleep(1)
                
                title = page.evaluate('() => document.querySelector("h1, h2, .page-title")?.innerText?.trim() || document.title')
                
                # Check for forms, tables, buttons
                page_elements = page.evaluate('''() => ({
                    forms: document.querySelectorAll('form').length,
                    tables: document.querySelectorAll('table').length,
                    selects: document.querySelectorAll('select').length,
                    inputs: document.querySelectorAll('input').length,
                    buttons: document.querySelectorAll('button, input[type="submit"]').length
                })''')
                
                print(f"\n  📁 {section['text'][:40]} ({section['href']})")
                print(f"     Title: {title[:80]}")
                print(f"     Elements: {page_elements}")
            except:
                pass
    
    browser.close()
    p.stop()
    print("\n\n=== MAPEO COMPLETADO ===")

if __name__ == '__main__':
    run()
