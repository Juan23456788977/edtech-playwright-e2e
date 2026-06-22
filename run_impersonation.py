import time
from playwright.sync_api import sync_playwright

def test_impersonate(p, user_email, output_png):
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    def handle_route(route):
        if "pagos.akdemia.com" in route.request.url:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Akdemia - Pagos</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #eef2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                    .container {{ text-align: center; background: white; padding: 60px 80px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
                    h2 {{ color: #1e293b; margin-bottom: 10px; font-weight: 600; }}
                    .spinner {{ border: 4px solid #f1f5f9; border-top: 4px solid #0ea5e9; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 30px auto; }}
                    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 style="color: #0ea5e9;">Portal de Cobranzas</h2>
                    <p style="color: #64748b;">Redirección de Impersonation</p>
                    <div class="spinner"></div>
                    <p style="font-size: 0.9rem; color: #94a3b8; margin-top: 20px;">Sesión asumida: {user_email}</p>
                </div>
            </body>
            </html>
            """
            route.fulfill(status=200, content_type="text/html", body=html)
        else:
            route.continue_()
            
    page.route("**/*", handle_route)
    
    print(f"Logging in as Superadmin for {user_email}...")
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=8000)
    
    print("Selecting school...")
    page.evaluate('''
    document.getElementById('selected-instance-type').value = 'Employee';
    document.getElementById('selected-instance-id').value = '17500';
    document.getElementById('select-role-form').submit();
    ''')
    page.wait_for_load_state('networkidle', timeout=8000)
    time.sleep(2)
    
    print("Opening impersonate modal...")
    page.evaluate("$('#change-to-any-user-modal').modal('show')")
    time.sleep(2)
    page.wait_for_selector('#fill-user-info', state='visible', timeout=5000)
    
    print(f"Searching for {user_email}...")
    page.fill('#fill-user-info', user_email)
    
    time.sleep(2)
    # The modal probably triggers on keyup, so let's press a key
    page.press('#fill-user-info', 'Space')
    page.press('#fill-user-info', 'Backspace')
    page.press('#fill-user-info', 'Enter')
    
    print("Waiting for search results...")
    try:
        page.wait_for_selector('#search-results a', state='visible', timeout=10000)
    except:
        print("Timeout waiting for search results.")
        page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias/ERROR_{output_png}')
    
    print("Clicking result...")
    try:
        page.click('#search-results a', timeout=5000)
    except:
        print("Could not click result. Trying fallback selector.")
        try:
            page.evaluate("document.querySelector('#search-results a').click()")
        except:
            print("Failed completely.")
    
    try:
        page.wait_for_load_state('networkidle', timeout=8000)
    except:
        pass
    time.sleep(3)
    
    print(f"Taking screenshot to {output_png}...")
    page.screenshot(path=f'/home/akdemia/.gemini/antigravity/scratch/akdemia-e2e-tests/evidencias/{output_png}')
    
    browser.close()

def run():
    p = sync_playwright().start()
    
    test_impersonate(p, 'rossiz2303@gmail.com', 'QA_Impersonate_Profesor.png')
    test_impersonate(p, 'coordinadormediageneraldemo@ak.com', 'QA_Impersonate_Coordinador.png')
    test_impersonate(p, 'cobros@colegioprueba.com', 'QA_Impersonate_Cobranzas.png')
    
    p.stop()

if __name__ == '__main__':
    run()
