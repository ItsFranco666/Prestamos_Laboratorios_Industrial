# Create a new file: utils/exporter.py
import pandas as pd
from tkinter import filedialog, messagebox
from database.models import (
    StudentModel, ProfesorModel, RoomModel, InventoryModel, EquiposModel,
    PersonalLaboratorioModel, RoomLoanModel, EquipmentLoanModel,
    ProyectosCurricularesModel, SedesModel
)

def export_database_to_excel():
    """
    Handles fetching data from all database tables and exporting it
    to a single Excel file with multiple sheets.
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        title="Guardar Reporte de Base de Datos"
    )

    if not file_path:
        return  # User cancelled the save dialog

    try:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Sheet 1: Proyectos Curriculares
            proyectos_df = pd.DataFrame(
                ProyectosCurricularesModel().get_all_proyectos(),
                columns=['ID', 'Nombre del Proyecto']
            )
            proyectos_df.to_excel(writer, sheet_name='Proyectos Curriculares', index=False)

            # Sheet 2: Sedes
            sedes_df = pd.DataFrame(SedesModel().get_all_sedes(), columns=['ID', 'Nombre de la Sede'])
            sedes_df.to_excel(writer, sheet_name='Sedes', index=False)
            
            # Sheet 3: Personal Laboratorio (using the new export method)
            personal_df = pd.DataFrame(
                PersonalLaboratorioModel().get_all_personal_for_export(),
                columns=['ID', 'Nombre', 'Cargo']
            )
            personal_df.to_excel(writer, sheet_name='Personal Laboratorio', index=False)

            # Sheet 4: Estudiantes
            students_df = pd.DataFrame(
                StudentModel().get_all_students(),
                columns=['Código', 'Nombre', 'Cédula', 'Proyecto Curricular']
            )
            students_df.to_excel(writer, sheet_name='Estudiantes', index=False)

            # Sheet 5: Profesores
            profesores_df = pd.DataFrame(
                ProfesorModel().get_all_profesores(),
                columns=['Cédula', 'Nombre', 'Proyecto Curricular']
            )
            profesores_df.to_excel(writer, sheet_name='Profesores', index=False)

            # Sheet 6: Salas
            rooms_df = pd.DataFrame(
                RoomModel().get_all_rooms_with_status(),
                columns=['ID', 'Código Interno', 'Nombre', 'Estado Actual']
            )
            rooms_df.to_excel(writer, sheet_name='Salas', index=False)

            # Sheet 7: Inventario General
            inventory_df = pd.DataFrame(
                InventoryModel().get_all_equipment(),
                columns=['Código', 'Marca/Serie', 'Responsable', 'Sede', 'Descripción', 'Contenido', 'Estado']
            )
            inventory_df.to_excel(writer, sheet_name='Inventario General', index=False)

            # Sheet 8: Equipos en Salas (using the new export method)
            equipos_df = pd.DataFrame(
                EquiposModel().get_all_equipos_for_export(),
                columns=['Código', 'Sala', 'Num. Equipo', 'Descripción', 'Estado', 'Observaciones']
            )
            equipos_df.to_excel(writer, sheet_name='Equipos en Salas', index=False)
            
            # Sheet 9: Préstamos de Salas
            room_loans_data = RoomLoanModel().get_room_loans()
            room_loans_df = pd.DataFrame(room_loans_data, columns=['ID', 'Tipo Usuario', 'Usuario', 'Sala', 'Fecha Entrada', 'Hora Salida', 'Laboratorista', 'Monitor', 'Observaciones', 'ID Usuario', 'loan_type', 'Num. Equipo', 'Estado Préstamo', 'Firma', 'Código Equipo'])
            room_loans_df.drop(columns=['loan_type']).to_excel(writer, sheet_name='Préstamos de Salas', index=False)

            # Sheet 10: Préstamos de Equipos
            equipment_loans_data = EquipmentLoanModel().get_equipment_loans()
            equipment_loans_df = pd.DataFrame(equipment_loans_data, columns=['ID', 'Tipo Usuario', 'Usuario', 'Equipo', 'Fecha Entrega', 'Fecha Devolución', 'Lab. Entrega', 'Monitor Entrega', 'Lab. Devolución', 'Monitor Devolución', 'Práctica', 'Estado', 'Observaciones', 'ID Usuario', 'loan_type', 'Código Equipo', 'ID Sala', 'Firma'])
            equipment_loans_df.drop(columns=['loan_type']).to_excel(writer, sheet_name='Préstamos de Equipos', index=False)
            
        messagebox.showinfo("Exportación Exitosa", f"Los datos se han guardado en:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Error de Exportación", f"Ocurrió un error al exportar los datos: {e}")