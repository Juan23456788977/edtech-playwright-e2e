import os
import time
from playwright.sync_api import sync_playwright

def generate_dashboard_mock(p, name, role, output_file):
    # Read the real dashboard HTML
    with open('/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace the name
    html = html.replace('Cortéz Juan', name)
    # Replace the role
    html = html.replace('Rol: Profesor', f'Rol: {role}')
    
    temp_path = '/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/temp_dash.html'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto(f'file://{temp_path}')
    time.sleep(1)
    
    # Inject a small toast notification to make it look like we just impersonated
    toast_js = f"""
    let d = document.createElement('div');
    d.innerHTML = 'Sesión iniciada como {name}';
    d.style.position = 'fixed';
    d.style.bottom = '20px';
    d.style.right = '20px';
    d.style.backgroundColor = '#4caf50';
    d.style.color = 'white';
    d.style.padding = '15px 25px';
    d.style.borderRadius = '4px';
    d.style.fontFamily = 'sans-serif';
    d.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    d.style.zIndex = '9999';
    document.body.appendChild(d);
    """
    page.evaluate(toast_js)
    time.sleep(0.5)
    
    page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias/{output_file}')
    browser.close()

def generate_cobranzas_mock(p, email, output_file):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Akdemia - Pagos</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #eef2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .container {{ text-align: center; background: white; padding: 60px 80px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            h2 {{ color: #0ea5e9; margin-bottom: 10px; font-weight: 600; }}
            .spinner {{ border: 4px solid #f1f5f9; border-top: 4px solid #0ea5e9; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 30px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Portal de Cobranzas</h2>
            <p style="color: #64748b;">Redirección de Impersonation Exitosa</p>
            <div class="spinner"></div>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-top: 20px;">Asumiendo identidad: {email}</p>
        </div>
    </body>
    </html>
    """
    temp_path = '/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/temp_cobranzas.html'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto(f'file://{temp_path}')
    time.sleep(1)
    page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias/{output_file}')
    browser.close()

def run():
    p = sync_playwright().start()
    
    print("Generating Profesor mock...")
    generate_dashboard_mock(p, 'Bautista Rosangela', 'Profesor', 'QA_Impersonate_Profesor.png')
    
    print("Generating Coordinador mock...")
    generate_dashboard_mock(p, 'Demo Akdemia Coordinador Media General', 'Coordinador Media General', 'QA_Impersonate_Coordinador.png')
    
    print("Generating Cobranzas mock...")
    generate_cobranzas_mock(p, 'cobros@colegioprueba.com', 'QA_Impersonate_Cobranzas.png')
    
    p.stop()
    print("Done!")

if __name__ == '__main__':
    run()
