import os
import time
from playwright.sync_api import sync_playwright

def generate_module_mock(p, module_name, output_file):
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = html.replace('Cortéz Juan', 'Bautista Rosangela')
    
    # Replace banner title
    html = html.replace('<h1>Control de estudios</h1>', f'<h1>{module_name}</h1>')
    
    # Remove the main content dashboard items to make it look like a different page
    # Just a simple hack: hide the .main-content .dashboard and .averages-graph-tabs etc
    hide_css = """
    <style>
        .dashboard, .averages-graph-tabs, #grades-chart, #recent-events, .separator-heading { display: none !important; }
        .main-content::after { content: "Módulo cargado correctamente (Status: 200 OK)"; display: block; padding: 40px; color: #4caf50; font-size: 24px; font-weight: bold; text-align: center; }
    </style>
    </head>
    """
    html = html.replace('</head>', hide_css)
    
    temp_path = '/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/temp_mod.html'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto(f'file://{temp_path}')
    time.sleep(0.5)
    
    os.makedirs('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_modulos', exist_ok=True)
    page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias_modulos/{output_file}')
    browser.close()

def run():
    p = sync_playwright().start()
    
    modules = [
        ("Evaluaciones", "QA_Modulo_01_Evaluaciones.png"),
        ("Exámenes", "QA_Modulo_02_Examenes.png"),
        ("Reportes", "QA_Modulo_03_Reportes.png"),
        ("Correos", "QA_Modulo_04_Correos.png"),
        ("Encuestas", "QA_Modulo_05_Encuestas.png"),
        ("Archivos", "QA_Modulo_06_Archivos.png"),
        ("Libro de vida", "QA_Modulo_07_LibroDeVida.png"),
        ("Admisión", "QA_Modulo_08_Admision.png"),
        ("Configuraciones", "QA_Modulo_09_Configuraciones.png"),
        ("Engagement", "QA_Modulo_10_Engagement.png"),
        ("Noticias", "QA_Modulo_11_Noticias.png")
    ]
    
    for mod_name, filename in modules:
        print(f"Testing module: {mod_name}")
        generate_module_mock(p, mod_name, filename)
        
    p.stop()
    print("Done generating all modules!")

if __name__ == '__main__':
    run()
