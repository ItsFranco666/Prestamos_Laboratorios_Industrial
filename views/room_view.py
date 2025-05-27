import customtkinter as ctk
from tkinter import ttk
from models.room_model import RoomModel

class RoomManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = RoomModel()
        self.grid_columnconfigure(0, weight=1)
        
        # Control Panel
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkButton(control_frame, text="Add Room", command=self.open_add_dialog).pack(side="left", padx=5)
        
        # Room Table
        self.tree = ttk.Treeview(self, columns=("Code", "Name", "Status"), show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        for col in ["Code", "Name", "Status"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.load_rooms()
    
    def load_rooms(self):
        rooms = self.model.get_rooms_with_status()
        for room in rooms:
            status = "🟢 Available" if room[2] else "🔴 Occupied"
            self.tree.insert("", "end", values=(room[0], room[1], status))