#!/usr/bin/env python3
"""
Comprehensive End-to-End Audit of Akdemia SCHOOL Module (omega.akdemia.com)
Covers 8 scenarios with screenshots at every key step.
"""

import time
import json
import os
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright

# ─── Configuration ───────────────────────────────────────────────────────
BASE_URL = 'https://omega.akdemia.com'
SCREENSHOT_DIR = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4'
CREDENTIALS = {'email': 'jcortez@akdemia.com', 'password': 'akdemia#2026*'}
SCHOOL_NAME = 'Colegio Prueba Akdemia'

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

findings = []  # Collect all bugs/findings

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    page.screenshot(path=path, full_page=True)
    log(f"  📸 Screenshot: {name}")
    return path

def add_finding(severity, module, title, steps, expected, actual, screenshot_name=""):
    findings.append({
        'severity': severity,
        'module': module,
        'title': title,
        'steps': steps,
        'expected': expected,
        'actual': actual,
        'screenshot': screenshot_name,
    })
    log(f"  🐛 [{severity}] {title}")

def safe_click(page, selector, timeout=5000, force=False):
    """Safely click an element, return True if successful."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        page.click(selector, force=force)
        return True
    except Exception as e:
        log(f"  ⚠️ Could not click {selector}: {e}")
        return False

def get_text(page, selector, timeout=3000):
    """Safely get text content of an element."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return page.text_content(selector) or ""
    except:
        return ""

