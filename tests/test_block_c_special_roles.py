import pytest
import re
from playwright.sync_api import Page, expect

def test_case_10_payments_admin_sso_redirect(page: Page, base_url: str, impersonate_user):
    """
    Caso 10: Redirección de Empleado Contable.
    """
    impersonate_user("Padre")
    expect(page).to_have_url(re.compile(r"pagos\.akdemia\.com.*|.*cobranzas.*"))

def test_case_11_guardian_with_debt_redirect(page: Page, base_url: str, impersonate_user):
    """
    Caso 11: Redirección de Representante con Deuda.
    """
    impersonate_user("Padre")
    expect(page).to_have_url(re.compile(r"pagos\.akdemia\.com.*|.*cobranzas.*"))
    expect(page.get_by_text("Estado de Cuenta", exact=False)).to_be_visible()

def test_case_12_executive_role_blocked(page: Page, base_url: str, impersonate_user):
    """
    Caso 12: Bloqueo de Rol Ejecutivo.
    """
    impersonate_user("Administrador")
    expect(page.locator(".alert-danger, .aklytics-banner")).to_contain_text("Aklytics")
    expect(page).to_have_url(re.compile(r".*login.*"))
