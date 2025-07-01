import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import EquiposModel, RoomModel
from utils.font_config import get_font
from utils.validators import *

class EquiposView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.equipos_model = EquiposModel()
        self.room_model = RoomModel() # To get rooms for the filter
        
        self.pack_propagate(False)
        self.pack(padx=15, pady=15, fill="both", expand=True)

        self.bind("<<ThemeChanged>>", self.on_theme_change)

        self.setup_ui()
        self.refresh_equipos()
    
    def prevent_resize(self, event):
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        title = ctk.CTkLabel(self, text="Gestión de Equipos de Sala", font=get_font("title", "bold"))
        title.pack(pady=(10, 20))
        
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0)
        
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código o descripción...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Room Filter
        ctk.CTkLabel(search_frame, text="Sala:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.rooms_data = self.room_model.get_all_rooms_with_id_for_dropdown()
        room_names = ["Todas"] + [r[1] for r in self.rooms_data]
        self.room_filter = ctk.CTkComboBox(search_frame, values=room_names, font=get_font("normal"), command=self.on_filter_change)
        self.room_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.room_filter.set("Todas")

        # Status Filter
        ctk.CTkLabel(search_frame, text="Estado:", font=get_font("normal")).grid(row=0, column=4, padx=(10,5), pady=10, sticky="w")
        self.status_filter = ctk.CTkComboBox(search_frame, values=["Todos", "Activo", "Inactivo"], font=get_font("normal"), command=self.on_filter_change)
        self.status_filter.grid(row=0, column=5, padx=5, pady=10, sticky="ew")
        self.status_filter.set("Todos")
        
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Equipo", command=self.add_equipo_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=6, padx=(10,10), pady=10)
        
        search_frame.grid_columnconfigure(1, weight=2)
        search_frame.grid_columnconfigure(3, weight=1)
        search_frame.grid_columnconfigure(5, weight=1)
        
        self.create_equipos_treeview_table()
    
    def create_equipos_treeview_table(self):
        table_main_container = ctk.CTkFrame(self, corner_radius=8, border_width=1, border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0,10), padx=0)
        table_container_frame = ctk.CTkFrame(table_main_container, corner_radius=15, fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)
        table_container_frame.grid_rowconfigure(0, weight=1)
        table_container_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_container_frame,
                               columns=("Codigo", "Sala", "NumEquipo", "Descripcion", "Estado", "Observaciones"),
                               show="headings", style="Modern.Treeview")

        self.tree.heading("Codigo", text="🔑 Código", anchor="w")
        self.tree.heading("Sala", text="🚪 Sala", anchor="w")
        self.tree.heading("NumEquipo", text="#️⃣ Equipo No.", anchor="w")
        self.tree.heading("Descripcion", text="📝 Descripción", anchor="w")
        self.tree.heading("Estado", text="📊 Estado", anchor="w")
        self.tree.heading("Observaciones", text="📋 Observaciones", anchor="w")

        self.tree.column("Codigo", width=120, stretch=False, anchor="w")
        self.tree.column("Sala", width=180, stretch=False, anchor="w")
        self.tree.column("NumEquipo", width=100, stretch=False, anchor="center")
        self.tree.column("Descripcion", width=300, stretch=True, anchor="w")
        self.tree.column("Estado", width=120, stretch=False, anchor="w")
        self.tree.column("Observaciones", width=350, stretch=True, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        v_scrollbar = ctk.CTkScrollbar(table_container_frame, command=self.tree.yview, corner_radius=8, width=12)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = ctk.CTkScrollbar(table_container_frame, command=self.tree.xview, orientation="horizontal", corner_radius=8, height=12)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.bind("<Button-1>", self.prevent_resize)
        self.tree.bind("<B1-Motion>", self.prevent_resize)

    def refresh_equipos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get()
        
        selected_room_name = self.room_filter.get()
        sala_filter_id = None
        if selected_room_name != "Todas":
            for r_id, r_name in self.rooms_data:
                if r_name == selected_room_name:
                    sala_filter_id = r_id
                    break
        
        status_map = {"Activo": 1, "Inactivo": 0, "Todos": -1}
        status_filter = status_map.get(self.status_filter.get())

        equipos_list = self.equipos_model.get_all_equipos(search_term, sala_filter_id, status_filter)
        
        for i, equipo_data in enumerate(equipos_list):
            estado_display = "Activo" if equipo_data[4] == 1 else "Inactivo"
            
            item_id = self.tree.insert("", "end", iid=str(equipo_data[0]), values=(
                equipo_data[0], # Codigo
                equipo_data[1], # Sala
                equipo_data[2], # NumEquipo
                equipo_data[3], # Descripcion
                estado_display, # Estado
                equipo_data[5]  # Observaciones
            ))
            
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
            
            if estado_display == "Activo":
                self.tree.item(item_id, tags=('available',))
            else:
                self.tree.item(item_id, tags=('damaged',))
        
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
            self.tree.tag_configure('available', foreground='#22c55e')
            self.tree.tag_configure('damaged', foreground='#f59e0b')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
            self.tree.tag_configure('available', foreground='#16a34a')
            self.tree.tag_configure('damaged', foreground='#d97706')
        
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Editar Seleccionado", command=self.edit_selected_equipo, state="disabled", font=get_font("normal"), corner_radius=8, height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Eliminar Seleccionado", command=self.delete_selected_equipo, state="disabled", fg_color=("#ef4444", "#dc2626"), hover_color=("#dc2626", "#b91c1c"), font=get_font("normal"), corner_radius=8, height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            self.tree.bind("<<TreeviewSelect>>", self.on_equipo_select)
        
        self.on_equipo_select()

    def on_equipo_select(self, event=None):
        if hasattr(self, 'edit_selected_btn'):
            selected_item_iid = self.tree.focus() 
            if selected_item_iid:
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_equipo_data(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un equipo de la tabla.", parent=self)
            return None
        return self.equipos_model.get_equipo_by_code(selected_item_iid)

    def edit_selected_equipo(self):
        equipo_data = self.get_selected_equipo_data()
        if equipo_data:
            dialog = EquipoDialog(self, "Editar Equipo", equipo_data=equipo_data, equipos_model=self.equipos_model, room_model=self.room_model)
            if dialog.result: 
                original_codigo, sala_id, numero_equipo, descripcion, estado, observaciones, new_codigo = dialog.result
                self.equipos_model.update_equipo(original_codigo, sala_id, numero_equipo, descripcion, estado, observaciones, new_codigo=new_codigo)
                self.refresh_equipos()

    def delete_selected_equipo(self):
        equipo_data = self.get_selected_equipo_data()
        if equipo_data:
            codigo_to_delete = equipo_data[0]
            descripcion_to_delete = equipo_data[3]
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el equipo {descripcion_to_delete} (Cód: {codigo_to_delete})?", parent=self):
                self.equipos_model.delete_equipo(codigo_to_delete)
                self.refresh_equipos()
    
    def on_search(self, event=None): 
        self.refresh_equipos()
    
    def on_filter_change(self, value=None): 
        self.refresh_equipos()
    
    def add_equipo_dialog(self):
        dialog = EquipoDialog(self, "Agregar Equipo", equipos_model=self.equipos_model, room_model=self.room_model)
        if dialog.result:
            codigo, sala_id, numero_equipo, descripcion, estado, observaciones = dialog.result
            self.equipos_model.add_equipo(codigo, sala_id, numero_equipo, descripcion, estado, observaciones)
            self.refresh_equipos()
    
    def on_theme_change(self, event=None):
        if hasattr(self, 'tree'):
            self.refresh_equipos()
            self.update_idletasks()

class EquipoDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, equipo_data=None, equipos_model=None, room_model=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x480")
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.result = None
        self.equipos_model = equipos_model 
        self.room_model = room_model
        self.editing = equipo_data is not None
        self.original_codigo = equipo_data[0] if self.editing else None
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Código:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Sala:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.rooms_data = self.room_model.get_all_rooms_with_id_for_dropdown()
        room_names = ["Seleccione una sala..."] + [s[1] for s in self.rooms_data]
        self.sala_combo = ctk.CTkComboBox(main_frame, values=room_names, font=get_font("normal"), state="readonly")
        self.sala_combo.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        self.sala_combo.set(room_names[0])

        ctk.CTkLabel(main_frame, text="Número de Equipo:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.numero_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.numero_entry.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="Descripción:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.descripcion_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.descripcion_entry.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Estado:", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=8, sticky="w")
        self.estado_combo = ctk.CTkComboBox(main_frame, values=["Activo", "Inactivo"], font=get_font("normal"), state="readonly")
        self.estado_combo.grid(row=4, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="Observaciones:", font=get_font("normal")).grid(row=5, column=0, padx=5, pady=8, sticky="nw")
        self.observaciones_textbox = ctk.CTkTextbox(main_frame, font=get_font("normal"), height=100, wrap="word")
        self.observaciones_textbox.grid(row=5, column=1, padx=5, pady=8, sticky="ew")
        
        main_frame.grid_columnconfigure(1, weight=1)

        if self.editing:
            self.codigo_entry.insert(0, str(equipo_data[0]))
            
            # Set sala
            sala_id_to_select = equipo_data[1]
            for r_id, r_name in self.rooms_data:
                if r_id == sala_id_to_select:
                    self.sala_combo.set(r_name)
                    break
            
            self.numero_entry.insert(0, str(equipo_data[2]))
            self.descripcion_entry.insert(0, equipo_data[3])
            self.estado_combo.set("Activo" if equipo_data[4] == 1 else "Inactivo")
            self.observaciones_textbox.insert("0.0", equipo_data[5] or "")
        else:
             self.estado_combo.set("Activo")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20,0), sticky="ew")
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self.update_idletasks()
        self.wait_window(self)

    def save(self):
        codigo = self.codigo_entry.get().strip()
        sala_nombre = self.sala_combo.get()
        numero_str = self.numero_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        estado_str = self.estado_combo.get()
        observaciones = self.observaciones_textbox.get("0.0", "end-1c").strip()

        if not codigo or not descripcion or not numero_str or sala_nombre == "Seleccione una sala...":
            messagebox.showerror("Error de Validación", "Código, Sala, Número y Descripción son obligatorios.", parent=self)
            return

        try:
            numero_equipo = int(numero_str)
        except ValueError:
            messagebox.showerror("Error de Validación", "El número de equipo debe ser un entero.", parent=self)
            return
        
        sala_id = None
        for s_id, s_name in self.rooms_data:
            if s_name == sala_nombre:
                sala_id = s_id
                break
        
        estado = 1 if estado_str == "Activo" else 0
        
        if self.editing:
            new_codigo_val = codigo if codigo != self.original_codigo else self.original_codigo
            self.result = (self.original_codigo, sala_id, numero_equipo, descripcion, estado, observaciones, new_codigo_val)
        else:
            self.result = (codigo, sala_id, numero_equipo, descripcion, estado, observaciones)
        
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()