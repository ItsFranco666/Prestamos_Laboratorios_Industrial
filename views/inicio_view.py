# In university_management/views/inicio_view.py
import customtkinter as ctk
import os
import sys
# Ensure PIL is installed: pip install Pillow
from PIL import Image, ImageTk

# Import views
from .estudiantes_view import StudentManagementView
# from .profesores_view import GestionProfesores # Keep as placeholder for now
from .room_management import RoomManagementView
# from .equipment_inventory import EquipmentInventoryView
# from .room_loans import RoomLoansView
# from .equipment_loans import EquipmentLoansView
from utils.font_config import get_font # Assuming utils is in PYTHONPATH or same level

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Gestión Universitaria")
        self.geometry("1400x850") # Slightly increased height for better spacing
        # self.configure(fg_color=("#f0f0f0", "#1a1a1a")) # Default CTk theme handles this well
        
        # Attempt to set app icon (paths might need adjustment based on your structure)
        self.set_app_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1) # Changed from 1 to 0 for the main content area
        
        self.current_view = None
        self.create_sidebar()
        self.create_main_content_area() # Renamed for clarity
        
        self.show_student_management() # Default view

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0) # Increased width slightly
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew") # rowspan to span header potentially
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Pushes logout/settings to bottom

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Sistema de\nGestión U", font=get_font("subtitle", "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", self.show_dashboard, "dashboard_icon.png"), # Placeholder icon names
            ("Estudiantes", self.show_student_management, "students_icon.png"),
            ("Profesores", self.show_professor_management, "professors_icon.png"),
            ("Salas", self.show_room_management, "rooms_icon.png"),
            ("Inventario Equipos", self.show_equipment_inventory, "inventory_icon.png"),
            ("Préstamos Salas", self.show_room_loans, "room_loan_icon.png"),
            ("Préstamos Equipos", self.show_equipment_loans, "equip_loan_icon.png")
        ]
        
        for i, (text, command, icon_name) in enumerate(nav_items, 1):
            # Placeholder for icon loading, replace with actual icon handling
            # icon_image = self.load_icon(icon_name) 
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                # image=icon_image, # Add when icons are ready
                # compound="left", anchor="w", # For icon alignment
                command=lambda cmd=command, view_name=text: self.switch_view(cmd, view_name),
                height=40,
                font=get_font("normal"),
                corner_radius=8, # Rounded buttons
                # fg_color="transparent", # If you want hover effects to be more prominent
                # hover_color=("#d3d3d3", "#333333")
            )
            btn.grid(row=i, column=0, padx=15, pady=6, sticky="ew")
            self.nav_buttons[text] = btn
        
        # Appearance mode toggle (optional)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Apariencia:", anchor="w", font=get_font("small"))
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10,0), sticky="sw")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode_event, font=get_font("small"))
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(0,20), sticky="sw")
        self.appearance_mode_optionemenu.set(ctk.get_appearance_mode())


    def create_main_content_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#ffffff", "#242424")) # Slightly different bg
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1) # Ensure content view expands

    def switch_view(self, view_command, view_name):
        if self.current_view:
            self.current_view.destroy() # Destroy the old view
        
        # Update button styles (optional: highlight active button)
        for name, button in self.nav_buttons.items():
            if name == view_name:
                button.configure(fg_color=("#3a7ebf", "#1f538d")) # Example active color
            else:
                button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])


        self.current_view = view_command() # This will call the specific show_... method
        if self.current_view and isinstance(self.current_view, ctk.CTkFrame): # If the method returns the frame
             self.current_view.pack(in_=self.main_frame, fill="both", expand=True, padx=10, pady=10) # Pack new view
        # If show_... methods directly pack into self.main_frame, no need to pack here.
        # The current implementation of show_... methods directly packs.

    def clear_main_content(self): # Used by show_... methods
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_view = None # Reset current view reference

    def show_dashboard(self):
        self.clear_main_content()
        label = ctk.CTkLabel(self.main_frame, text="Dashboard - En desarrollo", font=get_font("title"))
        label.pack(expand=True, padx=20, pady=20)
        self.current_view = label # Technically the label is the view here
        return label # Or return a frame containing the label

    def show_student_management(self):
        self.clear_main_content()
        student_view = StudentManagementView(self.main_frame)
        student_view.pack(fill="both", expand=True) # No extra padding here, let view handle it
        self.current_view = student_view
        return student_view

    def show_professor_management(self):
        self.clear_main_content()
        # As per instructions, keep this as a placeholder.
        # If you had a GestionProfesores view:
        # professor_view = GestionProfesores(self.main_frame)
        # professor_view.pack(fill="both", expand=True)
        # self.current_view = professor_view
        # return professor_view
        label = ctk.CTkLabel(self.main_frame, text="Gestión de Profesores - En desarrollo", font=get_font("title"))
        label.pack(expand=True, padx=20, pady=20)
        self.current_view = label
        return label
        
    def show_room_management(self):
        self.clear_main_content()
        room_view = RoomManagementView(self.main_frame)
        room_view.pack(fill="both", expand=True)
        self.current_view = room_view
        return room_view
    
    def show_equipment_inventory(self):
        self.clear_main_content()
        inventory_view = EquipmentInventoryView(self.main_frame)
        inventory_view.pack(fill="both", expand=True)
        self.current_view = inventory_view
        return inventory_view
    
    def show_room_loans(self):
        self.clear_main_content()
        room_loans_view = RoomLoansView(self.main_frame)
        room_loans_view.pack(fill="both", expand=True)
        self.current_view = room_loans_view
        return room_loans_view
    
    def show_equipment_loans(self):
        self.clear_main_content()
        equipment_loans_view = EquipmentLoansView(self.main_frame)
        equipment_loans_view.pack(fill="both", expand=True)
        self.current_view = equipment_loans_view
        return equipment_loans_view

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def set_app_icon(self):
        try:
            # Determine path to icon, assuming it's in an 'assets/icons' folder
            # relative to where main.py is run, or an absolute path.
            # This path needs to be correct for your environment.
            # If running main.py from university_management/
            icon_path_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icons", "app_icon.ico")
            icon_path_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icons", "app_icon.png")

            final_icon_path = None
            if os.path.exists(icon_path_ico):
                final_icon_path = icon_path_ico
            elif os.path.exists(icon_path_png): # Fallback to PNG
                 final_icon_path = icon_path_png
            
            if final_icon_path:
                if sys.platform == "win32" and final_icon_path.endswith(".ico"):
                    self.iconbitmap(final_icon_path)
                else: # For other OS or if only PNG is available
                    # Pillow is needed for PNG icons on Tkinter Toplevels
                    icon_image = Image.open(final_icon_path)
                    # Resize if necessary, e.g., icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo) # For window icon
                    # For taskbar on some systems, wm_iconphoto might be needed
                    # self.tk.call('wm', 'iconphoto', self._w, icon_photo) # Alternative
            else:
                print(f"Icon file not found. Searched: {icon_path_ico}, {icon_path_png}")
        except Exception as e:
            print(f"Error setting application icon: {e}")

# This part is usually in main.py
# if __name__ == "__main__":
#     ctk.set_appearance_mode("System")  # Default to system
#     ctk.set_default_color_theme("blue") # Or "green", "dark-blue"
#     app = MainWindow()
#     app.mainloop()
