# In university_management/views/inicio_view.py
import customtkinter as ctk
import os
import sys
# Ensure PIL is installed: pip install Pillow
from PIL import Image, ImageTk

# Import views
from .students_view import StudentsView
from .profesores_view import ProfesorManagementView
from .rooms_view import RoomsView
# from .equipment_inventory import EquipmentInventoryView # Assuming these exist or will be added
# from .room_loans import RoomLoansView
# from .equipment_loans import EquipmentLoansView
from utils.font_config import get_font # Assuming utils is in PYTHONPATH or same level

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Gestión Universitaria")
        self.geometry("1400x850")
        
        # Set app icon
        self.set_app_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_view = None
        self.create_sidebar()
        self.create_main_content_area()
        
        self.show_dashboard() # Default view

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=("#f0f0f0", "#1c1c1c"))
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Sistema de\nGestión de Laboratorios", font=get_font("subtitle", "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", self.show_dashboard, "dashboard_icon.png"),
            ("Estudiantes", self.show_students_view, "student_icon.png"),
            ("Profesores", self.show_professor_management, "professors_icon.png"),
            ("Salas", self.show_room_view, "rooms_icon.png"),
            ("Inventario Equipos", self.show_equipment_inventory, "inventory_icon.png"),
            ("Préstamos Salas", self.show_room_loans, "room_loan_icon.png"),
            ("Préstamos Equipos", self.show_equipment_loans, "equip_loan_icon.png")
        ]
        
        # Creacion de los botones del panel lateral
        for i, (text, command, icon_name) in enumerate(nav_items, 1):
            # Crear el botón
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=lambda cmd=command, view_name=text: self.switch_view(cmd, view_name),
                height=45,
                font=get_font("normal"),
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#ffd3a8", "#9c6d41"),
                text_color=("#2b2b2b", "#ffffff")
            )
            
            # Cargar y configurar el icono si existe
            try:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", icon_name)
                if os.path.exists(icon_path):
                    icon_image = Image.open(icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    btn.configure(image=icon_photo)
                    btn.image = icon_photo  # Mantener una referencia
            except Exception as e:
                print(f"Error loading icon {icon_name}: {e}")
            
            btn.grid(row=i, column=0, padx=15, pady=6, sticky="ew")
            self.nav_buttons[text] = btn
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Apariencia:", anchor="w", font=get_font("small"))
        self.appearance_mode_label.grid(row=len(nav_items)+1, column=0, padx=20, pady=(10,0), sticky="sw")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode_event, font=get_font("small"))
        self.appearance_mode_optionemenu.grid(row=len(nav_items)+2, column=0, padx=20, pady=(0,20), sticky="sw")
        self.appearance_mode_optionemenu.set(ctk.get_appearance_mode())

    def create_main_content_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#ffffff", "#242424"))
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def switch_view(self, view_command, view_name):
        if self.current_view:
            self.current_view.destroy()
        
        # Update button styles:
        # Only the active button gets a specific color, others are transparent.
        for name, button in self.nav_buttons.items():
            if name == view_name:
                button.configure(fg_color=("#ffa154", "#c95414"))  # Active button color
            else:
                button.configure(fg_color="transparent")  # Reset non-active buttons to transparent

        new_view = view_command() # This calls the show_... method which creates and packs the view
        self.current_view = new_view # Update self.current_view with the returned view instance

    def clear_main_content(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_dashboard(self):
        self.clear_main_content()
        label = ctk.CTkLabel(self.main_frame, text="Dashboard - En desarrollo", font=get_font("title"))
        label.pack(expand=True, padx=20, pady=20)
        # self.current_view should be set by switch_view after this returns
        return label 

    def show_students_view(self):
        self.clear_main_content()
        student_view = StudentsView(self.main_frame)
        student_view.pack(fill="both", expand=True)
        # self.current_view should be set by switch_view after this returns
        return student_view

    def show_professor_management(self):
        self.clear_main_content()
        student_view = ProfesorManagementView(self.main_frame)
        student_view.pack(fill="both", expand=True)
        return student_view
        
    def show_room_view(self):
        self.clear_main_content()
        # Assuming RoomView is correctly imported and defined
        rooms_view = RoomsView(self.main_frame)
        rooms_view.pack(fill="both", expand=True)
        return rooms_view
    
    def show_equipment_inventory(self):
        self.clear_main_content()
        # Assuming EquipmentInventoryView exists
        # from .equipment_inventory import EquipmentInventoryView
        # inventory_view = EquipmentInventoryView(self.main_frame)
        # inventory_view.pack(fill="both", expand=True)
        # return inventory_view
        label = ctk.CTkLabel(self.main_frame, text="Inventario Equipos - En desarrollo", font=get_font("title"))
        label.pack(expand=True, padx=20, pady=20)
        return label
    
    def show_room_loans(self):
        self.clear_main_content()
        # Assuming RoomLoansView exists
        # from .room_loans import RoomLoansView
        # room_loans_view = RoomLoansView(self.main_frame)
        # room_loans_view.pack(fill="both", expand=True)
        # return room_loans_view
        label = ctk.CTkLabel(self.main_frame, text="Préstamos Salas - En desarrollo", font=get_font("title"))
        label.pack(expand=True, padx=20, pady=20)
        return label
    
    def show_equipment_loans(self):
        self.clear_main_content()
        # Assuming EquipmentLoansView exists
        # from .equipment_loans import EquipmentLoansView
        # equipment_loans_view = EquipmentLoansView(self.main_frame)
        # equipment_loans_view.pack(fill="both", expand=True)
        # return equipment_loans_view
        label = ctk.CTkLabel(self.main_frame, text="Préstamos Equipos - En desarrollo", font=get_font("title"))
        label.pack(expand=True, padx=20, pady=20)
        return label

    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Handles theme change and ensures the current view updates immediately."""
        previous_mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode(new_appearance_mode)
        new_mode = ctk.get_appearance_mode()

        # Only proceed if the mode actually changed, or if "System" was reselected
        if previous_mode.lower() != new_mode.lower() or new_appearance_mode == "System":
            # Directly call on_theme_change for the current view if it exists and has the method
            if self.current_view and hasattr(self.current_view, 'on_theme_change'):
                self.current_view.on_theme_change()

    def set_app_icon(self):
        try:
            icon_path_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.ico")
            icon_path_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.png")

            final_icon_path = None
            if sys.platform == "win32" and os.path.exists(icon_path_ico):
                final_icon_path = icon_path_ico
            elif os.path.exists(icon_path_png):
                 final_icon_path = icon_path_png
            
            if final_icon_path:
                if sys.platform == "win32" and final_icon_path.endswith(".ico"):
                    self.iconbitmap(default=final_icon_path) # Use default parameter for .ico
                else:
                    icon_image = Image.open(final_icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo)
            else:
                print(f"Icon file not found. Searched: {icon_path_ico}, {icon_path_png}")
        except Exception as e:
            print(f"Error setting application icon: {e}")