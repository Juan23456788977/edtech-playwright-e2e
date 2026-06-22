import pytest
from playwright.sync_api import Page, expect

def test_case_13_roles_management_flag(page: Page, base_url: str, impersonate_user):
    """
    Caso 13: Interruptor de Roles en el Colegio (enable_roles_management).
    """
    # Escenario A: Bandera en false
    impersonate_user("laura")
    page.get_by_role("link", name="Configuración").click()
    expect(page.get_by_text("Roles y Permisos")).not_to_be_visible()
    
    # Intento de acceso directo por URL debe ser rechazado
    page.goto(f"{base_url}/settings/roles")
    expect(page.get_by_text("Acceso denegado")).to_be_visible()

    # Escenario B: Bandera en true
    # Volvemos a impersonar
    impersonate_user("carmen")
    page.get_by_role("link", name="Configuración").click()
    expect(page.get_by_text("Roles y Permisos")).to_be_visible()
    page.get_by_text("Roles y Permisos").click()
    expect(page.get_by_role("button", name="Crear Nuevo Rol")).to_be_visible()
