import pytest
from playwright.sync_api import Page, expect

def test_case_6_teacher_without_scopes(page: Page, base_url: str, impersonate_user):
    """
    Caso 6: Profesor sin Scopes.
    Ingresa, ve los menús, pero las calificaciones no listan datos.
    """
    impersonate_user("Profesor")
    
    page.get_by_role("link", name="Calificaciones").click()
    expect(page.get_by_text("No tienes secciones asignadas")).to_be_visible()

def test_case_7_teacher_with_specific_scope(page: Page, base_url: str, impersonate_user):
    """
    Caso 7: Profesor con Scope Específico.
    """
    impersonate_user("Profesor")
    
    page.get_by_role("link", name="Calificaciones").click()
    
    section_selector = page.locator(".section-selector")
    expect(section_selector).to_contain_text("Matemática")
    expect(section_selector).not_to_contain_text("Biología")

def test_case_8_administrative_role_without_scopes(page: Page, base_url: str, impersonate_user):
    """
    Caso 8: Rol Administrativo sin Scopes (Acceso Global).
    """
    impersonate_user("Administrador")
    
    page.get_by_role("link", name="Reportes").click()
    expect(page.get_by_text("Reporte Global de Plantel")).to_be_visible()

def test_case_9_school_year_change(page: Page, base_url: str, impersonate_user):
    """
    Caso 9: Cambio de Año Escolar.
    """
    impersonate_user("Padre")
    
    expect(page.locator(".active-school-year-badge")).to_contain_text("2026-2027")
    page.get_by_role("link", name="Calificaciones").click()
    expect(page.get_by_text("No tienes secciones asignadas")).to_be_visible()
