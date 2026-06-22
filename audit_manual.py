import time
import json
from playwright.sync_api import sync_playwright

findings = []

def add_finding(module, severity, title, description, expected, actual, screenshot=None):
    findings.append({
        'module': module,
        'severity': severity,
        'title': title,
        'description': description,
        'expected': expected,
        'actual': actual,
        'screenshot': screenshot
    })

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1366, 'height': 900})
    page = context.new_page()
    
    BASE = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4'

    # === LOGIN ===
    print("1. Login...")
    page.goto('https://omega.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    # Change role
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
    
    # Go to cobros
    links = page.evaluate('''() => Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText.trim(), href: a.href}))''')
    cobros_href = next((l['href'] for l in links if 'Cobranzas' in l['text']), None)
    page.goto(cobros_href)
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
    
    print("   Logged in and changed to Colegio Prueba Akdemia in Cobros")
    
    # === AUDIT DASHBOARD ===
    print("\n2. Auditing Dashboard...")
    page.screenshot(path=f'{BASE}/audit_dashboard_cobros.png', full_page=True)
    
    # Check dashboard cards/stats
    dashboard_data = page.evaluate('''() => {
        const texts = [];
        document.querySelectorAll('.card, .panel, .info-box, .stat, .widget, [class*="card"], [class*="dashboard"]').forEach(el => {
            texts.push(el.innerText.trim().substring(0, 200));
        });
        return {
            title: document.title,
            h1: document.querySelector('h1,h2')?.innerText?.trim() || 'N/A',
            cards: texts,
            links: Array.from(document.querySelectorAll('.sidebar a, nav a')).map(a => ({
                text: a.innerText.trim(), href: a.href, active: a.classList.contains('active')
            })).filter(l => l.text)
        };
    }''')
    print(f"   Title: {dashboard_data['title']}")
    print(f"   Cards: {len(dashboard_data['cards'])}")
    for i, card in enumerate(dashboard_data['cards'][:10]):
        print(f"     Card {i}: {card[:100]}")
    
    # Check for broken images, empty states
    broken = page.evaluate('''() => {
        const issues = [];
        document.querySelectorAll('img').forEach(img => {
            if (!img.complete || img.naturalWidth === 0) issues.push(img.src);
        });
        return issues;
    }''')
    if broken:
        add_finding('Dashboard', 'Low', 'Broken images', f'{len(broken)} broken images on dashboard', 'All images load', f'Broken: {broken}', f'{BASE}/audit_dashboard_cobros.png')
    
    # === AUDIT CONFIGURACIÓN ===
    print("\n3. Auditing Configuración...")
    page.click('#settings')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_config_cobros.png', full_page=True)
    
    config_data = page.evaluate('''() => {
        const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
            type: el.type, name: el.name, id: el.id, value: el.value?.substring(0, 50),
            required: el.required, placeholder: el.placeholder
        }));
        const labels = Array.from(document.querySelectorAll('label')).map(l => l.innerText.trim());
        const tables = document.querySelectorAll('table').length;
        return { inputs, labels, tables };
    }''')
    print(f"   Inputs: {len(config_data['inputs'])}")
    print(f"   Labels: {config_data['labels'][:10]}")
    print(f"   Tables: {config_data['tables']}")
    
    for inp in config_data['inputs']:
        if inp['name']:
            print(f"     [{inp['type']}] name={inp['name']} value='{inp['value']}' required={inp['required']}")
    
    # === AUDIT CLIENTES EXTERNOS ===
    print("\n4. Auditing Clientes Externos...")
    page.click('#external-clients')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_clientes_ext.png', full_page=True)
    
    clients_data = page.evaluate('''() => {
        const rows = document.querySelectorAll('table tbody tr');
        const headers = Array.from(document.querySelectorAll('table thead th')).map(th => th.innerText.trim());
        return {
            headers,
            rowCount: rows.length,
            firstRows: Array.from(rows).slice(0, 5).map(r => r.innerText.trim().substring(0, 100))
        };
    }''')
    print(f"   Headers: {clients_data['headers']}")
    print(f"   Rows: {clients_data['rowCount']}")
    
    # === AUDIT ESTADO DE CUENTA ===
    print("\n5. Auditing Estado de Cuenta...")
    page.click('#register_payment')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_estado_cuenta.png', full_page=True)
    
    estado_data = page.evaluate('''() => {
        return {
            forms: document.querySelectorAll('form').length,
            inputs: Array.from(document.querySelectorAll('input')).map(i => ({
                type: i.type, name: i.name, id: i.id, placeholder: i.placeholder
            })),
            selects: Array.from(document.querySelectorAll('select')).map(s => ({
                name: s.name, id: s.id,
                options: Array.from(s.options).map(o => o.text)
            })),
            bodyText: document.body.innerText.substring(0, 500)
        };
    }''')
    print(f"   Forms: {estado_data['forms']}")
    for i in estado_data['inputs']:
        if i['name'] or i['id']:
            print(f"     Input: name={i['name']} id={i['id']} type={i['type']} placeholder={i['placeholder']}")
    
    # === AUDIT PAGOS ===
    print("\n6. Auditing Pagos...")
    page.click('#payment_details')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_pagos.png', full_page=True)
    
    pagos_data = page.evaluate('''() => {
        const tables = document.querySelectorAll('table');
        const result = [];
        tables.forEach((t, idx) => {
            const headers = Array.from(t.querySelectorAll('thead th')).map(th => th.innerText.trim());
            const rows = t.querySelectorAll('tbody tr').length;
            result.push({idx, headers, rows});
        });
        return result;
    }''')
    print(f"   Tables: {len(pagos_data)}")
    for t in pagos_data:
        print(f"     Table {t['idx']}: {t['rows']} rows, headers: {t['headers'][:8]}")
    
    # === AUDIT DEUDAS ===
    print("\n7. Auditing Deudas...")
    page.click('#debts')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_deudas.png', full_page=True)
    
    deudas_text = page.evaluate('() => document.body.innerText.substring(0, 800)')
    print(f"   Content preview: {deudas_text[:200]}")
    
    # === AUDIT NOTAS DE DÉBITO ===
    print("\n8. Auditing Notas de Débito...")
    page.click('#debit-notes')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_notas_debito.png', full_page=True)
    
    notas_data = page.evaluate('''() => {
        const table = document.querySelector('table');
        if (!table) return {hasTable: false};
        return {
            hasTable: true,
            headers: Array.from(table.querySelectorAll('thead th')).map(th => th.innerText.trim()),
            rows: table.querySelectorAll('tbody tr').length
        };
    }''')
    print(f"   Notas Débito: {notas_data}")
    
    # === AUDIT NOTAS DE CRÉDITO ===
    print("\n9. Auditing Notas de Crédito...")
    page.click('#credit-notes')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_notas_credito.png', full_page=True)
    
    credito_data = page.evaluate('''() => {
        const table = document.querySelector('table');
        if (!table) return {hasTable: false};
        return {
            hasTable: true,
            headers: Array.from(table.querySelectorAll('thead th')).map(th => th.innerText.trim()),
            rows: table.querySelectorAll('tbody tr').length
        };
    }''')
    print(f"   Notas Crédito: {credito_data}")
    
    # === AUDIT TASA BCV ===
    print("\n10. Auditing Tasa BCV...")
    page.click('#official_exchange_rates')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_tasa_bcv.png', full_page=True)
    
    bcv_data = page.evaluate('''() => {
        const table = document.querySelector('table');
        if (!table) return {hasTable: false};
        const rows = Array.from(table.querySelectorAll('tbody tr')).slice(0, 5).map(r => r.innerText.trim());
        return {
            hasTable: true,
            headers: Array.from(table.querySelectorAll('thead th')).map(th => th.innerText.trim()),
            totalRows: table.querySelectorAll('tbody tr').length,
            firstRows: rows
        };
    }''')
    print(f"   Tasa BCV: {bcv_data.get('totalRows', 0)} rows")
    if bcv_data.get('firstRows'):
        for r in bcv_data['firstRows']:
            print(f"     {r[:100]}")
    
    # === AUDIT LIBRO DE VENTAS ===
    print("\n11. Auditing Libro de Ventas...")
    page.click('#sales-book')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    page.screenshot(path=f'{BASE}/audit_libro_ventas.png', full_page=True)
    
    ventas_data = page.evaluate('''() => {
        return {
            forms: document.querySelectorAll('form').length,
            inputs: Array.from(document.querySelectorAll('input')).map(i => ({
                type: i.type, name: i.name, id: i.id, value: i.value
            })).filter(i => i.name),
            bodyText: document.body.innerText.substring(0, 500)
        };
    }''')
    print(f"   Libro Ventas: {ventas_data['forms']} forms")
    print(f"   Content: {ventas_data['bodyText'][:200]}")
    
    # === UI/UX CONSISTENCY CHECK ===
    print("\n12. UI/UX Consistency Check...")
    
    # Check all pages for common issues
    pages_to_check = [
        ('#settings', 'Configuración'),
        ('#external-clients', 'Clientes Externos'),
        ('#register_payment', 'Estado de Cuenta'),
        ('#payment_details', 'Pagos'),
        ('#reports', 'Reportes'),
        ('#debit-notes', 'Notas Débito'),
        ('#credit-notes', 'Notas Crédito'),
    ]
    
    for selector, name in pages_to_check:
        try:
            page.click(selector)
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            issues = page.evaluate('''() => {
                const issues = [];
                
                // Check for console errors (via DOM)
                const alerts = document.querySelectorAll('.alert-danger, .alert-error, .error');
                alerts.forEach(a => issues.push({type: 'error_alert', text: a.innerText.trim()}));
                
                // Check for empty states without proper message
                const tables = document.querySelectorAll('table');
                tables.forEach(t => {
                    if (t.querySelectorAll('tbody tr').length === 0) {
                        const emptyMsg = t.closest('.panel, .card, .container')?.querySelector('.empty, .no-data, .text-muted');
                        if (!emptyMsg) issues.push({type: 'empty_table_no_message', text: 'Table is empty but no empty state message'});
                    }
                });
                
                // Check for broken links
                const links = document.querySelectorAll('a[href=""], a[href="#"], a[href="javascript:void(0)"]');
                if (links.length > 2) issues.push({type: 'placeholder_links', text: `${links.length} placeholder links found`});
                
                // Check for missing labels on inputs
                const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"])');
                let unlabeled = 0;
                inputs.forEach(i => {
                    if (!i.labels?.length && !i.getAttribute('aria-label') && !i.placeholder) unlabeled++;
                });
                if (unlabeled > 0) issues.push({type: 'unlabeled_inputs', text: `${unlabeled} inputs without labels`});
                
                return issues;
            }''')
            
            if issues:
                for issue in issues:
                    print(f"   ⚠️ [{name}] {issue['type']}: {issue['text']}")
                    add_finding(name, 'Medium', issue['type'], issue['text'], 'No UI issues', issue['text'])
        except Exception as e:
            print(f"   Error checking {name}: {e}")
    
    # Save findings
    with open(f'{BASE}/audit_findings_manual.json', 'w') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== AUDIT COMPLETE === {len(findings)} findings")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
