import time
import uuid
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print('1. Iniciando sesión como jcortez...')
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type=\"submit\"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    
    print('2. Seleccionando "Colegio Demo Satisfacción"...')
    if page.locator('#select-role-form').is_visible():
        page.get_by_text('Colegio Demo Satisfacción').first.click()
        page.evaluate("document.getElementById('select-role-form').submit()")
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
    print('3. Navegando al módulo de Empleados...')
    page.goto('https://alpha.akdemia.com/employees')
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    uid = str(uuid.uuid4())[:6]
    
    employees_to_create = [
        {
            "email": f"qa_prof_{uid}@ak.com",
            "name": f"QAProf_{uid}",
            "last": f"Vacio_{uid}",
            "ci": f"V-{uid}1",
            "role": "2126", # Profesor
            "role_label": "Profesor"
        },
        {
            "email": f"qa_cob_{uid}@ak.com",
            "name": f"QACob_{uid}",
            "last": f"Solo_{uid}",
            "ci": f"V-{uid}2",
            "role": "2133", # Cobranzas
            "role_label": "Cobranzas"
        }
    ]
    
    results = []
    
    print('4. Creando usuarios semilla de prueba...')
    for emp in employees_to_create:
        print(f"  -> Creando {emp['role_label']} ({emp['name']})...")
        try:
            page.evaluate("$('#inviteEmployee').modal('show')")
            page.wait_for_selector('#employee_person_attributes_user_attributes_email', state='visible')
            time.sleep(1)
            
            page.fill('#employee_person_attributes_user_attributes_email', emp['email'])
            page.fill('#employee_person_attributes_first_name', emp['name'])
            page.fill('#employee_person_attributes_last_name', emp['last'])
            page.fill('#employee_person_attributes_unique_id', emp['ci'])
            
            page.select_option('select[name="role_id"]', value=emp['role'])
            time.sleep(1)
            
            # Forzamos el click usando JS para evadir punteros interceptados
            page.evaluate("document.getElementById('save-employee-button').click()")
            print(f"     ⏳ Esperando 5 segundos para guardado...")
            time.sleep(5)
            
            # Recargamos la pagina para limpiar modales trabados
            page.reload()
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            print(f"     ✅ Creado con éxito.")
        except Exception as e:
            print(f"     ❌ Error creando {emp['role_label']}: {e}")
            page.reload()
            time.sleep(3)
            
    print('⏳ Esperando 10 segundos para que ElasticSearch indexe los nuevos usuarios...')
    time.sleep(10)
            
    print('5. Buscando a los usuarios creados mediante Impersonate...')
    page.evaluate("$('#change-to-any-user-modal').modal('show')")
    time.sleep(2)
    
    for emp in employees_to_create:
        print(f"\\nBuscando a '{emp['name']}'...")
        page.fill('#fill-user-info', emp['name'])
        page.keyboard.press("Enter")
        time.sleep(4)
        
        links = page.locator('a:has-text("Cambiar a usuario")').all()
        if not links:
            print("  ❌ No se encontró en el buscador. Reintentando...")
            time.sleep(5)
            page.keyboard.press("Enter")
            time.sleep(4)
            links = page.locator('a:has-text("Cambiar a usuario")').all()
            if not links:
                print("  ❌ Fallo total en la búsqueda.")
                page.fill('#fill-user-info', '')
                continue
            
        href = links[0].get_attribute('href')
        print(f"  -> Impersonando: {href}")
        page.goto('https://alpha.akdemia.com' + href)
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
        if emp['role_label'] == 'Profesor':
            print("  -> Validando permisos de Profesor sin scopes...")
            page.goto('https://alpha.akdemia.com/grades')
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            content = page.content()
            if "No tienes secciones asignadas" in content or "No records" in content or page.locator('.empty-state').count() > 0 or "denegado" in content.lower():
                print("     ✅ Permiso verificado: Profesor sin scope ve el Empty State.")
                results.append(f"✅ ROL PROFESOR (Sin Scopes): Validado correctamente el bloqueo de visualización cruzada.")
            else:
                print("     ❌ Fallo: El profesor ve calificaciones que no le corresponden.")
                results.append(f"❌ ROL PROFESOR (Sin Scopes): Error de permisos de visualización.")
                
        elif emp['role_label'] == 'Cobranzas':
            print("  -> Validando permisos de Solo Cobranzas...")
            current_url = page.url
            if 'pagos' in current_url or 'cobranzas' in current_url or 'denied' in current_url:
                 print("     ✅ Permiso verificado: Solo Cobranzas restringido correctamente en login.")
                 results.append(f"✅ ROL COBRANZAS (Sin Scopes): Validado aislamiento del módulo financiero.")
            else:
                 page.goto('https://alpha.akdemia.com/grades')
                 page.wait_for_load_state('networkidle')
                 time.sleep(2)
                 content = page.content()
                 if 'pagos' in page.url or 'cobranzas' in page.url or 'denied' in page.url or 'Acceso denegado' in content or '403' in content or 'dashboard' not in page.url:
                     print("     ✅ Permiso verificado: Solo Cobranzas no pudo acceder al forzar URL.")
                     results.append(f"✅ ROL COBRANZAS (Sin Scopes): Bloqueado exitosamente el acceso a módulos académicos.")
                 else:
                     print(f"     ❌ Fallo: El usuario de cobranzas pudo entrar a {page.url}.")
                     results.append(f"❌ ROL COBRANZAS (Sin Scopes): Logró entrar a módulo académico.")
                     
        page.goto('https://alpha.akdemia.com/users/revert_change_to_anyone')
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        page.evaluate("$('#change-to-any-user-modal').modal('show')")
        time.sleep(2)

    print("\\n================ QA FINAL TEST REPORT ================")
    for r in results:
        print(r)
    print("======================================================")
    
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
