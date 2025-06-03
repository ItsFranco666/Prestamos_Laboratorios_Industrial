import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import StudentModel
from utils.font_config import get_font # Asegúrate que utils.font_config exista y sea importable

class StudentManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent") # Hacer el frame principal transparente
        
        self.student_model = StudentModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15) # Padding general para la vista

        self.setup_ui()
        self.refresh_students()
    
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
        table_container_frame = ctk.CTkFrame(self)
        table_container_frame.pack(fill="both", expand=True, pady=(0,10), padx=0)

        style = ttk.Style()
        style.theme_use("default") # Base theme

        # Configure Treeview colors for dark/light mode (basic example)
        # These might need more fine-tuning based on the CustomTkinter theme
        # For a more integrated look, you might need to explore how CustomTkinter themes ttk widgets
        # or consider alternatives if perfect styling is crucial and hard with ttk.
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            style.configure("Treeview", 
                            background="#2e2e2e", 
                            foreground="white", 
                            fieldbackground="#2e2e2e", 
                            borderwidth=0,
                            rowheight=25) # Altura de fila
            style.map('Treeview', background=[('selected', '#555555')])
            style.configure("Treeview.Heading", 
                            background="#565b5e", 
                            foreground="white", 
                            font=get_font("normal", "bold"), # Usar font_config
                            borderwidth=0, relief="flat")
            style.map("Treeview.Heading", background=[('active', '#3c3c3c')])
        else: # Light mode
            style.configure("Treeview", 
                            background="#ebebeb", 
                            foreground="black", 
                            fieldbackground="#ebebeb", 
                            borderwidth=0,
                            rowheight=25)
            style.map('Treeview', background=[('selected', '#c0c0c0')])
            style.configure("Treeview.Heading", 
                            background="#d6d6d6", 
                            foreground="black", 
                            font=get_font("normal", "bold"),
                            borderwidth=0, relief="flat")
            style.map("Treeview.Heading", background=[('active', '#b0b0b0')])


        self.tree = ttk.Treeview(table_container_frame, 
                                 columns=("Codigo", "Nombre", "Cedula", "Proyecto", "Acciones"), 
                                 show="headings", style="Treeview")
        
        self.tree.heading("Codigo", text="Código", anchor="w")
        self.tree.heading("Nombre", text="Nombre", anchor="w")
        self.tree.heading("Cedula", text="Cédula", anchor="w")
        self.tree.heading("Proyecto", text="Proyecto Curricular", anchor="w")
        self.tree.heading("Acciones", text="Acciones", anchor="center")

        self.tree.column("Codigo", width=100, minwidth=80, stretch=False, anchor="w")
        self.tree.column("Nombre", width=250, minwidth=150, stretch=True, anchor="w")
        self.tree.column("Cedula", width=120, minwidth=100, stretch=False, anchor="w")
        self.tree.column("Proyecto", width=250, minwidth=150, stretch=True, anchor="w")
        self.tree.column("Acciones", width=150, minwidth=120, stretch=False, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        scrollbar = ctk.CTkScrollbar(table_container_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind double click for editing (optional, if you prefer this over buttons in action column)
        # self.tree.bind("<Double-1>", self.on_tree_double_click)

    def refresh_students(self):
        # Clear existing students from Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        project_filter = self.project_filter.get() if hasattr(self, 'project_filter') and self.project_filter.get() != "Todos" else ""
        
        students = self.student_model.get_all_students(search_term, project_filter_name=project_filter) # Pass project_filter_name
        
        for student_data in students:
            # student_data: (codigo, nombre, cedula, proyecto_nombre)
            # For the "Acciones" column, we'll insert the student's code (ID) to fetch for actions,
            # but display "Editar/Eliminar" or handle buttons differently.
            # A common way is to have buttons outside the tree or use the double-click.
            # If buttons are desired *in* the row, it's complex with ttk.Treeview without custom widgets.
            # For simplicity, we'll rely on a context menu or double-click, or separate action buttons.
            # Or, one can open a dialog upon selection.
            # Here, we'll just put text and handle actions via selection.
            
            # We need to store the actual student data (or at least the ID) with the tree item
            # One way is to use the `item` iid for the student code.
            # The values tuple should match the column order.
            self.tree.insert("", "end", iid=str(student_data[0]), values=(
                student_data[0], # Codigo
                student_data[1], # Nombre
                student_data[2], # Cedula
                student_data[3] or "Sin proyecto", # Proyecto
                "Ver Acciones" # Placeholder for Acciones column
            ))
        
        # Add a handler for selection to enable/show action buttons, or a context menu
        self.tree.bind("<<TreeviewSelect>>", self.on_student_select)
        
        # Frame for action buttons that appear upon selection
        self.selected_actions_frame = ctk.CTkFrame(self)
        self.selected_actions_frame.pack(pady=(10,0), padx=0, fill="x")

        self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Editar Seleccionado", 
                                             command=self.edit_selected_student, state="disabled", font=get_font("normal"))
        self.edit_selected_btn.pack(side="left", padx=5)

        self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Eliminar Seleccionado", 
                                               command=self.delete_selected_student, state="disabled", fg_color="red", font=get_font("normal"))
        self.delete_selected_btn.pack(side="left", padx=5)


    def on_student_select(self, event=None):
        selected_item_iid = self.tree.focus() # Gets the iid of the focused item
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
        
        # The iid is the student code. We need to fetch the full student data again for the dialog.
        # Or, if the 'values' in the treeview contained all necessary info, we could use that.
        # Let's assume student_model.get_student_by_code_or_id can fetch by code.
        # The `get_all_students` returns (codigo, nombre, cedula, proyecto_nombre)
        # The dialog needs (codigo, nombre, cedula, proyecto_nombre_actual_o_id)
        # We can reconstruct this or fetch fresh. Fetching fresh is safer.
        
        student_code = int(selected_item_iid)
        # This is a bit inefficient as we're re-fetching.
        # A better way would be to store the full student tuple in a dictionary keyed by code when loading.
        # For now, let's use the values from the tree, assuming they are sufficient for the dialog.
        # values = (codigo, nombre, cedula, proyecto_nombre, "Acciones")
        tree_values = self.tree.item(selected_item_iid, "values")
        
        # The dialog expects: (codigo, nombre, cedula, proyecto_nombre_para_mostrar_en_combobox)
        # The StudentModel.update_student expects: (original_codigo, nombre, cedula, proyecto_id, new_codigo=None)
        # We need to map proyecto_nombre back to proyecto_id for saving.
        
        return (int(tree_values[0]), tree_values[1], int(tree_values[2]), tree_values[3]) # codigo, nombre, cedula, proyecto_nombre


    def edit_selected_student(self):
        student_display_data = self.get_selected_student_data() # (codigo, nombre, cedula, proyecto_nombre)
        if student_display_data:
            # Pass this data to the dialog. The dialog will handle fetching project_id if needed for saving.
            dialog = StudentDialog(self, "Editar Estudiante", student_data_for_dialog=student_display_data, student_model=self.student_model)
            if dialog.result: # Dialog.result should be (codigo_original, nombre, cedula, proyecto_id, nuevo_codigo_si_cambio)
                original_codigo, nombre, cedula, proyecto_id, new_codigo = dialog.result
                self.student_model.update_student(original_codigo, nombre, cedula, proyecto_id, new_codigo=new_codigo)
                self.refresh_students()
                self.on_student_select() # Update button states

    def delete_selected_student(self):
        student_display_data = self.get_selected_student_data()
        if student_display_data:
            codigo_to_delete = student_display_data[0]
            nombre_to_delete = student_display_data[1]
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al estudiante {nombre_to_delete} (Cód: {codigo_to_delete})?", parent=self):
                self.student_model.delete_student(codigo_to_delete)
                self.refresh_students()
                self.on_student_select() # Update button states
    
    def on_search(self, event=None): # Added event=None for direct calls
        self.refresh_students()
    
    def on_filter_change(self, value=None): # Added value=None for direct calls
        self.refresh_students()
    
    def add_student_dialog(self):
        # Pass student_model to dialog so it can fetch projects for its combobox
        dialog = StudentDialog(self, "Agregar Estudiante", student_model=self.student_model)
        if dialog.result:
            # Dialog.result for add should be (codigo, nombre, cedula, proyecto_id)
            codigo, nombre, cedula, proyecto_id = dialog.result
            self.student_model.add_student(codigo, nombre, cedula, proyecto_id)
            self.refresh_students()

class StudentDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, student_data_for_dialog=None, student_model=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x400") # Adjusted size
        self.transient(parent)
        self.grab_set()
        self.lift() # Ensure it's on top

        self.result = None
        self.student_model = student_model # Passed from parent view
        self.editing = student_data_for_dialog is not None
        self.original_student_code = student_data_for_dialog[0] if self.editing else None

        # Center the dialog
        # self.after(10, self._center_dialog) # Delay centering slightly

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
        self.projects_data = self.student_model.get_curriculum_projects() # List of (id, nombre)
        project_names = ["Seleccione un proyecto..."] + [p[1] for p in self.projects_data]
        self.proyecto_combo = ctk.CTkComboBox(main_frame, values=project_names, font=get_font("normal"), state="readonly")
        self.proyecto_combo.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        self.proyecto_combo.set(project_names[0]) # Default to "Seleccione..."

        main_frame.grid_columnconfigure(1, weight=1)

        if self.editing:
            self.codigo_entry.insert(0, str(student_data_for_dialog[0]))
            self.nombre_entry.insert(0, student_data_for_dialog[1])
            self.cedula_entry.insert(0, str(student_data_for_dialog[2]))
            # student_data_for_dialog[3] is proyecto_nombre
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
        self.wait_window(self) # Crucial for modal behavior and getting result

    def _center_dialog(self):
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

