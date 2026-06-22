import pandas as pd
from openpyxl import load_workbook

def run():
    excel_path = "Plantilla_QA_Akdemia_RBAC_Actualizada_Manual.xlsx"
    print("Reading QA matrix spreadsheet...")
    
    # Read the existing data
    df = pd.read_excel(excel_path, sheet_name="Matriz QA")
    
    # Define the new row for QA-14
    new_row = {
        "ID Caso": "QA-14",
        "Bloque": "E. Reportes y Cobros",
        "Escenario de Prueba (Título)": "Reporte de Pagos Bancarizados (R006)",
        "Precondiciones y Configuración (Setup)": "Usuario administrador de pagos en colegios con Mercantil bancarizado (Angelo de Marta, Más Luz o Kalil Gibran).",
        "Pasos a Seguir": "1. Seleccionar 'Resumen de pagos bancarizados' (R006).\n2. Seleccionar banco Mercantil y rango de fechas.\n3. Generar Excel.",
        "Resultado Esperado (Comportamiento del Sistema)": "Se genera un Excel en una hoja con cabecera estándar (R006, RIF, etc.), 5 filas fijas de formas de pago en VES y fila de TOTAL, con 0s si no hay movimiento.",
        "Estado de Prueba": "[ FAIL ]",
        "Observaciones y Oportunidades de Mejora": "El reporte R006 no está visible/disponible en el dropdown de reportes en cobros-alpha.akdemia.com/reports/new. Reporte de pruebas manuales generado con capturas de pantalla.",
        "Evidencia (URL Video/Screenshot)": "Pruebas manuales fallidas. Captura cobros_reports.png adjunta como evidencia.",
        "Principio Profesional Aplicado": "Eficiencia: Identificar de un vistazo cuál forma de pago recauda más sin separar los pagos a mano."
    }
    
    # Check if QA-14 is already in the dataframe to avoid duplicates
    if "QA-14" not in df["ID Caso"].values:
        # Append the new row using loc
        df.loc[len(df)] = new_row
        print("QA-14 row added to DataFrame.")
    else:
        # Update it
        idx = df[df["ID Caso"] == "QA-14"].index[0]
        df.loc[idx] = new_row
        print("QA-14 row updated in DataFrame.")
        
    # Write back to Excel
    # Write to all spreadsheets
    for path in ["Plantilla_QA_Akdemia_RBAC_Actualizada_Manual.xlsx", "Plantilla_QA_Akdemia_RBAC_Actualizada.xlsx", "Plantilla_QA_Akdemia_RBAC.xlsx"]:
        writer = pd.ExcelWriter(path, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Matriz QA')
        
        # Format column widths
        worksheet = writer.sheets['Matriz QA']
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
        print("Saved updated QA Roadmap matrix to", path)

if __name__ == '__main__':
    run()
