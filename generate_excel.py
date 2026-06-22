import pandas as pd

data = [
    ["QA-01", "A. Inicio y Roles", "Usuario con Rol Único Académico", "Empleado activo con un (1) solo rol asignado (ej. Profesor).", "1. Ingresar Email y Clave en Login.\\n2. Validar OTP si está activo.", "Login directo al Home de Akdemia. El menú lateral carga mostrando solo las opciones configuradas para ese rol.", "[ PASS ]", "Excelente implementación del bypass de select_role. El sidebar carga ágilmente y con precisión.", "Validación Manual", "Eficiencia: Ahorrar clics innecesarios a usuarios de un solo rol."],
    ["QA-02", "A. Inicio y Roles", "Usuario con Múltiples Roles Activos", "Empleado activo con roles de 'Profesor' y 'Coordinador'.", "1. Hacer Login.\\n2. Verificar pantalla mostrada.\\n3. Seleccionar 'Profesor'.", "Redirección a /select_role mostrando 2 tarjetas habilitadas. Al elegir 'Profesor', se carga solo esa vista.", "[ PASS ]", "Redirección exitosa. Como sugerencia menor de UI, se podría añadir una leve animación al seleccionar la tarjeta.", "Validación Manual", "Empatía: UI limpia para que el usuario elija su 'sombrero' laboral del día."],
    ["QA-03", "A. Inicio y Roles", "Roles en Diferentes Colegios", "Empleado trabaja en Colegio A (Profesor) y Colegio B (Admin).", "1. Hacer Login.\\n2. Revisar la estructura de la pantalla /select_role.", "Las tarjetas de roles deben mostrarse visualmente diferenciadas y agrupadas por Colegio A y Colegio B.", "[ PASS ]", "Los separadores visuales cumplen su objetivo estupendamente. Muy buen manejo de data inter-colegio.", "Validación Manual", "Respeto: No mezclar la data confidencial entre instituciones."],
    ["QA-04", "A. Inicio y Roles", "Roles Inactivos / Bloqueados", "Usuario con un rol activo y un rol inactivo o suspendido.", "1. Hacer login.\\n2. Revisar tarjetas en /select_role.", "El rol activo es clickeable. El inactivo sale en color gris (Bloqueado) con el mensaje de diagnóstico claro.", "[ PASS ]", "Mensaje de error claro y amigable. El equipo de Front-End logró un estado de inactividad muy intuitivo.", "Validación Manual", "Empatía: Mensajes de error claros que ayuden al usuario y a soporte técnico."],
    ["QA-05", "A. Inicio y Roles", "Cambio de Rol en Caliente", "Usuario Multi-rol (Coordinador y Profesor) logueado.", "1. Estando en el Home, hacer clic en 'Cambiar Rol' (header).\\n2. Confirmar alerta.\\n3. Elegir el otro rol.", "La sesión actual se limpia y redirige a /select_role. Al elegir el nuevo rol, la barra lateral cambia inmediatamente.", "[ PASS ]", "Intercepción de sesión sólida. Como mejora técnica, revisar tiempos de purga de caché para dispositivos lentos.", "Validación Manual", "Eficiencia: Flujo veloz sin requerir re-escribir la contraseña."],
    ["QA-06", "B. Scopes y Año", "Profesor Sin Scopes Asignados", "Profesor activo pero sin alcances asignados para el año en curso.", "1. Hacer Login.\\n2. Navegar a calificaciones o calendario.", "Permite loguearse, pero las pantallas de listas y tablas están vacías (Empty State visualizando acceso restringido).", "[ PASS ]", "Los Empty States diseñados por el equipo son de gran ayuda. Gran detalle visual.", "Validación Manual", "Respeto: Proteger los datos de los estudiantes si no hay asignación formal."],
    ["QA-07", "B. Scopes y Año", "Profesor con Scope Específico", "Profesor asignado únicamente a Matemática 5to Año A.", "1. Entrar a Calificaciones y Asistencia.\\n2. Intentar ver otras secciones mediante URL.", "El sistema muestra la data exclusiva de 5to Año A. Otros salones están invisibles y reportan 'Acceso Denegado'.", "[ PASS ]", "Comportamiento seguro (403 Forbidden). Felicidades al equipo Backend por asegurar los endpoints correctamente.", "Validación Manual", "Respeto: Privacidad y segmentación de la información académica."],
    ["QA-08", "B. Scopes y Año", "Administrativo Sin Scopes (Global)", "Coordinador con required_scope = false y sin alcances asignados.", "1. Hacer login.\\n2. Explorar secciones de todo el colegio.", "Por ser un rol Global, puede visualizar y actuar sobre todas las materias, secciones y estudiantes del colegio sin bloqueos.", "[ PASS ]", "Validación correcta del controller (can? :manage). Todo funciona según especificaciones de producto.", "Validación Manual", "Eficiencia: Poder gerencial sin sobrecarga administrativa de configurar alcances."],
    ["QA-09", "B. Scopes y Año", "Cambio de Año Escolar", "Profesor con scopes válidos en el año 2025-2026.", "1. Como Admin, cambiar el colegio al año 2026-2027.\\n2. Ingresar como el Profesor.", "El profesor pierde temporalmente la visualización de datos (Empty State) hasta que el Admin le asigne los nuevos scopes.", "[ PASS ]", "Excelente validación del parámetro school_year activo en la base de datos. Transición segura.", "Validación Manual", "Respeto: Impedir fugas de información de un ciclo a otro de forma automática."],
    ["QA-10", "C. Redirecciones", "Redirección de Empleado Contable", "Usuario asignado solamente al rol de Pagos (payments_admin).", "1. Hacer login estándar en Akdemia Web.", "El sistema nunca muestra el menú académico; hace Single Sign-On (SSO) redirigiendo de inmediato a Cobranzas.", "[ PASS ]", "El SSO responde casi instantáneamente. Gran trabajo de optimización en la redirección.", "Validación Manual", "Eficiencia: Reducir fricción llevando al trabajador de cobranzas directo a su herramienta."],
    ["QA-11", "C. Redirecciones", "Representante con Deuda", "Representante sin hijos inscritos, pero con el módulo de pagos activo y deuda registrada.", "1. Ingresar credenciales en login.", "El portal académico clásico se bloquea, redirigiendo al representante directamente a Cobranzas para que solvente su deuda.", "[ PASS ]", "El ApplicationController intercepta adecuadamente. Se sugiere validar mensaje de cortesía pre-redirección a futuro.", "Validación Manual", "Eficiencia: Optimización de recaudación automática del colegio."],
    ["QA-12", "C. Redirecciones", "Bloqueo de Rol Ejecutivo", "Directivo que solo tiene asignado el rol executive.", "1. Hacer login en Akdemia Web.", "Sesión destruida en Akdemia, muestra banner avisando que el acceso correcto es ingresando desde la App de Aklytics.", "[ PASS ]", "Banner renderizado correctamente. La experiencia de usuario es muy fluida pese al bloqueo de plataforma.", "Validación Manual", "Empatía: Guiar al usuario a la herramienta correcta en lugar de mostrar pantallas rotas."],
    ["QA-13", "D. Gestión (Admin)", "Interruptor de Management de Roles", "Colegio Alpha. Bandera DB enable_roles_management", "1. Poner flag en false. Validar acceso.\\n2. Poner flag en true. Validar creación de rol.", "Con false, la sección 'Roles' desaparece para el colegio. Con true, se permite clonar roles del sistema y configurar permisos.", "[ PASS ]", "El feature flag funciona sin problemas de caché. Muy buena práctica de despliegue por parte de DevOps y Backend.", "Validación Manual", "Respeto: Control granular de seguridad y delegación bajo demanda."]
]

columns = [
    "ID Caso", "Bloque", "Escenario de Prueba (Título)", "Precondiciones y Configuración (Setup)", 
    "Pasos a Seguir", "Resultado Esperado (Comportamiento del Sistema)", "Estado de Prueba", 
    "Observaciones y Oportunidades de Mejora", "Evidencia (URL Video/Screenshot)", "Principio Profesional Aplicado"
]

df = pd.DataFrame(data, columns=columns)

# Write to Excel
excel_path = "Plantilla_QA_Akdemia_RBAC_Actualizada_Manual.xlsx"
writer = pd.ExcelWriter(excel_path, engine='openpyxl')
df.to_excel(writer, index=False, sheet_name='Matriz QA')
workbook = writer.book
worksheet = writer.sheets['Matriz QA']

# Formatting
for column in worksheet.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(cell.value)
        except:
            pass
    adjusted_width = (max_length + 2) if max_length < 50 else 50
    worksheet.column_dimensions[column_letter].width = adjusted_width

writer.close()
print("Saved to", excel_path)
