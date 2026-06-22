import json
from playwright.sync_api import Page

def test_dump_users(page: Page, base_url: str):
    page.goto(f"{base_url}/login")
    page.fill("#email_login", "jcortez@akdemia.com")
    page.fill("#password_login", "akdemia#2026*")
    page.click("input[type='submit'][value='Iniciar sesión']")
    
    page.get_by_text("Colegio Prueba Akdemia").first.click()
    page.evaluate("document.getElementById('select-role-form').submit()")
    
    users = {}
    for term in ['a', 'e', 'profesor', 'admin', 'padre']:
        page.goto(f"{base_url}/users/search_for_change_to_anyone?search_input={term}")
        links = page.locator('a').all_inner_texts()
        users[term] = links
        
    with open('dumped_users.json', 'w') as f:
        json.dump(users, f, indent=2)
