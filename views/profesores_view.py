import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import ProfesorModel
from utils.font_config import get_font

class ProfesorManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent") # Hacer el frame principal transparente
        
        self.profesor_model = ProfesorModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15) # Padding general para la vista

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        self.setup_ui()
        self.refresh_professors()
    
    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(self, text="Gestión de Profesores", font=get_font("title", "bold"))
        title.pack(pady=(0, 20)) # Padding inferior para separar del siguiente frame
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0) # Padding inferior y sin padding horizontal interno al search_frame
        
        # Search entry
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Cédula o nombre...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Project filter
        ctk.CTkLabel(search_frame, text="Proyecto:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.project_filter = ctk.CTkComboBox(search_frame, 
                                             values=["Todos"] + [p[1] for p in self.profesor_model.get_curriculum_projects()],
                                             font=get_font("normal"))
        self.project_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.project_filter.set("Todos")
        self.project_filter.configure(command=self.on_filter_change)
        
        # Add professor button
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Profesor", command=self.add_professor_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=4, padx=(10,10), pady=10) # Padding a ambos lados
        
        search_frame.grid_columnconfigure(1, weight=3) # Más peso a la búsqueda
        search_frame.grid_columnconfigure(3, weight=2) # Peso al filtro
        
        # Professors table using ttk.Treeview for proper column alignment
        self.create_professors_treeview_table()
    
    def create_professors_treeview_table(self):
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
                               columns=("Cedula", "Nombre", "Proyecto"),
                               show="tree headings",
                               style="Modern.Treeview")

        # Configurar headers con texto visible y estilos modernos
        self.tree.heading("Cedula", text="🆔 Cédula", anchor="w")
        self.tree.heading("Nombre", text="👤 Nombre", anchor="w")
        self.tree.heading("Proyecto", text="📁 Proyecto Curricular", anchor="w")

        # Configurar columnas - sin columna de acciones
        self.tree.column("#0", width=0, stretch=False)  # Ocultar columna del tree
        self.tree.column("Cedula", width=150, minwidth=120, stretch=False, anchor="w")
        self.tree.column("Nombre", width=300, minwidth=200, stretch=True, anchor="w")
        self.tree.column("Proyecto", width=350, minwidth=200, stretch=True, anchor="w")

        # Pack del Treeview con padding para el efecto de borde redondeado
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar moderna
        scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                   command=self.tree.yview,
                                   corner_radius=8,
                                   width=12)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0,5))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def refresh_professors(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        project_filter = self.project_filter.get() if hasattr(self, 'project_filter') and self.project_filter.get() != "Todos" else ""
        
        profesores = self.profesor_model.get_all_profesores(search_term, project_filter_name=project_filter) 
        
        for i, profesor_data in enumerate(profesores):
            # Simplificar la visualización sin iconos excesivos para mejor legibilidad
            cedula_display = str(profesor_data[0])
            nombre_display = profesor_data[1]
            proyecto_display = profesor_data[2] or 'Sin proyecto'
            
            item_id = self.tree.insert("", "end", iid=str(profesor_data[0]), values=(
                cedula_display,
                nombre_display, 
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
                                                 command=self.edit_selected_professor, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_professor, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Bind selection event after buttons are created
            self.tree.bind("<<TreeviewSelect>>", self.on_professor_select)
        
        self.on_professor_select() # Ensure buttons are in correct state after refresh

    def on_professor_select(self, event=None):
        if hasattr(self, 'edit_selected_btn'): # Check if buttons exist
            selected_item_iid = self.tree.focus() 
            if selected_item_iid:
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_professor_data(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un profesor de la tabla.", parent=self)
            return None
        
        tree_values = self.tree.item(selected_item_iid, "values")
        # Los valores ahora están limpios, sin necesidad de remover iconos
        cedula = int(tree_values[0])
        nombre = tree_values[1]
        proyecto = tree_values[2]
        
        return (cedula, nombre, proyecto)

    def edit_selected_professor(self):
        profesor_display_data = self.get_selected_professor_data()
        if profesor_display_data:
            dialog = ProfesorDialog(self, "Editar Profesor", profesor_data_for_dialog=profesor_display_data, profesor_model=self.profesor_model)
            if dialog.result: 
                original_cedula, nombre, proyecto_id, new_cedula = dialog.result
                self.profesor_model.update_profesor(original_cedula, nombre, proyecto_id, new_cedula=new_cedula)
                self.refresh_professors()

    def delete_selected_professor(self):
        profesor_display_data = self.get_selected_professor_data()
        if profesor_display_data:
            cedula_to_delete = profesor_display_data[0]
            nombre_to_delete = profesor_display_data[1]
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al profesor {nombre_to_delete} (Céd: {cedula_to_delete})?", parent=self):
                self.profesor_model.delete_profesor(cedula_to_delete)
                self.refresh_professors()
    
    def on_search(self, event=None): 
        self.refresh_professors()
    
    def on_filter_change(self, value=None): 
        self.refresh_professors()
    
    def add_professor_dialog(self):
        dialog = ProfesorDialog(self, "Agregar Profesor", profesor_model=self.profesor_model)
        if dialog.result:
            cedula, nombre, proyecto_id = dialog.result
            self.profesor_model.add_profesor(cedula, nombre, proyecto_id)
            self.refresh_professors()
    
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
            self.refresh_professors()
            
            # update_idletasks can help ensure Tkinter processes pending drawing tasks
            self.tree.update_idletasks()
            self.update_idletasks()

class ProfesorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, profesor_data_for_dialog=None, profesor_model=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x400") 
        self.transient(parent)
        self.grab_set()
        self.lift() 

        self.result = None
        self.profesor_model = profesor_model 
        self.editing = profesor_data_for_dialog is not None
        self.original_cedula = profesor_data_for_dialog[0] if self.editing else None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Cédula:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.cedula_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.cedula_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre Completo:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Proyecto Curricular:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.projects_data = self.profesor_model.get_curriculum_projects() 
        project_names = ["Seleccione un proyecto..."] + [p[1] for p in self.projects_data]
        self.proyecto_combo = ctk.CTkComboBox(main_frame, values=project_names, font=get_font("normal"), state="readonly")
        self.proyecto_combo.grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        self.proyecto_combo.set(project_names[0]) 

        main_frame.grid_columnconfigure(1, weight=1)

        if self.editing:
            self.cedula_entry.insert(0, str(profesor_data_for_dialog[0]))
            self.nombre_entry.insert(0, profesor_data_for_dialog[1])
            if profesor_data_for_dialog[2] and profesor_data_for_dialog[2] != "Sin proyecto":
                self.proyecto_combo.set(profesor_data_for_dialog[2])
            else:
                self.proyecto_combo.set("Seleccione un proyecto...")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20,0), sticky="ew")
        
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)

        self.cedula_entry.focus_set()
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
        cedula_str = self.cedula_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        proyecto_nombre_seleccionado = self.proyecto_combo.get()

        if not cedula_str or not nombre:
            messagebox.showerror("Error de Validación", "Cédula y Nombre son obligatorios.", parent=self)
            return
        
        if not is_valid_id(cedula_str):
            messagebox.showerror("Error de Validación", "La cédula debe ser un número de 11 dígitos.", parent=self)
            return
        
        proyecto_id = None
        if proyecto_nombre_seleccionado != "Seleccione un proyecto...":
            for p_id, p_name in self.projects_data:
                if p_name == proyecto_nombre_seleccionado:
                    proyecto_id = p_id
                    break
        
        if self.editing:
            new_cedula_val = int(cedula_str) if int(cedula_str) != self.original_cedula else self.original_cedula
            self.result = (self.original_cedula, nombre, proyecto_id, new_cedula_val)
        else:
            self.result = (int(cedula_str), nombre, proyecto_id)
        
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()