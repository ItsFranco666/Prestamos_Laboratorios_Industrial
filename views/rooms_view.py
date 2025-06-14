import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import RoomModel
from utils.font_config import get_font

class RoomsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.room_model = RoomModel()
        
        self.pack_propagate(False)
        self.pack(padx=15, pady=15, fill="both", expand=True)

        self.bind("<<ThemeChanged>>", self.on_theme_change)

        # Orden correcto de inicialización
        self.setup_ui()
        self.refresh_rooms()
    
    def setup_ui(self):
        title = ctk.CTkLabel(self, text="Gestión de Salas", font=get_font("title", "bold"))
        title.pack(pady=(0, 20))
        
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0)
        
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código o nombre de la sala...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Sala", command=self.add_room_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=2, padx=(10,10), pady=10)
        
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Llamada para crear la tabla
        self.create_rooms_treeview_table()
    
    def create_rooms_treeview_table(self):
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
                          font=get_font("normal", "bold"),
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
                          font=get_font("normal", "bold"),
                          padding=(10, 8))
            
            style.map("Modern.Treeview.Heading", 
                     background=[('active', "#CFD8DC")])

        # Container para el Treeview con bordes redondeados internos
        table_container_frame = ctk.CTkFrame(table_main_container, 
                                           corner_radius=15,
                                           fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Crear el Treeview con estilo moderno
        self.tree = ttk.Treeview(table_container_frame,
                               columns=("Codigo", "Nombre", "Estado"),
                               show="tree headings",
                               style="Modern.Treeview")

        # Configurar headers con texto visible y estilos modernos
        self.tree.heading("Codigo", text="📋 Código Interno", anchor="w")
        self.tree.heading("Nombre", text="🏢 Nombre", anchor="w")
        self.tree.heading("Estado", text="🚦 Estado", anchor="center")

        # Configurar columnas
        self.tree.column("#0", width=0, stretch=False)  # Ocultar columna del tree
        self.tree.column("Codigo", width=150, minwidth=120, stretch=False, anchor="w")
        self.tree.column("Nombre", width=400, minwidth=250, stretch=True, anchor="w")
        self.tree.column("Estado", width=150, minwidth=120, stretch=False, anchor="center")

        # Pack del Treeview con padding para el efecto de borde redondeado
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar moderna
        scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                   command=self.tree.yview,
                                   corner_radius=8,
                                   width=12)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0,5))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def update_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        
        new_row_height = 35
        current_mode = ctk.get_appearance_mode()
        
        if current_mode == "Dark":
            tree_bg, text_color, selected_color, heading_bg, alternate_bg = ("#2b2b2b", "#ffffff", "#404040", "#4B5563", "#323232")
            active_heading_bg = "#525E75"
        else: # Light mode
            tree_bg, text_color, selected_color, heading_bg, alternate_bg = ("#ffffff", "#2b2b2b", "#e3f2fd", "#E5E7EB", "#f8f9fa")
            active_heading_bg = "#CFD8DC"
        
        # Estilo general de la tabla
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
        
        # Estilo de los encabezados
        style.configure("Modern.Treeview.Heading",
                      background=heading_bg,
                      foreground=text_color,
                      borderwidth=0,
                      relief="flat",
                      font=get_font("normal", "bold"),
                      padding=(10, 8))
        
        style.map("Modern.Treeview.Heading", background=[('active', active_heading_bg)])
        
        # Estilos para las filas (tags)
        if hasattr(self, 'tree'):
            self.tree.tag_configure('alternate', background=alternate_bg)
            self.tree.tag_configure('Disponible', foreground="#22c55e") # Green
            self.tree.tag_configure('Ocupada', foreground="#ef4444") # Red

    def refresh_rooms(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener datos y filtrar
        search_term = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        all_rooms = self.room_model.get_all_rooms_with_status()
        
        rooms_to_display = [
            room for room in all_rooms 
            if not search_term or search_term in str(room[1]).lower() or search_term in room[2].lower()
        ]
        
        # Poblar tabla con datos
        for i, room_data in enumerate(rooms_to_display):
            id_sala, codigo, nombre, estado = room_data
            
            # Asignar tags para colores de fila alternos
            tags = []
            if i % 2 == 1:
                tags.append('alternate')
            
            # Crear un tag específico para el estado
            estado_tag = f'status_{estado}'
            tags.append(estado_tag)

            self.tree.insert("", "end", iid=str(id_sala), values=(codigo, nombre, estado), tags=tags)
        
        # Configurar tags para filas alternadas y estados
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
            
        # Configurar colores solo para el estado
        self.tree.tag_configure('status_Disponible', foreground="#22c55e")  # Verde
        self.tree.tag_configure('status_Ocupada', foreground="#ef4444")    # Rojo
        
        # Configurar botones de acción si no existen
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Editar Seleccionada", command=self.edit_selected_room, state="disabled", font=get_font("normal"), corner_radius=8, height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Eliminar Seleccionada", command=self.delete_selected_room, state="disabled", fg_color=("#ef4444", "#dc2626"), hover_color=("#dc2626", "#b91c1c"), font=get_font("normal"), corner_radius=8, height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            self.tree.bind("<<TreeviewSelect>>", self.on_room_select)
        
        self.on_room_select()

    def on_room_select(self, event=None):
        if hasattr(self, 'edit_selected_btn'):
            selected_item_iid = self.tree.focus() 
            is_selected = bool(selected_item_iid)
            self.edit_selected_btn.configure(state="normal" if is_selected else "disabled")
            self.delete_selected_btn.configure(state="normal" if is_selected else "disabled")

    def get_selected_room_data(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una sala de la tabla.", parent=self)
            return None
        
        tree_values = self.tree.item(selected_item_iid, "values")
        return (tree_values[0], tree_values[1])  # Retorna (codigo_interno, nombre)

    def edit_selected_room(self):
        room_data = self.get_selected_room_data()
        if room_data:
            dialog = RoomDialog(self, "Editar Sala", room_data_for_dialog=room_data)
            if dialog.result: 
                original_codigo, nombre, new_codigo = dialog.result
                self.room_model.update_room(original_codigo, nombre, new_codigo=new_codigo)
                self.refresh_rooms()

    def delete_selected_room(self):
        room_data = self.get_selected_room_data()
        if room_data:
            codigo, nombre = room_data
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar la sala {nombre} (Cód: {codigo})?", parent=self):
                self.room_model.delete_room(codigo)
                self.refresh_rooms()
    
    def on_search(self, event=None): 
        self.refresh_rooms()
    
    def add_room_dialog(self):
        dialog = RoomDialog(self, "Agregar Sala")
        if dialog.result:
            codigo, nombre = dialog.result
            self.room_model.add_room(codigo, nombre)
            self.refresh_rooms()
    
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
            
            # Configurar tags para filas alternadas y estados
            self.tree.tag_configure('alternate', background=alternate_bg)
            self.tree.tag_configure('status_Disponible', foreground="#22c55e")  # Verde
            self.tree.tag_configure('status_Ocupada', foreground="#ef4444")    # Rojo
            
            # Re-populating the tree is crucial for ttk styles to apply to items
            self.refresh_rooms()
            
            # update_idletasks can help ensure Tkinter processes pending drawing tasks
            self.tree.update_idletasks()
            self.update_idletasks()

# El diálogo no necesita cambios, pero lo incluyo por completitud
class RoomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, room_data_for_dialog=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250") 
        self.transient(parent)
        self.grab_set()
        self.lift() 

        self.result = None
        self.editing = room_data_for_dialog is not None
        self.original_room_code = room_data_for_dialog[0] if self.editing else None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Código Interno:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre de la Sala:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        main_frame.grid_columnconfigure(1, weight=1)

        if self.editing:
            self.codigo_entry.insert(0, str(room_data_for_dialog[0]))
            self.nombre_entry.insert(0, room_data_for_dialog[1])
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20,0), sticky="ew")
        
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)

        self.codigo_entry.focus_set()
        self.wait_window(self) 

    def save(self):
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()

        if not codigo or not nombre:
            messagebox.showerror("Error de Validación", "Código y Nombre son obligatorios.", parent=self)
            return
            
        if self.editing:
            self.result = (self.original_room_code, nombre, codigo)
        else:
            self.result = (codigo, nombre)
        
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()