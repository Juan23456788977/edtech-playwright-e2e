import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    
    download_dir = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/downloads'
    os.makedirs(download_dir, exist_ok=True)
    
    context = browser.new_context(
        viewport={'width': 1366, 'height': 900},
        accept_downloads=True
    )
    page = context.new_page()
    
    # Capture all downloads
    downloads = []
    page.on('download', lambda d: downloads.append(d))

    BASE_URL = 'https://omega.akdemia.com'
    print(f"1. Login en {BASE_URL}")
    page.goto(f'{BASE_URL}/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    print("2. Cambio de rol en Omega...")
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
    
    print("3. Ir a Cobranzas...")
    links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(), href: a.href
        }));
    }''')
    cobranzas_href = next((l['href'] for l in links if 'Cobranzas' in l['text']), None)
    page.goto(cobranzas_href)
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("4. Cambio de colegio en Cobros...")
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
    
    print("5. Ir a Reportes...")
    page.click('#reports')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    print("6. Seleccionando R006...")
    page.select_option('select[name="report[report_information]"]', '22')
    time.sleep(3)  # Wait for dynamic fields to load
    
    # Screenshot with R006 selected and bank field visible
    ss1 = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/omega_r006_ready.png'
    page.screenshot(path=ss1, full_page=True)
    print(f"   Screenshot R006 listo: {ss1}")
    
    print("7. Haciendo clic en 'Generar'...")
    page.locator('input[type="submit"], button, a').filter(has_text='Generar').first.click()
    time.sleep(10)  # Wait for download or page response
    
    # Check for downloads
    if downloads:
        for d in downloads:
            download_path = os.path.join(download_dir, d.suggested_filename)
            d.save_as(download_path)
            print(f"   ✅ DESCARGA: {download_path} ({d.suggested_filename})")
    else:
        print("   No se detectó descarga de archivo")
    
    # Take final screenshot
    ss_final = '/home/akdemia/.gemini/antigravity/brain/c6b5c0a1-b7eb-473e-a2ba-9cc94e7de3a4/omega_r006_final_v5.png'
    page.screenshot(path=ss_final, full_page=True)
    print(f"   Screenshot final: {ss_final}")
    print(f"   URL final: {page.url}")
    
    # Check for any alerts/messages on page
    alerts = page.evaluate('''() => {
        let els = document.querySelectorAll('.alert, .error, .notice, .flash, .toast, .message');
        return Array.from(els).map(a => a.innerText.trim());
    }''')
    if alerts:
        print(f"   Mensajes: {alerts}")
    
    # Check page content for any table or result
    body_text = page.evaluate('() => document.body.innerText.substring(0, 1000)')
    if 'error' in body_text.lower() or 'no se' in body_text.lower():
        print(f"   Posible error en página: {body_text[:300]}")
    
    browser.close()
    p.stop()
    print("\nPrueba completada.")

if __name__ == '__main__':
    run()
