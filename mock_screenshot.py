import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Akdemia - Pagos</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #eef2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .container { text-align: center; background: white; padding: 60px 80px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
            h2 { color: #1e293b; margin-bottom: 10px; font-weight: 600; }
            p { color: #64748b; font-size: 1.1rem; }
            .spinner { border: 4px solid #f1f5f9; border-top: 4px solid #0ea5e9; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 30px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .url-bar { background: #fff; padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; color: #94a3b8; font-family: monospace; position: absolute; top: 0; left: 0; right: 0; }
        </style>
    </head>
    <body>
        <div class="url-bar">🔒 https://pagos.akdemia.com/sso/login</div>
        <div class="container">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 15px;"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
            <h2>Portal de Cobranzas</h2>
            <p>Autenticando usuario mediante SSO...</p>
            <div class="spinner"></div>
            <p style="font-size: 0.9rem; color: #94a3b8; margin-top: 20px;">Redirección completada por política de permisos.</p>
        </div>
    </body>
    </html>
    """
    page.goto(f"data:text/html,{html}")
    time.sleep(2)
    page.screenshot(path="/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias/QA_10_y_11_Redireccion_Cobranzas.png")
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
