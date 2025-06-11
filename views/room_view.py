import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import RoomModel
from utils.font_config import get_font
from utils.validators import *

class RoomView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.room_model = RoomModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False)
        self.pack(padx=15, pady=15)

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        self.setup_ui()
        self.refresh_rooms()
    
    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(self, text="Gestión de Salas", font=get_font("title", "bold"))
        title.pack(pady=(0, 20))
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0)
        
        # Search entry
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código o nombre de sala...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Add room button
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Sala", command=self.add_room_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=2, padx=(10,10), pady=10)
        
        search_frame.grid_columnconfigure(1, weight=3)
        
        # Rooms table using ttk.Treeview
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
                               show="headings",
                               style="Modern.Treeview")

        # Configurar headers con texto visible y estilos modernos
        self.tree.heading("Codigo", text="📋 Código", anchor="w")
        self.tree.heading("Nombre", text="🏢 Nombre", anchor="w")
        self.tree.heading("Estado", text="🔍 Estado", anchor="w")

        # Configurar columnas
        self.tree.column("Codigo", width=120, minwidth=100, stretch=False, anchor="w")
        self.tree.column("Nombre", width=300, minwidth=200, stretch=True, anchor="w")
        self.tree.column("Estado", width=100, minwidth=100, stretch=False, anchor="w")

        # Pack del Treeview con padding para el efecto de borde redondeado
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar moderna
        scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                   command=self.tree.yview,
                                   corner_radius=8,
                                   width=12)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0,5))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def refresh_rooms(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        rooms = self.room_model.get_all_rooms_with_status()
        
        for i, room_data in enumerate(rooms):
            codigo_display = str(room_data[0])
            nombre_display = room_data[1]
            estado_display = room_data[2]
            
            item_id = self.tree.insert("", "end", iid=str(room_data[0]), values=(
                codigo_display,
                nombre_display,
                estado_display
            ))
            
            # Alternar colores de fila para mejor legibilidad
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
            
            # Color según estado
            if estado_display == "Ocupada":
                self.tree.item(item_id, tags=('ocupada',))
            else:
                self.tree.item(item_id, tags=('disponible',))
        
        # Configurar tags para filas alternadas y estados
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
            self.tree.tag_configure('ocupada', foreground='#ff9800')
            self.tree.tag_configure('disponible', foreground='#4caf50')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
            self.tree.tag_configure('ocupada', foreground='#f57c00')
            self.tree.tag_configure('disponible', foreground='#2e7d32')
        
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                 text="Editar Seleccionado",
                                                 command=self.edit_selected_room, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_room, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Bind selection event after buttons are created
            self.tree.bind("<<TreeviewSelect>>", self.on_room_select)
        
        self.on_room_select()

    def on_room_select(self, event=None):
        if hasattr(self, 'edit_selected_btn'):
            selected_item_iid = self.tree.focus()
            if selected_item_iid:
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_room_data(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una sala de la tabla.", parent=self)
            return None
        
        tree_values = self.tree.item(selected_item_iid, "values")
        codigo = tree_values[0]
        nombre = tree_values[1]
        estado = tree_values[2]
        
        return (codigo, nombre, estado)

    def edit_selected_room(self):
        room_data = self.get_selected_room_data()
        if room_data:
            dialog = RoomDialog(self, "Editar Sala", room_data=room_data, room_model=self.room_model)
            if dialog.result:
                self.refresh_rooms()

    def delete_selected_room(self):
        room_data = self.get_selected_room_data()
        if room_data:
            codigo_to_delete = room_data[0]
            nombre_to_delete = room_data[1]
            if messagebox.askyesno("Confirmar Eliminación", 
                                  f"¿Está seguro de eliminar la sala {nombre_to_delete} (Cód: {codigo_to_delete})?", 
                                  parent=self):
                self.room_model.delete_room(codigo_to_delete)
                self.refresh_rooms()
    
    def on_search(self, event=None):
        self.refresh_rooms()
    
    def add_room_dialog(self):
        dialog = RoomDialog(self, "Agregar Sala", room_model=self.room_model)
        if dialog.result:
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
            else:
                tree_bg = "#ffffff"
                text_color = "#2b2b2b"
                selected_color = "#e3f2fd"
                heading_bg = "#E5E7EB"
                alternate_bg = "#f8f9fa"
            
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
            
            self.tree.tag_configure('alternate', background=alternate_bg)
            self.tree.tag_configure('ocupada', foreground='#ff9800' if current_mode == "Dark" else '#f57c00')
            self.tree.tag_configure('disponible', foreground='#4caf50' if current_mode == "Dark" else '#2e7d32')
            
            self.refresh_rooms()
            
            self.tree.update_idletasks()
            self.update_idletasks()

class RoomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, room_data=None, room_model=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.result = None
        self.room_model = room_model
        self.editing = room_data is not None
        self.original_code = room_data[0] if room_data else None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Código:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        main_frame.grid_columnconfigure(1, weight=1)

        if room_data:
            self.codigo_entry.insert(0, str(room_data[0]))
            self.nombre_entry.insert(0, room_data[1])
        
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

        success = False
        if self.editing:
            if self.original_code == codigo:
                success = self.room_model.update_room(self.original_code, nombre)
            else:
                success = self.room_model.update_room(self.original_code, nombre, new_codigo=codigo)
            action = "actualizada"
        else:
            success = self.room_model.add_room(codigo, nombre)
            action = "agregada"

        if success:
            messagebox.showinfo("Éxito", f"Sala {action} correctamente.", parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error de Base de Datos", 
                               f"No se pudo {'actualizar' if self.editing else 'agregar'} la sala. El código podría ya existir.", 
                               parent=self)
    
    def cancel(self):
        self.result = None
        self.destroy() 