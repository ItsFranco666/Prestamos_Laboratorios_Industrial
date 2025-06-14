import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import StudentModel
from utils.font_config import get_font # Asegúrate que utils.font_config exista y sea importable
from utils.validators import *

class StudentsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent") # Hacer el frame principal transparente
        
        self.student_model = StudentModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15, fill="both", expand=True) # Padding general para la vista

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        self.setup_ui()
        self.refresh_students()
    
    def prevent_resize(self, event):
        """Impide que el usuario redimensione las columnas con el mouse."""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(self, text="Gestión de Estudiantes", font=get_font("title", "bold"))
        title.pack(pady=(0, 20)) # Padding inferior para separar del siguiente frame
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0) # Padding inferior y sin padding horizontal interno al search_frame
        
        # Search entry
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código, nombre o cédula...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Project filter
        ctk.CTkLabel(search_frame, text="Proyecto:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.project_filter = ctk.CTkComboBox(search_frame, 
                                             values=["Todos"] + [p[1] for p in self.student_model.get_curriculum_projects()],
                                             font=get_font("normal"))
        self.project_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.project_filter.set("Todos")
        self.project_filter.configure(command=self.on_filter_change)
        
        # Add student button
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Estudiante", command=self.add_student_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=4, padx=(10,10), pady=10) # Padding a ambos lados
        
        search_frame.grid_columnconfigure(1, weight=3) # Más peso a la búsqueda
        search_frame.grid_columnconfigure(3, weight=2) # Peso al filtro
        
        # Students table using ttk.Treeview for proper column alignment
        self.create_students_treeview_table()
    
    def create_students_treeview_table(self):
        # Container frame principal con bordes redondeados y sombra
        table_main_container = ctk.CTkFrame(self, corner_radius=8, 
                                          border_width=1,
                                          border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0,10), padx=0)

        # Configurar estilo del Treeview para apariencia moderna
        style = ttk.Style()
        style.theme_use("default")

        # Altura de fila más generosa
        new_row_height = 35

        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            tree_bg = "#2b2b2b"
            text_color = "#ffffff" 
            selected_color = "#404040"
            heading_bg = "#4B5563"
            
            style.configure("Modern.Treeview", 
                          background=tree_bg,
                          foreground=text_color,
                          fieldbackground=tree_bg,
                          borderwidth=0,
                          relief="flat",
                          rowheight=new_row_height,
                          font=get_font("normal"))
            
            style.map('Modern.Treeview', 
                     background=[('selected', selected_color)],
                     foreground=[('selected', text_color)])
            
            # Estilo del header moderno
            style.configure("Modern.Treeview.Heading",
                          background=heading_bg,
                          foreground=text_color,
                          borderwidth=0,
                          relief="flat",
                          font=get_font("normal"),
                          padding=(10, 8))
            
            style.map("Modern.Treeview.Heading", 
                     background=[('active', "#525E75")])
        else:
            tree_bg = "#ffffff"
            text_color = "#2b2b2b"
            selected_color = "#e3f2fd"
            heading_bg = "#E5E7EB"
            
            style.configure("Modern.Treeview",
                          background=tree_bg,
                          foreground=text_color,
                          fieldbackground=tree_bg,
                          borderwidth=0,
                          relief="flat",
                          rowheight=new_row_height,
                          font=get_font("normal"))
            
            style.map('Modern.Treeview',
                     background=[('selected', selected_color)],
                     foreground=[('selected', text_color)])
            
            # Estilo del header moderno
            style.configure("Modern.Treeview.Heading",
                          background=heading_bg,
                          foreground=text_color,
                          borderwidth=0,
                          relief="flat",
                          font=get_font("normal"),
                          padding=(10, 8))
            
            style.map("Modern.Treeview.Heading", 
                     background=[('active', "#CFD8DC")])

        # Container para el Treeview con bordes redondeados internos
        table_container_frame = ctk.CTkFrame(table_main_container, 
                                           corner_radius=15,
                                           fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Crear el Treeview con estilo moderno (SIN columna de acciones)
        self.tree = ttk.Treeview(table_container_frame,
                               columns=("Codigo", "Nombre", "Cedula", "Proyecto"),
                               show="tree headings",
                               style="Modern.Treeview")

        # Configurar headers con texto visible y estilos modernos
        self.tree.heading("Codigo", text="📋 Código", anchor="w")
        self.tree.heading("Nombre", text="👤 Nombre", anchor="w")
        self.tree.heading("Cedula", text="🆔 Cédula", anchor="w")
        self.tree.heading("Proyecto", text="📁 Proyecto Curricular", anchor="w")

        # Configurar columnas para que se ajusten automáticamente sin poder ser modificadas
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("Codigo", width=120, stretch=False, anchor="w")      # Ancho fijo
        self.tree.column("Nombre", width=300, stretch=True, anchor="w")       # Se estira para ocupar espacio
        self.tree.column("Cedula", width=150, stretch=False, anchor="w")      # Ancho fijo
        self.tree.column("Proyecto", width=350, stretch=True, anchor="w")     # Se estira para ocupar espacio

        # Pack del Treeview con padding para el efecto de borde redondeado
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # <<-- NUEVO: Vincular los eventos del mouse al método que previene la redimensión -->>
        self.tree.bind("<Button-1>", self.prevent_resize)
        self.tree.bind("<B1-Motion>", self.prevent_resize)
        
        # Scrollbar moderna
        scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                   command=self.tree.yview,
                                   corner_radius=8,
                                   width=12)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0,5))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def refresh_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        project_filter = self.project_filter.get() if hasattr(self, 'project_filter') and self.project_filter.get() != "Todos" else ""
        
        students = self.student_model.get_all_students(search_term, project_filter_name=project_filter) 
        
        for i, student_data in enumerate(students):
            # Simplificar la visualización sin iconos excesivos para mejor legibilidad
            codigo_display = str(student_data[0])
            nombre_display = student_data[1]
            cedula_display = str(student_data[2])
            proyecto_display = student_data[3] or 'Sin proyecto'
            
            item_id = self.tree.insert("", "end", iid=str(student_data[0]), values=(
                codigo_display,
                nombre_display, 
                cedula_display,
                proyecto_display
            ))
            
            # Alternar colores de fila para mejor legibilidad
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
        
        # Configurar tags para filas alternadas
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
        
        if not hasattr(self, 'selected_actions_frame'): # Create actions frame only once
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                 text="Editar Seleccionado",
                                                 command=self.edit_selected_student, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_student, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Bind selection event after buttons are created
            self.tree.bind("<<TreeviewSelect>>", self.on_student_select)
        
        self.on_student_select() # Ensure buttons are in correct state after refresh

    def on_student_select(self, event=None):
        if hasattr(self, 'edit_selected_btn'): # Check if buttons exist
            selected_item_iid = self.tree.focus() 
            if selected_item_iid:
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_student_data(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un estudiante de la tabla.", parent=self)
            return None
        
        tree_values = self.tree.item(selected_item_iid, "values")
        # Los valores ahora están limpios, sin necesidad de remover iconos
        codigo = int(tree_values[0])
        nombre = tree_values[1]
        cedula = int(tree_values[2])
        proyecto = tree_values[3]
        
        return (codigo, nombre, cedula, proyecto)

    def edit_selected_student(self):
        student_display_data = self.get_selected_student_data()
        if student_display_data:
            dialog = StudentDialog(self, "Editar Estudiante", student_data_for_dialog=student_display_data, student_model=self.student_model)
            if dialog.result: 
                original_codigo, nombre, cedula, proyecto_id, new_codigo = dialog.result
                self.student_model.update_student(original_codigo, nombre, cedula, proyecto_id, new_codigo=new_codigo)
                self.refresh_students()

    def delete_selected_student(self):
        student_display_data = self.get_selected_student_data()
        if student_display_data:
            codigo_to_delete = student_display_data[0]
            nombre_to_delete = student_display_data[1]
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al estudiante {nombre_to_delete} (Cód: {codigo_to_delete})?", parent=self):
                self.student_model.delete_student(codigo_to_delete)
                self.refresh_students()
    
    def on_search(self, event=None): 
        self.refresh_students()
    
    def on_filter_change(self, value=None): 
        self.refresh_students()
    
    def add_student_dialog(self):
        dialog = StudentDialog(self, "Agregar Estudiante", student_model=self.student_model)
        if dialog.result:
            codigo, nombre, cedula, proyecto_id = dialog.result
            self.student_model.add_student(codigo, nombre, cedula, proyecto_id)
            self.refresh_students()
    
    def on_theme_change(self, event=None):
        if hasattr(self, 'tree'):
            style = ttk.Style()
            current_mode = ctk.get_appearance_mode()
            
            if current_mode == "Dark":
                tree_bg = "#2b2b2b"
                text_color = "#ffffff" 
                selected_color = "#404040"
                heading_bg = "#4B5563"
                alternate_bg = "#323232"
            else: # Light mode
                tree_bg = "#ffffff"
                text_color = "#2b2b2b"
                selected_color = "#e3f2fd"
                heading_bg = "#E5E7EB"
                alternate_bg = "#f8f9fa"
            
            # Ensure font is re-fetched if it could change, or use a consistent reference
            normal_font = get_font("normal")
            bold_font = get_font("normal", "bold")

            style.configure("Modern.Treeview", 
                          background=tree_bg,
                          foreground=text_color,
                          fieldbackground=tree_bg,
                          borderwidth=0,
                          relief="flat",
                          rowheight=35,
                          font=normal_font)
            
            style.map('Modern.Treeview', 
                     background=[('selected', selected_color)],
                     foreground=[('selected', text_color)])
            
            style.configure("Modern.Treeview.Heading",
                          background=heading_bg,
                          foreground=text_color,
                          borderwidth=0,
                          relief="flat",
                          font=bold_font,
                          padding=(10, 8))
            
            style.map("Modern.Treeview.Heading", 
                     background=[('active', "#525E75" if current_mode == "Dark" else "#CFD8DC")])
            
            # Configurar tags para filas alternadas
            self.tree.tag_configure('alternate', background=alternate_bg)
            
            # Re-populating the tree is crucial for ttk styles to apply to items
            self.refresh_students()
            
            # update_idletasks can help ensure Tkinter processes pending drawing tasks
            self.tree.update_idletasks()
            self.update_idletasks()

class StudentDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, student_data_for_dialog=None, student_model=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x400") 
        self.transient(parent)
        self.grab_set()
        self.lift() 

        self.result = None
        self.student_model = student_model 
        self.editing = student_data_for_dialog is not None
        self.original_student_code = student_data_for_dialog[0] if self.editing else None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Código:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre Completo:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Cédula:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.cedula_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.cedula_entry.grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Proyecto Curricular:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.projects_data = self.student_model.get_curriculum_projects() 
        project_names = ["Seleccione un proyecto..."] + [p[1] for p in self.projects_data]
        self.proyecto_combo = ctk.CTkComboBox(main_frame, values=project_names, font=get_font("normal"), state="readonly")
        self.proyecto_combo.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        self.proyecto_combo.set(project_names[0]) 

        main_frame.grid_columnconfigure(1, weight=1)

        if self.editing:
            self.codigo_entry.insert(0, str(student_data_for_dialog[0]))
            self.nombre_entry.insert(0, student_data_for_dialog[1])
            self.cedula_entry.insert(0, str(student_data_for_dialog[2]))
            if student_data_for_dialog[3] and student_data_for_dialog[3] != "Sin proyecto":
                self.proyecto_combo.set(student_data_for_dialog[3])
            else:
                self.proyecto_combo.set("Seleccione un proyecto...")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20,0), sticky="ew")
        
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)

        self.codigo_entry.focus_set()
        self.wait_window(self) 

    def _center_dialog(self): # This method might not be strictly necessary if parent centering works well
        self.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")
    
    def save(self):
        codigo_str = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        cedula_str = self.cedula_entry.get().strip()
        proyecto_nombre_seleccionado = self.proyecto_combo.get()

        if not codigo_str or not nombre or not cedula_str:
            messagebox.showerror("Error de Validación", "Código, Nombre y Cédula son obligatorios.", parent=self)
            return
        
        try:
            codigo = int(codigo_str)
            cedula = int(cedula_str)
        except ValueError:
            messagebox.showerror("Error de Validación", "Código y Cédula deben ser números enteros.", parent=self)
            return
            
        
        proyecto_id = None
        if proyecto_nombre_seleccionado != "Seleccione un proyecto...":
            for p_id, p_name in self.projects_data:
                if p_name == proyecto_nombre_seleccionado:
                    proyecto_id = p_id
                    break
        
        if self.editing:
            new_codigo_val = codigo if codigo != self.original_student_code else self.original_student_code
            self.result = (self.original_student_code, nombre, cedula, proyecto_id, new_codigo_val)
        else:
            self.result = (codigo, nombre, cedula, proyecto_id)
        
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()