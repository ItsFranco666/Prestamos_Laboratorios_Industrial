import customtkinter as ctk
from tkinter import messagebox
from database.models import RoomModel

class RoomManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="black")
        
        self.room_model = RoomModel()
        self.setup_ui()
        self.refresh_rooms()
    
    def setup_ui(self):
        self.pack(fill="both", expand=True, padx=20, pady=20) # pack self

        title = ctk.CTkLabel(self, text="Gestión de Salas", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20), anchor="w") #
        
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(fill="x", pady=(0, 10))
        add_frame.grid_columnconfigure(0, weight=1) # Make label take available space
        
        # Add student button
        add_btn = ctk.CTkButton(add_frame, text="+ Agregar Sala", command=self.add_room_dialog)
        add_btn.grid(row=0, column=1, padx=0, pady=10) # Align to the right
        
        self.create_rooms_table()
    
    def create_rooms_table(self): #
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True)
        
        headers = ["Código", "Nombre", "Estado", "Acciones"]
        header_content_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_content_frame.pack(fill="x", pady=(5,0))

        header_content_frame.grid_columnconfigure(0, weight=1) # Codigo
        header_content_frame.grid_columnconfigure(1, weight=3) # Nombre
        header_content_frame.grid_columnconfigure(2, weight=1) # Estado
        header_content_frame.grid_columnconfigure(3, weight=1, minsize=100) # Acciones
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_content_frame, text=header, font=ctk.CTkFont(weight="bold"), anchor="w")
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew") #
        
        self.rooms_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent") #
        self.rooms_scroll.pack(fill="both", expand=True, pady=(0,5))
    
    def refresh_rooms(self):
        for widget in self.rooms_scroll.winfo_children():
            widget.destroy()
        
        rooms = self.room_model.get_all_rooms() #
        
        for room_data in rooms: # Renamed from room to room_data to avoid conflict with module
            self.create_room_row(room_data)
    
    def create_room_row(self, room_data):
        row_frame = ctk.CTkFrame(self.rooms_scroll)
        row_frame.pack(fill="x", pady=2, padx=2)
        
        row_frame.grid_columnconfigure(0, weight=1) # Codigo
        row_frame.grid_columnconfigure(1, weight=3) # Nombre
        row_frame.grid_columnconfigure(2, weight=1) # Estado
        row_frame.grid_columnconfigure(3, weight=1, minsize=100) # Acciones

        codigo_label = ctk.CTkLabel(row_frame, text=str(room_data[0]), anchor="w") #
        codigo_label.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        
        nombre_label = ctk.CTkLabel(row_frame, text=room_data[1], anchor="w") #
        nombre_label.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        status_color = "green" if room_data[2] == "Disponible" else "red" #
        estado_label = ctk.CTkLabel(row_frame, text=room_data[2], text_color=status_color, anchor="w") #
        estado_label.grid(row=0, column=2, padx=5, pady=2, sticky="ew")
        
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=3, padx=5, pady=0, sticky="e")
        
        edit_btn = ctk.CTkButton(action_frame, text="Editar", width=70, command=lambda r=room_data: self.edit_room_dialog(r))
        edit_btn.pack(side="left", padx=(0,2), pady=2)
    
    def add_room_dialog(self): #
        dialog = RoomDialog(self, "Agregar Sala", room_model=self.room_model)
        if dialog.result:
            if self.room_model.add_room(*dialog.result):
                self.refresh_rooms()
                messagebox.showinfo("Éxito", "Sala agregada correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo agregar la sala. Verifique que el código no esté duplicado.") #
    
    def edit_room_dialog(self, room_data): #
        dialog = RoomDialog(self, "Editar Sala", room_data=room_data, room_model=self.room_model)
        if dialog.result:
            # dialog.result should be (codigo, nombre). update_room takes (codigo, nombre)
            if self.room_model.update_room(dialog.result[0], dialog.result[1]): # Corrected call
                self.refresh_rooms()
                messagebox.showinfo("Éxito", "Sala actualizada correctamente.")
            else:
                messagebox.showerror("Error","No se pudo actualizar la sala.")


class RoomDialog:
    def __init__(self, parent, title, room_data=None, room_model=None): #
        self.result = None
        self.room_model = room_model if room_model else RoomModel()
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x230") # Increased height for padding
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.after(10, lambda: self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2),
                                                               parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2))))
        
        self.setup_dialog(room_data)
        parent.wait_window(self.dialog) #
    
    def setup_dialog(self, room_data):
        main_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Código:").pack(pady=(0,2), anchor="w")
        self.codigo_entry = ctk.CTkEntry(main_frame)
        self.codigo_entry.pack(pady=(0,10), fill="x")
        
        ctk.CTkLabel(main_frame, text="Nombre:").pack(pady=(0,2), anchor="w")
        self.nombre_entry = ctk.CTkEntry(main_frame) #
        self.nombre_entry.pack(pady=(0,10), fill="x")
        
        if room_data:
            self.codigo_entry.insert(0, str(room_data[0]))
            self.nombre_entry.insert(0, room_data[1])
            self.codigo_entry.configure(state="disabled") 
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent") #
        button_frame.pack(pady=(20,0), fill="x")
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save)
        save_btn.grid(row=0, column=0, padx=(0,5), sticky="ew")
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", hover_color="darkgray")
        cancel_btn.grid(row=0, column=1, padx=(5,0), sticky="ew")
    
    def save(self):
        codigo_str = self.codigo_entry.get()
        nombre = self.nombre_entry.get()

        if not all([codigo_str, nombre]): #
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self.dialog)
            return
        
        try:
            codigo = int(codigo_str)
        except ValueError:
            messagebox.showerror("Error", "El código debe ser un número.", parent=self.dialog) #
            return
        
        self.result = (codigo, nombre) #
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()