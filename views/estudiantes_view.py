import customtkinter as ctk
from tkinter import messagebox
from database.models import StudentModel
from utils.font_config import get_font

class StudentManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.student_model = StudentModel()
        self.setup_ui()
        self.refresh_students()
    
    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(self, text="Gestión de Estudiantes", font=get_font("title", "bold"))
        title.pack(pady=(10, 30))
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Search entry
        ctk.CTkLabel(search_frame, text="Buscar:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código, nombre o cédula...")
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Project filter
        ctk.CTkLabel(search_frame, text="Proyecto:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.project_filter = ctk.CTkComboBox(search_frame, values=["Todos"] + [p[1] for p in self.student_model.get_curriculum_projects()])
        self.project_filter.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.project_filter.set("Todos")
        self.project_filter.configure(command=self.on_filter_change)
        
        # Add student button
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Estudiante", command=self.add_student_dialog)
        add_btn.grid(row=0, column=4, padx=10, pady=10)
        
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_columnconfigure(3, weight=1)
        
        # Students table
        self.create_students_table()
    
    def create_students_table(self):
        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True)
        
        # Headers
        headers = ["Código", "Nombre", "Cédula", "Proyecto Curricular", "Acciones"]
        header_frame = ctk.CTkFrame(table_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold"))
            if i == len(headers) - 1:  # Actions column
                label.pack(side="right", padx=10, pady=10)
            else:
                label.pack(side="left", padx=10, pady=10)
        
        # Scrollable frame for students
        self.students_scroll = ctk.CTkScrollableFrame(table_frame)
        self.students_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def refresh_students(self):
        # Clear existing students
        for widget in self.students_scroll.winfo_children():
            widget.destroy()
        
        # Get filter values
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        project_filter = self.project_filter.get() if hasattr(self, 'project_filter') and self.project_filter.get() != "Todos" else ""
        
        # Get students
        students = self.student_model.get_all_students(search_term, project_filter)
        
        for student in students:
            self.create_student_row(student)
    
    def create_student_row(self, student):
        row_frame = ctk.CTkFrame(self.students_scroll)
        row_frame.pack(fill="x", pady=2)
        
        # Student info
        info_frame = ctk.CTkFrame(row_frame)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        codigo_label = ctk.CTkLabel(info_frame, text=str(student[0]), width=100)
        codigo_label.pack(side="left", padx=10, pady=5)
        
        nombre_label = ctk.CTkLabel(info_frame, text=student[1], width=200)
        nombre_label.pack(side="left", padx=10, pady=5)
        
        cedula_label = ctk.CTkLabel(info_frame, text=str(student[2]), width=120)
        cedula_label.pack(side="left", padx=10, pady=5)
        
        proyecto_label = ctk.CTkLabel(info_frame, text=student[3] or "Sin proyecto")
        proyecto_label.pack(side="left", padx=10, pady=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(row_frame)
        action_frame.pack(side="right", padx=5, pady=5)
        
        edit_btn = ctk.CTkButton(action_frame, text="Editar", width=70, command=lambda s=student: self.edit_student_dialog(s))
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(action_frame, text="Eliminar", width=70, fg_color="red", command=lambda s=student: self.delete_student(s[0]))
        delete_btn.pack(side="left", padx=2)
    
    def on_search(self, event):
        self.refresh_students()
    
    def on_filter_change(self, value):
        self.refresh_students()
    
    def add_student_dialog(self):
        dialog = StudentDialog(self, "Agregar Estudiante")
        if dialog.result:
            self.student_model.add_student(*dialog.result)
            self.refresh_students()
    
    def edit_student_dialog(self, student):
        dialog = StudentDialog(self, "Editar Estudiante", student)
        if dialog.result:
            self.student_model.update_student(*dialog.result)
            self.refresh_students()
    
    def delete_student(self, codigo):
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el estudiante {codigo}?"):
            self.student_model.delete_student(codigo)
            self.refresh_students()

class StudentDialog:
    def __init__(self, parent, title, student_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.student_model = StudentModel()
        self.setup_dialog(student_data)
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def setup_dialog(self, student_data):
        # Form fields
        ctk.CTkLabel(self.dialog, text="Código:").pack(pady=5)
        self.codigo_entry = ctk.CTkEntry(self.dialog)
        self.codigo_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.dialog, text="Nombre:").pack(pady=5)
        self.nombre_entry = ctk.CTkEntry(self.dialog)
        self.nombre_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.dialog, text="Cédula:").pack(pady=5)
        self.cedula_entry = ctk.CTkEntry(self.dialog)
        self.cedula_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.dialog, text="Proyecto Curricular:").pack(pady=5)
        projects = self.student_model.get_curriculum_projects()
        project_names = [p[1] for p in projects]
        self.proyecto_combo = ctk.CTkComboBox(self.dialog, values=project_names)
        self.proyecto_combo.pack(pady=5, padx=20, fill="x")
        
        # Fill data if editing
        if student_data:
            self.codigo_entry.insert(0, str(student_data[0]))
            self.nombre_entry.insert(0, student_data[1])
            self.cedula_entry.insert(0, str(student_data[2]))
            if student_data[3]:
                self.proyecto_combo.set(student_data[3])
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(pady=20, fill="x", padx=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save)
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel)
        cancel_btn.pack(side="right", padx=5)
    
    def save(self):
        # Validate fields
        if not all([self.codigo_entry.get(), self.nombre_entry.get(), self.cedula_entry.get()]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            codigo = int(self.codigo_entry.get())
            cedula = int(self.cedula_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Código y cédula deben ser números")
            return
        
        # Get project ID
        projects = self.student_model.get_curriculum_projects()
        proyecto_id = None
        if self.proyecto_combo.get():
            for p in projects:
                if p[1] == self.proyecto_combo.get():
                    proyecto_id = p[0]
                    break
        
        self.result = (codigo, self.nombre_entry.get(), cedula, proyecto_id)
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()