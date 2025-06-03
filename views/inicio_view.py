import customtkinter as ctk
import os
import sys
import tkinter as tk
from views.estudiantes_view import StudentManagementView
from views.profesores_view import GestionProfesores
# from views.room_management import RoomManagementView
# from views.equipment_inventory import EquipmentInventoryView
# from views.room_loans import RoomLoansView
# from views.equipment_loans import EquipmentLoansView
from utils.font_config import get_font
from PIL import Image, ImageTk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Sistema de Gestión Universitaria")
        self.geometry("1400x800")
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        print("Iniciando configuración de la ventana...")
        self.set_app_icon()

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_main_content()
        
        # Show initial view
        self.show_student_management()
    
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Sistema de\nGestión", 
            font=get_font("subtitle", "bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Estudiantes", self.show_student_management),
            ("Profesores", self.show_professor_management),
            ("Salas", self.show_room_management),
            ("Inventario", self.show_equipment_inventory),
            ("Préstamos Salas", self.show_room_loans),
            ("Préstamos Equipos", self.show_equipment_loans)
        ]
        
        for i, (text, command) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=command,
                height=40,
                font=get_font("normal")
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[text] = btn
    
    def create_main_content(self):
        # Main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
    
    def clear_main_content(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_main_content()
        label = ctk.CTkLabel(
            self.main_frame, 
            text="Dashboard - En desarrollo",
            font=get_font("title")
        )
        label.pack(expand=True)
    
    def show_student_management(self):
        self.clear_main_content()
        student_view = StudentManagementView(self.main_frame)
        student_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_professor_management(self):
        self.clear_main_content()
        vista_profesor = GestionProfesores
        label = ctk.CTkLabel(
            self.main_frame, 
            text="Gestión de Profesores - En desarrollo",
            font=ctk.CTkFont(size=24)
        )
        label.pack(expand=True)
    
    def show_room_management(self):
        self.clear_main_content()
        room_view = RoomManagementView(self.main_frame)
        room_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_equipment_inventory(self):
        self.clear_main_content()
        inventory_view = EquipmentInventoryView(self.main_frame)
        inventory_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_room_loans(self):
        self.clear_main_content()
        room_loans_view = RoomLoansView(self.main_frame)
        room_loans_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    def show_equipment_loans(self):
        self.clear_main_content()
        equipment_loans_view = EquipmentLoansView(self.main_frame)
        equipment_loans_view.pack(fill="both", expand=True, padx=20, pady=20)

    def set_app_icon(self):
        """Configura el icono de la aplicación tanto en la ventana como en la barra de tareas"""
        try:
            # Buscar el icono en diferentes ubicaciones
            icon_path = self.get_icon_path(".ico")
            if not icon_path:
                icon_path = self.get_icon_path(".png")
            
            if icon_path:
                print(f"Configurando icono desde: {icon_path}")
                
                # Cargar y configurar el icono
                icon_image = Image.open(icon_path)
                # Redimensionar a un tamaño estándar para la barra de tareas (32x32)
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage
                icon_photo = ImageTk.PhotoImage(icon_image)
                
                # Configurar el icono para la barra de tareas
                self.wm_iconphoto(True, icon_photo)
                
                # Mantener una referencia al icono
                self.icon_photo = icon_photo
                
                # Configuración específica para Windows
                if sys.platform == "win32":
                    try:
                        self.iconbitmap(icon_path)
                    except Exception as e:
                        print(f"Error al configurar iconbitmap: {e}")
                
                print("Icono configurado exitosamente")
            else:
                print("No se encontró ningún archivo de icono")
                
        except Exception as e:
            print(f"Error al cargar el icono: {e}")
            print(f"Ruta del icono intentada: {icon_path}")

    def get_icon_path(self, extension):
        """Busca un icono en varias ubicaciones posibles"""
        possible_names = ["icon", "app_icon", "logo"]
        possible_dirs = [".", "./icons", "../icons", "../assets", "./assets"]
        
        for name in possible_names:
            for directory in possible_dirs:
                path = os.path.join(directory, name + extension)
                if os.path.exists(path):
                    return os.path.abspath(path)
        return None