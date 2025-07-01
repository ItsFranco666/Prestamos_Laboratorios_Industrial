import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import InventoryModel
from utils.font_config import get_font
from utils.validators import *

class InventoryView(ctk.CTkFrame):
    def __init__(self, parent):
        # Hacer el frame principal transparente
        super().__init__(parent, fg_color="transparent")
        
        # Inicializa el modelo de datos para interactuar con la base de datos de inventario
        self.inventory_model = InventoryModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15, fill="both", expand=True) # Padding general para la vista

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        # Creacion de UI y llenar datos de tabla
        self.setup_ui()
        self.refresh_inventory()
    
    def prevent_resize(self, event):
        """Impide que el usuario redimensione las columnas con el mouse"""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        '''Metodo para construir los componentes visuales de la vista (título, cuadro de búsqueda, filtros y botones)'''
        # Titulo
        title = ctk.CTkLabel(self, text="Gestión de Inventario", font=get_font("title", "bold"))
        title.pack(pady=(10, 20)) # Padding inferior para separar del siguiente frame
        
        # Frame para cuadro de busqueda y filtros
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0) # Padding inferior y sin padding horizontal interno al search_frame
        
        # Cuadro de busqueda 
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código o descripción...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Vincula el evento de liberación de tecla para llamar a la función de búsqueda
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filtro por estado
        ctk.CTkLabel(search_frame, text="Estado:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.status_filter = ctk.CTkComboBox(search_frame, 
                                           values=["Todos", "DISPONIBLE", "EN USO", "DAÑADO"],
                                           font=get_font("normal"))
        self.status_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.status_filter.set("Todos") # Establece "Todos" como valor por defecto
        # Configura el comando a ejecutar cuando cambia la selección del filtro
        self.status_filter.configure(command=self.on_filter_change)
        
        # Filtro por marca/serie
        ctk.CTkLabel(search_frame, text="Marca/Serie:", font=get_font("normal")).grid(row=0, column=4, padx=(10,5), pady=10, sticky="w")
        self.brand_serial_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar por marca o serie...", font=get_font("normal"))
        self.brand_serial_entry.grid(row=0, column=5, padx=5, pady=10, sticky="ew")
        self.brand_serial_entry.bind("<KeyRelease>", self.on_search)
        
        # Boton añadir equipo
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Equipo", command=self.add_equipment_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=6, padx=(10,10), pady=10)
        
        # Configura la expansión de las columnas en el grid del frame de búsqueda
        search_frame.grid_columnconfigure(1, weight=3) # Más peso a la búsqueda
        search_frame.grid_columnconfigure(3, weight=1) # Peso al filtro de estado
        search_frame.grid_columnconfigure(5, weight=2) # Peso al filtro de marca/serie
        
        # Llama al método para crear la tabla de inventario
        self.create_inventory_treeview_table()
    
    def create_inventory_treeview_table(self):
        """
        Configures the ttk.Treeview widget to display inventory data,
        including headers, columns, and both vertical and horizontal scrollbars.
        """
        # Main container for the table with a border
        table_main_container = ctk.CTkFrame(self, corner_radius=8, 
                                          border_width=1,
                                          border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0,10), padx=0)

        # Inner frame for the table with background and padding
        table_container_frame = ctk.CTkFrame(table_main_container, 
                                           corner_radius=15,
                                           fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Configure the grid layout for the table container
        table_container_frame.grid_rowconfigure(0, weight=1)
        table_container_frame.grid_columnconfigure(0, weight=1)

        # Create the Treeview using the global "Modern.Treeview" style
        self.tree = ttk.Treeview(table_container_frame,
                               columns=("Codigo", "MarcaSerie", "Responsable", "Ubicacion", "Descripcion", "Contenido", "Estado"),
                               show="headings", # Use "headings" to hide the first empty column
                               style="Modern.Treeview")

        # Table Headers
        self.tree.heading("Codigo", text="🔑 Código", anchor="w")
        self.tree.heading("MarcaSerie", text="🏷️ Marca/Serie", anchor="w")
        self.tree.heading("Responsable", text="👤 Responsable", anchor="w")
        self.tree.heading("Ubicacion", text="📍 Ubicación", anchor="w")
        self.tree.heading("Descripcion", text="📝 Descripción", anchor="w")
        self.tree.heading("Contenido", text="📦 Contenido", anchor="w")
        self.tree.heading("Estado", text="📊 Estado", anchor="w")

        # Table Columns (width and stretch behavior)
        self.tree.column("Codigo", width=120, stretch=False, anchor="w")
        self.tree.column("MarcaSerie", width=180, stretch=False, anchor="w")
        self.tree.column("Responsable", width=220, stretch=False, anchor="w")
        self.tree.column("Ubicacion", width=180, stretch=False, anchor="w")
        self.tree.column("Descripcion", width=300, stretch=False, anchor="w") # Set a fixed initial width
        self.tree.column("Contenido", width=250, stretch=False, anchor="w")
        self.tree.column("Estado", width=120, stretch=False, anchor="w")

        # Place the Treeview in the grid
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Vertical Scrollbar for the table
        v_scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                     command=self.tree.yview,
                                     corner_radius=8,
                                     width=12)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Horizontal Scrollbar for the table
        h_scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                     command=self.tree.xview,
                                     orientation="horizontal",
                                     corner_radius=8,
                                     height=12)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure the Treeview to scroll with both scrollbars
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Prevent the user from resizing columns
        self.tree.bind("<Button-1>", self.prevent_resize)
        self.tree.bind("<B1-Motion>", self.prevent_resize)

    def refresh_inventory(self):
        """
        Limpia la tabla, obtiene los equipos del inventario aplicando
        los filtros de búsqueda, estado y marca/serie, y vuelve a llenar la tabla.
        """
        # Elimina todos los items existentes en el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtiene los términos de búsqueda y filtros actuales
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        status_filter = self.status_filter.get() if hasattr(self, 'status_filter') and self.status_filter.get() != "Todos" else ""
        brand_serial_filter = self.brand_serial_entry.get() if hasattr(self, 'brand_serial_entry') else ""
        
        # Llama al modelo para obtener la lista de equipos filtrada
        equipment = self.inventory_model.get_all_equipment(search_term, status_filter, brand_serial_filter)
        
        # Itera sobre los equipos obtenidos y los inserta en la tabla.
        for i, equipment_data in enumerate(equipment):
            # Simplificar la visualización sin iconos excesivos para mejor legibilidad
            codigo_display = str(equipment_data[0])
            marca_serie_display = equipment_data[1]
            responsable_display = equipment_data[2]
            ubicacion_display = equipment_data[3]
            descripcion_display = equipment_data[4]
            contenido_display = equipment_data[5]
            estado_display = equipment_data[6]
            
            # Inserta una nueva fila en el Treeview.
            item_id = self.tree.insert("", "end", iid=str(equipment_data[0]), values=(
                codigo_display,
                marca_serie_display,
                responsable_display,
                ubicacion_display,
                descripcion_display,
                contenido_display,
                estado_display
            ))
            
            # Alternar colores de fila para mejor legibilidad
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
            
            # Colorear el estado
            if estado_display == "EN USO":
                self.tree.item(item_id, tags=('in_use',))
            elif estado_display == "DAÑADO":
                self.tree.item(item_id, tags=('damaged',))
            elif estado_display == "DISPONIBLE":
                self.tree.item(item_id, tags=('available',))
        
        # Configurar el color de las filas alternas y estados según el tema actual
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
            self.tree.tag_configure('in_use', foreground='#f59e0b')
            self.tree.tag_configure('damaged', foreground='#ef4444')
            self.tree.tag_configure('available', foreground='#22c55e')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
            self.tree.tag_configure('in_use', foreground='#d97706')
            self.tree.tag_configure('damaged', foreground='#dc2626')
            self.tree.tag_configure('available', foreground='#16a34a')
        
        # Crea el frame y los botones de acciones (Editar/Eliminar) si no existen.
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                 text="Editar Seleccionado",
                                                 command=self.edit_selected_equipment, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_equipment, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Vincula el evento de selección en la tabla a la función on_equipment_select.
            self.tree.bind("<<TreeviewSelect>>", self.on_equipment_select)
        
        # Llama a on_equipment_select para establecer el estado inicial de los botones.
        self.on_equipment_select()

    def on_equipment_select(self, event=None):
        """
        Manejador de evento para la selección de un equipo en la tabla.
        Habilita o deshabilita los botones de "Editar" y "Eliminar" según
        si hay un equipo seleccionado o no.
        """
        if hasattr(self, 'edit_selected_btn'): # Check if buttons exist
            # Obtiene el identificador del item seleccionado.
            selected_item_iid = self.tree.focus() 
            if selected_item_iid:
                # Si hay selección, habilita los botones.
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                # Si no hay selección, deshabilita los botones.
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_equipment_data(self):
        """
        Obtiene los datos del equipo actualmente seleccionado en la tabla.
        Retorna una tupla con los datos del equipo o None si no hay selección.
        """
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un equipo de la tabla.", parent=self)
            return None
        
        # Obtiene los valores de las columnas del item seleccionado.
        tree_values = self.tree.item(selected_item_iid, "values")
        # Los valores ahora están limpios, sin necesidad de remover iconos
        codigo = tree_values[0]
        marca_serie = tree_values[1]
        responsable = tree_values[2]
        ubicacion = tree_values[3]
        descripcion = tree_values[4]
        contenido = tree_values[5]
        estado = tree_values[6]
        
        return (codigo, marca_serie, responsable, ubicacion, descripcion, contenido, estado)

    def edit_selected_equipment(self):
        """
        Abre un diálogo para editar la información del equipo seleccionado.
        Si la edición es exitosa, actualiza la base de datos y refresca la tabla.
        """
        equipment_display_data = self.get_selected_equipment_data()
        if equipment_display_data:
            # Crea y muestra el diálogo de edición.
            dialog = EquipmentDialog(self, "Editar Equipo", equipment_data_for_dialog=equipment_display_data, inventory_model=self.inventory_model)
            # Si el diálogo se cerró guardando cambios...
            if dialog.result: 
                original_codigo, marca_serie, documento_funcionario, nombre_funcionario, descripcion, contenido, estado, sede_id, new_codigo = dialog.result
                # Llama al modelo para actualizar el equipo.
                self.inventory_model.update_equipment(original_codigo, marca_serie, documento_funcionario, nombre_funcionario, 
                                                    descripcion, contenido, estado, sede_id, new_codigo=new_codigo)
                # Refresca la tabla para mostrar los cambios.
                self.refresh_inventory()

    def delete_selected_equipment(self):
        """
        Elimina el equipo seleccionado de la base de datos, previa confirmación.
        """
        equipment_display_data = self.get_selected_equipment_data()
        if equipment_display_data:
            codigo_to_delete = equipment_display_data[0]
            descripcion_to_delete = equipment_display_data[4]
            # Muestra un cuadro de diálogo de confirmación.
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el equipo {descripcion_to_delete} (Cód: {codigo_to_delete})?", parent=self):
                # Llama al modelo para eliminar el equipo.
                self.inventory_model.delete_equipment(codigo_to_delete)
                # Refresca la tabla.
                self.refresh_inventory()
    
    def on_search(self, event=None): 
        """
        Se ejecuta cada vez que el usuario escribe en el campo de búsqueda.
        Llama a refresh_inventory para filtrar los resultados.
        """
        self.refresh_inventory()
    
    def on_filter_change(self, value=None): 
        """
        Se ejecuta cuando el usuario cambia el valor del filtro de estado.
        Llama a refresh_inventory para aplicar el nuevo filtro.
        """
        self.refresh_inventory()
    
    def add_equipment_dialog(self):
        """
        Abre un diálogo para agregar un nuevo equipo.
        Si se guarda el nuevo equipo, lo agrega a la base de datos y refresca la tabla.
        """
        dialog = EquipmentDialog(self, "Agregar Equipo", inventory_model=self.inventory_model)
        # Si el diálogo se cerró guardando...
        if dialog.result:
            codigo, marca_serie, documento_funcionario, nombre_funcionario, descripcion, contenido, estado, sede_id = dialog.result
            # Llama al modelo para agregar el nuevo equipo.
            self.inventory_model.add_equipment(codigo, marca_serie, documento_funcionario, nombre_funcionario, 
                                             descripcion, contenido, estado, sede_id)
            # Refresca la tabla para mostrar el nuevo registro.
            self.refresh_inventory()
    
    # --- MODIFICADO: Simplificar el método de cambio de tema ---
    def on_theme_change(self, event=None):
        """
        Actualiza la vista cuando cambia el tema. Los estilos ya fueron 
        actualizados globalmente por MainWindow.
        """
        if hasattr(self, 'tree'):
            # Solo necesitamos refrescar la lista de equipos para que 
            # los nuevos colores de las filas alternas se apliquen.
            # Los estilos base del Treeview se actualizan automáticamente.
            self.refresh_inventory()
            self.update_idletasks()

