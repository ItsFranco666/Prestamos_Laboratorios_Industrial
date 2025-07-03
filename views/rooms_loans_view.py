import customtkinter as ctk
from tkinter import messagebox, ttk
# The models are now correctly pointing to the updated RoomLoanModel
from database.models import RoomLoanModel, PersonalLaboratorioModel, StudentModel, ProfesorModel, RoomModel
from utils.font_config import get_font
from datetime import datetime
import os, sys
from PIL import Image, ImageTk

class RoomLoansView(ctk.CTkFrame):
    """
    A view for managing room loans, including creating new loans and viewing history.
    It features conditional fields based on user type (Student vs. Professor).
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.pack_propagate(False)
        self.pack(padx=15, pady=15, fill="both", expand=True)

        # Initialize models
        self.room_loan_model = RoomLoanModel()
        self.personal_model = PersonalLaboratorioModel()
        self.student_model = StudentModel()
        self.profesor_model = ProfesorModel()
        self.room_model = RoomModel()

        self.setup_ui()
        self._show_new_loan_view()

    def setup_ui(self):
        """Sets up the main navigation and content frames."""
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=(0, 15), padx=0, fill="x")

        self.new_loan_btn = ctk.CTkButton(self.nav_frame, text="Nuevo Préstamo", command=self._show_new_loan_view, font=get_font("normal", "bold"), text_color=("#222","#fff"))
        self.new_loan_btn.pack(side="left", padx=(0, 5))

        self.history_btn = ctk.CTkButton(self.nav_frame, text="Historial de Préstamos", command=self._show_history_view, font=get_font("normal", "bold"), text_color=("#222","#fff"))
        self.history_btn.pack(side="left", padx=5)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    def _clear_content_frame(self):
        """Clears all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_new_loan_view(self):
        """Displays the form for creating a new room loan."""
        self._clear_content_frame()
        self.new_loan_btn.configure(fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"))
        self.history_btn.configure(fg_color=("#f5f5f5", "#232323"), hover_color=("#ffd3a8", "#9c6d41"))

        title = ctk.CTkLabel(self.content_frame, text="Registrar Nuevo Préstamo de Sala", font=get_font("title", "bold"))
        title.pack(pady=(10, 30))

        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="both", expand=False, padx=0, pady=(0, 10))

        form_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_grid.pack(fill="x", expand=True, padx=20, pady=20)
        form_grid.columnconfigure(1, weight=1)

        # User Type
        ctk.CTkLabel(form_grid, text="Tipo de Usuario:*", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(form_grid, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly", command=self._on_user_type_change)
        self.user_type_combo.set("Estudiante")
        self.user_type_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # User ID (Student Code or Professor Cedula)
        ctk.CTkLabel(form_grid, text="Código/Cédula:*", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.user_id_entry = ctk.CTkEntry(form_grid, placeholder_text="Código de estudiante o cédula de profesor", font=get_font("normal"))
        self.user_id_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # Room
        ctk.CTkLabel(form_grid, text="Sala:*", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.salas_data = [] # Se inicializa vacío y se llena en _on_user_type_change
        self.sala_combo = ctk.CTkComboBox(form_grid, values=["Seleccione una sala..."], font=get_font("normal"), state="readonly")
        self.sala_combo.set("Seleccione una sala...")
        self.sala_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Equipment Number (Conditional)
        self.numero_equipo_label = ctk.CTkLabel(form_grid, text="Número de Equipo:", font=get_font("normal"))
        self.numero_equipo_label.grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.numero_equipo_entry = ctk.CTkEntry(form_grid, placeholder_text="Número del equipo asignado en la sala (opcional)", font=get_font("normal"))
        self.numero_equipo_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        # Lab Technician
        ctk.CTkLabel(form_grid, text="Laboratorista:*", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=10, sticky="w")
        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        lab_names = ["Seleccione..."] + [p[1] for p in self.laboratoristas_data]
        self.lab_combo = ctk.CTkComboBox(form_grid, values=lab_names, font=get_font("normal"), state="readonly")
        self.lab_combo.set(lab_names[0])
        self.lab_combo.grid(row=4, column=1, padx=5, pady=10, sticky="ew")

        # Monitor
        ctk.CTkLabel(form_grid, text="Monitor:", font=get_font("normal")).grid(row=5, column=0, padx=5, pady=10, sticky="w")
        self.monitores_data = self.personal_model.get_monitores()
        monitor_names = ["Seleccione..."] + [p[1] for p in self.monitores_data]
        self.monitor_combo = ctk.CTkComboBox(form_grid, values=monitor_names, font=get_font("normal"), state="readonly")
        self.monitor_combo.set(monitor_names[0])
        self.monitor_combo.grid(row=5, column=1, padx=5, pady=10, sticky="ew")

        # Observations
        ctk.CTkLabel(form_grid, text="Novedad/Observaciones:", font=get_font("normal")).grid(row=6, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(form_grid, height=120, font=get_font("normal"))
        self.obs_textbox.grid(row=6, column=1, padx=5, pady=10, sticky="ew")

        # Save Button
        save_btn = ctk.CTkButton(form_grid, text="Guardar Préstamo", command=self._save_loan, font=get_font("normal", "bold"))
        save_btn.grid(row=7, column=0, columnspan=2, pady=20, padx=5, sticky="ew")

        # Set initial state for conditional field
        self._on_user_type_change()

    def _on_user_type_change(self, event=None):
        """Handles the conditional logic for fields based on user type, including the room list."""
        user_type = self.user_type_combo.get()
        
        if user_type == "Profesor":
            self.numero_equipo_entry.delete(0, 'end')
            self.numero_equipo_entry.configure(state="disabled", placeholder_text="No aplica para profesores")
            self.numero_equipo_label.configure(text="Número de Equipo:") # Sin asterisco
            # Los profesores solo ven salas disponibles
            self.salas_data = self.room_model.get_available_rooms_for_dropdown()
        else: # Estudiante
            self.numero_equipo_entry.configure(state="normal", placeholder_text="Número del equipo asignado en la sala (opcional)")
            self.numero_equipo_label.configure(text="Número de Equipo:") # Sin asterisco
            # Los estudiantes ven todas las salas
            self.salas_data = self.room_model.get_all_rooms_with_id_for_dropdown()

        sala_names = ["Seleccione una sala..."] + [s[1] for s in self.salas_data]
        current_selection = self.sala_combo.get()
        self.sala_combo.configure(values=sala_names)
        # Mantener la selección si aún es válida, de lo contrario, reiniciar
        if current_selection in sala_names:
            self.sala_combo.set(current_selection)
        else:
            self.sala_combo.set(sala_names[0])

    def _save_loan(self):
        """Validates form data and saves the new room loan."""
        user_type = self.user_type_combo.get()
        user_id = self.user_id_entry.get().strip()
        sala_nombre = self.sala_combo.get()
        lab_nombre = self.lab_combo.get()
        
        # --- Initial validation ---
        if not all([user_id, sala_nombre != "Seleccione una sala...", lab_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Código/Cédula, Sala y Laboratorista son obligatorios.", parent=self)
            return

        # --- Conditional validation for student ---
        numero_equipo = None
        if user_type == "Estudiante":
            numero_equipo_str = self.numero_equipo_entry.get().strip()
            if numero_equipo_str:
                try:
                    numero_equipo = int(numero_equipo_str)
                except ValueError:
                    messagebox.showerror("Error de Validación", "El Número de Equipo debe ser un valor numérico si se proporciona.", parent=self)
                    return

        # --- User existence validation (with new profile workflow) ---
        user_exists = self.student_model.get_student_by_code_or_id(user_id) if user_type == "Estudiante" else self.profesor_model.get_professor_by_id(user_id)
        
        if not user_exists:
            if messagebox.askyesno("Crear Nuevo Perfil", f"El {user_type.lower()} con ID '{user_id}' no existe.\n¿Desea crear un nuevo perfil para proceder con el préstamo?", parent=self):
                success = self.student_model.add_blank_student(user_id) if user_type == "Estudiante" else self.profesor_model.add_blank_profesor(user_id)
                if not success:
                    messagebox.showerror("Error", f"No se pudo crear el nuevo perfil. El préstamo ha sido cancelado.", parent=self)
                    return
            else:
                return # User cancelled creation

        # --- Proceed with saving the loan ---
        monitor_nombre = self.monitor_combo.get()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None) if monitor_nombre != "Seleccione..." else None
        
        fecha_entrada = datetime.now()

        # Call the appropriate model method based on user type
        if user_type == "Estudiante":
            result = self.room_loan_model.add_loan_student(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, numero_equipo, observaciones)
        else: # Profesor
            result = self.room_loan_model.add_loan_professor(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, observaciones)

        if result:
            messagebox.showinfo("Éxito", "Préstamo de sala registrado correctamente.", parent=self)
            self._show_new_loan_view()
        else:
            messagebox.showerror("Error en Base de Datos", "No se pudo registrar el préstamo. Verifique que la sala esté disponible.", parent=self)

    def _show_history_view(self):
        """Displays the history of all room loans in a filterable table."""
        self._clear_content_frame()
        self.history_btn.configure(fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"))
        self.new_loan_btn.configure(fg_color=("#f5f5f5", "#232323"), hover_color=("#ffd3a8", "#9c6d41"))
        
        title = ctk.CTkLabel(self.content_frame, text="Historial de Préstamos de Salas", font=get_font("title", "bold"))
        title.pack(pady=(10, 10))
        
        # --- Filter Frame ---
        self.filter_frame = ctk.CTkFrame(self.content_frame)
        self.filter_frame.pack(fill="x", pady=(0, 15), padx=0)
        self.filter_frame.grid_columnconfigure(1, weight=2) # Search entry
        self.filter_frame.grid_columnconfigure(3, weight=1) # User type
        self.filter_frame.grid_columnconfigure(5, weight=1) # Status
        self.filter_frame.grid_columnconfigure(7, weight=1) # Room
        
        ctk.CTkLabel(self.filter_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Usuario, sala...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._apply_filters)
        
        ctk.CTkLabel(self.filter_frame, text="Tipo:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.user_type_filter = ctk.CTkComboBox(self.filter_frame, values=["Todos", "Estudiante", "Profesor"], font=get_font("normal"), command=self._apply_filters)
        self.user_type_filter.set("Todos")
        self.user_type_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.filter_frame, text="Estado:", font=get_font("normal")).grid(row=0, column=4, padx=(10,5), pady=10, sticky="w")
        self.status_filter = ctk.CTkComboBox(self.filter_frame, values=["Todos", "En Préstamo", "Finalizado"], font=get_font("normal"), command=self._apply_filters)
        self.status_filter.set("Todos")
        self.status_filter.grid(row=0, column=5, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(self.filter_frame, text="Sala:", font=get_font("normal")).grid(row=0, column=6, padx=(10,5), pady=10, sticky="w")
        self.all_salas_data = self.room_model.get_all_rooms_with_id_for_dropdown()
        sala_filter_names = ["Todas"] + [s[1] for s in self.all_salas_data]
        self.sala_filter_combo = ctk.CTkComboBox(self.filter_frame, values=sala_filter_names, font=get_font("normal"), command=self._apply_filters)
        self.sala_filter_combo.set("Todas")
        self.sala_filter_combo.grid(row=0, column=7, padx=(5,10), pady=10, sticky="ew")

        # --- Table with Border Frame (as in original file) ---
        table_main_container = ctk.CTkFrame(self.content_frame, corner_radius=8, border_width=1, border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0, 10), padx=0)
        table_container_frame = ctk.CTkFrame(table_main_container, corner_radius=15, fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)
        table_container_frame.grid_rowconfigure(0, weight=1)
        table_container_frame.grid_columnconfigure(0, weight=1)
        
        # NUEVO ORDEN DE COLUMNAS
        columns = ("tipo_usuario", "fecha_entrada", "estado", "usuario_nombre", "usuario_id", "sala_nombre", "laboratorista", "monitor", "hora_salida", "numero_equipo", "firma", "observaciones")
        self.tree = ttk.Treeview(table_container_frame, columns=columns, show="headings", style="Modern.Treeview")
        
        for col, text in [
            ("tipo_usuario", "👤 Tipo"),
            ("fecha_entrada", "📅 Fecha Entrada"),
            ("estado", "📊 Estado"),
            ("usuario_nombre", "👤 Nombre Usuario"),
            ("usuario_id", "🆔 ID"),
            ("sala_nombre", "🚪 Sala"),
            ("laboratorista", "👨‍🔬 Laboratorista"),
            ("monitor", "👥 Monitor"),
            ("hora_salida", "🕒 Hora Salida"),
            ("numero_equipo", "💻 Equipo"),
            ("firma", "✏️ Firma"),
            ("observaciones", "📝 Observaciones")
        ]:
            self.tree.heading(col, text=text, anchor='w')

        for col, width, anchor in [
            ("tipo_usuario", 110, 'w'),
            ("fecha_entrada", 160, 'w'),
            ("estado", 110, 'w'),
            ("usuario_nombre", 250, 'w'),
            ("usuario_id", 130, 'w'),
            ("sala_nombre", 100, 'center'),
            ("laboratorista", 250, 'w'),
            ("monitor", 250, 'w'),
            ("hora_salida", 130, 'center'),
            ("numero_equipo", 100, 'center'),
            ("firma", 120, 'center'),
            ("observaciones", 350, 'w')
        ]:
            self.tree.column(col, width=width, stretch=False, minwidth=width, anchor=anchor)
        self.tree.column("observaciones", stretch=True)

        v_scroll = ctk.CTkScrollbar(table_container_frame, command=self.tree.yview, corner_radius=8, width=16)
        h_scroll = ctk.CTkScrollbar(table_container_frame, command=self.tree.xview, orientation="horizontal", corner_radius=8, height=16)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=(5, 0))
        v_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=(5, 0))
        h_scroll.grid(row=1, column=0, sticky="ew", padx=(5, 0), pady=(0, 5))
        
        self._populate_history_treeview()
        
        # --- Action Buttons (layout matching original file) ---
        self.actions_frame = ctk.CTkFrame(self.content_frame, corner_radius=12)
        self.actions_frame.pack(pady=(15, 0), padx=0, fill="x")
        self.return_btn = ctk.CTkButton(self.actions_frame, text="Registrar Salida", command=self._return_selected_room, state="disabled", font=get_font("normal"), corner_radius=8, height=35, fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"), text_color=("#222","#fff"))
        self.return_btn.pack(side="left", padx=8, pady=8)
        
        # Edit and Delete buttons aligned to the right
        self.delete_btn = ctk.CTkButton(self.actions_frame, text="Eliminar", command=self._delete_selected_loan, state="disabled", fg_color=("#b3261e", "#e4675f"), hover_color=("#8b1e17", "#b8514a"), font=get_font("normal"), corner_radius=8, height=35, text_color=("#222","#fff"))
        self.delete_btn.pack(side="right", padx=8, pady=8)
        self.edit_btn = ctk.CTkButton(self.actions_frame, text="Editar", command=self._edit_selected_loan, state="disabled", font=get_font("normal"), corner_radius=8, height=35, text_color=("#222","#fff"))
        self.edit_btn.pack(side="right", padx=8, pady=8)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_loan_select)
        self._on_loan_select()

    def _apply_filters(self, event=None):
        """Repopulates the history view when a filter changes."""
        if hasattr(self, 'tree'):
            self._populate_history_treeview()

    def _populate_history_treeview(self):
        """Fetches data from the model and populates the Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sala_filter_name = self.sala_filter_combo.get()
        sala_filter_id = next((s[0] for s in self.all_salas_data if s[1] == sala_filter_name), None)

        loans = self.room_loan_model.get_room_loans(
            search_term=self.search_entry.get(),
            user_type_filter=self.user_type_filter.get(),
            status_filter=self.status_filter.get(),
            sala_filter_id=sala_filter_id
        )
        
        # Configurar solo el texto en amarillo para préstamos activos
        current_mode = ctk.get_appearance_mode()
        yellow_fg = '#f59e0b'
        self.tree.tag_configure('active_loan', foreground=yellow_fg)
        self.tree.tag_configure('alternate', background='#323232' if current_mode == "Dark" else '#f8f9fa')

        for i, loan in enumerate(loans):
            (loan_id, tipo_usuario, usuario_nombre, sala_nombre, fecha_entrada, hora_salida, 
             laboratorista, monitor, observaciones, user_id, loan_type, numero_equipo, 
             estado_prestamo, firma) = loan

            f_entrada_str = datetime.fromisoformat(fecha_entrada).strftime('%Y-%m-%d %H:%M')
            values = (
                tipo_usuario,
                f_entrada_str,
                estado_prestamo,
                usuario_nombre or 'N/A',
                user_id or 'N/A',
                sala_nombre or 'N/A',
                laboratorista or 'N/A',
                monitor or 'N/A',
                hora_salida or 'PENDIENTE',
                numero_equipo if numero_equipo is not None else 'N/A',
                firma or '',
                observaciones or ''
            )
            tags = ('alternate',) if i % 2 == 1 else ()
            if estado_prestamo == 'En Préstamo':
                tags += ('active_loan',)
            iid = f"{loan_type}_{loan_id}"
            self.tree.insert("", "end", iid=iid, values=values, tags=tags)
        
        self.loan_data = {f"{loan[10]}_{loan[0]}": loan for loan in loans}

    def _on_loan_select(self, event=None):
        """Updates button states based on the selected loan."""
        selected_iid = self.tree.focus()
        
        if not selected_iid or not (loan_details := self.loan_data.get(selected_iid)):
            self.return_btn.configure(state="disabled")
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            return
        
        # Enable edit and delete for any selected loan
        self.edit_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        
        # Enable "Registrar Salida" only if the loan is active
        if loan_details[12] == 'En Préstamo': # estado_prestamo
            self.return_btn.configure(state="normal")
        else:
            self.return_btn.configure(state="disabled")

    def _return_selected_room(self):
        """Opens the dialog to register the exit from a room."""
        selected_iid = self.tree.focus()
        if not selected_iid or not (loan_details := self.loan_data.get(selected_iid)):
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo activo para registrar la salida.", parent=self)
            return

        dialog = RoomReturnDialog(self, "Registrar Salida de Sala", loan_details)
        if dialog.result:
            self.refresh_loans()

    def _edit_selected_loan(self):
        """Opens the dialog to edit the selected loan."""
        selected_iid = self.tree.focus()
        if not selected_iid or not (loan_summary := self.loan_data.get(selected_iid)):
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo para editar.", parent=self)
            return
        
        # The edit dialog now handles all CRUD operations and models itself
        dialog = RoomEditDialog(
            parent=self, 
            title="Editar Préstamo de Sala", 
            loan_summary=loan_summary,
            loan_model=self.room_loan_model,
            personal_model=self.personal_model,
            student_model=self.student_model,
            profesor_model=self.profesor_model,
            room_model=self.room_model
        )
        if dialog.result:
            self.refresh_loans()

    def _delete_selected_loan(self):
        """Deletes the selected loan record after confirmation."""
        selected_iid = self.tree.focus()
        if not selected_iid or not (loan_details := self.loan_data.get(selected_iid)):
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo para eliminar.", parent=self)
            return
            
        loan_id, loan_type = loan_details[0], loan_details[10]

        if messagebox.askyesno("Confirmar Eliminación", 
                               f"¿Está seguro de que desea eliminar permanentemente el préstamo ID: {loan_id}?",
                               parent=self, icon=messagebox.WARNING):
            
            if self.room_loan_model.delete_loan(loan_id, loan_type):
                messagebox.showinfo("Éxito", "El préstamo ha sido eliminado.", parent=self)
                self.refresh_loans()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el préstamo.", parent=self)
    
    def refresh_loans(self):
        """Refreshes the loan history table."""
        if hasattr(self, 'tree'):
            self._populate_history_treeview()
            self._on_loan_select()
            self.update_idletasks()

# The RoomReturnDialog remains largely the same but is included for completeness
class RoomReturnDialog(ctk.CTkToplevel):
    """Dialog for registering the exit time and signature for a room loan."""
    def __init__(self, parent, title, loan_data):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x320")
        self.transient(parent)
        self.grab_set()
        self.lift()
        
        self.loan_data = loan_data
        self.room_loan_model = RoomLoanModel()
        self.result = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(main_frame, text="Hora de Salida:*", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.hora_salida_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.hora_salida_entry.insert(0, datetime.now().strftime('%H:%M:%S'))
        self.hora_salida_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Firma (ID):*", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.firma_entry = ctk.CTkEntry(main_frame, placeholder_text="Ingrese ID de quien firma la salida", font=get_font("normal"))
        self.firma_entry.insert(0, str(self.loan_data[9])) # user_id
        self.firma_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Novedad/Obs.:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(main_frame, height=100, font=get_font("normal"))
        if self.loan_data[8]: self.obs_textbox.insert("1.0", self.loan_data[8])
        self.obs_textbox.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")
        save_btn = ctk.CTkButton(button_frame, text="Confirmar Salida", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self._center_dialog()
        self.wait_window(self)

    def _center_dialog(self):
        """Centra el diálogo en la ventana padre."""
        self.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")

    def save(self):
        hora_salida = self.hora_salida_entry.get().strip()
        firma = self.firma_entry.get().strip()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        if not all([hora_salida, firma]):
            messagebox.showerror("Error de Validación", "La Hora de Salida y la Firma son obligatorias.", parent=self)
            return
        
        try:
            datetime.strptime(hora_salida, '%H:%M:%S')
        except ValueError:
            messagebox.showerror("Formato incorrecto", "La hora debe estar en formato HH:MM:SS.", parent=self)
            return

        loan_id, loan_type = self.loan_data[0], self.loan_data[10]
        if self.room_loan_model.update_room_loan_exit(loan_id, loan_type, hora_salida, observaciones, firma):
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro de salida.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()

# The new Edit Dialog that allows changing user type and all fields
class RoomEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, loan_summary, loan_model, personal_model, student_model, profesor_model, room_model):
        super().__init__(parent)
        self.title(title)
        self.geometry("900x700")
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.loan_model = loan_model
        self.personal_model = personal_model
        self.student_model = student_model
        self.profesor_model = profesor_model
        self.room_model = room_model
        self.loan_id = loan_summary[0]
        self.original_loan_type = loan_summary[10]
        self.loan_details = self.loan_model.get_room_loan_details(self.loan_id, self.original_loan_type)
        self.result = None

        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="Detalles del Préstamo de Sala")
        scrollable_frame.pack(expand=True, fill="both", padx=15, pady=15)
        scrollable_frame.columnconfigure(1, weight=1)

        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        self.monitores_data = self.personal_model.get_monitores()
        self.salas_data = self.room_model.get_all_rooms_with_id_for_dropdown()

        row_idx = 0
        # Tipo de Usuario
        ctk.CTkLabel(scrollable_frame, text="Tipo de Usuario:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(scrollable_frame, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly")
        self.user_type_combo.set("Estudiante" if self.original_loan_type == "student" else "Profesor")
        self.user_type_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # ID Usuario
        ctk.CTkLabel(scrollable_frame, text="Código/Cédula Usuario:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.user_id_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        # --- Corrección: Mapear índices según tipo de préstamo ---
        self.idx = {
            'id': 0, 'fecha_entrada': 1, 'laboratorista': 2, 'monitor': 3, 'sala_id': 4, 'usuario_id': 5,
            'hora_salida': 6, 'numero_equipo': 7, 'firma': 8, 'observaciones': 9
        } if self.original_loan_type == 'student' else {
            'id': 0, 'fecha_entrada': 1, 'laboratorista': 2, 'monitor': 3, 'sala_id': 4, 'usuario_id': 5,
            'hora_salida': 6, 'firma': 7, 'observaciones': 8, 'numero_equipo': None
        }
        self.user_id_entry.insert(0, self.loan_details[self.idx['usuario_id']])
        self.user_id_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Fecha Entrada
        ctk.CTkLabel(scrollable_frame, text="Fecha Entrada:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.fecha_entrada_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        self.fecha_entrada_entry.insert(0, datetime.fromisoformat(self.loan_details[self.idx['fecha_entrada']]).strftime('%Y-%m-%d %H:%M:%S'))
        self.fecha_entrada_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Hora Salida
        ctk.CTkLabel(scrollable_frame, text="Hora Salida:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.hora_salida_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        if self.loan_details[self.idx['hora_salida']]:
            self.hora_salida_entry.insert(0, self.loan_details[self.idx['hora_salida']])
        self.hora_salida_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Sala
        ctk.CTkLabel(scrollable_frame, text="Sala:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        sala_names = ["Ninguna"] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(scrollable_frame, values=sala_names, font=get_font("normal"), state="readonly")
        current_sala_name = next((s[1] for s in self.salas_data if s[0] == self.loan_details[self.idx['sala_id']]), "Ninguna")
        self.sala_combo.set(current_sala_name)
        self.sala_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Número Equipo
        ctk.CTkLabel(scrollable_frame, text="Número Equipo:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.numero_equipo_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        if self.original_loan_type == 'student' and self.loan_details[self.idx['numero_equipo']] is not None:
            self.numero_equipo_entry.insert(0, str(self.loan_details[self.idx['numero_equipo']]))
        self.numero_equipo_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Laboratorista
        lab_names = ["Ninguno"] + [p[1] for p in self.laboratoristas_data]
        ctk.CTkLabel(scrollable_frame, text="Laboratorista:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.lab_combo = ctk.CTkComboBox(scrollable_frame, values=lab_names, font=get_font("normal"), state="readonly")
        current_lab_name = next((p[1] for p in self.laboratoristas_data if p[0] == self.loan_details[self.idx['laboratorista']]), "Ninguno")
        self.lab_combo.set(current_lab_name)
        self.lab_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Monitor
        monitor_names = ["Ninguno"] + [p[1] for p in self.monitores_data]
        ctk.CTkLabel(scrollable_frame, text="Monitor:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.monitor_combo = ctk.CTkComboBox(scrollable_frame, values=monitor_names, font=get_font("normal"), state="readonly")
        current_monitor_name = next((p[1] for p in self.monitores_data if p[0] == self.loan_details[self.idx['monitor']]), "Ninguno")
        self.monitor_combo.set(current_monitor_name)
        self.monitor_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Firma
        ctk.CTkLabel(scrollable_frame, text="Firma (ID):", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.firma_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        if self.loan_details[self.idx['firma']] is not None and self.loan_details[self.idx['firma']]:
             self.firma_entry.insert(0, self.loan_details[self.idx['firma']])
        self.firma_entry.configure(state="disabled") # La firma no se edita aquí
        self.firma_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Observaciones
        ctk.CTkLabel(scrollable_frame, text="Observaciones:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(scrollable_frame, height=100, font=get_font("normal"))
        if self.loan_details[self.idx['observaciones']]:
            self.obs_textbox.insert("1.0", self.loan_details[self.idx['observaciones']])
        self.obs_textbox.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Botones
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        save_btn = ctk.CTkButton(button_frame, text="Guardar Cambios", command=self.save, font=get_font("normal", "bold"))
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self._center_dialog()
        self.wait_window(self)

    def _center_dialog(self):
        """Centra el diálogo en la ventana padre."""
        self.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")

    def save(self):
        update_data = {}
        # Validar y recolectar datos
        selected_user_type_str = self.user_type_combo.get()
        new_loan_type = "student" if selected_user_type_str == "Estudiante" else "professor"
        new_user_id = self.user_id_entry.get().strip()
        new_fecha_entrada = self.fecha_entrada_entry.get().strip()
        new_hora_salida = self.hora_salida_entry.get().strip()
        sala_nombre = self.sala_combo.get()
        numero_equipo_str = self.numero_equipo_entry.get().strip()
        lab_nombre = self.lab_combo.get()
        monitor_nombre = self.monitor_combo.get()
        # La firma no se recolecta, ya no es editable
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()

        # Validaciones básicas
        if not new_user_id:
            messagebox.showerror("Error", "El Código/Cédula del usuario no puede estar vacío.", parent=self)
            return
        if not new_fecha_entrada:
            messagebox.showerror("Error", "La Fecha de Entrada es obligatoria.", parent=self)
            return
        try:
            new_fecha_entrada_iso = datetime.strptime(new_fecha_entrada, '%Y-%m-%d %H:%M:%S').isoformat()
        except ValueError:
            messagebox.showerror("Formato de Fecha Inválido", "La Fecha de Entrada debe estar en formato YYYY-MM-DD HH:MM:SS.", parent=self)
            return
        # Hora salida puede ser vacía
        new_hora_salida_val = new_hora_salida if new_hora_salida else None

        # Sala
        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        # Número equipo
        numero_equipo_val = None
        if new_loan_type == 'student' and numero_equipo_str:
            try:
                numero_equipo_val = int(numero_equipo_str)
            except ValueError:
                messagebox.showerror("Error", "Número de equipo debe ser numérico si se proporciona.", parent=self)
                return
        # Laboratorista y monitor
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None) if lab_nombre != "Ninguno" else None
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None) if monitor_nombre != "Ninguno" else None

        # Construir update_data
        if new_user_id != str(self.loan_details[self.idx['usuario_id']]):
            update_data['usuario_id'] = new_user_id
        if new_fecha_entrada_iso != self.loan_details[self.idx['fecha_entrada']]:
            update_data['fecha_entrada'] = new_fecha_entrada_iso
        if new_hora_salida_val != self.loan_details[self.idx['hora_salida']]:
            update_data['hora_salida'] = new_hora_salida_val
        if sala_id != self.loan_details[self.idx['sala_id']]:
            update_data['sala_id'] = sala_id
        if new_loan_type == 'student' and numero_equipo_val != self.loan_details[self.idx['numero_equipo']]:
            update_data['numero_equipo'] = numero_equipo_val
        if laboratorista_id != self.loan_details[self.idx['laboratorista']]:
            update_data['laboratorista'] = laboratorista_id
        if monitor_id != self.loan_details[self.idx['monitor']]:
            update_data['monitor'] = monitor_id
        
        obs_idx = self.idx['observaciones']
        if observaciones != (self.loan_details[obs_idx] or ''):
            update_data['novedad' if new_loan_type == 'student' else 'observaciones'] = observaciones

        if not update_data:
            messagebox.showinfo("Sin cambios", "No se detectaron cambios para guardar.", parent=self)
            return

        success = self.loan_model.update_room_loan(self.loan_id, self.original_loan_type, update_data)
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "El préstamo ha sido actualizado correctamente.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el préstamo en la base de datos.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()