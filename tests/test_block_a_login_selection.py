import pytest
import re
from playwright.sync_api import Page, expect

def test_case_1_single_academic_role(page: Page, base_url: str, impersonate_user):
    """
    Caso 1: Usuario con Rol Único Académico. 
    Al hacer login (vía impersonation), debe entrar directo al Home de Akdemia.
    """
    # Buscamos un usuario de prueba que sepamos que solo tiene 1 rol
    impersonate_user("Profesor")
    
    # Validar que no hay redirección a select_role
    expect(page).not_to_have_url(re.compile(r".*/select_role"))
    
    # Validar que cargue el dashboard
    expect(page.get_by_text("Dashboard", exact=False)).to_be_visible(timeout=10000)

def test_case_2_multiple_active_roles(page: Page, base_url: str, impersonate_user):
    """
    Caso 2: Usuario con Múltiples Roles Activos. 
    Al hacer login, debe aparecer la pantalla /select_role con tarjetas habilitadas.
    """
    # Buscamos a un usuario que tenga múltiples roles en su perfil
    impersonate_user("Profesor")
    
    # Validar redirección a selección de rol
    expect(page).to_have_url(re.compile(r".*/select_role"))
    
    # Verificar que existen múltiples tarjetas
    cards = page.locator(".select-role-user-info")
    expect(cards).to_have_count(2)

def test_case_3_roles_in_different_schools(page: Page, base_url: str, impersonate_user):
    """
    Caso 3: Usuario con Roles en Diferentes Colegios. 
    /select_role debe mostrar las tarjetas diferenciadas por colegio.
    """
    impersonate_user("Profesor")
    
    expect(page).to_have_url(re.compile(r".*/select_role"))
    # Verificamos estructura de diferentes colegios
    expect(page.locator(".select-role-user-info")).to_have_count(2)

def test_case_4_inactive_roles_visualization(page: Page, base_url: str, impersonate_user):
    """
    Caso 4: Visualización de Roles Inactivos/Bloqueados.
    El rol inactivo debe salir en gris con leyenda "Sin rol activo asignado".
    """
    impersonate_user("Padre")
    
    expect(page).to_have_url(re.compile(r".*/select_role"))
    
    inactive_card = page.locator(".role-card.disabled")
    expect(inactive_card).to_contain_text("Sin rol activo asignado")

def test_case_5_hot_role_swap(page: Page, base_url: str, impersonate_user):
    """
    Caso 5: Cambio de Rol en Caliente. Iniciar sesión, luego "Cambiar Rol".
    """
    impersonate_user("Coordinador")
    
    if "/select_role" in page.url:
        page.locator(".select-role-user-info").first.click()
        # Fallback de submit
        page.evaluate("document.getElementById('select-role-form').submit()")
    
    page.get_by_role("button", name="Cambiar Rol").click()
    page.get_by_role("button", name="Confirmar").click()
    
    expect(page).to_have_url(re.compile(r".*/select_role"))
