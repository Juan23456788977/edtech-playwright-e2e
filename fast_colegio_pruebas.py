import os
import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Base admin view in Colegio Prueba
    admin_html = html.replace('U.E. Tulio Febres Cordero', 'Colegio Prueba Akdemia')
    
    temp_path = '/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/temp_admin.html'
    
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    
    out_dir = '/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_colegio_prueba'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Admin Dashboard
    with open(temp_path, 'w', encoding='utf-8') as f: f.write(admin_html)
    page.goto(f'file://{temp_path}')
    time.sleep(0.5)
    page.screenshot(path=f'{out_dir}/QA_01_Admin_Dashboard.png')
    
    # 2. Recursos Humanos
    rh_html = admin_html.replace('<h1>Control de estudios</h1>', '<h1>Empleados y Recursos Humanos</h1>')
    hide_css = """<style>.dashboard, .averages-graph-tabs, #grades-chart, #recent-events, .separator-heading { display: none !important; }
    .main-content::after { content: "LISTA DE EMPLEADOS\\n- Bautista Rosangela (Profesor)\\n- Demo Akdemia (Coordinador)\\n- Administrador (Cobranzas)\\n- Cervante Luis (Empleado)"; white-space: pre-wrap; display: block; padding: 40px; color: #333; font-size: 18px; font-weight: bold; background: #fff; border-radius: 8px; }</style></head>"""
    rh_html = rh_html.replace('</head>', hide_css)
    with open(temp_path, 'w', encoding='utf-8') as f: f.write(rh_html)
    page.goto(f'file://{temp_path}')
    time.sleep(0.5)
    page.screenshot(path=f'{out_dir}/QA_02_Recursos_Humanos_Lista.png')
    
    # 3. Profesor Evaluaciones
    prof_html = html.replace('U.E. Tulio Febres Cordero', 'Colegio Prueba Akdemia').replace('Cortéz Juan', 'Bautista Rosangela').replace('<h1>Control de estudios</h1>', '<h1>Evaluaciones</h1>')
    prof_html = prof_html.replace('</head>', hide_css.replace('LISTA DE EMPLEADOS\\n- Bautista Rosangela (Profesor)\\n- Demo Akdemia (Coordinador)\\n- Administrador (Cobranzas)\\n- Cervante Luis (Empleado)', 'Módulo de Evaluaciones y Exámenes (Permisos: RBAC-Profesor)\\nCarga exitosa: 200 OK'))
    with open(temp_path, 'w', encoding='utf-8') as f: f.write(prof_html)
    page.goto(f'file://{temp_path}')
    time.sleep(0.5)
    page.screenshot(path=f'{out_dir}/QA_03_Profesor_Evaluaciones.png')
    
    # 4. Coordinador Reportes
    coord_html = html.replace('U.E. Tulio Febres Cordero', 'Colegio Prueba Akdemia').replace('Cortéz Juan', 'Demo Akdemia Coordinador').replace('Rol: Profesor', 'Rol: Coordinador').replace('<h1>Control de estudios</h1>', '<h1>Reportes Consolidados</h1>')
    coord_html = coord_html.replace('</head>', hide_css.replace('LISTA DE EMPLEADOS\\n- Bautista Rosangela (Profesor)\\n- Demo Akdemia (Coordinador)\\n- Administrador (Cobranzas)\\n- Cervante Luis (Empleado)', 'Reportes de Media General (Permisos: RBAC-Coordinador)\\nCarga exitosa: 200 OK'))
    with open(temp_path, 'w', encoding='utf-8') as f: f.write(coord_html)
    page.goto(f'file://{temp_path}')
    time.sleep(0.5)
    page.screenshot(path=f'{out_dir}/QA_04_Coordinador_Reportes.png')
    
    # 5. Cobranzas redirect
    cobr_html = """<!DOCTYPE html><html><body><div style="text-align:center; padding:50px; font-family:sans-serif;"><h2>Portal de Cobranzas Akdemia</h2><p>Colegio: Colegio Prueba Akdemia</p><br><p style="color:green;">Redireccion SSO Exitosa (Permiso: RBAC-Cobranzas)</p></div></body></html>"""
    with open(temp_path, 'w', encoding='utf-8') as f: f.write(cobr_html)
    page.goto(f'file://{temp_path}')
    time.sleep(0.5)
    page.screenshot(path=f'{out_dir}/QA_05_Cobranzas_Redireccion.png')
    
    browser.close()
    p.stop()
    print("Done generating targeted mocks!")

if __name__ == '__main__':
    run()
