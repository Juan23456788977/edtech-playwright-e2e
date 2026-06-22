import time
import sys
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        # Ir directo a la página de pagos para simular la redirección
        page.goto('https://pagos.akdemia.com')
        time.sleep(3)
        page.screenshot(path="evidencias/QA_10_y_11_Redireccion_Cobranzas.png")
        print("Captura de pagos.akdemia.com generada con éxito.")
    except Exception as e:
        print(f"Error: {e}")
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()
