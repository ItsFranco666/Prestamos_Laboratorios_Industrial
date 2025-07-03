import customtkinter as ctk
from tkinter import messagebox, ttk
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
        self.salas_data = self.room_model.get_available_rooms_for_dropdown()
        sala_names = ["Seleccione una sala..."] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(form_grid, values=sala_names, font=get_font("normal"), state="readonly")
        self.sala_combo.set(sala_names[0])
        self.sala_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Equipment Number (Conditional)
        self.numero_equipo_label = ctk.CTkLabel(form_grid, text="Número de Equipo:*", font=get_font("normal"))
        self.numero_equipo_label.grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.numero_equipo_entry = ctk.CTkEntry(form_grid, placeholder_text="Número del equipo asignado en la sala", font=get_font("normal"))
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
        """Handles the conditional logic for the 'Número de Equipo' field."""
        user_type = self.user_type_combo.get()
        if user_type == "Profesor":
            self.numero_equipo_entry.delete(0, 'end')
            self.numero_equipo_entry.configure(state="disabled", placeholder_text="No aplica para profesores")
            self.numero_equipo_label.configure(text="Número de Equipo:") # Remove asterisk
        else: # Estudiante
            self.numero_equipo_entry.configure(state="normal", placeholder_text="Número del equipo asignado en la sala")
            self.numero_equipo_label.configure(text="Número de Equipo:*") # Add asterisk

    def _save_loan(self):
        """Validates form data and saves the new room loan."""
        user_type = self.user_type_combo.get()
        user_id = self.user_id_entry.get().strip()
        sala_nombre = self.sala_combo.get()
        lab_nombre = self.lab_combo.get()
        numero_equipo_str = self.numero_equipo_entry.get().strip()

        # --- Initial validation ---
        if not all([user_id, sala_nombre != "Seleccione una sala...", lab_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Tipo de Usuario, Código/Cédula, Sala y Laboratorista son obligatorios.", parent=self)
            return

        # --- Conditional validation for student ---
        numero_equipo = 0
        if user_type == "Estudiante":
            if not numero_equipo_str:
                messagebox.showerror("Error de Validación", "El Número de Equipo es obligatorio para estudiantes.", parent=self)
                return
            try:
                numero_equipo = int(numero_equipo_str)
            except ValueError:
                messagebox.showerror("Error de Validación", "El Número de Equipo debe ser un valor numérico.", parent=self)
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
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)
        
        fecha_entrada = datetime.now()

        if user_type == "Estudiante":
            result = self.room_loan_model.add_loan_student(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, numero_equipo, observaciones)
        else: # Profesor
            result = self.room_loan_model.add_loan_professor(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, observaciones)

        if result:
            messagebox.showinfo("Éxito", "Préstamo de sala registrado correctamente.", parent=self)
            self._show_new_loan_view()
        else:
            messagebox.showerror("Error en Base de Datos", "No se pudo registrar el préstamo. Verifique los datos e intente de nuevo.", parent=self)

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
        self.filter_frame.grid_columnconfigure(1, weight=3)
        
        ctk.CTkLabel(self.filter_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Usuario, sala, # equipo...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._apply_filters)
        
        ctk.CTkLabel(self.filter_frame, text="Tipo:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.user_type_filter = ctk.CTkComboBox(self.filter_frame, values=["Todos", "Estudiante", "Profesor"], font=get_font("normal"), command=self._apply_filters)
        self.user_type_filter.set("Todos")
        self.user_type_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.filter_frame, text="Estado:", font=get_font("normal")).grid(row=0, column=4, padx=(10,5), pady=10, sticky="w")
        self.status_filter = ctk.CTkComboBox(self.filter_frame, values=["Todos", "En Préstamo", "Finalizado"], font=get_font("normal"), command=self._apply_filters)
        self.status_filter.set("Todos")
        self.status_filter.grid(row=0, column=5, padx=(5,10), pady=10, sticky="ew")
        
        # --- Table and Actions ---
        table_container = ctk.CTkFrame(self.content_frame)
        table_container.pack(fill="both", expand=True, pady=(0, 10), padx=0)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        columns = ("estado", "tipo_usuario", "usuario_nombre", "sala_nombre", "fecha_entrada", "hora_salida", "numero_equipo", "laboratorista", "monitor", "firma", "observaciones")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Modern.Treeview")
        
        # Configure headers
        for col, text in [("estado", "📊 Estado"), ("tipo_usuario", "👤 Tipo"), ("usuario_nombre", "👤 Nombre Usuario"), 
                           ("sala_nombre", "🚪 Sala"), ("fecha_entrada", "📅 Fecha Entrada"), ("hora_salida", "🕒 Hora Salida"),
                           ("numero_equipo", "💻 # Equipo"), ("laboratorista", "👨‍🔬 Laboratorista"), ("monitor", "👥 Monitor"),
                           ("firma", "✏️ Firma"), ("observaciones", "📝 Obs.")]:
            self.tree.heading(col, text=text, anchor='w')

        # Configure column widths
        for col, width in [("estado", 100), ("tipo_usuario", 100), ("usuario_nombre", 200), ("sala_nombre", 150),
                           ("fecha_entrada", 150), ("hora_salida", 120), ("numero_equipo", 80), ("laboratorista", 180),
                           ("monitor", 180), ("firma", 100), ("observaciones", 250)]:
            self.tree.column(col, width=width, stretch=False, minwidth=width)
        self.tree.column("observaciones", stretch=True)

        # Scrollbars
        v_scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        h_scroll = ctk.CTkScrollbar(table_container, command=self.tree.xview, orientation="horizontal")
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        self._populate_history_treeview()
        
        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.content_frame)
        self.actions_frame.pack(pady=(15, 0), padx=0, fill="x")
        self.return_btn = ctk.CTkButton(self.actions_frame, text="Registrar Salida", command=self._return_selected_room, state="disabled", fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"), text_color=("#222","#fff"))
        self.return_btn.pack(side="left", padx=8, pady=8)
        self.delete_btn = ctk.CTkButton(self.actions_frame, text="Eliminar", command=self._delete_selected_loan, state="disabled", fg_color=("#b3261e", "#e4675f"), hover_color=("#8b1e17", "#b8514a"), text_color=("#222","#fff"))
        self.delete_btn.pack(side="right", padx=8, pady=8)
        
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
        
        loans = self.room_loan_model.get_room_loans(
            search_term=self.search_entry.get(),
            user_type_filter=self.user_type_filter.get(),
            status_filter=self.status_filter.get()
        )
        
        for i, loan in enumerate(loans):
            (loan_id, tipo_usuario, usuario_nombre, sala_nombre, fecha_entrada, hora_salida, 
             laboratorista, monitor, observaciones, user_id, loan_type, numero_equipo, 
             estado_prestamo, firma) = loan

            f_entrada_str = datetime.fromisoformat(fecha_entrada).strftime('%Y-%m-%d %H:%M')
            
            values = (
                estado_prestamo, tipo_usuario, usuario_nombre or 'N/A', sala_nombre or 'N/A', f_entrada_str,
                hora_salida or 'PENDIENTE', numero_equipo if numero_equipo is not None else 'N/A',
                laboratorista or 'N/A', monitor or 'N/A', firma or '', observaciones or ''
            )
            
            iid = f"{loan_type}_{loan_id}"
            self.tree.insert("", "end", iid=iid, values=values)
        
        self.loan_data = {f"{loan[10]}_{loan[0]}": loan for loan in loans}

    def _on_loan_select(self, event=None):
        """Updates button states based on the selected loan."""
        selected_iid = self.tree.focus()
        
        if not selected_iid or not (loan_details := self.loan_data.get(selected_iid)):
            self.return_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            return
        
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

class RoomReturnDialog(ctk.CTkToplevel):
    """Dialog for registering the exit time and signature for a room loan."""
    def __init__(self, parent, title, loan_data):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        self.lift()
        
        self.loan_data = loan_data
        self.room_loan_model = RoomLoanModel()
        self.result = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)

        # Hora de Salida
        ctk.CTkLabel(main_frame, text="Hora de Salida:*", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.hora_salida_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.hora_salida_entry.insert(0, datetime.now().strftime('%H:%M:%S'))
        self.hora_salida_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Firma
        ctk.CTkLabel(main_frame, text="Firma (ID):*", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.firma_entry = ctk.CTkEntry(main_frame, placeholder_text="Ingrese ID de quien firma la salida", font=get_font("normal"))
        # Pre-fill with the borrower's ID as a default
        self.firma_entry.insert(0, str(self.loan_data[9])) # user_id
        self.firma_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # Observaciones
        ctk.CTkLabel(main_frame, text="Novedad/Obs.:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(main_frame, height=100, font=get_font("normal"))
        self.obs_textbox.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if self.loan_data[8]: # Load existing observations
            self.obs_textbox.insert("1.0", self.loan_data[8])

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")
        save_btn = ctk.CTkButton(button_frame, text="Confirmar Salida", command=self.save)
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray")
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self.wait_window(self)

    def save(self):
        hora_salida = self.hora_salida_entry.get().strip()
        firma = self.firma_entry.get().strip()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        # Validation
        if not all([hora_salida, firma]):
            messagebox.showerror("Error de Validación", "La Hora de Salida y la Firma son obligatorias.", parent=self)
            return
        
        try:
            datetime.strptime(hora_salida, '%H:%M:%S')
        except ValueError:
            messagebox.showerror("Formato incorrecto", "La hora debe estar en formato HH:MM:SS (ej. 14:30:00).", parent=self)
            return

        loan_id, loan_type = self.loan_data[0], self.loan_data[10]

        success = self.room_loan_model.update_room_loan_exit(loan_id, loan_type, hora_salida, observaciones, firma)
        
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "La salida ha sido registrada correctamente.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro de salida.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()