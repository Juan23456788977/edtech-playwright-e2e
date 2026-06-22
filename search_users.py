from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    
    with page.expect_navigation():
        page.click('input[type="submit"][value="Iniciar sesión"]')
        
    page.get_by_text('Colegio Prueba Akdemia').first.click()
    
    with page.expect_navigation(timeout=10000):
        page.evaluate('document.getElementById("select-role-form").submit()')
        
    print('Navigation finished! On page:', page.url)
    
    # Hacer clic en cambiar usuario y buscar
    btn = page.locator('a, button, li').filter(has_text='Cambiar a cualquier usuario').first
    btn.evaluate('el => el.click()')
    
    # Forzar mostrar el modal (por si el click fallo)
    page.evaluate('''() => {
        if (typeof jQuery !== 'undefined' && jQuery('#change-to-any-user-modal').length) {
            jQuery('#change-to-any-user-modal').modal('show');
        } else {
            const m = document.getElementById('change-to-any-user-modal');
            if (m) {
                m.style.display = 'block';
                m.style.opacity = '1';
                m.classList.add('in');
            }
        }
    }''')
    
    search_input = page.locator('#fill-user-info')
    search_input.wait_for(state='visible', timeout=5000)
    
    search_input.fill('prueba')
    search_input.press('Enter')
    
    page.wait_for_timeout(3000)
    print('>>> Búsqueda PRUEBA completada. Leyendo resultados... <<<')
    results = page.locator('.modal-content table tbody')
    if results.count() > 0:
        print(results.inner_text())
    else:
        print("No results found or table missing.")
        
    # Search for profesor
    search_input.fill('profesor')
    search_input.press('Enter')
    page.wait_for_timeout(3000)
    print('>>> Búsqueda PROFESOR completada. Leyendo resultados... <<<')
    results = page.locator('.modal-content table tbody')
    if results.count() > 0:
        print(results.inner_text())
        
    # Search for ejecutivo
    search_input.fill('ejecutivo')
    search_input.press('Enter')
    page.wait_for_timeout(3000)
    print('>>> Búsqueda EJECUTIVO completada. Leyendo resultados... <<<')
    if results.count() > 0:
        print(results.inner_text())

    # Search for deud
    search_input.fill('deud')
    search_input.press('Enter')
    page.wait_for_timeout(3000)
    print('>>> Búsqueda DEUD completada. Leyendo resultados... <<<')
    if results.count() > 0:
        print(results.inner_text())

    browser.close()
    p.stop()

run()