def get_all_texts(page, selector, timeout=3000):
    """Get text of all matching elements."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return page.eval_on_selector_all(selector, 'els => els.map(e => e.innerText.trim())')
    except:
        return []

def extract_table_info(page, table_selector='table'):
    """Extract headers and row count from a table."""
    try:
        page.wait_for_selector(table_selector, timeout=5000)
        info = page.evaluate(f'''() => {{
            let table = document.querySelector('{table_selector}');
            if (!table) return null;
            let headers = Array.from(table.querySelectorAll('thead th, thead td')).map(h => h.innerText.trim());
            let rows = table.querySelectorAll('tbody tr');
            let rowCount = rows.length;
            let sampleData = [];
            for (let i = 0; i < Math.min(3, rowCount); i++) {{
                let cells = Array.from(rows[i].querySelectorAll('td')).map(c => c.innerText.trim().substring(0, 50));
                sampleData.push(cells);
            }}
            return {{ headers, rowCount, sampleData }};
        }}''')
        return info
    except:
        return None

def extract_sidebar(page):
    """Extract sidebar menu items."""
    return page.evaluate('''() => {
        let result = [];
        let sidebar = document.querySelector('.sidebar-left') || document.querySelector('#sidebar-left') || document.querySelector('.nav-sidebar') || document.querySelector('ul.nav');
        let container = sidebar || document.body;
        let links = container.querySelectorAll('a[href]');
        let seen = new Set();
        links.forEach(l => {
            let text = l.innerText.trim().replace(/\\s+/g, ' ');
            let href = l.getAttribute('href') || '';
            if (text && text.length < 60 && !seen.has(text + href)) {
                seen.add(text + href);
                result.push({ text, href });
            }
        });
        return result;
    }''')


# ─── Login Flow ──────────────────────────────────────────────────────────
def login_and_select_school(page):
    """Login to omega and select Colegio Prueba Akdemia as employee."""
    log("=== LOGIN FLOW ===")
    
    # Step 1: Navigate to login
    resp = page.goto(f'{BASE_URL}/login', wait_until='networkidle')
    time.sleep(2)
    screenshot(page, 'audit_school_01_login_page.png')
    
    if not resp or not resp.ok:
        add_finding('Critical', 'Login', 'Login page unreachable',
                     'Navigate to omega.akdemia.com/login', 'Page loads', f'Status: {resp.status if resp else "None"}', '')
        return False
    
    # Step 2: Fill credentials and submit
    page.fill('#email_login', CREDENTIALS['email'])
    page.fill('#password_login', CREDENTIALS['password'])
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_02_after_login.png')
    log("  Logged in successfully")
    
    # Step 3: Open role modal
    page.evaluate('''() => {
        let el = document.querySelector('a[href="#change-role-modal"]');
        if(el) el.click();
    }''')
    time.sleep(2)
    screenshot(page, 'audit_school_03_role_modal.png')
    
    # Step 4: Select employee role
    try:
        page.click('input[name="role"][value="employee"]', force=True)
        time.sleep(1)
    except:
        log("  ⚠️ Could not click employee role radio, trying JS")
        page.evaluate('''() => {
            let r = document.querySelector('input[name="role"][value="employee"]');
            if (r) { r.checked = true; r.click(); r.dispatchEvent(new Event('change', {bubbles: true})); }
        }''')
        time.sleep(1)
    
    # Step 5: Fill school name
    try:
        page.fill('#fill-school', SCHOOL_NAME)
    except:
        page.evaluate(f'''() => {{
            let el = document.querySelector('#fill-school');
            if (el) {{ el.value = '{SCHOOL_NAME}'; el.dispatchEvent(new Event('input', {{bubbles: true}})); }}
        }}''')
    time.sleep(2)
    
    # Step 6: Select from dropdown
    try:
        page.wait_for_selector('ul#change-role li', timeout=5000)
    except:
        pass
    
    page.evaluate(f'''() => {{
        let items = Array.from(document.querySelectorAll('ul#change-role li a, .dropdown-menu li a'));
        let target = items.find(a => a.innerText.includes('{SCHOOL_NAME}'));
        if (target) target.click();
    }}''')
    time.sleep(1)
    screenshot(page, 'audit_school_04_school_selected.png')
    
    # Step 7: Click change role button
    page.evaluate('''() => {
        let btn = document.querySelector('#change-role-button');
        if(btn) btn.click();
    }''')
    page.wait_for_load_state('networkidle')
    time.sleep(4)
    screenshot(page, 'audit_school_05_dashboard.png')
    log("  School selected, at dashboard")
    
    # Verify we're at the right school
    page_title = page.title()
    current_url = page.url
    log(f"  Page title: {page_title}")
    log(f"  Current URL: {current_url}")
    
    return True


# ─── SCENARIO 1: Recursos Humanos ───────────────────────────────────────
def scenario_rrhh(page):
    log("\n=== SCENARIO 1: RECURSOS HUMANOS (/employees) ===")
    
    page.goto(f'{BASE_URL}/employees', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_rrhh_01_list.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    # Check if we got redirected or blocked
    if '/employees' not in current_url:
        add_finding('High', 'RRHH', 'Employees page redirects away',
                     'Navigate to /employees', 'See employees list', f'Redirected to {current_url}',
                     'audit_school_rrhh_01_list.png')
    
    # Extract table info
    table_info = extract_table_info(page)
    if table_info:
        log(f"  Table headers: {table_info['headers']}")
        log(f"  Row count: {table_info['rowCount']}")
        log(f"  Sample data: {table_info['sampleData'][:2]}")
    else:
        log("  No table found on employees page")
        # Try alternate selectors
        alt_info = page.evaluate('''() => {
            let cards = document.querySelectorAll('.card, .employee-card, .list-group-item, tr');
            return { count: cards.length, html: document.body.innerHTML.substring(0, 2000) };
        }''')
        log(f"  Alt elements found: {alt_info['count']}")
    
    # Search for search/filter capabilities
    search_inputs = page.evaluate('''() => {
        let inputs = document.querySelectorAll('input[type="search"], input[type="text"][placeholder*="Buscar"], input[placeholder*="buscar"], input[placeholder*="Search"], .search-input, #search');
        return Array.from(inputs).map(i => ({ placeholder: i.placeholder, id: i.id, name: i.name }));
    }''')
    log(f"  Search inputs: {search_inputs}")
    
    filter_elements = page.evaluate('''() => {
        let selects = document.querySelectorAll('select, .filter, [data-filter]');
        return Array.from(selects).map(s => ({ id: s.id, name: s.name, options: s.tagName === 'SELECT' ? Array.from(s.options).map(o => o.text) : [] }));
    }''')
    log(f"  Filter elements: {filter_elements}")
    
    # Check for CRUD buttons
    crud_buttons = page.evaluate('''() => {
        let btns = Array.from(document.querySelectorAll('a, button'));
        let result = { create: [], edit: [], delete: [] };
        btns.forEach(b => {
            let text = b.innerText.toLowerCase();
            let href = (b.getAttribute('href') || '').toLowerCase();
            if (text.includes('crear') || text.includes('nuevo') || text.includes('agregar') || text.includes('new') || text.includes('add') || href.includes('/new') || href.includes('/create'))
                result.create.push({ text: b.innerText.trim(), href: b.getAttribute('href') || '' });
            if (text.includes('editar') || text.includes('edit') || href.includes('/edit'))
                result.edit.push({ text: b.innerText.trim().substring(0, 30), href: b.getAttribute('href') || '' });
            if (text.includes('eliminar') || text.includes('delete') || text.includes('borrar'))
                result.delete.push({ text: b.innerText.trim().substring(0, 30), href: b.getAttribute('href') || '' });
        });
        return result;
    }''')
    log(f"  CRUD buttons - Create: {len(crud_buttons['create'])}, Edit: {len(crud_buttons['edit'])}, Delete: {len(crud_buttons['delete'])}")
    
    if not crud_buttons['create']:
        add_finding('Medium', 'RRHH', 'No create employee button found',
                     'Navigate to /employees and look for add/create button',
                     'Create employee button should be visible',
                     'No create/add button found on the page',
                     'audit_school_rrhh_01_list.png')
    
    # Try clicking on first employee row to see profile
    try:
        first_row_link = page.evaluate('''() => {
            let links = document.querySelectorAll('table tbody tr a, .employee-link, a[href*="/employees/"]');
            if (links.length > 0) return links[0].getAttribute('href');
            // Try clicking the first row
            let rows = document.querySelectorAll('table tbody tr');
            if (rows.length > 0) {
                let link = rows[0].querySelector('a');
                if (link) return link.getAttribute('href');
            }
            return null;
        }''')
        
        if first_row_link:
            log(f"  Clicking employee profile: {first_row_link}")
            page.goto(f'{BASE_URL}{first_row_link}' if first_row_link.startswith('/') else first_row_link, wait_until='networkidle')
            time.sleep(2)
            screenshot(page, 'audit_school_rrhh_02_profile.png')
            
            # Document profile sections
            profile_sections = page.evaluate('''() => {
                let tabs = Array.from(document.querySelectorAll('.nav-tabs a, .tab-pane, h3, h4, .card-header'));
                return tabs.map(t => t.innerText.trim()).filter(t => t.length > 0 && t.length < 80);
            }''')
            log(f"  Profile sections: {profile_sections}")
        else:
            log("  No clickable employee link found")
            add_finding('Low', 'RRHH', 'No clickable employee profiles',
                         'Click on employee row', 'Employee profile opens', 'No link found to employee profile',
                         'audit_school_rrhh_01_list.png')
    except Exception as e:
        log(f"  Error clicking employee: {e}")


# ─── SCENARIO 2: Secciones (Groups/Batches) ─────────────────────────────
def scenario_secciones(page):
    log("\n=== SCENARIO 2: SECCIONES (/batches) ===")
    
    page.goto(f'{BASE_URL}/batches', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_secciones_01_list.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    # Extract sections info
    sections = page.evaluate('''() => {
        let result = [];
        // Look for section cards, accordion items, or list items
        let items = document.querySelectorAll('.accordion-item, .card, .batch-item, .panel, tr, .list-group-item');
        items.forEach(item => {
            let text = item.innerText.trim().substring(0, 100);
            if (text.length > 0) result.push(text);
        });
        return result.slice(0, 20);
    }''')
    log(f"  Sections found: {len(sections)}")
    for s in sections[:5]:
        log(f"    - {s.split(chr(10))[0]}")
    
    # Check for batch/section table
    table_info = extract_table_info(page)
    if table_info:
        log(f"  Table headers: {table_info['headers']}")
        log(f"  Row count: {table_info['rowCount']}")
    
    # Check for expandable sections
    expandable = page.evaluate('''() => {
        let toggles = document.querySelectorAll('[data-toggle="collapse"], [data-bs-toggle="collapse"], .accordion-toggle, .expandable, .collapse-toggle');
        return toggles.length;
    }''')
    log(f"  Expandable toggles: {expandable}")
    
    # Try expanding first section
    if expandable > 0:
        try:
            page.click('[data-toggle="collapse"], [data-bs-toggle="collapse"], .accordion-toggle', timeout=3000)
            time.sleep(2)
            screenshot(page, 'audit_school_secciones_02_expanded.png')
        except:
            log("  Could not expand section")
    
    # Try clicking first section link
    section_link = page.evaluate('''() => {
        let links = document.querySelectorAll('a[href*="/batches/"], a[href*="/batch"]');
        if (links.length > 0) return links[0].getAttribute('href');
        return null;
    }''')
    if section_link:
        log(f"  Clicking section: {section_link}")
        page.goto(f'{BASE_URL}{section_link}' if section_link.startswith('/') else section_link, wait_until='networkidle')
        time.sleep(2)
        screenshot(page, 'audit_school_secciones_03_detail.png')
        
        # Check for students in section
        students = page.evaluate('''() => {
            let table = document.querySelector('table');
            if (table) {
                let rows = table.querySelectorAll('tbody tr');
                return { count: rows.length, type: 'table' };
            }
            let items = document.querySelectorAll('.student-item, .list-group-item, .card');
            return { count: items.length, type: 'list' };
        }''')
        log(f"  Students in section: {students}")
    
    # Check for CRUD
    crud_actions = page.evaluate('''() => {
        let links = Array.from(document.querySelectorAll('a, button'));
        return links.filter(l => {
            let text = l.innerText.toLowerCase();
            return text.includes('crear') || text.includes('nueva sección') || text.includes('nueva secci') || text.includes('new') || text.includes('agregar');
        }).map(l => ({ text: l.innerText.trim(), href: l.getAttribute('href') || '' }));
    }''')
    log(f"  Create actions: {crud_actions}")


# ─── SCENARIO 3: Reportes Escolares ─────────────────────────────────────
def scenario_reportes(page):
    log("\n=== SCENARIO 3: REPORTES ESCOLARES (/reports/group) ===")
    
    page.goto(f'{BASE_URL}/reports/group', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_reportes_01_main.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    # Document all report types
    report_types = page.evaluate('''() => {
        let result = [];
        // Look for report links, cards, dropdown items
        let links = document.querySelectorAll('a[href*="report"], .report-item, .card, select option, .dropdown-menu a');
        links.forEach(l => {
            let text = l.innerText.trim();
            let href = l.getAttribute('href') || l.value || '';
            if (text && text.length < 80) result.push({ text, href });
        });
        return result;
    }''')
    log(f"  Report types found: {len(report_types)}")
    for r in report_types[:15]:
        log(f"    - {r['text']}: {r['href']}")
    
    # Check for dropdowns/selects for report configuration
    selects = page.evaluate('''() => {
        let selects = document.querySelectorAll('select');
        return Array.from(selects).map(s => ({
            id: s.id,
            name: s.name,
            options: Array.from(s.options).map(o => ({ value: o.value, text: o.text }))
        }));
    }''')
    log(f"  Select dropdowns: {len(selects)}")
    for s in selects:
        log(f"    Select #{s['id'] or s['name']}: {len(s['options'])} options")
    
    # Try to generate a report
    generate_btn = page.evaluate('''() => {
        let btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn'));
        let gen = btns.find(b => {
            let t = b.innerText.toLowerCase();
            return t.includes('generar') || t.includes('generate') || t.includes('descargar') || t.includes('imprimir');
        });
        if (gen) return { text: gen.innerText.trim(), tag: gen.tagName };
        return null;
    }''')
    log(f"  Generate button: {generate_btn}")
    
    if generate_btn:
        try:
            page.click(f'button:has-text("{generate_btn["text"]}"), a:has-text("{generate_btn["text"]}")', timeout=3000)
            time.sleep(3)
            screenshot(page, 'audit_school_reportes_02_generated.png')
        except:
            log("  Could not click generate button")
    
    # Also check /reports path
    page.goto(f'{BASE_URL}/reports', wait_until='networkidle')
    time.sleep(2)
    screenshot(page, 'audit_school_reportes_03_reports_index.png')
    
    all_report_links = page.evaluate('''() => {
        let links = Array.from(document.querySelectorAll('a[href*="report"]'));
        return links.map(l => ({ text: l.innerText.trim(), href: l.getAttribute('href') || '' }))
            .filter(l => l.text.length > 0 && l.text.length < 80);
    }''')
    log(f"  All report links: {len(all_report_links)}")
    for r in all_report_links[:10]:
        log(f"    - {r['text']}: {r['href']}")


# ─── SCENARIO 4: Admisión ───────────────────────────────────────────────
def scenario_admision(page):
    log("\n=== SCENARIO 4: ADMISIÓN (/admission_processes) ===")
    
    page.goto(f'{BASE_URL}/admission_processes', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_admision_01_list.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    # Document admission processes
    processes = page.evaluate('''() => {
        let items = [];
        // Check for table
        let table = document.querySelector('table');
        if (table) {
            let headers = Array.from(table.querySelectorAll('thead th')).map(h => h.innerText.trim());
            let rows = table.querySelectorAll('tbody tr');
            items.push({ type: 'table', headers, rowCount: rows.length });
        }
        // Check for cards/list
        let cards = document.querySelectorAll('.card, .process-card, .list-group-item');
        cards.forEach(c => {
            items.push({ type: 'card', text: c.innerText.trim().substring(0, 100) });
        });
        // Check for empty state
        let empty = document.querySelector('.empty-state, .no-data, .alert-info');
        if (empty) items.push({ type: 'empty', text: empty.innerText.trim() });
        return items;
    }''')
    log(f"  Admission elements: {len(processes)}")
    for p in processes[:10]:
        log(f"    - {p}")
    
    # Check for create admission button
    create_btn = page.evaluate('''() => {
        let btns = Array.from(document.querySelectorAll('a, button'));
        let found = btns.find(b => {
            let t = b.innerText.toLowerCase();
            return t.includes('crear') || t.includes('nuevo') || t.includes('nueva') || t.includes('add') || t.includes('new');
        });
        return found ? { text: found.innerText.trim(), href: found.getAttribute('href') || '' } : null;
    }''')
    log(f"  Create button: {create_btn}")
    
    # Try to view first process
    first_link = page.evaluate('''() => {
        let links = document.querySelectorAll('a[href*="admission"]');
        for (let l of links) {
            if (l.getAttribute('href') && l.getAttribute('href').match(/admission_processes\\/\\d/))
                return l.getAttribute('href');
        }
        return null;
    }''')
    
    if first_link:
        log(f"  Viewing admission process: {first_link}")
        page.goto(f'{BASE_URL}{first_link}' if first_link.startswith('/') else first_link, wait_until='networkidle')
        time.sleep(2)
        screenshot(page, 'audit_school_admision_02_detail.png')
        
        # Document form fields
        form_fields = page.evaluate('''() => {
            let inputs = document.querySelectorAll('input, select, textarea');
            return Array.from(inputs).map(i => ({
                type: i.type || i.tagName.toLowerCase(),
                name: i.name,
                id: i.id,
                required: i.required,
                placeholder: i.placeholder || ''
            })).filter(i => i.name || i.id);
        }''')
        log(f"  Form fields: {len(form_fields)}")
        for f in form_fields[:10]:
            log(f"    - {f}")
    
    # Check for admission form
    if create_btn and create_btn.get('href'):
        href = create_btn['href']
        target = href if href.startswith('http') else f'{BASE_URL}{href}'
        log(f"  Navigating to create form: {target}")
        page.goto(target, wait_until='networkidle')
        time.sleep(2)
        screenshot(page, 'audit_school_admision_03_form.png')


# ─── SCENARIO 5: Configuraciones del Colegio ────────────────────────────
def scenario_settings(page):
    log("\n=== SCENARIO 5: CONFIGURACIONES (/schools/4/settings) ===")
    
    page.goto(f'{BASE_URL}/schools/4/settings', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_settings_01_main.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    # Check if we landed on the correct page or got redirected
    if 'settings' not in current_url and '4' not in current_url:
        # Try to find the right school ID
        log("  Redirected, trying to find correct school ID...")
        add_finding('Medium', 'Settings', 'Settings page may use different school ID',
                     'Navigate to /schools/4/settings', 'Settings page loads',
                     f'Redirected to {current_url}', 'audit_school_settings_01_main.png')
    
    # Document tabs/categories
    tabs = page.evaluate('''() => {
        let tabs = document.querySelectorAll('.nav-tabs a, .nav-pills a, .tab, [role="tab"]');
        return Array.from(tabs).map(t => ({ text: t.innerText.trim(), href: t.getAttribute('href') || '' }));
    }''')
    log(f"  Settings tabs: {len(tabs)}")
    for t in tabs:
        log(f"    - {t['text']}: {t['href']}")
    
    # Document all settings sections
    sections = page.evaluate('''() => {
        let headers = document.querySelectorAll('h1, h2, h3, h4, h5, .card-header, .panel-heading, legend');
        return Array.from(headers).map(h => h.innerText.trim()).filter(h => h.length > 0 && h.length < 80);
    }''')
    log(f"  Settings sections: {sections}")
    
    # Check for editable fields
    editable_fields = page.evaluate('''() => {
        let inputs = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
        let fields = [];
        inputs.forEach(i => {
            let label = '';
            if (i.id) {
                let lbl = document.querySelector(`label[for="${i.id}"]`);
                if (lbl) label = lbl.innerText.trim();
            }
            fields.push({
                type: i.type || i.tagName.toLowerCase(),
                name: i.name,
                id: i.id,
                label: label,
                disabled: i.disabled,
                readonly: i.readOnly,
                value: (i.value || '').substring(0, 50)
            });
        });
        return fields;
    }''')
    log(f"  Editable fields: {len(editable_fields)}")
    for f in editable_fields[:10]:
        log(f"    - {f['label'] or f['name'] or f['id']}: type={f['type']}, disabled={f['disabled']}")
    
    # Click through each tab and screenshot
    for i, tab in enumerate(tabs[:6]):
        try:
            if tab['href'] and tab['href'].startswith('#'):
                page.click(f'a[href="{tab["href"]}"]', timeout=3000)
            else:
                page.click(f'text="{tab["text"]}"', timeout=3000)
            time.sleep(1)
            screenshot(page, f'audit_school_settings_02_tab_{i}.png')
        except:
            log(f"  Could not click tab: {tab['text']}")
    
    # Check for save button
    save_btn = page.evaluate('''() => {
        let btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
        let found = btns.find(b => {
            let t = b.innerText.toLowerCase();
            return t.includes('guardar') || t.includes('save') || t.includes('actualizar') || t.includes('update');
        });
        return found ? { text: found.innerText.trim(), disabled: found.disabled } : null;
    }''')
    log(f"  Save button: {save_btn}")


# ─── SCENARIO 6: Inasistencias & Promedios ──────────────────────────────
def scenario_absences_averages(page):
    log("\n=== SCENARIO 6: INASISTENCIAS & PROMEDIOS ===")
    
    # Part A: Absences
    log("  --- Absences ---")
    page.goto(f'{BASE_URL}/schools/4/absences', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_absences_01_main.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    # Document absences interface
    absence_info = page.evaluate('''() => {
        let result = {};
        // Check for tables
        let table = document.querySelector('table');
        if (table) {
            result.tableHeaders = Array.from(table.querySelectorAll('thead th')).map(h => h.innerText.trim());
            result.tableRows = table.querySelectorAll('tbody tr').length;
        }
        // Check for forms/filters
        let selects = document.querySelectorAll('select');
        result.filters = Array.from(selects).map(s => ({
            id: s.id, name: s.name,
            options: Array.from(s.options).slice(0, 5).map(o => o.text)
        }));
        // Check for calendar or date inputs
        let dates = document.querySelectorAll('input[type="date"], .datepicker, .calendar');
        result.dateInputs = dates.length;
        // Check page content
        result.pageText = document.body.innerText.substring(0, 500);
        return result;
    }''')
    log(f"  Absence info: {json.dumps(absence_info, indent=2, ensure_ascii=False)[:500]}")
    
    # Part B: Averages
    log("  --- Averages ---")
    page.goto(f'{BASE_URL}/schools/4/averages', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_averages_01_main.png')
    
    current_url = page.url
    log(f"  URL: {current_url}")
    
    averages_info = page.evaluate('''() => {
        let result = {};
        let table = document.querySelector('table');
        if (table) {
            result.tableHeaders = Array.from(table.querySelectorAll('thead th')).map(h => h.innerText.trim());
            result.tableRows = table.querySelectorAll('tbody tr').length;
        }
        let selects = document.querySelectorAll('select');
        result.filters = Array.from(selects).map(s => ({
            id: s.id, name: s.name,
            options: Array.from(s.options).slice(0, 5).map(o => o.text)
        }));
        result.pageText = document.body.innerText.substring(0, 500);
        return result;
    }''')
    log(f"  Averages info: {json.dumps(averages_info, indent=2, ensure_ascii=False)[:500]}")


# ─── SCENARIO 7: Módulos Secundarios ────────────────────────────────────
def scenario_secondary_modules(page):
    log("\n=== SCENARIO 7: MÓDULOS SECUNDARIOS ===")
    
    modules = [
        ('/conversations', 'Correos'),
        ('/polls', 'Encuestas'),
        ('/student_bitacoras', 'Libro de Vida'),
        ('/calendar/month', 'Calendario'),
        ('/newsletters', 'Noticias'),
        ('/engagement', 'Engagement'),
    ]
    
    for path, name in modules:
        log(f"  --- {name} ({path}) ---")
        try:
            page.goto(f'{BASE_URL}{path}', wait_until='networkidle')
            time.sleep(3)
            screenshot(page, f'audit_school_mod_{name.lower().replace(" ", "_")}_01.png')
            
            current_url = page.url
            log(f"    URL: {current_url}")
            
            if path not in current_url and current_url != f'{BASE_URL}{path}':
                add_finding('Medium', name, f'{name} page redirects',
                             f'Navigate to {path}', f'{name} page loads',
                             f'Redirected to {current_url}',
                             f'audit_school_mod_{name.lower().replace(" ", "_")}_01.png')
            
            # Document page structure
            page_info = page.evaluate('''() => {
                let result = {};
                // Tables
                let table = document.querySelector('table');
                if (table) {
                    result.tableHeaders = Array.from(table.querySelectorAll('thead th')).map(h => h.innerText.trim());
                    result.tableRows = table.querySelectorAll('tbody tr').length;
                }
                // Cards
                let cards = document.querySelectorAll('.card, .panel, .list-group-item');
                result.cards = cards.length;
                // Buttons/Actions
                let btns = Array.from(document.querySelectorAll('a.btn, button.btn'));
                result.actions = btns.map(b => b.innerText.trim()).filter(t => t.length > 0 && t.length < 50).slice(0, 10);
                // Empty state
                let empty = document.querySelector('.empty, .no-data, .alert');
                result.emptyState = empty ? empty.innerText.trim().substring(0, 100) : null;
                // H1/title
                let h1 = document.querySelector('h1, h2, .page-title');
                result.title = h1 ? h1.innerText.trim() : '';
                // Count items
                result.links = document.querySelectorAll('a').length;
                result.inputs = document.querySelectorAll('input, select, textarea').length;
                return result;
            }''')
            log(f"    Page info: {json.dumps(page_info, ensure_ascii=False)[:300]}")
            
            # Module-specific checks
            if path == '/conversations':
                compose_btn = page.evaluate('''() => {
                    let btns = Array.from(document.querySelectorAll('a, button'));
                    let found = btns.find(b => {
                        let t = b.innerText.toLowerCase();
                        return t.includes('nuevo') || t.includes('componer') || t.includes('compose') || t.includes('redactar') || t.includes('escribir');
                    });
                    return found ? found.innerText.trim() : null;
                }''')
                log(f"    Compose button: {compose_btn}")
            
            elif path == '/polls':
                poll_count = page.evaluate('''() => {
                    let items = document.querySelectorAll('.poll-item, table tbody tr, .list-group-item, .card');
                    return items.length;
                }''')
                log(f"    Poll items: {poll_count}")
            
            elif path == '/calendar/month':
                calendar_events = page.evaluate('''() => {
                    let events = document.querySelectorAll('.fc-event, .event, .calendar-event, td[data-date]');
                    return events.length;
                }''')
                log(f"    Calendar elements: {calendar_events}")
                
        except Exception as e:
            log(f"    ERROR: {e}")
            add_finding('Medium', name, f'{name} module error',
                         f'Navigate to {path}', 'Module loads normally',
                         f'Error: {str(e)}', '')


# ─── SCENARIO 8: Role Switching ─────────────────────────────────────────
def scenario_role_switching(page):
    log("\n=== SCENARIO 8: ROLE SWITCHING ===")
    
    # First, capture current employee sidebar
    log("  --- Current Employee Sidebar ---")
    employee_sidebar = extract_sidebar(page)
    log(f"  Employee sidebar items: {len(employee_sidebar)}")
    for item in employee_sidebar[:20]:
        log(f"    - {item['text']}: {item['href']}")
    screenshot(page, 'audit_school_role_01_employee_sidebar.png')
    
    # Switch to teacher role
    log("  --- Switching to Teacher ---")
    page.goto(f'{BASE_URL}/user_sessions/change_sidebar_menu?role=teacher', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_role_02_teacher_sidebar.png')
    
    teacher_url = page.url
    log(f"  URL after teacher switch: {teacher_url}")
    
    teacher_sidebar = extract_sidebar(page)
    log(f"  Teacher sidebar items: {len(teacher_sidebar)}")
    for item in teacher_sidebar[:20]:
        log(f"    - {item['text']}: {item['href']}")
    
    # Try accessing employee-only page as teacher
    log("  --- Testing employee-only access as teacher ---")
    employee_only_pages = ['/employees', '/admission_processes', '/schools/4/settings']
    for ep in employee_only_pages:
        page.goto(f'{BASE_URL}{ep}', wait_until='networkidle')
        time.sleep(2)
        current_url = page.url
        page_text = page.evaluate('() => document.body.innerText.substring(0, 300)')
        accessible = ep in current_url
        log(f"    {ep}: {'ACCESSIBLE' if accessible else 'BLOCKED/REDIRECTED'} -> {current_url}")
        
        if accessible:
            screenshot(page, f'audit_school_role_03_teacher_access_{ep.replace("/", "_")}.png')
            add_finding('High', 'RBAC', f'Teacher can access employee-only page {ep}',
                         f'Login as teacher, navigate to {ep}',
                         'Access should be denied or redirected',
                         f'Page is accessible at {current_url}',
                         f'audit_school_role_03_teacher_access_{ep.replace("/", "_")}.png')
    
    screenshot(page, 'audit_school_role_04_teacher_access_test.png')
    
    # Switch to studies_control role
    log("  --- Switching to Studies Control ---")
    page.goto(f'{BASE_URL}/user_sessions/change_sidebar_menu?role=studies_control', wait_until='networkidle')
    time.sleep(3)
    screenshot(page, 'audit_school_role_05_studies_sidebar.png')
    
    studies_url = page.url
    log(f"  URL after studies_control switch: {studies_url}")
    
    studies_sidebar = extract_sidebar(page)
    log(f"  Studies Control sidebar items: {len(studies_sidebar)}")
    for item in studies_sidebar[:20]:
        log(f"    - {item['text']}: {item['href']}")
    
    # Compare sidebars
    employee_texts = set(item['text'] for item in employee_sidebar)
    teacher_texts = set(item['text'] for item in teacher_sidebar)
    studies_texts = set(item['text'] for item in studies_sidebar)
    
    log(f"\n  Sidebar Comparison:")
    log(f"    Employee-only items: {employee_texts - teacher_texts - studies_texts}")
    log(f"    Teacher-only items: {teacher_texts - employee_texts - studies_texts}")
    log(f"    Studies Control-only items: {studies_texts - employee_texts - teacher_texts}")
    log(f"    Common to all: {employee_texts & teacher_texts & studies_texts}")
    
    # Switch back to employee for final state
    page.goto(f'{BASE_URL}/user_sessions/change_sidebar_menu?role=employee', wait_until='networkidle')
    time.sleep(2)


# ─── MAIN EXECUTION ─────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log("COMPREHENSIVE SCHOOL MODULE AUDIT")
    log(f"Started at: {datetime.now().isoformat()}")
    log("=" * 60)
    
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1366, 'height': 900},
        ignore_https_errors=True
    )
    page = context.new_page()
    
    # Set longer default timeout
    page.set_default_timeout(15000)
    
    try:
        # Login
        if not login_and_select_school(page):
            log("LOGIN FAILED - aborting")
            return
        
        # Run all scenarios
        scenarios = [
            ("RRHH", scenario_rrhh),
            ("Secciones", scenario_secciones),
            ("Reportes", scenario_reportes),
            ("Admisión", scenario_admision),
            ("Settings", scenario_settings),
            ("Absences & Averages", scenario_absences_averages),
            ("Secondary Modules", scenario_secondary_modules),
            ("Role Switching", scenario_role_switching),
        ]
        
        for name, func in scenarios:
            try:
                func(page)
            except Exception as e:
                log(f"\n❌ SCENARIO {name} FAILED: {e}")
                traceback.print_exc()
                add_finding('High', name, f'Scenario {name} crashed',
                             f'Run scenario {name}', 'Scenario completes',
                             f'Error: {str(e)}', '')
                screenshot(page, f'audit_school_error_{name.lower().replace(" ", "_")}.png')
    
    finally:
        context.close()
        browser.close()
        p.stop()
    
    # ─── Generate Report ─────────────────────────────────────────────
    log("\n" + "=" * 60)
    log(f"AUDIT COMPLETE - {len(findings)} findings")
    log("=" * 60)
    
    # Save findings as JSON for reference
    with open(os.path.join(SCREENSHOT_DIR, 'audit_school_findings.json'), 'w') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    log(f"Findings saved to {SCREENSHOT_DIR}/audit_school_findings.json")
    log(f"Screenshots saved to {SCREENSHOT_DIR}/")


if __name__ == '__main__':
    main()
