import customtkinter as ctk
from tkinter import ttk
from models.student_model import StudentModel

class StudentManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = StudentModel()
        self.grid_columnconfigure(0, weight=1)
        
        # Search and Filter Row
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, sticky="ew")
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", padx=5)
        
        self.project_filter = ctk.CTkComboBox(self.search_frame, values=self.get_projects())
        self.project_filter.pack(side="left", padx=5)
        
        self.add_btn = ctk.CTkButton(self.search_frame, text="+ Add Student", command=self.open_add_dialog)
        self.add_btn.pack(side="right", padx=5)
        
        # Student Table
        self.tree = ttk.Treeview(self, columns=("Code", "Name", "ID", "Project"), show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        # Configure columns
        for col in ["Code", "Name", "ID", "Project"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.load_students()
    
    def get_projects(self):
        return [project[1] for project in self.model.get_all_projects()]
    
    def load_students(self, filter_project=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        students = self.model.get_students(filter_project)
        for student in students:
            self.tree.insert("", "end", values=student)
    
    def open_add_dialog(self):
        AddStudentDialog(self, self.model)