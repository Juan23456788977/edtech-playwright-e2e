import time
import json
from playwright.sync_api import sync_playwright

findings = []
BASE = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4'

def add_finding(module, severity, title, description):
    findings.append({'module': module, 'severity': severity, 'title': title, 'description': description})

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()

    # === LOGIN ===
    print("1. Login...")
    page.goto('https://omega.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    # Change role to employee + Colegio Prueba
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
    print("   OK - Logged in as Employee @ Colegio Prueba Akdemia")
    
    # === DASHBOARD ESCOLAR ===
    print("\n2. Dashboard Escolar...")
    page.screenshot(path=f'{BASE}/audit_school_dashboard.png', full_page=True)
    
    dashboard = page.evaluate('''() => {
        const sidebar = Array.from(document.querySelectorAll('.sidebar a, nav a, .sidenav a')).map(a => ({
            text: a.innerText.trim(), href: a.href, active: a.classList.contains('active')
        })).filter(l => l.text && l.href.includes('akdemia'));
        
        const cards = Array.from(document.querySelectorAll('.card, .panel, .widget, .info-box, [class*="card"]')).map(c => 
            c.innerText.trim().substring(0, 150)
        );
        
        return { sidebar, cards, title: document.title, bodyPreview: document.body.innerText.substring(0, 500) };
    }''')
    print(f"   Sidebar items: {len(dashboard['sidebar'])}")
    print(f"   Body: {dashboard['bodyPreview'][:200]}")
    
    # === RECURSOS HUMANOS ===
    print("\n3. Recursos Humanos...")
    page.goto('https://omega.akdemia.com/employees')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_rrhh.png', full_page=True)
    
    rrhh = page.evaluate('''() => {
        const tables = document.querySelectorAll('table');
        const result = [];
        tables.forEach((t, i) => {
            const headers = Array.from(t.querySelectorAll('thead th, th')).map(th => th.innerText.trim());
            const rows = t.querySelectorAll('tbody tr').length;
            result.push({idx: i, headers, rows});
        });
        const forms = document.querySelectorAll('form').length;
        const inputs = document.querySelectorAll('input:not([type="hidden"])').length;
        const buttons = Array.from(document.querySelectorAll('button, a.btn, input[type="submit"]')).map(b => b.innerText.trim()).filter(t => t);
        return { tables: result, forms, inputs, buttons: buttons.slice(0, 15), bodyPreview: document.body.innerText.substring(0, 800) };
    }''')
    print(f"   Tables: {len(rrhh['tables'])}")
    for t in rrhh['tables']:
        print(f"     Table {t['idx']}: {t['rows']} rows, headers: {t['headers'][:8]}")
    print(f"   Buttons: {rrhh['buttons'][:10]}")
    
    # === SECCIONES ===
    print("\n4. Secciones...")
    page.goto('https://omega.akdemia.com/batches')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_secciones.png', full_page=True)
    
    secciones = page.evaluate('''() => {
        const items = Array.from(document.querySelectorAll('.panel, .card, .accordion, [class*="section"], .list-group-item, tr, li')).map(el => 
            el.innerText.trim().substring(0, 100)
        ).filter(t => t && t.length > 3);
        return { items: items.slice(0, 30), bodyPreview: document.body.innerText.substring(0, 1000) };
    }''')
    print(f"   Content items: {len(secciones['items'])}")
    print(f"   Body: {secciones['bodyPreview'][:300]}")
    
    # === REPORTES ESCOLARES ===
    print("\n5. Reportes Escolares...")
    page.goto('https://omega.akdemia.com/reports/group')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_reportes.png', full_page=True)
    
    reportes = page.evaluate('''() => {
        const selects = Array.from(document.querySelectorAll('select')).map(s => ({
            name: s.name, id: s.id,
            options: Array.from(s.options).map(o => ({value: o.value, text: o.text}))
        }));
        const links = Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(), href: a.href
        })).filter(l => l.text && l.href.includes('report'));
        return { selects, links: links.slice(0, 20), bodyPreview: document.body.innerText.substring(0, 800) };
    }''')
    print(f"   Selects: {len(reportes['selects'])}")
    for s in reportes['selects']:
        print(f"     {s['name'] or s['id']}: {len(s['options'])} options")
        for o in s['options'][:5]:
            print(f"       - {o['text']} (value={o['value']})")
    
    # === ADMISIÓN ===
    print("\n6. Admisión...")
    page.goto('https://omega.akdemia.com/admission_processes')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_admision.png', full_page=True)
    
    admision = page.evaluate('''() => {
        return {
            tables: document.querySelectorAll('table').length,
            forms: document.querySelectorAll('form').length,
            buttons: Array.from(document.querySelectorAll('button, a.btn')).map(b => b.innerText.trim()).filter(t => t).slice(0, 10),
            bodyPreview: document.body.innerText.substring(0, 800)
        };
    }''')
    print(f"   Tables: {admision['tables']}, Forms: {admision['forms']}")
    print(f"   Buttons: {admision['buttons']}")
    print(f"   Body: {admision['bodyPreview'][:300]}")
    
    # === CONFIGURACIONES ===
    print("\n7. Configuraciones...")
    page.goto('https://omega.akdemia.com/schools/4/settings')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_config.png', full_page=True)
    
    config = page.evaluate('''() => {
        const tabs = Array.from(document.querySelectorAll('.nav-tabs a, .tab-link, [role="tab"]')).map(t => t.innerText.trim());
        const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), select, textarea')).map(i => ({
            type: i.type || i.tagName, name: i.name, id: i.id
        }));
        return { tabs, inputs: inputs.slice(0, 20), bodyPreview: document.body.innerText.substring(0, 800) };
    }''')
    print(f"   Tabs: {config['tabs']}")
    print(f"   Inputs: {len(config['inputs'])}")
    
    # === INASISTENCIAS ===
    print("\n8. Inasistencias...")
    page.goto('https://omega.akdemia.com/schools/4/absences')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_inasistencias.png', full_page=True)
    
    inasist = page.evaluate('''() => {
        return {
            tables: document.querySelectorAll('table').length,
            forms: document.querySelectorAll('form').length,
            bodyPreview: document.body.innerText.substring(0, 600)
        };
    }''')
    print(f"   Tables: {inasist['tables']}, Forms: {inasist['forms']}")
    print(f"   Body: {inasist['bodyPreview'][:300]}")
    
    # === PROMEDIOS ===
    print("\n9. Promedios...")
    page.goto('https://omega.akdemia.com/schools/4/averages')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_promedios.png', full_page=True)
    
    promedios = page.evaluate('''() => {
        return {
            tables: document.querySelectorAll('table').length,
            selects: Array.from(document.querySelectorAll('select')).map(s => ({
                name: s.name, options: Array.from(s.options).map(o => o.text).slice(0, 10)
            })),
            bodyPreview: document.body.innerText.substring(0, 600)
        };
    }''')
    print(f"   Tables: {promedios['tables']}")
    print(f"   Body: {promedios['bodyPreview'][:300]}")
    
    # === CORREOS ===
    print("\n10. Correos...")
    page.goto('https://omega.akdemia.com/conversations')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_correos.png', full_page=True)
    
    correos = page.evaluate('''() => ({
        bodyPreview: document.body.innerText.substring(0, 600),
        buttons: Array.from(document.querySelectorAll('button, a.btn')).map(b => b.innerText.trim()).filter(t => t).slice(0, 10)
    })''')
    print(f"   Body: {correos['bodyPreview'][:200]}")
    print(f"   Buttons: {correos['buttons']}")
    
    # === ENCUESTAS ===
    print("\n11. Encuestas...")
    page.goto('https://omega.akdemia.com/polls')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_encuestas.png', full_page=True)
    
    # === LIBRO DE VIDA ===
    print("\n12. Libro de Vida...")
    page.goto('https://omega.akdemia.com/student_bitacoras')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_bitacora.png', full_page=True)
    
    # === CALENDARIO ===
    print("\n13. Calendario...")
    page.goto('https://omega.akdemia.com/calendar/month')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_calendario.png', full_page=True)
    
    # === NOTICIAS ===
    print("\n14. Noticias...")
    page.goto('https://omega.akdemia.com/newsletters')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_noticias.png', full_page=True)
    
    # === ENGAGEMENT ===
    print("\n15. Engagement...")
    page.goto('https://omega.akdemia.com/engagement')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_engagement.png', full_page=True)
    
    # === PREFERENCIAS ===
    print("\n16. Preferencias...")
    page.goto('https://omega.akdemia.com/user_accounts/195244')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_preferencias.png', full_page=True)
    
    # === USUARIOS BLOQUEADOS ===
    print("\n17. Usuarios Bloqueados...")
    page.goto('https://omega.akdemia.com/schools/4/blocked_users')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_bloqueados.png', full_page=True)
    
    # === SWITCH TO TEACHER ROLE ===
    print("\n18. Switching to Teacher role...")
    page.goto('https://omega.akdemia.com/user_sessions/change_sidebar_menu?role=teacher')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_role_teacher.png', full_page=True)
    
    teacher_sidebar = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.sidebar a, nav a, .sidenav a')).map(a => ({
            text: a.innerText.trim(), href: a.href
        })).filter(l => l.text && l.href.includes('akdemia') && !l.href.includes('#'));
    }''')
    print(f"   Teacher sidebar: {len(teacher_sidebar)} items")
    for item in teacher_sidebar:
        print(f"     - {item['text'][:40]} -> {item['href']}")
    
    # === SWITCH TO STUDIES CONTROL ===
    print("\n19. Switching to Studies Control role...")
    page.goto('https://omega.akdemia.com/user_sessions/change_sidebar_menu?role=studies_control')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_school_role_control.png', full_page=True)
    
    control_sidebar = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.sidebar a, nav a, .sidenav a')).map(a => ({
            text: a.innerText.trim(), href: a.href
        })).filter(l => l.text && l.href.includes('akdemia') && !l.href.includes('#'));
    }''')
    print(f"   Control sidebar: {len(control_sidebar)} items")
    for item in control_sidebar:
        print(f"     - {item['text'][:40]} -> {item['href']}")

    # Save findings
    with open(f'{BASE}/audit_school_findings.json', 'w') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    browser.close()
    p.stop()
    print(f"\n=== SCHOOL AUDIT COMPLETE === {len(findings)} findings")

if __name__ == '__main__':
    run()
