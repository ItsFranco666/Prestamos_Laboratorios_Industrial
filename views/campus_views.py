import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import SedesModel
from utils.font_config import get_font
from utils.validators import *

class SedesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.sedes_model = SedesModel()
        
        self.pack_propagate(False)
        self.pack(padx=15, pady=15, fill="both", expand=True)

        self.bind("<<ThemeChanged>>", self.on_theme_change)

        self.setup_ui()
        self.refresh_sedes()
    
    def prevent_resize(self, event):
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        title = ctk.CTkLabel(self, text="Gestión de Sedes", font=get_font("title", "bold"))
        title.pack(pady=(10, 20))
        
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0)
        
        ctk.CTkLabel(search_frame, text="Buscar por nombre:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Nombre de la sede...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Sede", command=self.add_sede_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=2, padx=(10,10), pady=10)
        
        search_frame.grid_columnconfigure(1, weight=1)
        
        self.create_sedes_treeview_table()
    
    def create_sedes_treeview_table(self):
        table_main_container = ctk.CTkFrame(self, corner_radius=8, border_width=1, border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0,10), padx=0)
        table_container_frame = ctk.CTkFrame(table_main_container, corner_radius=15, fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)
        table_container_frame.grid_rowconfigure(0, weight=1)
        table_container_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_container_frame,
                               columns=("ID", "Nombre"),
                               show="headings", style="Modern.Treeview")

        self.tree.heading("ID", text="🆔 ID", anchor="w")
        self.tree.heading("Nombre", text="🏷️ Nombre de la Sede", anchor="w")

        self.tree.column("ID", width=100, stretch=False, anchor="w")
        self.tree.column("Nombre", width=600, stretch=True, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        v_scrollbar = ctk.CTkScrollbar(table_container_frame, command=self.tree.yview, corner_radius=8, width=12)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        self.tree.bind("<Button-1>", self.prevent_resize)
        self.tree.bind("<B1-Motion>", self.prevent_resize)

    def refresh_sedes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get()
        sedes_list = self.sedes_model.get_all_sedes(search_term)
        
        for i, sede_data in enumerate(sedes_list):
            item_id = self.tree.insert("", "end", iid=str(sede_data[0]), values=(sede_data[0], sede_data[1]))
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
        
        current_mode = ctk.get_appearance_mode()
        self.tree.tag_configure('alternate', background=('#f8f9fa' if current_mode == "Light" else '#323232'))
        
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Editar Seleccionado", command=self.edit_selected_sede, state="disabled", font=get_font("normal"), corner_radius=8, height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, text="Eliminar Seleccionado", command=self.delete_selected_sede, state="disabled", fg_color=("#ef4444", "#dc2626"), hover_color=("#dc2626", "#b91c1c"), font=get_font("normal"), corner_radius=8, height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            self.tree.bind("<<TreeviewSelect>>", self.on_sede_select)
        
        self.on_sede_select()

    def on_sede_select(self, event=None):
        if hasattr(self, 'edit_selected_btn'):
            if self.tree.focus():
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_sede_data(self):
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una sede de la tabla.", parent=self)
            return None
        return self.tree.item(selected_item_iid, "values")

    def edit_selected_sede(self):
        sede_data = self.get_selected_sede_data()
        if sede_data:
            dialog = SedeDialog(self, "Editar Sede", sede_data=sede_data)
            if dialog.result: 
                sede_id, nombre = dialog.result
                self.sedes_model.update_sede(sede_id, nombre)
                self.refresh_sedes()

    def delete_selected_sede(self):
        sede_data = self.get_selected_sede_data()
        if sede_data:
            sede_id, nombre = sede_data
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar la sede '{nombre}' (ID: {sede_id})?\n\nNota: No se podrá eliminar si está asignada a elementos del inventario.", parent=self):
                if not self.sedes_model.delete_sede(sede_id):
                    messagebox.showerror("Error", f"No se pudo eliminar la sede '{nombre}'. Es posible que esté en uso.", parent=self)
                self.refresh_sedes()
    
    def on_search(self, event=None): 
        self.refresh_sedes()
    
    def add_sede_dialog(self):
        dialog = SedeDialog(self, "Agregar Sede")
        if dialog.result:
            _, nombre = dialog.result
            self.sedes_model.add_sede(nombre)
            self.refresh_sedes()
    
    def on_theme_change(self, event=None):
        if hasattr(self, 'tree'):
            self.refresh_sedes()
            self.update_idletasks()

class SedeDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, sede_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x150")
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.result = None
        self.editing = sede_data is not None
        self.sede_id = sede_data[0] if self.editing else None
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Nombre de la Sede:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        main_frame.grid_columnconfigure(1, weight=1)

        if self.editing:
            self.nombre_entry.insert(0, sede_data[1])

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, pady=(20,0), sticky="ew")
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self._center_dialog()
        self.update_idletasks()
        self.wait_window(self)
        
    def _center_dialog(self):
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
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showerror("Error de Validación", "El nombre es obligatorio.", parent=self)
            return
        
        self.result = (self.sede_id, nombre)
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()