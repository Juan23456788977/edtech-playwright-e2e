from playwright.sync_api import sync_playwright
import time

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("https://cobros.akdemia.com/users/sign_in")
        time.sleep(5)
        print("URL:", page.url)
        content = page.content()
        print(f"Content length: {len(content)}")
        # Look for text "Correo electrónico" or "Contraseña" or "input"
        print("Has input:", "input" in content.lower())
        print("Has email:", "email" in content.lower())
        print("Has password:", "password" in content.lower())
        with open("devise_login_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved devise_login_dump.html")
    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == "__main__":
    run()
