import customtkinter as ctk
from tkinter import ttk, messagebox
from database import models
from utils import validators
from PIL import Image
import os

ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")

class StudentManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.app = app_instance # To access notification bar or other app-level methods

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # For the table/scrollable frame

        # --- Title ---
        title_label = ctk.CTkLabel(self, text="Student Management", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # --- Controls Frame (Search, Filter, Add) ---
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=0, column=0, padx=20, pady=(10,10), sticky="ew", columnspan=2) # columnspan if more columns later
        # controls_frame.grid_columnconfigure(4, weight=1) # Push add button to the right if needed

        self.search_entry = ctk.CTkEntry(controls_frame, placeholder_text="Search by Code, Name, ID...")
        self.search_entry.pack(side="left", padx=(0, 10), pady=10, fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda event: self.load_students())


        self.search_button = ctk.CTkButton(controls_frame, text="Search", command=self.load_students, width=100)
        self.search_button.pack(side="left", padx=(0, 10), pady=10)

        # Curriculum Project Filter
        self.proyectos_curriculares = ["Todos"] + [pc['nombre'] for pc in models.get_all_proyectos_curriculares() or []]
        self.project_filter_var = ctk.StringVar(value="Todos")
        self.project_filter_menu = ctk.CTkOptionMenu(controls_frame, variable=self.project_filter_var,
                                                     values=self.proyectos_curriculares, command=lambda _: self.load_students())
        self.project_filter_menu.pack(side="left", padx=(0, 10), pady=10)
        
        try:
            icon_add = ctk.CTkImage(Image.open(os.path.join(ASSETS_PATH, "add.png")), size=(20,20))
            self.add_student_button = ctk.CTkButton(controls_frame, text="Add Student", image=icon_add, command=self.open_add_student_dialog)
        except:
            self.add_student_button = ctk.CTkButton(controls_frame, text="Add Student", command=self.open_add_student_dialog)
        self.add_student_button.pack(side="right", padx=(10,0), pady=10)


        # --- Student List (Table using Treeview) ---
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default") # Use a base theme that allows configuration

        # Configure Treeview colors to match customtkinter (approximate)
        # You might need to fine-tune these colors based on your CTk theme
        bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        header_bg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        header_fg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["text_color"])
        selected_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"])


        style.configure("Treeview",
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', selected_color)], foreground=[('selected', text_color)])
        style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground=header_fg,
                        relief="flat",
                        font=('Arial', 10, 'bold'))
        style.map("Treeview.Heading",
                  background=[('active', self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"]))])


        self.student_table = ttk.Treeview(table_frame, columns=("Code", "Name", "ID", "Curriculum Project", "Actions"), show="headings", style="Treeview")
        
        self.student_table.heading("Code", text="Code")
        self.student_table.heading("Name", text="Name")
        self.student_table.heading("ID", text="ID (Cédula)")
        self.student_table.heading("Curriculum Project", text="Curriculum Project")
        self.student_table.heading("Actions", text="Actions", anchor="center")

        self.student_table.column("Code", width=100, anchor="w")
        self.student_table.column("Name", width=250, anchor="w")
        self.student_table.column("ID", width=100, anchor="w")
        self.student_table.column("Curriculum Project", width=200, anchor="w")
        self.student_table.column("Actions", width=120, anchor="center", stretch=False)

        # Scrollbar (if needed, Treeview can be slow with many rows)
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.student_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.student_table.configure(yscrollcommand=scrollbar.set)
        self.student_table.pack(expand=True, fill="both")
        
        self.load_students()

    def load_students(self):
        # Clear existing items
        for item in self.student_table.get_children():
            self.student_table.delete(item)

        search_term = self.search_entry.get()
        project_filter = self.project_filter_var.get()
        
        students_data = models.get_students(search_term=search_term, project_filter=project_filter)
        
        if students_data:
            for i, student in enumerate(students_data):
                # Insert data row
                item_id = self.student_table.insert("", "end", values=(
                    student["codigo"],
                    student["nombre"],
                    student["cedula"],
                    student["proyecto_curricular"] if student["proyecto_curricular"] else "N/A"
                ), tags=(f'row_{i}', student["codigo"])) # Use student code as a tag for easy retrieval

                # Create a frame for buttons in the "Actions" cell (this is complex with ttk.Treeview)
                # A simpler approach for ttk.Treeview is to handle actions on row selection or double-click.
                # For direct buttons in rows, CTkScrollableFrame with custom rows is better.
                # For now, let's add a placeholder and handle edit/delete via selection.
                self.student_table.item(item_id, values=(
                    student["codigo"], student["nombre"], student["cedula"],
                    student["proyecto_curricular"] if student["proyecto_curricular"] else "N/A",
                    "Edit | Delete" # Placeholder text
                ))
        
        self.student_table.bind("<Double-1>", self.on_row_double_click) # For editing
        # Could add a context menu for delete on right-click as well

    def on_row_double_click(self, event):
        item_id = self.student_table.focus() # Get selected item
        if not item_id:
            return
        item_values = self.student_table.item(item_id, "values")
        student_code = item_values[0] # Assuming code is the first column
        self.open_edit_student_dialog(student_code)


    def open_add_student_dialog(self):
        dialog = StudentDialog(self, title="Add New Student", app_instance=self.app)
        # Dialog will handle its own logic and call self.load_students() on success

    def open_edit_student_dialog(self, student_code):
        student_data = models.get_student_by_code(student_code)
        if student_data:
            dialog = StudentDialog(self, title=f"Edit Student - {student_data['nombre']}", student_data=student_data, app_instance=self.app)
        else:
            self.app.show_notification(f"Student with code {student_code} not found.", "error")
            
    def confirm_delete_student(self):
        selected_item = self.student_table.focus()
        if not selected_item:
            self.app.show_notification("Please select a student to delete.", "error")
            return

        item_values = self.student_table.item(selected_item, "values")
        student_code = item_values[0]
        student_name = item_values[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student {student_name} (Code: {student_code})? This action cannot be undone.", icon='warning'):
            if models.delete_student(student_code):
                self.app.show_notification(f"Student {student_name} deleted successfully.", "success")
                self.load_students()
            else:
                self.app.show_notification(f"Failed to delete student {student_name}. They might have active loans or other dependencies.", "error")
    
    def refresh_proyectos_dropdown(self):
        self.proyectos_curriculares = ["Todos"] + [pc['nombre'] for pc in models.get_all_proyectos_curriculares() or []]
        self.project_filter_menu.configure(values=self.proyectos_curriculares)
        # Optionally, re-add a "Add new curriculum" button here or in a dedicated admin section
        # For now, assuming curriculum projects are managed elsewhere or pre-populated.


class StudentDialog(ctk.CTkToplevel):
    def __init__(self, parent_frame, title, app_instance, student_data=None):
        super().__init__(parent_frame)
        self.parent_frame = parent_frame # StudentManagementFrame instance
        self.app = app_instance # Main App instance
        self.student_data = student_data # None for Add, existing data for Edit

        self.title(title)
        self.geometry("450x350")
        self.transient(parent_frame) # Keep dialog on top of parent
        self.grab_set() # Modal behavior

        self.grid_columnconfigure(1, weight=1)

        # Fields
        ctk.CTkLabel(self, text="Code:").grid(row=0, column=0, padx=20, pady=(20,5), sticky="w")
        self.code_entry = ctk.CTkEntry(self, placeholder_text="e.g., 20201020001")
        self.code_entry.grid(row=0, column=1, padx=20, pady=(20,5), sticky="ew")

        ctk.CTkLabel(self, text="Full Name:").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Firstname Lastname")
        self.name_entry.grid(row=1, column=1, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="ID (Cédula):").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.id_entry = ctk.CTkEntry(self, placeholder_text="e.g., 1001234567")
        self.id_entry.grid(row=2, column=1, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Curriculum Project:").grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.proyectos = models.get_all_proyectos_curriculares() or []
        self.proyecto_names = [p['nombre'] for p in self.proyectos]
        self.proyecto_map = {p['nombre']: p['id'] for p in self.proyectos} # Name to ID map
        self.proyecto_id_map = {p['id']: p['nombre'] for p in self.proyectos} # ID to Name map

        self.proyecto_var = ctk.StringVar()
        self.proyecto_menu = ctk.CTkOptionMenu(self, variable=self.proyecto_var, values=self.proyecto_names if self.proyecto_names else ["N/A - Add projects first"])
        self.proyecto_menu.grid(row=3, column=1, padx=20, pady=5, sticky="ew")
        if not self.proyecto_names:
            self.proyecto_menu.configure(state="disabled")


        # Buttons Frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(20,10), sticky="ew")
        buttons_frame.grid_columnconfigure((0,1), weight=1)


        self.submit_button = ctk.CTkButton(buttons_frame, text="Save Student" if not student_data else "Update Student", command=self.submit)
        self.submit_button.grid(row=0, column=0, padx=(0,5), pady=5, sticky="ew")

        self.cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=self.destroy, fg_color="gray")
        self.cancel_button.grid(row=0, column=1, padx=(5,0), pady=5, sticky="ew")

        if self.student_data:
            self.populate_form()
            if self.student_data.get('codigo'): # If editing, code should not be changed
                self.code_entry.configure(state="disabled")

    def populate_form(self):
        self.code_entry.insert(0, str(self.student_data.get("codigo", "")))
        self.name_entry.insert(0, self.student_data.get("nombre", ""))
        self.id_entry.insert(0, str(self.student_data.get("cedula", "")))
        
        proyecto_id = self.student_data.get("proyecto_curricular_id")
        if proyecto_id and proyecto_id in self.proyecto_id_map:
            self.proyecto_var.set(self.proyecto_id_map[proyecto_id])
        elif self.proyecto_names:
             self.proyecto_var.set(self.proyecto_names[0]) # Default to first if not set or invalid
        else:
            self.proyecto_var.set("")


    def submit(self):
        code_str = self.code_entry.get()
        name = self.name_entry.get()
        id_str = self.id_entry.get()
        proyecto_nombre = self.proyecto_var.get()

        # Validations
        if not validators.is_not_empty(code_str) and not self.student_data: # Code required for new students
            self.app.show_notification("Student code is required.", "error")
            self.code_entry.focus()
            return
        if self.student_data: # If editing, use original code
            code = self.student_data['codigo']
        elif not validators.is_integer(code_str):
            self.app.show_notification("Student code must be a number.", "error")
            self.code_entry.focus()
            return
        else:
            code = int(code_str)


        if not validators.is_not_empty(name):
            self.app.show_notification("Student name is required.", "error")
            self.name_entry.focus()
            return
        if not validators.is_not_empty(id_str) or not validators.is_integer(id_str):
            self.app.show_notification("Student ID (Cédula) must be a valid number.", "error")
            self.id_entry.focus()
            return
        
        cedula = int(id_str)
        proyecto_id = self.proyecto_map.get(proyecto_nombre) if proyecto_nombre and proyecto_nombre != "N/A - Add projects first" else None

        try:
            if self.student_data: # Editing existing student
                original_code = self.student_data['codigo']
                success = models.update_student(original_code, name, cedula, proyecto_id)
                action = "updated"
            else: # Adding new student
                success = models.add_student(code, name, cedula, proyecto_id)
                action = "added"
            
            if success:
                self.app.show_notification(f"Student {name} {action} successfully!", "success")
                self.parent_frame.load_students() # Refresh the list in the parent frame
                self.destroy()
            else:
                # More specific error from models.py would be helpful here
                self.app.show_notification(f"Failed to {action} student. Code or ID might already exist, or invalid project.", "error")
        except Exception as e:
            self.app.show_notification(f"An error occurred: {e}", "error")