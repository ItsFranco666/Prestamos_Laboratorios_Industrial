import customtkinter as ctk
from tkinter import messagebox
from database.models import Profesor

class GestionProfesores(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.profesor_modelo = Profesor()
        self.setup_ui()
        self.refresh_profesores()
    
    def setup_ui(self):
        title = ctk.CTkLabel(self, text="Gestión de Profesores", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        # Recuadro busqueda y boton
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(10, 20))
        
        # Cuadro de busqueda
        ctk.CTkLabel(search_frame, text="Buscar:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código, nombre o cédula...")
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filtro por proyecto
        ctk.CTkLabel(search_frame, text="Proyecto:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.project_filter = ctk.CTkComboBox(search_frame, values=["Todos"] + [p[1] for p in self.profesor_modelo.get_curriculum_projects()])
        self.project_filter.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.project_filter.set("Todos")
        self.project_filter.configure(command=self.on_filter_change)
        
        # Add student button
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Profesor", command=self.add_student_dialog)
        add_btn.grid(row=0, column=4, padx=10, pady=10)
        
        search_frame.grid_columnconfigure(1, weight=1)
        search_frame.grid_columnconfigure(3, weight=1)
        
        # Students table
        self.create_tabla_profesores()
    
    def create_tabla_profesores(self):
        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True)
        
        # Headers
        headers = ["Cédula" "Nombre", "Proyecto Curricular", "Acciones"]
        header_frame = ctk.CTkFrame(table_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold"))
            if i == len(headers) - 1:  # Actions column
                label.pack(side="right", padx=10, pady=10)
            else:
                label.pack(side="left", padx=10, pady=10)
        
        # Scrollable frame for students
        self.profesores_scroll = ctk.CTkScrollableFrame(table_frame)
        self.profesores_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def refresh_profesores(self):
        # Borrar datos de tabla de profesores
        for widget in self.students_scroll.winfo_children():
            widget.destroy()
        
        # Agarrar los filtros de busqueda
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        project_filter = self.project_filter.get() if hasattr(self, 'project_filter') and self.project_filter.get() != "Todos" else ""
        
        # Obtener listado de profesores
        profesores = self.profesor_modelo.get_profesores(search_term, project_filter)
        
        for profesor in profesores:
            self.create_fila_profesor(profesor)
    
    def create_fila_profesor(self, profesor):
        row_frame = ctk.CTkFrame(self.profesores_scroll)
        row_frame.pack(fill="x", pady=2)
        
        # Informacion del profesor
        info_frame = ctk.CTkFrame(row_frame)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        cedula_label = ctk.CTkLabel(info_frame, text=str(pofesor[0]), width=120)
        cedula_label.pack(side="left", padx=10, pady=5)
        
        nombre_label = ctk.CTkLabel(info_frame, text=student[1], width=300)
        nombre_label.pack(side="left", padx=10, pady=5)   
        
        proyecto_label = ctk.CTkLabel(info_frame, text=student[2] or "Sin proyecto", width=300)
        proyecto_label.pack(side="left", padx=10, pady=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(row_frame)
        action_frame.pack(side="right", padx=5, pady=5)
        
        edit_btn = ctk.CTkButton(action_frame, text="Editar", width=70, command=lambda p=profesor: self.edit_profesor(p))
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(action_frame, text="Eliminar", width=70, fg_color="red", command=lambda p=profesor: self.delete_profesor(p[0], p[1]))
        delete_btn.pack(side="left", padx=2)
    
    def on_search(self, event):
        self.refresh_profesores()
    
    def on_filter_change(self, value):
        self.refresh_profesores()
    
    def add_profesor_dialog(self):
        dialog = DialogProfesor(self, "Agregar Profesor")
        if dialog.result:
            self.profesor_modelo.add_profesor(*dialog.result)
            self.refresh_profesores()
    
    def edit_profesor_dialog(self, profesor):
        dialog = DialogProfesor(self, "Editar Profesor", profesor)
        if dialog.result:
            self.profesor_modelo.update_profesor(*dialog.result)
            self.refresh_profesores()
    
    def delete_profesor(self, cedula, nombre):
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el profesor {nombre}?"):
            self.profesor_modelo.delete_profesor(cedula)
            self.refresh_profesores()

class DialogProfesor:
    def __init__(self, parent, title, datos_profesor=None):
        self.result = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.profesor_modelo = Profesor()
        self.setup_dialog(datos_profesor)
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def setup_dialog(self, datos_profesor):
        # Form fields
        ctk.CTkLabel(self.dialog, text="Cédula:").pack(pady=5)
        self.cedula_entry = ctk.CTkEntry(self.dialog)
        self.cedula_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.dialog, text="Nombre:").pack(pady=5)
        self.nombre_entry = ctk.CTkEntry(self.dialog)
        self.nombre_entry.pack(pady=5, padx=20, fill="x")
                
        ctk.CTkLabel(self.dialog, text="Proyecto Curricular:").pack(pady=5)
        proyectos = self.profesor_modelo.get_proyectos()
        nombres_proyectos = [p[1] for p in proyectos]
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
        projects = self.profesor_modelo.get_curriculum_projects()
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