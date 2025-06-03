# In university_management/views/room_management.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import RoomModel
from utils.font_config import get_font
from utils.validators import is_not_empty, is_integer

class RoomManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.room_model = RoomModel()
        self.parent_app = parent # To access main app methods if needed, e.g. for centering dialogs

        self.setup_ui()
        self.load_rooms()

    def setup_ui(self):
        self.pack(fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(self, text="Gestión de Salas", font=get_font("title", "bold"))
        title_label.pack(pady=(10, 20))

        # Action Frame (Add button)
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(fill="x", padx=20, pady=(0, 10))

        add_button = ctk.CTkButton(action_frame, text="Nueva Sala", command=self.open_add_room_dialog, font=get_font("normal"))
        add_button.pack(side="left")
        
        # Search (Optional - can be added later if needed)
        # self.search_entry = ctk.CTkEntry(action_frame, placeholder_text="Buscar sala...")
        # self.search_entry.pack(side="left", padx=10, expand=True, fill="x")
        # self.search_entry.bind("<KeyRelease>", self.filter_rooms)

        # Table Frame for Treeview
        table_container = ctk.CTkFrame(self)
        table_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Treeview Style
        style = ttk.Style()
        style.theme_use("default") # Use a base theme that allows configuration

        # Configure Treeview colors for dark/light mode (basic example)
        # These might need more fine-tuning based on the CustomTkinter theme
        style.configure("Treeview", 
                        background="#2e2e2e", 
                        foreground="white", 
                        fieldbackground="#2e2e2e", 
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#555555')])
        style.configure("Treeview.Heading", 
                        background="#565b5e", 
                        foreground="white", 
                        font=('Arial', 10, 'bold'),
                        borderwidth=0)
        style.map("Treeview.Heading",
            background=[('active', '#3c3c3c')])


        self.tree = ttk.Treeview(table_container, columns=("Codigo", "Nombre", "Estado", "Acciones"), show="headings", style="Treeview")
        self.tree.heading("Codigo", text="Código")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Acciones", text="Acciones")

        self.tree.column("Codigo", width=100, anchor="center")
        self.tree.column("Nombre", width=300)
        self.tree.column("Estado", width=100, anchor="center")
        self.tree.column("Acciones", width=150, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar for Treeview
        scrollbar = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind double click to edit
        self.tree.bind("<Double-1>", self.on_double_click_edit)


    def load_rooms(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rooms = self.room_model.get_all_rooms_with_status()
        for room in rooms:
            codigo, nombre, estado = room
            # For actions, we'll handle them via context menu or double click
            # Or add buttons directly if ttkbootstrap or similar is used.
            # For now, actions are implied by edit/delete buttons in dialogs or context menus.
            item_id = self.tree.insert("", "end", values=(codigo, nombre, estado, "Editar/Eliminar"))
            
            # Apply tag for coloring based on status
            if estado == "Ocupada":
                self.tree.item(item_id, tags=('ocupada',))
            else:
                self.tree.item(item_id, tags=('disponible',))
        
        self.tree.tag_configure('ocupada', foreground='orange')
        self.tree.tag_configure('disponible', foreground='lightgreen')


    def on_double_click_edit(self, event):
        item_id = self.tree.focus() # Get selected item
        if not item_id:
            return
        item_values = self.tree.item(item_id, "values")
        if item_values:
            room_code = item_values[0]
            self.open_edit_room_dialog(room_code)

    def open_add_room_dialog(self):
        dialog = RoomDialog(self, title="Agregar Nueva Sala", room_model=self.room_model, parent_app=self.parent_app)
        if dialog.result:
            self.load_rooms()

    def open_edit_room_dialog(self, room_code):
        room_data = self.room_model.get_room_by_code(room_code)
        if room_data:
            dialog = RoomDialog(self, title=f"Editar Sala {room_code}", room_model=self.room_model, room_data=room_data, edit_mode=True, parent_app=self.parent_app)
            if dialog.result:
                self.load_rooms()
        else:
            messagebox.showerror("Error", f"No se encontró la sala con código {room_code}.")

    # def filter_rooms(self, event=None): # Basic search example
    #     search_term = self.search_entry.get().lower()
    #     for item in self.tree.get_children():
    #         values = self.tree.item(item, 'values')
    #         if any(search_term in str(val).lower() for val in values[:2]): # Search in code or name
    #             # This approach requires re-inserting or showing/hiding.
    #             # Simpler to just reload with a filter in the model if performance is an issue.
    #             # For now, this is a client-side filter which is okay for small datasets.
    #             # A more robust way is to call self.room_model.get_filtered_rooms(search_term)
    #             # and then self.load_rooms() with the filtered data.
    #             pass # Placeholder for actual filtering logic or reload
    #     # For now, just reload all rooms and the user can visually scan
    #     self.load_rooms()


class RoomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, room_model, room_data=None, edit_mode=False, parent_app=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250")
        self.transient(parent) # Make dialog stay on top of parent
        self.grab_set()      # Modal behavior

        self.room_model = room_model
        self.edit_mode = edit_mode
        self.original_code = room_data[0] if room_data else None
        self.result = None
        
        # Center dialog relative to the main application window
        if parent_app:
            x = parent_app.winfo_x() + (parent_app.winfo_width() // 2) - (400 // 2)
            y = parent_app.winfo_y() + (parent_app.winfo_height() // 2) - (250 // 2)
            self.geometry(f"+{x}+{y}")


        # --- Widgets ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Código de Sala:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.code_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.code_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Nombre de Sala:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.name_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        main_frame.grid_columnconfigure(1, weight=1)

        if room_data:
            self.code_entry.insert(0, str(room_data[0]))
            self.name_entry.insert(0, room_data[1])
            if self.edit_mode: # Optionally disable code editing for existing rooms if PK change is complex
                 pass # self.code_entry.configure(state="disabled") # Or allow it

        # --- Buttons ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20,0))

        save_button = ctk.CTkButton(button_frame, text="Guardar", command=self.save_room, font=get_font("normal"))
        save_button.pack(side="left", padx=10)

        if self.edit_mode:
            delete_button = ctk.CTkButton(button_frame, text="Eliminar", command=self.delete_room, fg_color="red", font=get_font("normal"))
            delete_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, font=get_font("normal"))
        cancel_button.pack(side="right", padx=10)
        
        self.lift() # Ensure dialog is on top
        self.code_entry.focus_set()


    def save_room(self):
        code_str = self.code_entry.get()
        name = self.name_entry.get()

        if not is_not_empty(code_str) or not is_not_empty(name):
            messagebox.showerror("Error de Validación", "Código y Nombre no pueden estar vacíos.", parent=self)
            return
        if not is_integer(code_str):
            messagebox.showerror("Error de Validación", "El código debe ser un número entero.", parent=self)
            return
        
        code = int(code_str)

        success = False
        if self.edit_mode:
            if self.original_code == code: # PK not changed
                 success = self.room_model.update_room(self.original_code, name)
            else: # PK changed
                 success = self.room_model.update_room(self.original_code, name, new_codigo=code)
            action = "actualizada"
        else:
            success = self.room_model.add_room(code, name)
            action = "agregada"

        if success:
            messagebox.showinfo("Éxito", f"Sala {action} correctamente.", parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error de Base de Datos", f"No se pudo {'actualizar' if self.edit_mode else 'agregar'} la sala. El código podría ya existir o hubo otro error.", parent=self)

    def delete_room(self):
        if not self.edit_mode or not self.original_code:
            return

        if messagebox.askyesno("Confirmar Eliminación", 
                               f"¿Está seguro de que desea eliminar la sala {self.original_code} - {self.name_entry.get()}? Esta acción no se puede deshacer.", 
                               parent=self):
            try:
                self.room_model.delete_room(self.original_code)
                messagebox.showinfo("Eliminada", "La sala ha sido eliminada.", parent=self)
                self.result = True # Indicate an action was taken
                self.destroy()
            except Exception as e: # More specific exceptions can be caught from model
                messagebox.showerror("Error", f"No se pudo eliminar la sala. Puede tener préstamos asociados.\nError: {e}", parent=self)
