import csv
import sys

data = [
    ["ID Caso", "Bloque", "Escenario de Prueba (Título)", "Precondiciones y Configuración (Setup)", "Pasos a Seguir", "Resultado Esperado (Comportamiento del Sistema)", "Estado de Prueba (Pass/Fail)", "Evidencia o Resultados (Output real)"],
    
    # Bloque A
    ["QA-01", "Bloque A: Autenticación y Carga de Contexto", "Inicio de Sesión y Verificación de Entorno", "Usuario con rol activo en al menos un colegio registrado en el sistema. Entorno de Alpha configurado.", "1. Ingresar a la URL de Alpha.\\n2. Introducir credenciales válidas.\\n3. Hacer clic en 'Ingresar'.", "El usuario accede al sistema. La sesión se inicia correctamente. Se debe cargar el contexto inicial del usuario.", "[ PASS ]", "Captura adjunta (QA_01_Login_Credentials.png)"],
    ["QA-02", "Bloque A: Autenticación y Carga de Contexto", "Pantalla de Selección de Roles/Colegios (Usuario Multicolegio)", "El usuario tiene roles asignados en múltiples colegios o múltiples roles en el mismo colegio.", "1. Completar exitosamente el inicio de sesión.\\n2. Esperar a la redirección post-login.", "El sistema muestra la pantalla intermedia de selección. Muestra todas las opciones disponibles agrupadas por colegio.", "[ PASS ]", "Captura adjunta (QA_02_Select_Role.png)"],
    ["QA-03", "Bloque A: Autenticación y Carga de Contexto", "Separación de la UI por Colegio (Navbar y Temas)", "El usuario ha seleccionado un rol y ha ingresado a un colegio específico.", "1. Observar la barra de navegación superior (Navbar).\\n2. Navegar a otras vistas dentro del mismo colegio.", "El Navbar refleja el colegio activo. Los menús y datos corresponden exclusivamente a ese colegio.", "[ PASS ]", "Captura adjunta (QA_03_Separacion_Colegios.png)"],
    ["QA-04", "Bloque A: Autenticación y Carga de Contexto", "Acceso con Rol Suspendido/Inactivo", "Usuario tiene un rol en estado 'inactivo' o su colegio ha sido suspendido.", "1. Intentar iniciar sesión.\\n2. Intentar seleccionar la tarjeta del colegio inactivo.", "La tarjeta del rol inactivo está deshabilitada visualmente y no se puede seleccionar. No hay acceso a los datos de ese colegio.", "[ PASS ]", "Captura adjunta (QA_04_Tarjetas_Inactivas.png)"],
    ["QA-05", "Bloque A: Autenticación y Carga de Contexto", "Cambio Rápido de Roles (Switch Context)", "El usuario ya está dentro del dashboard de un colegio.", "1. Hacer clic en el botón superior 'Cambiar de Rol'.\\n2. Seleccionar un rol distinto en otro colegio.", "El sistema limpia la sesión actual y carga el nuevo contexto sin requerir volver a ingresar la contraseña.", "[ PASS ]", "Captura adjunta (QA_05_Boton_Cambiar_Rol.png)"],

    # Bloque C
    ["QA-06", "Bloque C: Privacidad de la Información (Profesores)", "Verificación de acceso a Calificaciones", "Usuario con rol de 'Profesor'.", "1. Iniciar sesión y seleccionar colegio.\\n2. Navegar al módulo de 'Control de Calificaciones' o listado de alumnos.", "El profesor sólo ve la lista de los estudiantes que le fueron asignados.", "[ FAIL ]", "BUG CRÍTICO: La página retorna Error 404 (Not Found). (Ver QA_06_y_07_Control_Calificaciones.png)"],
    ["QA-07", "Bloque C: Privacidad de la Información (Profesores)", "Intento de visualización de notas de estudiantes no asignados", "Usuario con rol de 'Profesor'. Conocer ID de un estudiante no asignado.", "1. Forzar URL en el navegador con el ID del estudiante no asignado (ej: /students/{id}/grades).", "El sistema rechaza la solicitud y muestra error de permisos o redirige al inicio.", "[ FAIL ]", "BUG CRÍTICO: El módulo entero arroja Error 404. No se puede validar la privacidad."],

    # Bloque E
    ["QA-08", "Bloque E: Acceso Global (Superadmin)", "Acceso a Información de todos los Colegios", "Usuario con rol de 'Super Administrador'.", "1. Iniciar sesión.\\n2. Navegar por los dashboards de diferentes colegios usando la barra de búsqueda.", "Puede acceder a cualquier colegio y realizar configuraciones sin estar en la nómina explícita de este.", "[ PASS ]", "Captura adjunta (QA_08_Acceso_Global_Admin.png)"],
    ["QA-09", "Bloque E: Acceso Global (Superadmin)", "Restricción contra la Modificación Inversa (Superadmin no se auto-bloquea)", "Usuario con rol 'Super Administrador'.", "1. Navegar al gestor de roles.\\n2. Intentar remover sus propios privilegios de Superadmin.", "El sistema oculta la opción o rechaza el guardado con un mensaje de protección.", "[ PASS ]", "Bloqueo efectivo. El botón de remover privilegios está deshabilitado."],

    # Bloque F
    ["QA-10", "Bloque F: Redirecciones Externas Seguras (Cobranzas)", "Redirección de Empleado Contable (payments_admin)", "Usuario con rol 'payments_admin' pero NO es representante.", "1. Intentar acceder a un módulo de pagos en Akdemia Web.", "Es redirigido mediante SSO al portal de cobranzas (pagos.akdemia.com) con sesión iniciada y permisos administrativos.", "[ PASS ]", "Captura adjunta (QA_10_y_11_Redireccion_Cobranzas.png)"],
    ["QA-11", "Bloque F: Redirecciones Externas Seguras (Cobranzas)", "Redirección de Representante con Deuda", "Usuario con rol 'Representante' y al menos una factura con estatus 'vencida'.", "1. Iniciar sesión normalmente.", "Tras la selección de rol, es redirigido forzosamente a cobranzas antes de poder ver el inicio (Muro).", "[ PASS ]", "Captura adjunta (QA_10_y_11_Redireccion_Cobranzas.png)"],
    ["QA-12", "Bloque F: Redirecciones Externas Seguras (Cobranzas)", "Protección de Sesión tras Redirección", "Usuario 'payments_admin' ha sido redirigido a Cobranzas.", "1. Intentar regresar atrás con el navegador a Akdemia Web.\\n2. Intentar acceder al dashboard (Muro).", "La sesión local de Akdemia Web ha sido destruida u ocultada; no puede regresar sin volver a autenticarse.", "[ PASS ]", "No se puede retroceder, la sesión principal ha caducado."],

    # Bloque G
    ["QA-13", "Bloque G: Escalabilidad del Switch", "Interruptor de Roles de Colegio (Feature Flag)", "Superadmin con acceso a panel de base de datos o UI de settings globales.", "1. Apagar el flag 'enable_roles_management' para un colegio específico.\\n2. Iniciar sesión como usuario de ese colegio.", "El colegio revierte instantáneamente a usar las reglas Legacy (hardcoded).", "[ PASS ]", "Captura adjunta (QA_13_Settings_Colegio.png)"]
]

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Matriz QA - Roles Akdemia"

header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True)
pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
fail_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

for col_num, header_title in enumerate(data[0], 1):
    cell = ws.cell(row=1, column=col_num, value=header_title)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for row_num, row_data in enumerate(data[1:], 2):
    for col_num, cell_value in enumerate(row_data, 1):
        cell = ws.cell(row=row_num, column=col_num, value=cell_value)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        if col_num == 7:  # Status column
            if "PASS" in cell_value:
                cell.fill = pass_fill
                cell.font = Font(color="006100", bold=True)
            elif "FAIL" in cell_value:
                cell.fill = fail_fill
                cell.font = Font(color="9C0006", bold=True)

# Adjust columns
for col in ws.columns:
    max_length = 0
    column = col[0].column_letter
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = (max_length + 2)
    if adjusted_width > 50:
        adjusted_width = 50
    ws.column_dimensions[column].width = adjusted_width

wb.save("/home/akdemia/.gemini/antigravity/scratch/Reporte_QA_Akdemia2_0_Manual_Correccion_Bug.xlsx")
