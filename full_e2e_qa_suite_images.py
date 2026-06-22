import time
import sys
import os
from playwright.sync_api import sync_playwright

def run():
    # Crear directorio para las evidencias
    os.makedirs('evidencias', exist_ok=True)
    
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("==================================================")
    print("  INICIANDO BATERÍA DE PRUEBAS E2E AKDEMIA 2.0 CON CAPTURAS")
    print("==================================================")
    
    # === BLOQUE A ===
    print("\\n>>> BLOQUE A: Inicio de Sesión y Selección de Roles")
    try:
        page.goto('https://alpha.akdemia.com/login')
        page.fill('#email_login', 'jcortez@akdemia.com')
        page.fill('#password_login', 'akdemia#2026*')
        page.screenshot(path="evidencias/QA_01_Login_Credentials.png")
        page.click('input[type="submit"]')
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
        if "select_role" in page.url:
            print("✅ QA-02 PASS: Redirigido a /select_role.")
            page.screenshot(path="evidencias/QA_02_Select_Role.png", full_page=True)
            
            if page.locator('.school-card').count() > 0 or page.locator('text="Colegio Demo Satisfacción"').count() > 0:
                print("✅ QA-03 PASS: Separación visual confirmada.")
                page.screenshot(path="evidencias/QA_03_Separacion_Colegios.png", full_page=True)
                
            if page.locator('.disabled').count() > 0 or page.locator('text="inactivo"').count() > 0:
                print("✅ QA-04 PASS: Tarjetas inactivas.")
                page.screenshot(path="evidencias/QA_04_Tarjetas_Inactivas.png")
                
            page.get_by_text('Colegio Demo Satisfacción').first.click()
            page.evaluate("document.getElementById('select-role-form').submit()")
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
        # Caso 5: Cambio de rol en caliente
        if page.locator('#change-role').first.is_visible() or page.locator('a:has-text("Cambiar")').first.is_visible():
            print("✅ QA-05 PASS: Botón de cambio de rol.")
            page.screenshot(path="evidencias/QA_05_Boton_Cambiar_Rol.png")
            
    except Exception as e:
        print(f"❌ Error en Bloque A: {e}")

    # === BLOQUE B ===
    print("\\n>>> BLOQUE B: Reglas de Scopes y Año Escolar")
    try:
        # Caso 8
        page.goto('https://alpha.akdemia.com/employees')
        time.sleep(2)
        page.screenshot(path="evidencias/QA_08_Acceso_Global_Admin.png")
             
        # Casos 6 y 7
        page.goto('https://alpha.akdemia.com/grades')
        time.sleep(2)
        page.screenshot(path="evidencias/QA_06_y_07_Control_Calificaciones.png")
            
    except Exception as e:
        print(f"❌ Error en Bloque B: {e}")

    # === BLOQUE C ===
    print("\\n>>> BLOQUE C: Roles Especiales y Redirecciones SSO")
    try:
        page.goto('https://alpha.akdemia.com/invoices')
        time.sleep(2)
        page.screenshot(path="evidencias/QA_10_y_11_Redireccion_Cobranzas.png")
    except Exception as e:
        print(f"❌ Error en Bloque C: {e}")
        
    # === BLOQUE D ===
    print("\\n>>> BLOQUE D: Gestión (Admin)")
    try:
        page.goto('https://alpha.akdemia.com/schools/149/settings')
        time.sleep(2)
        page.screenshot(path="evidencias/QA_13_Settings_Colegio.png")
    except Exception as e:
        print(f"❌ Error en Bloque D: {e}")

    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
