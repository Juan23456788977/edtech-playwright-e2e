import pytest
from playwright.sync_api import Page, expect

@pytest.fixture
def impersonate_user(page: Page, base_url: str):
    """
    Fixture que provee una función para hacer login como jcortez@akdemia.com,
    entrar al Colegio Prueba Akdemia y buscar un usuario específico para impersonar.
    """
    def _impersonate(search_term: str):
        # 1. Login
        page.goto(f"{base_url}/login")
        page.fill("#email_login", "jcortez@akdemia.com")
        page.fill("#password_login", "akdemia#2026*")
        page.click("input[type='submit'][value='Iniciar sesión']")
        
        # 2. Ir a Colegio Prueba Akdemia
        # Damos click y hacemos submit del form
        page.get_by_text("Colegio Prueba Akdemia").first.click()
        with page.expect_navigation():
            page.evaluate("document.getElementById('select-role-form').submit()")
        
        # 3. Click en Cambiar a cualquier usuario
        btn_cambiar = page.locator("a, button, li").filter(has_text="Cambiar a cualquier usuario").first
        btn_cambiar.evaluate("el => el.click()")
        
        page.evaluate("""() => {
            if (typeof $ !== 'undefined' && $('#change-to-any-user-modal').length) {
                $('#change-to-any-user-modal').modal('show');
            }
        }""")
        page.wait_for_timeout(1000)
        
        # 4. Disparar directamente el ajax de búsqueda para saltarnos el bug de UI
        page.evaluate(f"() => new Promise(resolve => jQuery.get('/users/search_for_change_to_anyone', {{ search_input: '{search_term}' }}).done(resolve))")
        
        # 5. Esperar a que salgan los resultados (enlaces dentro de divs, no hay tabla)
        page.wait_for_selector("#search-results a", timeout=5000)
        
        # 6. Hacer clic en el primer resultado ("Cambiar a usuario")
        page.locator("#search-results a").first.click()
        
        # 6. Esperar a que la redireccion se complete
        page.wait_for_load_state("networkidle")
        
    return _impersonate
