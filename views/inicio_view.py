import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys
from PIL import Image, ImageTk
from utils.font_config import get_font
from utils.exporter import export_database_to_excel
from .personal_view import PersonalView
from .students_view import StudentsView
from .profesores_view import ProfessorsView
from .rooms_view import RoomsView
from .inventory_view import InventoryView
from .rooms_loans_view import RoomLoansView
from .equipment_loans_view import EquipmentLoansView
from .projects_view import ProyectosView
from .campus_views import SedesView
from .equipment_view import EquiposView
from .dashboard_view import DashboardView

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Gestión de Laboratorios de Producción")
        self.geometry("1400x850")
        
        # Set app icon
        self.set_app_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Set the initial theme based on the system, then configure styles
        # This ensures the app starts with the system's theme
        ctk.set_appearance_mode("System") 
        self.setup_ttk_styles()
        
        self.current_view = None
        self.logo_image_label = None  # Referencia para actualizar la imagen
        self.logo_image = None        # Mantener referencia a la imagen para evitar garbage collection
        self.create_sidebar()
        self.centrar_ventana()
        self.create_main_content_area()
        
        self.show_dashboard() # Default view
    
    def centrar_ventana(self):
        self.update_idletasks()

        ancho = 1400
        alto = 850

        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def get_system_theme(self):
        """Detects the current system theme."""
        try:
            # Using darkdetect library to check if the system is in dark mode
            import darkdetect
            return "Dark" if darkdetect.isDark() else "Light"
        except ImportError:
            # Fallback to Light theme if darkdetect is not installed
            return "Light"
    
    def setup_ttk_styles(self, theme_mode=None):
        """Configures the styles for ttk.Treeview globally."""
        if theme_mode is None:
            theme_mode = ctk.get_appearance_mode()
        
        # If the theme is "System", detect the actual system theme
        if theme_mode == "System":
            theme_mode = self.get_system_theme()

        style = ttk.Style()
        style.theme_use("default")
        
        normal_font = get_font("normal")
        bold_font = get_font("normal", "bold") # Use bold font for headers

        # Colors based on the theme
        if theme_mode == "Dark":
            tree_bg, text_color, selected_color, heading_bg, heading_active_bg = \
            ("#2b2b2b", "#ffffff", "#404040", "#4B5563", "#525E75")
        else: # Light
            tree_bg, text_color, selected_color, heading_bg, heading_active_bg = \
            ("#ffffff", "#2b2b2b", "#e3f2fd", "#E5E7EB", "#CFD8DC")

        # Main style for the Treeview
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
        
        # Style for Treeview headings
        style.configure("Modern.Treeview.Heading",
                        background=heading_bg,
                        foreground=text_color,
                        borderwidth=0,
                        relief="flat",
                        font=bold_font,
                        padding=(10, 8))
        style.map("Modern.Treeview.Heading", 
                  background=[('active', heading_active_bg)])

    def get_logo_image_path(self, theme_mode=None):
        """Devuelve la ruta de la imagen de logo según el tema."""
        import os
        if theme_mode is None:
            theme_mode = ctk.get_appearance_mode()
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        if theme_mode == "Dark":
            return os.path.join(base_path, "Dark_UD.png")
        else:
            return os.path.join(base_path, "Ligth_UD.png")

    def load_logo_image(self, theme_mode=None):
        """Carga la imagen de logo adecuada según el tema, respetando la transparencia."""
        from PIL import Image
        import os
        logo_path = self.get_logo_image_path(theme_mode)
        if os.path.exists(logo_path):
            img = Image.open(logo_path).convert("RGBA")  # Asegura canal alfa
            img = img.resize((128, 128), Image.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=(128, 128))
        return None

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#EBEBEB", "#1c1c1c"))
        self.sidebar_frame.grid(row=0, column=0, rowspan=1, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(13, weight=1) # Adjust row configure to push items to the bottom

        # --- SOLO LOGO CENTRADO ---
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=0, pady=(10, 10), sticky="nsew")
        logo_frame.grid_columnconfigure(0, weight=1)
        logo_frame.grid_rowconfigure(0, weight=1)

        self.logo_image = self.load_logo_image()
        self.logo_image_label = ctk.CTkLabel(
            logo_frame,
            image=self.logo_image,
            text="",
            width=100,
            height=100,
            fg_color="transparent"
        )
        self.logo_image_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        self.nav_buttons = {}
        nav_items = [
            ("📊    Dashboard", self.show_dashboard),
            ("📁    Préstamo de Salas", self.show_room_loans),
            ("📁    Préstamo de Equipos", self.show_equipment_loans),
            ("👤    Personal", self.show_personal),
            ("👤    Estudiantes", self.show_students_view),
            ("👤    Profesores", self.show_professor_management),
            ("🚪    Salas", self.show_room_view),
            ("🔧    Inventario", self.show_equipment_inventory),
            ("🔧    Equipos", self.show_equipos_view),
            ("🏢    Proyectos Curriculares", self.show_proyectos_curriculares_view),
            ("🏢    Sedes", self.show_sedes_view)
        ]
        
        for i, (text, command) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=text,
                command=lambda cmd=command, view_name=text: self.switch_view(cmd, view_name),
                height=45, font=get_font("normal"), corner_radius=8, fg_color="transparent",
                hover_color=("#ffd3a8", "#9c6d41"), text_color=("#2b2b2b", "#ffffff"), anchor="w"
            )
            btn.grid(row=i, column=0, padx=30, pady=0, sticky="ew")
            self.nav_buttons[text] = btn
        
        # --- EXPORT BUTTON ---
        # Cargar el icono de Excel
        excel_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "excel_icon.png")
        excel_icon_image = None
        if os.path.exists(excel_icon_path):
            excel_icon_image = ctk.CTkImage(
                light_image=Image.open(excel_icon_path),
                dark_image=Image.open(excel_icon_path),
                size=(24, 24)
            )

        self.export_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Exportar a Excel",
            image=excel_icon_image,
            compound="left",  # Icono a la izquierda del texto
            command=self.export_data,
            height=40,
            font=get_font("small", "bold"),
            corner_radius=8,
            fg_color=("#1D6F42", "#107C41"),
            hover_color=("#155B33", "#158E4C")
        )
        self.export_button.grid(row=len(nav_items) + 1, column=0, padx=20, pady=(12, 8), sticky="sew")

        # --- APPEARANCE MODE WIDGETS ---
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Apariencia:", anchor="w", font=get_font("small"))
        self.appearance_mode_label.grid(row=len(nav_items) + 2, column=0, padx=20, pady=(10, 0), sticky="sw")
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Claro", "Oscuro"],
            command=self.change_appearance_mode_event, 
            font=get_font("small"),
            fg_color=("#ffa154", "#c95414"),
            button_color=("#ff8c33", "#b34a0e"),
            button_hover_color=("#ff7b1a", "#9e400c")
        )
        self.appearance_mode_optionemenu.grid(row=len(nav_items) + 3, column=0, padx=20, pady=(0, 20), sticky="sw")

        current_mode = "Claro" if ctk.get_appearance_mode() == "Light" else "Oscuro"
        self.appearance_mode_optionemenu.set(current_mode)
    
    def export_data(self):
        """
        Calls the exporter utility to save all database data to an Excel file.
        """
        try:
            # The exporter function handles the file dialog and messaging
            export_database_to_excel()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el proceso de exportación: {e}")


    def create_main_content_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#ffffff", "#242424"))
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def switch_view(self, view_command, view_name):
        if self.current_view:
            self.current_view.destroy()
        
        # Update button styles: only the active button gets a specific color
        for name, button in self.nav_buttons.items():
            if name == view_name:
                button.configure(fg_color=("#ffa154", "#c95414"))  # Active button color
            else:
                button.configure(fg_color="transparent")  # Reset non-active buttons

        new_view = view_command()
        self.current_view = new_view

    def clear_main_content(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_dashboard(self):
        self.clear_main_content()
        personal_view = DashboardView(self.main_frame)
        personal_view.pack(fill="both", expand=True)
        return personal_view
    
    def show_personal(self):
        self.clear_main_content()
        personal_view = PersonalView(self.main_frame)
        personal_view.pack(fill="both", expand=True)
        return personal_view

    def show_students_view(self):
        self.clear_main_content()
        student_view = StudentsView(self.main_frame)
        student_view.pack(fill="both", expand=True)
        return student_view

    def show_professor_management(self):
        self.clear_main_content()
        student_view = ProfessorsView(self.main_frame)
        student_view.pack(fill="both", expand=True)
        return student_view
        
    def show_room_view(self):
        self.clear_main_content()
        rooms_view = RoomsView(self.main_frame)
        rooms_view.pack(fill="both", expand=True)
        return rooms_view
    
    def show_equipment_inventory(self):
        self.clear_main_content()
        inventory_view = InventoryView(self.main_frame)
        inventory_view.pack(fill="both", expand=True)
        return inventory_view
    
    def show_equipos_view(self):
        self.clear_main_content()
        inventory_view = EquiposView(self.main_frame)
        inventory_view.pack(fill="both", expand=True)
        return inventory_view
    
    def show_room_loans(self):
        self.clear_main_content()
        room_loans_view = RoomLoansView(self.main_frame)
        room_loans_view.pack(fill="both", expand=True)
        return room_loans_view
    
    def show_equipment_loans(self): 
        self.clear_main_content()
        equipment_loans_view = EquipmentLoansView(self.main_frame)
        equipment_loans_view.pack(fill="both", expand=True)
        return equipment_loans_view

    def show_proyectos_curriculares_view(self):
        self.clear_main_content()
        equipment_loans_view = ProyectosView(self.main_frame)
        equipment_loans_view.pack(fill="both", expand=True)
        return equipment_loans_view

    def show_sedes_view(self):
        self.clear_main_content()
        equipment_loans_view = SedesView(self.main_frame)
        equipment_loans_view.pack(fill="both", expand=True)
        return equipment_loans_view

    def update_logo_image(self, theme_mode=None):
        """Actualiza la imagen del logo según el tema."""
        self.logo_image = self.load_logo_image(theme_mode)
        if self.logo_image_label:
            self.logo_image_label.configure(image=self.logo_image)

    def change_appearance_mode_event(self, new_appearance_mode_spanish: str):
        """Handles theme changes and ensures the current view is updated."""
        # Map the Spanish labels to CustomTkinter's internal theme names
        theme_map = {"Claro": "Light", "Oscuro": "Dark"}
        new_appearance_mode = theme_map.get(new_appearance_mode_spanish, "Light")

        ctk.set_appearance_mode(new_appearance_mode)
        
        # Re-apply ttk styles for the new theme
        self.setup_ttk_styles(theme_mode=new_appearance_mode)
        
        # Force the current view to update
        if self.current_view:
            # Call a generic on_theme_change method if it exists
            if hasattr(self.current_view, 'on_theme_change'):
                self.current_view.on_theme_change()
            # Fallback to specific refresh methods
            elif hasattr(self.current_view, 'refresh_students'):
                self.current_view.refresh_students()
            elif hasattr(self.current_view, 'refresh_professors'):
                self.current_view.refresh_professors()
            elif hasattr(self.current_view, 'refresh_rooms'):
                self.current_view.refresh_rooms()
            elif hasattr(self.current_view, 'refresh_inventory'):
                self.current_view.refresh_inventory()
            elif hasattr(self.current_view, 'refresh_loans'):
                self.current_view.refresh_loans()
            
            # Force UI update
            self.current_view.update_idletasks()
        # Actualizar imagen del logo
        self.update_logo_image(new_appearance_mode)
    # --- MODIFIED SECTION END ---

    def set_app_icon(self):
        try:
            # When running as a PyInstaller executable, sys._MEIPASS is the path to the temp folder
            # where bundled files are extracted. Otherwise, it's the directory of the script.
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            
            # Define the paths to icon files (both .ico and .png for compatibility)
            icon_path_ico = os.path.join(base_path, "..", "assets", "app_icon.ico")
            icon_path_png = os.path.join(base_path, "..", "assets", "app_icon.png")

            # Comprobación explícita de existencia de los iconos
            if not os.path.exists(icon_path_ico):
                print(f"[ADVERTENCIA] No se encontró el icono .ico en: {icon_path_ico}")
            else:
                print(f"Se encontró el icono .ico en: {icon_path_ico}")
            if not os.path.exists(icon_path_png):
                print(f"[ADVERTENCIA] No se encontró el icono .png en: {icon_path_png}")
            else:
                print(f"Se encontró el icono .png en: {icon_path_png}")
            
            # Determine the final icon path based on the existence of files
            final_icon_path = None
            if sys.platform == "win32" and os.path.exists(icon_path_ico):
                final_icon_path = icon_path_ico
            elif os.path.exists(icon_path_png):
                final_icon_path = icon_path_png
            
            # Set the application icon for both window and taskbar
            if final_icon_path:
                if sys.platform == "win32" and final_icon_path.endswith(".ico"):
                    self.iconbitmap(default=final_icon_path)  # Use default for .ico
                else:
                    icon_image = Image.open(final_icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo)  # Set for the window and taskbar
            else:
                print(f"Icon file not found. Searched: {icon_path_ico}, {icon_path_png}")
        except Exception as e:
            print(f"Error setting application icon: {e}")