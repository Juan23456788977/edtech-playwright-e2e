#!/usr/bin/env python3
"""
Comprehensive E2E Audit of Akdemia Cobros (Billing) Module
==========================================================
Scenarios:
  1. Full Payment Flow
  2. All Report Types
  3. Deudas Module
  4. Notas de Débito & Crédito
  5. Configuración
  6. Tasa BCV & Libro de Ventas
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

# ── Config ───────────────────────────────────────────────────────────────
OMEGA_URL  = "https://omega.akdemia.com"
COBROS_URL = "https://cobros.akdemia.com"
EMAIL      = "jcortez@akdemia.com"
PASSWORD   = "akdemia#2026*"
SCHOOL     = "Colegio Prueba Akdemia"

SCREENSHOT_DIR = "/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ── Logging helper ───────────────────────────────────────────────────────
findings = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    page.screenshot(path=path, full_page=True)
    log(f"  📸 Screenshot: {name}")
    return path

def add_finding(severity, module, url, title, steps, expected, actual, screenshot_name=""):
    findings.append({
        "severity": severity,
        "module": module,
        "url": url,
        "title": title,
        "steps": steps,
        "expected": expected,
        "actual": actual,
        "screenshot": screenshot_name,
    })
    log(f"  🐛 [{severity}] {title}")

def safe_click(page, selector, timeout=5000, force=False):
    """Click an element, return True if success, False otherwise."""
    try:
        el = page.locator(selector).first
        el.wait_for(state="visible", timeout=timeout)
        el.click(force=force)
        return True
    except Exception:
        try:
            el = page.locator(selector).first
            el.click(force=True)
            return True
        except Exception:
            return False

def safe_fill(page, selector, value, timeout=5000, delay=0):
    try:
        el = page.locator(selector).first
        el.wait_for(state="visible", timeout=timeout)
        if delay:
            el.click()
            el.fill("")
            el.type(value, delay=delay)
        else:
            el.fill(value)
        return True
    except Exception:
        return False

def wait_and_dismiss_modals(page):
    """Dismiss session-warning or other bootstrap modals if they appear."""
    try:
        modal = page.locator("#session-warning-modal")
        if modal.is_visible():
            page.click("#extend-session-button", force=True)
            time.sleep(0.5)
    except Exception:
        pass

def get_page_text(page):
    try:
        return page.evaluate("document.body.innerText")
    except Exception:
        return ""

def get_page_html(page):
    try:
        return page.evaluate("document.body.innerHTML")
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════════════════════
# LOGIN FLOW
# ══════════════════════════════════════════════════════════════════════════
def login_and_navigate_to_cobros(page):
    """Follow the CRITICAL LOGIN FLOW exactly."""
    log("═══ STEP 1: Login at omega.akdemia.com ═══")
    page.goto(f"{OMEGA_URL}/login", wait_until="networkidle", timeout=30000)
    time.sleep(2)
    screenshot(page, "audit_01_login_page.png")

    page.fill("#email_login", EMAIL)
    page.fill("#password_login", PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    screenshot(page, "audit_02_after_login.png")
    log(f"  URL after login: {page.url}")

    # ── Check if we landed on a select-role page or dashboard ────────
    body_text = get_page_text(page)

    # Try the CRITICAL LOGIN FLOW role change method
    log("═══ STEP 2: Change role to employee ═══")
    
    # Check if there's a role-option form (direct school selection page)
    has_role_options = page.locator("div.role-option").count() > 0
    
    if has_role_options:
        log("  Found role-option form (select-role page)")
        # Look for Colegio Prueba Akdemia
        prueba_option = page.locator("div.role-option", has_text="Colegio Prueba Akdemia").first
        try:
            prueba_option.wait_for(state="visible", timeout=5000)
            prueba_option.click()
            time.sleep(1)
            screenshot(page, "audit_03_school_selected.png")
            with page.expect_navigation(timeout=15000):
                page.evaluate("document.getElementById('select-role-form').submit()")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            screenshot(page, "audit_04_after_school_submit.png")
            log(f"  URL after school selection: {page.url}")
        except Exception as e:
            log(f"  ⚠ Colegio Prueba Akdemia not found directly. Error: {e}")
            # Try clicking first available
            page.locator("div.role-option").first.click()
            time.sleep(1)
            with page.expect_navigation(timeout=15000):
                page.evaluate("document.getElementById('select-role-form').submit()")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
    else:
        log("  No role-option form found. Trying role change modal flow...")
        # Try the modal flow
        try:
            page.click('a[href="#change-role-modal"]', timeout=5000)
            time.sleep(1)
            page.click('input[name="role"][value="employee"]', force=True)
            time.sleep(0.5)
            safe_fill(page, '#fill-school', SCHOOL)
            time.sleep(1)
            page.click('.dropdown-toggle')
            time.sleep(1)
            page.locator('li', has_text=SCHOOL).first.click()
            time.sleep(0.5)
            page.click('#change-role-button')
            page.wait_for_load_state("networkidle")
            time.sleep(3)
        except Exception as e:
            log(f"  ⚠ Modal flow also failed: {e}")
    
    screenshot(page, "audit_05_omega_dashboard.png")
    
    # ── Navigate to cobros ───────────────────────────────────────────
    log("═══ STEP 3: Navigate to cobros.akdemia.com ═══")
    
    # Try clicking "Ir a Cobranzas" link if visible
    try:
        cobranzas_link = page.locator("a", has_text="Cobranzas").first
        if cobranzas_link.is_visible():
            cobranzas_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            log(f"  Navigated via 'Cobranzas' link. URL: {page.url}")
        else:
            raise Exception("Link not visible")
    except Exception:
        log("  Direct nav to cobros.akdemia.com")
        page.goto(COBROS_URL, wait_until="networkidle", timeout=30000)
        time.sleep(5)
    
    screenshot(page, "audit_06_cobros_initial.png")
    log(f"  URL at cobros: {page.url}")
    
    # ── Check if we're on a select_role page in cobros ───────────────
    current_url = page.url
    body_text = get_page_text(page)
    
    if "select_role" in current_url or "role-option" in get_page_html(page):
        log("  On cobros select-role page, selecting school...")
        has_role_opts = page.locator("div.role-option").count() > 0
        if has_role_opts:
            prueba = page.locator("div.role-option", has_text="Colegio Prueba").first
            try:
                prueba.click()
                time.sleep(1)
                with page.expect_navigation(timeout=15000):
                    page.evaluate("document.getElementById('select-role-form').submit()")
                page.wait_for_load_state("networkidle")
                time.sleep(3)
            except Exception:
                page.locator("div.role-option").first.click()
                time.sleep(1)
                with page.expect_navigation(timeout=15000):
                    page.evaluate("document.getElementById('select-role-form').submit()")
                page.wait_for_load_state("networkidle")
                time.sleep(3)
        screenshot(page, "audit_07_cobros_after_school.png")
    
    # ── Try the cobros school change if "Cambio de Rol" link present ──
    change_role_link = page.locator("#change-role")
    if change_role_link.count() > 0:
        log("  Checking if school is correct in cobros header...")
        school_name_el = page.locator("#school-name p").first
        try:
            current_school = school_name_el.inner_text().strip()
            log(f"  Current school in cobros: '{current_school}'")
            if "Prueba" not in current_school:
                log("  ⚠ Need to change school inside cobros...")
                change_role_link.click()
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                screenshot(page, "audit_08_cobros_role_change.png")
                
                # On the select_role page in cobros
                prueba = page.locator("div.role-option", has_text="Colegio Prueba").first
                try:
                    prueba.click()
                    time.sleep(1)
                    with page.expect_navigation(timeout=15000):
                        page.evaluate("document.getElementById('select-role-form').submit()")
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                except Exception:
                    log("  ⚠ Could not find Colegio Prueba option in cobros. Using first available.")
                    page.locator("div.role-option").first.click()
                    time.sleep(1)
                    with page.expect_navigation(timeout=15000):
                        page.evaluate("document.getElementById('select-role-form').submit()")
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
        except Exception as e:
            log(f"  ⚠ School name check error: {e}")
    
    screenshot(page, "audit_09_cobros_home_final.png")
    
    # Record what school we're actually in
    try:
        final_school = page.locator("#school-name p").first.inner_text().strip()
        log(f"  ✅ Final school in cobros: '{final_school}'")
    except Exception:
        log("  ⚠ Could not determine final school")
    
    log(f"  ✅ Cobros home URL: {page.url}")
    return True


# ══════════════════════════════════════════════════════════════════════════
# SCENARIO 1: Full Payment Flow
# ══════════════════════════════════════════════════════════════════════════
def scenario_1_payment_flow(page):
    log("\n" + "="*70)
    log("SCENARIO 1: Full Payment Flow")
    log("="*70)
    
    # 1a. Navigate to Estado de Cuenta
    log("── 1a. Navigate to Estado de Cuenta ──")
    page.goto(f"{COBROS_URL}/services_students/show/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    screenshot(page, "audit_s1_01_estado_cuenta.png")
    log(f"  URL: {page.url}")
    
    body_text = get_page_text(page)
    body_html = get_page_html(page)
    
    # Check for search functionality
    search_input = page.locator('input[type="text"]#fill-student-info, input[placeholder*="búsqueda"], input.form-control[type="text"]').first
    has_search = False
    try:
        search_input.wait_for(state="visible", timeout=5000)
        has_search = True
        log("  ✅ Search input found")
    except Exception:
        log("  ⚠ No search input found on Estado de Cuenta page")
        # Try other selectors
        try:
            search_input = page.locator('input#fill-student-info').first
            search_input.wait_for(state="attached", timeout=3000)
            has_search = True
            log("  ✅ Found #fill-student-info (may be hidden)")
        except Exception:
            log("  ❌ Cannot find any student search input")
    
    # 1b. Search for a student
    log("── 1b. Search for a student ──")
    if has_search:
        try:
            search_input.click(force=True)
            search_input.fill("")
            search_input.type("Prueba", delay=100)
            time.sleep(2)
            screenshot(page, "audit_s1_02_student_search.png")
            
            # Wait for search results
            page.wait_for_timeout(3000)
            
            # Check if search results appeared
            results_html = get_page_html(page)
            search_results = page.locator('#search-results a, .search-result, table tbody tr')
            result_count = search_results.count()
            log(f"  Search results count: {result_count}")
            
            if result_count > 0:
                # Try pressing Enter to trigger search
                search_input.press("Enter")
                time.sleep(3)
                screenshot(page, "audit_s1_03_search_results.png")
                
                # Click first result
                try:
                    first_result = search_results.first
                    first_result.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                    screenshot(page, "audit_s1_04_student_selected.png")
                    log(f"  ✅ Student selected. URL: {page.url}")
                except Exception as e:
                    log(f"  ⚠ Could not click search result: {e}")
            else:
                # Try pressing Enter
                search_input.press("Enter")
                time.sleep(3)
                screenshot(page, "audit_s1_03_search_enter.png")
                result_count2 = search_results.count()
                log(f"  After Enter - results: {result_count2}")
                
                if result_count2 == 0:
                    add_finding("Medium", "Estado de Cuenta", page.url,
                                "No search results for 'Prueba' query",
                                "1. Go to Estado de Cuenta\n2. Type 'Prueba' in search",
                                "Search results should appear",
                                "No results found - may be empty school or search issue",
                                "audit_s1_03_search_enter.png")
        except Exception as e:
            log(f"  ❌ Search failed: {e}")
            screenshot(page, "audit_s1_02_search_error.png")
    
    # 1c. Try to create/register a payment (explore the payment registration)
    log("── 1c. Explore payment registration ──")
    # Check if there's a payment button or form on the page
    payment_buttons = page.locator('a[href*="payment"], button:has-text("Pago"), a:has-text("Registrar"), button:has-text("Registrar")')
    log(f"  Payment-related buttons/links: {payment_buttons.count()}")
    
    # Document the Estado de Cuenta page structure
    all_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim().substring(0, 50),
            href: a.href
        })).filter(a => a.text.length > 0);
    }''')
    log(f"  Links on page: {len(all_links)}")
    for link in all_links[:20]:
        log(f"    - [{link['text']}] → {link['href']}")
    
    # 1d. Navigate to Pagos list
    log("── 1d. Navigate to Pagos list ──")
    page.goto(f"{COBROS_URL}/payment_documents/payment_details_employee/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    screenshot(page, "audit_s1_05_pagos_list.png")
    log(f"  URL: {page.url}")
    
    body_text = get_page_text(page)
    
    # Check for payment table
    table = page.locator("table")
    if table.count() > 0:
        rows = page.locator("table tbody tr")
        log(f"  ✅ Payment table found. Rows: {rows.count()}")
        if rows.count() == 0:
            log("  ⚠ Payment table is empty")
    else:
        log("  ⚠ No payment table found")
        if "no hay" in body_text.lower() or "sin resultados" in body_text.lower():
            log("  ℹ Page shows 'no results' message")
    
    # Check for filters on Pagos page
    filters = page.locator("select, input[type='date'], .datepicker, .k-datepicker")
    log(f"  Filters/inputs found: {filters.count()}")
    
    screenshot(page, "audit_s1_06_pagos_detail.png")


# ══════════════════════════════════════════════════════════════════════════
# SCENARIO 2: All Report Types
# ══════════════════════════════════════════════════════════════════════════
def scenario_2_reports(page):
    log("\n" + "="*70)
    log("SCENARIO 2: All Report Types")
    log("="*70)
    
    page.goto(f"{COBROS_URL}/reports/new", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    screenshot(page, "audit_s2_00_reports_page.png")
    log(f"  URL: {page.url}")
    
    # Get all report options
    report_options = page.evaluate('''() => {
        let select = document.querySelector('select[name="report[report_information]"]');
        if (!select) select = document.querySelector('select.js-report-information');
        if (!select) return [];
        return Array.from(select.options).map(o => ({text: o.text, value: o.value, disabled: o.disabled}));
    }''')
    
    log(f"  Report types found: {len(report_options)}")
    for opt in report_options:
        log(f"    - [{opt['value']}] {opt['text']} {'(disabled)' if opt.get('disabled') else ''}")
    
    if len(report_options) == 0:
        add_finding("Critical", "Reportes", page.url,
                    "No report options found in dropdown",
                    "1. Navigate to Reportes\n2. Check report dropdown",
                    "12+ report options available",
                    "Dropdown is empty or not found",
                    "audit_s2_00_reports_page.png")
        return
    
    # Test each report type
    results = {}
    for i, opt in enumerate(report_options):
        if opt.get('disabled'):
            log(f"\n  ── Report {i+1}/{len(report_options)}: {opt['text']} (SKIPPED - disabled) ──")
            results[opt['text']] = "SKIPPED (disabled)"
            continue
            
        log(f"\n  ── Report {i+1}/{len(report_options)}: {opt['text']} ──")
        
        try:
            # Navigate fresh to reports page for each report
            page.goto(f"{COBROS_URL}/reports/new", wait_until="networkidle", timeout=30000)
            time.sleep(2)
            wait_and_dismiss_modals(page)
            
            # Select the report type
            page.select_option('select[name="report[report_information]"]', value=opt['value'])
            time.sleep(2)
            
            screenshot(page, f"audit_s2_{i+1:02d}_{opt['value']}_selected.png")
            
            # Get the report sub-options that appeared
            sub_filters = page.evaluate('''() => {
                let visible = [];
                document.querySelectorAll('.js-report-fields').forEach(el => {
                    if (el.style.display !== 'none') {
                        visible.push(el.innerHTML.substring(0, 200));
                    }
                });
                // Also check report_type select
                let reportType = document.querySelector('select[name="report[report_type]"]');
                if (reportType && !reportType.disabled) {
                    visible.push('report_type: ' + Array.from(reportType.options).map(o => o.text).join(', '));
                }
                return visible;
            }''')
            log(f"    Sub-filters visible: {len(sub_filters)}")
            
            # Set date range if available (use a wide range for testing)
            start_date = page.locator('#report_start_date')
            end_date = page.locator('#report_end_date')
            
            if start_date.count() > 0:
                try:
                    if not start_date.is_disabled():
                        page.evaluate('''() => {
                            let sd = document.getElementById('report_start_date');
                            let ed = document.getElementById('report_end_date');
                            if (sd) { sd.value = '01/01/2025'; }
                            if (ed) { ed.value = '19/06/2026'; }
                        }''')
                        log("    Set date range: 01/01/2025 - 19/06/2026")
                except Exception:
                    pass
            
            # Click Generate
            generate_btn = page.locator('button[type="submit"]:has-text("Generar"), input[type="submit"]').first
            
            # Listen for response
            response_data = {"status": None, "message": ""}
            
            def handle_response(response):
                if "/reports" in response.url and response.request.method == "POST":
                    response_data["status"] = response.status
                    try:
                        response_data["message"] = response.text()[:500]
                    except Exception:
                        pass
            
            page.on("response", handle_response)
            
            try:
                generate_btn.click(force=True)
                time.sleep(5)
            except Exception as e:
                log(f"    ⚠ Click generate failed: {e}")
                # Try JS submit
                page.evaluate("document.getElementById('new_report').submit()")
                time.sleep(5)
            
            page.remove_listener("response", handle_response)
            
            screenshot(page, f"audit_s2_{i+1:02d}_{opt['value']}_result.png")
            
            # Check for success/error messages
            page_text = get_page_text(page)
            page_html = get_page_html(page)
            
            if "se está generando" in page_text.lower() or "reporte se está generando" in page_text.lower():
                log(f"    ✅ SUCCESS: Report is generating")
                results[opt['text']] = "SUCCESS"
            elif "generado" in page_text.lower() or "exitosamente" in page_text.lower():
                log(f"    ✅ SUCCESS: Report generated")
                results[opt['text']] = "SUCCESS"
            elif "error" in page_text.lower():
                log(f"    ❌ ERROR in response")
                results[opt['text']] = "ERROR"
                add_finding("High", "Reportes", page.url,
                           f"Report '{opt['text']}' generation failed with error",
                           f"1. Go to Reportes\n2. Select '{opt['text']}'\n3. Click Generar",
                           "Report should generate successfully",
                           "Error message displayed",
                           f"audit_s2_{i+1:02d}_{opt['value']}_result.png")
            elif response_data["status"] and response_data["status"] >= 400:
                log(f"    ❌ HTTP {response_data['status']}")
                results[opt['text']] = f"HTTP {response_data['status']}"
                add_finding("High", "Reportes", page.url,
                           f"Report '{opt['text']}' returned HTTP {response_data['status']}",
                           f"1. Go to Reportes\n2. Select '{opt['text']}'\n3. Click Generar",
                           "HTTP 200 response",
                           f"HTTP {response_data['status']} error",
                           f"audit_s2_{i+1:02d}_{opt['value']}_result.png")
            else:
                # Check for flash notices
                flash = page.locator(".alert, .flash, .notice, #notices")
                flash_text = ""
                for fi in range(flash.count()):
                    t = flash.nth(fi).inner_text().strip()
                    if t:
                        flash_text += t + " "
                
                if flash_text:
                    log(f"    ℹ Flash message: {flash_text[:100]}")
                    if "error" in flash_text.lower():
                        results[opt['text']] = f"ERROR: {flash_text[:80]}"
                    else:
                        results[opt['text']] = f"OK: {flash_text[:80]}"
                else:
                    log(f"    ℹ No clear success/error message. Page redirected to: {page.url}")
                    results[opt['text']] = f"REDIRECT: {page.url}"
            
        except Exception as e:
            log(f"    ❌ Exception: {e}")
            results[opt['text']] = f"EXCEPTION: {str(e)[:80]}"
            screenshot(page, f"audit_s2_{i+1:02d}_{opt['value']}_exception.png")
    
    # Summary
    log("\n  ── Reports Summary ──")
    for name, result in results.items():
        status_emoji = "✅" if "SUCCESS" in str(result) or "OK" in str(result) else "❌" if "ERROR" in str(result) or "EXCEPTION" in str(result) else "⚠"
        log(f"    {status_emoji} {name}: {result}")
    
    return results


# ══════════════════════════════════════════════════════════════════════════
# SCENARIO 3: Deudas Module
# ══════════════════════════════════════════════════════════════════════════
def scenario_3_deudas(page):
    log("\n" + "="*70)
    log("SCENARIO 3: Deudas Module")
    log("="*70)
    
    page.goto(f"{COBROS_URL}/school_settings/debts", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    screenshot(page, "audit_s3_01_deudas_page.png")
    log(f"  URL: {page.url}")
    
    body_text = get_page_text(page)
    body_html = get_page_html(page)
    
    # Check page elements
    has_table = page.locator("table").count() > 0
    has_loading = "cargando" in body_text.lower() or page.locator(".loading, #loading").count() > 0
    has_empty = "no hay" in body_text.lower() or "sin deudas" in body_text.lower() or "vacío" in body_text.lower()
    
    log(f"  Has table: {has_table}")
    log(f"  Is loading: {has_loading}")
    log(f"  Shows empty state: {has_empty}")
    
    if has_table:
        rows = page.locator("table tbody tr")
        log(f"  Table rows: {rows.count()}")
        
        # Get table headers
        headers = page.evaluate('''() => {
            let ths = document.querySelectorAll('table thead th, table th');
            return Array.from(ths).map(th => th.innerText.trim());
        }''')
        log(f"  Table headers: {headers}")
        
        if rows.count() > 0:
            # Get first few rows of data
            first_rows = page.evaluate('''() => {
                let rows = document.querySelectorAll('table tbody tr');
                let data = [];
                for (let i = 0; i < Math.min(rows.length, 3); i++) {
                    let cells = rows[i].querySelectorAll('td');
                    data.push(Array.from(cells).map(c => c.innerText.trim().substring(0, 30)));
                }
                return data;
            }''')
            log(f"  First rows: {first_rows}")
    
    # Check for filters
    filters = page.locator("select, .filter, input[type='text']")
    log(f"  Filters/inputs: {filters.count()}")
    
    # Check for action buttons
    actions = page.locator("button, a.btn")
    action_texts = []
    for i in range(min(actions.count(), 10)):
        t = actions.nth(i).inner_text().strip()
        if t:
            action_texts.append(t)
    log(f"  Action buttons: {action_texts}")
    
    # Check page title/banner
    banner = page.locator(".banner-container-thin h1, .my-title")
    if banner.count() > 0:
        log(f"  Page title: {banner.first.inner_text().strip()}")
    
    # Document all sidebar items visible
    sidebar_items = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.sidebar a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href,
            selected: a.classList.contains('selected')
        }));
    }''')
    log(f"  Sidebar items: {len(sidebar_items)}")
    for item in sidebar_items:
        sel = " ★" if item.get('selected') else ""
        log(f"    - {item['text']}{sel}")
    
    screenshot(page, "audit_s3_02_deudas_detail.png")


# ══════════════════════════════════════════════════════════════════════════
# SCENARIO 4: Notas de Débito & Crédito
# ══════════════════════════════════════════════════════════════════════════
def scenario_4_notas(page):
    log("\n" + "="*70)
    log("SCENARIO 4: Notas de Débito & Crédito")
    log("="*70)
    
    # 4a. Look for Notas de Débito in the sidebar or navigation
    log("── 4a. Looking for Notas de Débito ──")
    
    # First, go to cobros home to check sidebar
    page.goto(f"{COBROS_URL}/school_settings/home_employee/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    
    # Extract all sidebar links
    sidebar_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.sidebar a, .rollout-menu a, .nav-stacked a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href,
            id: a.id
        }));
    }''')
    
    log(f"  Sidebar links found: {len(sidebar_links)}")
    
    nota_debito_url = None
    nota_credito_url = None
    libro_ventas_url = None
    
    for link in sidebar_links:
        log(f"    - [{link.get('id','')}] {link['text']} → {link['href']}")
        if "débito" in link['text'].lower() or "debito" in link['text'].lower():
            nota_debito_url = link['href']
        if "crédito" in link['text'].lower() or "credito" in link['text'].lower():
            nota_credito_url = link['href']
        if "libro" in link['text'].lower() or "ventas" in link['text'].lower():
            libro_ventas_url = link['href']
    
    # Try common URLs for Notas de Débito
    debit_note_urls = [
        f"{COBROS_URL}/debit_notes",
        f"{COBROS_URL}/debit_notes/new",
        f"{COBROS_URL}/notas_debito",
        f"{COBROS_URL}/school_settings/debit_notes",
    ]
    
    if nota_debito_url:
        debit_note_urls.insert(0, nota_debito_url)
    
    log("── 4b. Testing Notas de Débito URLs ──")
    debit_note_found = False
    for url in debit_note_urls:
        try:
            resp = page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(2)
            
            if resp and resp.status < 400 and page.url != f"{COBROS_URL}/login" and "select_role" not in page.url:
                log(f"  ✅ Accessible: {url} → {page.url}")
                screenshot(page, "audit_s4_01_nota_debito.png")
                debit_note_found = True
                
                # Document what we see
                body_text = get_page_text(page)
                log(f"  Page content (first 200 chars): {body_text[:200]}")
                
                # Check for form elements
                forms = page.locator("form")
                log(f"  Forms: {forms.count()}")
                
                buttons = page.locator("button, a.btn, input[type='submit']")
                for bi in range(min(buttons.count(), 5)):
                    log(f"  Button: {buttons.nth(bi).inner_text().strip()}")
                
                break
            else:
                log(f"  ❌ Not accessible: {url} (status: {resp.status if resp else 'None'})")
        except Exception as e:
            log(f"  ❌ Error: {url}: {str(e)[:60]}")
    
    if not debit_note_found:
        add_finding("Medium", "Notas de Débito", COBROS_URL,
                    "Notas de Débito section not found in navigation",
                    "1. Login to cobros\n2. Look for 'Notas de Débito' in sidebar",
                    "Notas de Débito section should be accessible",
                    "Section not found in sidebar or common URLs",
                    "audit_s4_01_nota_debito.png")
    
    # 4c. Try Notas de Crédito
    log("── 4c. Testing Notas de Crédito ──")
    credit_note_urls = [
        f"{COBROS_URL}/credit_notes",
        f"{COBROS_URL}/credit_notes/new",
        f"{COBROS_URL}/notas_credito",
        f"{COBROS_URL}/school_settings/credit_notes",
    ]
    
    if nota_credito_url:
        credit_note_urls.insert(0, nota_credito_url)
    
    credit_note_found = False
    for url in credit_note_urls:
        try:
            resp = page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(2)
            
            if resp and resp.status < 400 and page.url != f"{COBROS_URL}/login" and "select_role" not in page.url:
                log(f"  ✅ Accessible: {url} → {page.url}")
                screenshot(page, "audit_s4_02_nota_credito.png")
                credit_note_found = True
                
                body_text = get_page_text(page)
                log(f"  Page content (first 200 chars): {body_text[:200]}")
                break
            else:
                log(f"  ❌ Not accessible: {url}")
        except Exception as e:
            log(f"  ❌ Error: {url}: {str(e)[:60]}")
    
    if not credit_note_found:
        add_finding("Medium", "Notas de Crédito", COBROS_URL,
                    "Notas de Crédito section not found in navigation",
                    "1. Login to cobros\n2. Look for 'Notas de Crédito' in sidebar",
                    "Notas de Crédito section should be accessible",
                    "Section not found in sidebar or common URLs",
                    "audit_s4_02_nota_credito.png")
    
    screenshot(page, "audit_s4_03_notas_summary.png")


# ══════════════════════════════════════════════════════════════════════════
# SCENARIO 5: Configuración
# ══════════════════════════════════════════════════════════════════════════
def scenario_5_configuracion(page):
    log("\n" + "="*70)
    log("SCENARIO 5: Configuración")
    log("="*70)
    
    page.goto(f"{COBROS_URL}/school_settings/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    screenshot(page, "audit_s5_01_config_page.png")
    log(f"  URL: {page.url}")
    
    body_text = get_page_text(page)
    body_html = get_page_html(page)
    
    # Document all forms/settings on the page
    forms = page.locator("form")
    log(f"  Forms found: {forms.count()}")
    
    # Document all input fields
    inputs = page.evaluate('''() => {
        let inputs = document.querySelectorAll('input, select, textarea');
        return Array.from(inputs).map(i => ({
            type: i.type || i.tagName,
            name: i.name,
            id: i.id,
            value: i.value ? i.value.substring(0, 50) : '',
            placeholder: i.placeholder || '',
            required: i.required,
            disabled: i.disabled
        })).filter(i => i.type !== 'hidden' && i.name !== 'authenticity_token');
    }''')
    
    log(f"  Input fields: {len(inputs)}")
    for inp in inputs:
        log(f"    - [{inp['type']}] name={inp['name']} id={inp['id']} req={inp['required']} dis={inp['disabled']}")
    
    # Check for tabs or sections
    tabs = page.locator('.nav-tabs a, .tab-pane, .panel-heading, .separator-heading h3, .separator-heading h4')
    tab_texts = []
    for i in range(tabs.count()):
        t = tabs.nth(i).inner_text().strip()
        if t:
            tab_texts.append(t)
    log(f"  Sections/tabs: {tab_texts}")
    
    # Check for sub-pages in configuration
    config_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.content-body a, .main-content a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href
        })).filter(a => a.text.length > 0);
    }''')
    
    log(f"  Configuration sub-links: {len(config_links)}")
    for cl in config_links[:15]:
        log(f"    - {cl['text']} → {cl['href']}")
    
    screenshot(page, "audit_s5_02_config_detail.png")
    
    # 5b. Test validation - try empty submit on any visible form
    log("── 5b. Testing form validation ──")
    if forms.count() > 0:
        try:
            submit_btn = page.locator('button[type="submit"], input[type="submit"]').first
            if submit_btn.count() > 0:
                submit_btn.click(force=True)
                time.sleep(2)
                screenshot(page, "audit_s5_03_empty_submit.png")
                
                # Check for validation messages
                validation_msgs = page.locator('.error, .field_with_errors, .invalid-feedback, .help-block.error, .has-error')
                log(f"  Validation messages after empty submit: {validation_msgs.count()}")
                
                page_text = get_page_text(page)
                if "error" in page_text.lower() or "requerido" in page_text.lower() or "required" in page_text.lower():
                    log("  ✅ Validation working - error messages shown")
                else:
                    log("  ⚠ No validation errors shown after empty submit")
                    add_finding("Low", "Configuración", page.url,
                               "No validation feedback on empty form submission",
                               "1. Go to Configuración\n2. Click submit without filling fields",
                               "Validation error messages should appear",
                               "No visible validation feedback",
                               "audit_s5_03_empty_submit.png")
        except Exception as e:
            log(f"  ⚠ Validation test error: {e}")
    
    # 5c. Explore sub-pages of configuration
    log("── 5c. Exploring configuration sub-pages ──")
    config_sub_urls = [
        f"{COBROS_URL}/school_settings/payment_methods",
        f"{COBROS_URL}/school_settings/bank_accounts",
        f"{COBROS_URL}/school_settings/currencies",
        f"{COBROS_URL}/school_settings/invoicing",
        f"{COBROS_URL}/school_settings/services",
        f"{COBROS_URL}/school_settings/notifications",
    ]
    
    for url in config_sub_urls:
        try:
            resp = page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(2)
            
            if resp and resp.status < 400 and "select_role" not in page.url and page.url != f"{COBROS_URL}/login":
                log(f"  ✅ {url.split('/')[-1]}: accessible")
                screenshot(page, f"audit_s5_sub_{url.split('/')[-1]}.png")
            else:
                log(f"  ❌ {url.split('/')[-1]}: not accessible (status: {resp.status if resp else 'redirect'})")
        except Exception as e:
            log(f"  ❌ {url.split('/')[-1]}: error - {str(e)[:50]}")


# ══════════════════════════════════════════════════════════════════════════
# SCENARIO 6: Tasa BCV & Libro de Ventas
# ══════════════════════════════════════════════════════════════════════════
def scenario_6_tasa_bcv(page):
    log("\n" + "="*70)
    log("SCENARIO 6: Tasa BCV & Libro de Ventas")
    log("="*70)
    
    # 6a. Tasa BCV
    log("── 6a. Tasa BCV ──")
    page.goto(f"{COBROS_URL}/official_exchange_rate/index", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    wait_and_dismiss_modals(page)
    screenshot(page, "audit_s6_01_tasa_bcv.png")
    log(f"  URL: {page.url}")
    
    body_text = get_page_text(page)
    body_html = get_page_html(page)
    
    # Check for exchange rate display
    rate_elements = page.locator('.rate, .exchange-rate, .tasa, td')
    log(f"  Rate-related elements: {rate_elements.count()}")
    
    # Check for table with rates
    if page.locator("table").count() > 0:
        headers = page.evaluate('''() => {
            let ths = document.querySelectorAll('table th');
            return Array.from(ths).map(th => th.innerText.trim());
        }''')
        log(f"  Table headers: {headers}")
        
        rows = page.locator("table tbody tr")
        log(f"  Rate rows: {rows.count()}")
        
        if rows.count() > 0:
            first_rows = page.evaluate('''() => {
                let rows = document.querySelectorAll('table tbody tr');
                let data = [];
                for (let i = 0; i < Math.min(rows.length, 5); i++) {
                    let cells = rows[i].querySelectorAll('td');
                    data.push(Array.from(cells).map(c => c.innerText.trim().substring(0, 40)));
                }
                return data;
            }''')
            log(f"  Recent rates:")
            for row in first_rows:
                log(f"    {row}")
            
            # Check if the most recent rate is current
            if first_rows:
                last_row = first_rows[0]
                log(f"  Latest rate entry: {last_row}")
                # Check if date is recent (within last 7 days)
                today = datetime.now().strftime("%d/%m/%Y")
                log(f"  Today: {today}")
    
    # Check for update button/form
    update_btn = page.locator('button:has-text("Actualizar"), a:has-text("Actualizar"), button:has-text("Crear"), a:has-text("Nueva")')
    log(f"  Update/Create buttons: {update_btn.count()}")
    for i in range(min(update_btn.count(), 5)):
        log(f"    Button: {update_btn.nth(i).inner_text().strip()}")
    
    # Check for forms
    forms = page.locator("form")
    log(f"  Forms: {forms.count()}")
    
    screenshot(page, "audit_s6_02_tasa_detail.png")
    
    # 6b. Libro de Ventas
    log("── 6b. Libro de Ventas ──")
    libro_urls = [
        f"{COBROS_URL}/libro_ventas",
        f"{COBROS_URL}/sales_book",
        f"{COBROS_URL}/sales_books",
        f"{COBROS_URL}/school_settings/sales_book",
        f"{COBROS_URL}/school_settings/libro_ventas",
        f"{COBROS_URL}/libro_de_ventas",
    ]
    
    libro_found = False
    for url in libro_urls:
        try:
            resp = page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(2)
            
            if resp and resp.status < 400 and "select_role" not in page.url and page.url != f"{COBROS_URL}/login":
                log(f"  ✅ Libro de Ventas found at: {url}")
                screenshot(page, "audit_s6_03_libro_ventas.png")
                libro_found = True
                
                body_text = get_page_text(page)
                log(f"  Content: {body_text[:200]}")
                break
        except Exception:
            pass
    
    if not libro_found:
        # Maybe it's part of reports or configuration
        log("  ℹ Libro de Ventas not found as standalone page")
        log("  Checking if it's available as a report type...")
        
        page.goto(f"{COBROS_URL}/reports/new", wait_until="networkidle", timeout=15000)
        time.sleep(2)
        
        options = page.evaluate('''() => {
            let select = document.querySelector('select[name="report[report_information]"]');
            if (!select) return [];
            return Array.from(select.options).map(o => o.text.toLowerCase());
        }''')
        
        if any("libro" in opt or "ventas" in opt for opt in options):
            log("  ✅ Found 'Libro de Ventas' as report type")
        else:
            log("  ⚠ 'Libro de Ventas' not found anywhere")
            add_finding("Low", "Libro de Ventas", COBROS_URL,
                       "Libro de Ventas not found in navigation or reports",
                       "1. Login to cobros\n2. Search for 'Libro de Ventas' in sidebar and reports",
                       "Should be accessible as a menu item or report type",
                       "Not found",
                       "audit_s6_01_tasa_bcv.png")
    
    screenshot(page, "audit_s6_04_final.png")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
def main():
    log("╔══════════════════════════════════════════════════════════════════╗")
    log("║  COMPREHENSIVE AUDIT: Akdemia Cobros/Billing Module           ║")
    log(f"║  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║")
    log("╚══════════════════════════════════════════════════════════════════╝")
    
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1366, 'height': 900},
        ignore_https_errors=True
    )
    page = context.new_page()
    page.set_default_timeout(30000)
    
    report_results = {}
    
    try:
        # Login
        login_success = login_and_navigate_to_cobros(page)
        
        if not login_success:
            log("❌ LOGIN FAILED - cannot proceed with audit")
            return
        
        # Scenario 1: Payment Flow
        try:
            scenario_1_payment_flow(page)
        except Exception as e:
            log(f"❌ Scenario 1 failed: {e}")
            traceback.print_exc()
            screenshot(page, "audit_s1_error.png")
        
        # Scenario 2: Reports
        try:
            report_results = scenario_2_reports(page) or {}
        except Exception as e:
            log(f"❌ Scenario 2 failed: {e}")
            traceback.print_exc()
            screenshot(page, "audit_s2_error.png")
        
        # Scenario 3: Deudas
        try:
            scenario_3_deudas(page)
        except Exception as e:
            log(f"❌ Scenario 3 failed: {e}")
            traceback.print_exc()
            screenshot(page, "audit_s3_error.png")
        
        # Scenario 4: Notas
        try:
            scenario_4_notas(page)
        except Exception as e:
            log(f"❌ Scenario 4 failed: {e}")
            traceback.print_exc()
            screenshot(page, "audit_s4_error.png")
        
        # Scenario 5: Configuración
        try:
            scenario_5_configuracion(page)
        except Exception as e:
            log(f"❌ Scenario 5 failed: {e}")
            traceback.print_exc()
            screenshot(page, "audit_s5_error.png")
        
        # Scenario 6: Tasa BCV & Libro de Ventas
        try:
            scenario_6_tasa_bcv(page)
        except Exception as e:
            log(f"❌ Scenario 6 failed: {e}")
            traceback.print_exc()
            screenshot(page, "audit_s6_error.png")
        
    except Exception as e:
        log(f"❌ FATAL ERROR: {e}")
        traceback.print_exc()
        screenshot(page, "audit_fatal_error.png")
    finally:
        browser.close()
        p.stop()
    
    # ── Generate Summary ─────────────────────────────────────────────
    log("\n" + "="*70)
    log("AUDIT COMPLETE")
    log("="*70)
    log(f"Total findings: {len(findings)}")
    for f in findings:
        log(f"  [{f['severity']}] {f['module']}: {f['title']}")
    
    # Save findings as JSON for the report generator
    findings_path = os.path.join(SCREENSHOT_DIR, "audit_findings.json")
    with open(findings_path, 'w') as f:
        json.dump({
            "findings": findings,
            "report_results": report_results,
            "timestamp": datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    log(f"Findings saved to: {findings_path}")


if __name__ == "__main__":
    main()
