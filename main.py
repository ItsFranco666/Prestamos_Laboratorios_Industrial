import customtkinter as ctk
from views.student_view import StudentManagementView
from views.room_view import RoomManagementView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("University Loan Management")
        self.geometry("1200x800")
        
        # Navigation Frame
        self.nav_frame = ctk.CTkFrame(self, width=200)
        self.nav_frame.pack(side="left", fill="y")
        
        # Main Container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(side="right", fill="both", expand=True)
        
        # Navigation Buttons
        self.create_nav_buttons()
        self.current_view = None
        
    def create_nav_buttons(self):
        buttons = [
            ("Student Management", self.show_student_management),
            ("Rooms", self.show_room_management),
            # ... Other modules ...
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(self.nav_frame, text=text, command=command)
            btn.pack(pady=5, padx=10, fill="x")
    
    def show_student_management(self):
        self.clear_main_container()
        self.current_view = StudentManagementView(self.main_container)
    
    def show_room_management(self):
        self.clear_main_container()
        self.current_view = RoomManagementView(self.main_container)
    
    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()