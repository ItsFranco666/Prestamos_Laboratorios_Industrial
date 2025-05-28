import customtkinter as ctk
from views.estudiantes_view import StudentManagementView
from views.profesores_view import GestionProfesores
# from views.room_management import RoomManagementView
# from views.equipment_inventory import EquipmentInventoryView
# from views.room_loans import RoomLoansView
# from views.equipment_loans import EquipmentLoansView

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Sistema de Gestión Universitaria")
        self.geometry("1400x800")
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        
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
            font=ctk.CTkFont(size=18, weight="bold")
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
                font=ctk.CTkFont(size=14)
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
            font=ctk.CTkFont(size=24)
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