class EquipmentDialog(ctk.CTkToplevel):
    """
    Clase para la ventana de diálogo (popup) que se usa tanto para agregar
    como para editar equipos.
    """
    def __init__(self, parent, title, equipment_data_for_dialog=None, inventory_model=None):
        """
        Constructor for the equipment dialog.
        :param parent: The parent window.
        :param title: The title of the dialog window.
        :param equipment_data_for_dialog: Equipment data if editing, None if adding.
        :param inventory_model: The instance of the inventory data model.
        """
        super().__init__(parent)
        self.title(title)
        # --- MODIFIED: Increased height for the new textbox ---
        self.geometry("800x550") 
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.result = None
        self.inventory_model = inventory_model 
        self.editing = equipment_data_for_dialog is not None
        self.original_equipment_code = equipment_data_for_dialog[0] if self.editing else None
        
        # This will hold the status if it's determined automatically (add mode, or 'IN USE' in edit mode)
        self.fixed_status = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Field definitions ---
        ctk.CTkLabel(main_frame, text="Código:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Marca/Serie:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.marca_serie_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.marca_serie_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Documento Funcionario:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.documento_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.documento_entry.grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre Funcionario:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.nombre_funcionario_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_funcionario_entry.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Descripción:", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=8, sticky="w")
        self.descripcion_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.descripcion_entry.grid(row=4, column=1, padx=5, pady=8, sticky="ew")
        
        # --- MODIFIED: Changed "Contenido" from Entry to Textbox for long text ---
        ctk.CTkLabel(main_frame, text="Contenido:", font=get_font("normal")).grid(row=5, column=0, padx=5, pady=8, sticky="nw")
        self.contenido_textbox = ctk.CTkTextbox(main_frame, font=get_font("normal"), height=120, wrap="word")
        self.contenido_textbox.grid(row=5, column=1, padx=5, pady=8, sticky="ew")
        
        # --- MODIFIED: Conditional logic for the "Estado" field ---
        ctk.CTkLabel(main_frame, text="Estado:", font=get_font("normal")).grid(row=6, column=0, padx=5, pady=8, sticky="w")
        if self.editing:
            current_status = equipment_data_for_dialog[6]
            if current_status == "EN USO":
                # If editing and item is on loan, show a non-editable field
                self.estado_widget = ctk.CTkEntry(main_frame, font=get_font("normal"))
                self.estado_widget.insert(0, "EN USO (No editable por préstamo activo)")
                self.estado_widget.configure(state="disabled")
                self.fixed_status = "EN USO"
            else:
                # If not on loan, allow changing between DISPONIBLE and DAÑADO
                self.estado_widget = ctk.CTkComboBox(main_frame,
                                                     values=["DISPONIBLE", "DAÑADO"],
                                                     font=get_font("normal"),
                                                     state="readonly")
                self.estado_widget.set(current_status)
        else:
            # If adding a new item, status is automatically "DISPONIBLE" and not editable
            self.estado_widget = ctk.CTkEntry(main_frame, font=get_font("normal"))
            self.estado_widget.insert(0, "DISPONIBLE (Automático al crear)")
            self.estado_widget.configure(state="disabled")
            self.fixed_status = "DISPONIBLE"
        self.estado_widget.grid(row=6, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Sede:", font=get_font("normal")).grid(row=7, column=0, padx=5, pady=8, sticky="w")
        self.sedes_data = self.inventory_model.get_sedes()
        sede_names = ["Seleccione una sede..."] + [s[1] for s in self.sedes_data]
        self.sede_combo = ctk.CTkComboBox(main_frame, 
                                        values=sede_names,
                                        font=get_font("normal"),
                                        state="readonly")
        self.sede_combo.grid(row=7, column=1, padx=5, pady=8, sticky="ew")
        self.sede_combo.set(sede_names[0])

        main_frame.grid_columnconfigure(1, weight=1)

        # Populate fields if in edit mode
        if self.editing:
            self.codigo_entry.insert(0, str(equipment_data_for_dialog[0]))
            self.marca_serie_entry.insert(0, equipment_data_for_dialog[1])
            responsable_parts = equipment_data_for_dialog[2].split(' (')
            if len(responsable_parts) == 2:
                nombre = responsable_parts[0]
                documento = responsable_parts[1].rstrip(')')
                self.nombre_funcionario_entry.insert(0, nombre)
                self.documento_entry.insert(0, documento)
            self.descripcion_entry.insert(0, equipment_data_for_dialog[4])
            # Use the new textbox for content
            self.contenido_textbox.insert("0.0", equipment_data_for_dialog[5])
            # Status is handled by the logic above
            if equipment_data_for_dialog[3] != 'N/A':
                self.sede_combo.set(equipment_data_for_dialog[3])
        
        # Action buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=8, column=0, columnspan=2, pady=(20,0), sticky="ew")
        
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self._center_dialog()
        self.codigo_entry.focus_set()
        self.wait_window(self)

    def _center_dialog(self): # This method might not be strictly necessary if parent centering works well
        """
        Método auxiliar para centrar el diálogo en relación a la ventana principal.
        """
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
        """
        Runs when the "Guardar" button is pressed.
        Validates the input data, packages it in self.result, and closes the dialog.
        """
        codigo = self.codigo_entry.get().strip()
        marca_serie = self.marca_serie_entry.get().strip()
        documento_funcionario = self.documento_entry.get().strip()
        nombre_funcionario = self.nombre_funcionario_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        # --- MODIFIED: Get content from the textbox ---
        contenido = self.contenido_textbox.get("0.0", "end-1c").strip()
        
        # --- MODIFIED: Get status based on the dialog's logic ---
        if self.fixed_status:
            # Status was determined automatically (Add mode or "IN USE" on Edit)
            estado = self.fixed_status
        else:
            # Status was selectable from the ComboBox
            estado = self.estado_widget.get()

        sede_nombre = self.sede_combo.get()

        if not codigo or not descripcion:
            messagebox.showerror("Error de Validación", "Código y Descripción son obligatorios.", parent=self)
            return
        
        sede_id = None
        if sede_nombre != "Seleccione una sede...":
            for s_id, s_name in self.sedes_data:
                if s_name == sede_nombre:
                    sede_id = s_id
                    break
        
        if self.editing:
            new_codigo_val = codigo if codigo != self.original_equipment_code else self.original_equipment_code
            self.result = (self.original_equipment_code, marca_serie, documento_funcionario, nombre_funcionario,
                          descripcion, contenido, estado, sede_id, new_codigo_val)
        else:
            self.result = (codigo, marca_serie, documento_funcionario, nombre_funcionario,
                          descripcion, contenido, estado, sede_id)
        
        self.destroy()
    
    def cancel(self):
        """
        Se ejecuta al presionar el botón "Cancelar".
        Establece el resultado como None y cierra el diálogo.
        """
        self.result = None
        self.destroy()