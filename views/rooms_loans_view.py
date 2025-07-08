import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import RoomLoanModel, PersonalLaboratorioModel, StudentModel, ProfesorModel, RoomModel, EquiposModel
from utils.font_config import get_font
from datetime import datetime
import os, sys
import cv2
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
        self.equipos_model = EquiposModel()

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
        
        # Create a frame to hold the entry and the button
        user_id_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
        user_id_frame.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        user_id_frame.columnconfigure(0, weight=1) # Make entry expand
        
        self.user_id_entry = ctk.CTkEntry(user_id_frame, placeholder_text="Código de estudiante o cédula de profesor", font=get_font("normal"))
        self.user_id_entry.grid(row=0, column=0, sticky="ew")
        
        # QR Scan Button
        self.scan_btn = ctk.CTkButton(user_id_frame, text="Scan QR", command=self._scan_qr_code, width=80)
        self.scan_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Room
        ctk.CTkLabel(form_grid, text="Sala:*", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.salas_data = [] 
        self.sala_combo = ctk.CTkComboBox(form_grid, values=["Seleccione una sala..."], font=get_font("normal"), state="readonly")
        self.sala_combo.set("Seleccione una sala...")
        self.sala_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Equipment Identifier (Conditional)
        self.equipo_label = ctk.CTkLabel(form_grid, text="Identificador de Equipo:", font=get_font("normal"))
        self.equipo_label.grid(row=3, column=0, padx=5, pady=10, sticky="w")

        equipo_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
        equipo_frame.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        equipo_frame.columnconfigure((0, 2), weight=1)
        equipo_frame.columnconfigure(1, weight=0)

        self.equipo_code_entry = ctk.CTkEntry(equipo_frame, placeholder_text="Código de Equipo")
        self.equipo_code_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(equipo_frame, text="Ó", font=get_font("normal", "bold")).grid(row=0, column=1, padx=5)

        self.equipo_number_entry = ctk.CTkEntry(equipo_frame, placeholder_text="Nro. Equipo en Sala")
        self.equipo_number_entry.grid(row=0, column=2, sticky="ew", padx=(10, 0))

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

        self._on_user_type_change()
    
    def _scan_qr_code(self):
        """Activa la cámara para escanear un QR usando el detector de OpenCV."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error de Cámara", "No se pudo acceder a la cámara del dispositivo.", parent=self)
            return

        # Inicializa el detector de QR de OpenCV
        detector = cv2.QRCodeDetector()
        scanned_code = None

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Detecta y decodifica el código QR
                data, bbox, _ = detector.detectAndDecode(frame)

                # Si se detecta un código QR y tiene datos
                if data:
                    scanned_code = data
                    # Dibuja un polígono alrededor del QR detectado
                    if bbox is not None:
                        # cv2.polylines necesita que los puntos sean enteros
                        points = bbox[0].astype(int)
                        cv2.polylines(frame, [points], True, (0, 255, 0), 2)
                        
                        # Muestra un mensaje de éxito sobre el frame
                        cv2.putText(frame, "Codigo leido!", (points[0][0], points[0][1] - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow("QR Code Scanner - Presione 'q' para cerrar", frame)

                if scanned_code:
                    cv2.waitKey(1000)  # Muestra el mensaje por 1 segundo
                    break

                # Cierra la ventana si se presiona 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        # Actualiza el campo de texto si se escaneó un código
        if scanned_code:
            self.user_id_entry.delete(0, 'end')
            self.user_id_entry.insert(0, scanned_code)
        else:
            messagebox.showinfo("Información", "No se leyó ningún código QR válido.", parent=self)
            
    def _on_user_type_change(self, event=None):
        """Handles the conditional logic for fields based on user type, including the room list."""
        user_type = self.user_type_combo.get()
        
        if user_type == "Profesor":
            self.equipo_code_entry.delete(0, 'end')
            self.equipo_number_entry.delete(0, 'end')
            self.equipo_code_entry.configure(state="disabled")
            self.equipo_number_entry.configure(state="disabled")
            self.equipo_label.configure(text="Identificador de Equipo:") # No asterisk
            self.salas_data = self.room_model.get_available_rooms_for_dropdown()
        else: # Estudiante
            self.equipo_code_entry.configure(state="normal")
            self.equipo_number_entry.configure(state="normal")
            self.equipo_label.configure(text="Identificador de Equipo:*") # With asterisk
            self.salas_data = self.room_model.get_all_rooms_with_id_for_dropdown()

        sala_names = ["Seleccione una sala..."] + [s[1] for s in self.salas_data]
        current_selection = self.sala_combo.get()
        self.sala_combo.configure(values=sala_names)
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
        
        if not all([user_id, sala_nombre != "Seleccione una sala...", lab_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Código/Cédula, Sala y Laboratorista son obligatorios.", parent=self)
            return

        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        if not sala_id:
            messagebox.showerror("Error de Validación", "Debe seleccionar una sala válida.", parent=self)
            return

        equipo_codigo_val = None
        if user_type == "Estudiante":
            equipo_code_str = self.equipo_code_entry.get().strip()
            equipo_number_str = self.equipo_number_entry.get().strip()

            if not equipo_code_str and not equipo_number_str:
                messagebox.showerror("Error de Validación", "Para préstamos a estudiantes, debe proporcionar el Código del Equipo o el Número de Equipo en la sala.", parent=self)
                return
            if equipo_code_str and equipo_number_str:
                messagebox.showwarning("Ambigüedad", "Por favor, proporcione solo el Código del Equipo o el Número de Equipo, no ambos.", parent=self)
                return

            equipo_number_val = None
            if equipo_number_str:
                try:
                    equipo_number_val = int(equipo_number_str)
                except ValueError:
                    messagebox.showerror("Error de Validación", "El Número de Equipo debe ser un valor numérico.", parent=self)
                    return
            
            equipo_encontrado = self.equipos_model.get_equipo_by_identifier(
                sala_id=sala_id,
                codigo=equipo_code_str if equipo_code_str else None,
                numero_equipo=equipo_number_val
            )

            if not equipo_encontrado:
                messagebox.showerror("No Encontrado", "No se encontró el equipo con los datos proporcionados para la sala seleccionada.", parent=self)
                return
            
            if equipo_code_str and equipo_encontrado[1] != sala_id:
                 messagebox.showerror("Error de Ubicación", f"El equipo '{equipo_code_str}' no pertenece a la sala seleccionada.", parent=self)
                 return
            
            equipo_codigo_val = equipo_encontrado[0]

        user_exists = self.student_model.get_student_by_code_or_id(user_id) if user_type == "Estudiante" else self.profesor_model.get_professor_by_id(user_id)
        
        if not user_exists:
            if messagebox.askyesno("Crear Nuevo Perfil", f"El {user_type.lower()} con ID '{user_id}' no existe.\n¿Desea crear un nuevo perfil para proceder con el préstamo?", parent=self):
                success = self.student_model.add_blank_student(user_id) if user_type == "Estudiante" else self.profesor_model.add_blank_profesor(user_id)
                if not success:
                    messagebox.showerror("Error", f"No se pudo crear el nuevo perfil. El préstamo ha sido cancelado.", parent=self)
                    return
            else:
                return

        monitor_nombre = self.monitor_combo.get()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None) if monitor_nombre != "Seleccione..." else None
        
        fecha_entrada = datetime.now()

        if user_type == "Estudiante":
            result = self.room_loan_model.add_loan_student(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, equipo_codigo_val, observaciones)
        else:
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
        
        self.filter_frame = ctk.CTkFrame(self.content_frame)
        self.filter_frame.pack(fill="x", pady=(0, 15), padx=0)
        self.filter_frame.grid_columnconfigure(1, weight=2)
        self.filter_frame.grid_columnconfigure(3, weight=1)
        self.filter_frame.grid_columnconfigure(5, weight=1)
        self.filter_frame.grid_columnconfigure(7, weight=1)
        
        ctk.CTkLabel(self.filter_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Usuario, sala, equipo...", font=get_font("normal"))
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

        table_main_container = ctk.CTkFrame(self.content_frame, corner_radius=8, border_width=1, border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0, 10), padx=0)
        table_container_frame = ctk.CTkFrame(table_main_container, corner_radius=15, fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)
        table_container_frame.grid_rowconfigure(0, weight=1)
        table_container_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("tipo_usuario", "fecha_entrada", "estado", "usuario_nombre", "usuario_id", "sala_nombre", "laboratorista", "monitor", "hora_salida", "numero_equipo", "firma", "observaciones")
        self.tree = ttk.Treeview(table_container_frame, columns=columns, show="headings", style="Modern.Treeview")
        
        for col, text in [
            ("tipo_usuario", "👤 Tipo"), ("fecha_entrada", "📅 Fecha Entrada"), ("estado", "📊 Estado"),
            ("usuario_nombre", "👤 Nombre Usuario"), ("usuario_id", "🆔 ID"), ("sala_nombre", "🚪 Sala"),
            ("laboratorista", "👨‍🔬 Laboratorista"), ("monitor", "👥 Monitor"), ("hora_salida", "🕒 Hora Salida"),
            ("numero_equipo", "💻 Equipo Nro."), ("firma", "✏️ Firma"), ("observaciones", "📝 Observaciones")
        ]:
            self.tree.heading(col, text=text, anchor='w')

        for col, width, anchor in [
            ("tipo_usuario", 110, 'w'), ("fecha_entrada", 160, 'w'), ("estado", 110, 'w'),
            ("usuario_nombre", 250, 'w'), ("usuario_id", 130, 'w'), ("sala_nombre", 100, 'center'),
            ("laboratorista", 250, 'w'), ("monitor", 250, 'w'), ("hora_salida", 130, 'center'),
            ("numero_equipo", 100, 'center'), ("firma", 120, 'center'), ("observaciones", 350, 'w')
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
        
        self.actions_frame = ctk.CTkFrame(self.content_frame, corner_radius=12)
        self.actions_frame.pack(pady=(15, 0), padx=0, fill="x")
        self.return_btn = ctk.CTkButton(self.actions_frame, text="Registrar Salida", command=self._return_selected_room, state="disabled", font=get_font("normal"), corner_radius=8, height=35, fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"), text_color=("#222","#fff"))
        self.return_btn.pack(side="left", padx=8, pady=8)
        
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
        
        current_mode = ctk.get_appearance_mode()
        yellow_fg = '#f59e0b'
        self.tree.tag_configure('active_loan', foreground=yellow_fg)
        self.tree.tag_configure('alternate', background='#323232' if current_mode == "Dark" else '#f8f9fa')

        for i, loan in enumerate(loans):
            (loan_id, tipo_usuario, usuario_nombre, sala_nombre, fecha_entrada, hora_salida, 
             laboratorista, monitor, observaciones, user_id, loan_type, numero_equipo, 
             estado_prestamo, firma, equipo_codigo) = loan

            f_entrada_str = datetime.fromisoformat(fecha_entrada).strftime('%Y-%m-%d %H:%M')
            values = (
                tipo_usuario, f_entrada_str, estado_prestamo,
                usuario_nombre or 'N/A', user_id or 'N/A', sala_nombre or 'N/A',
                laboratorista or 'N/A', monitor or 'N/A', hora_salida or 'PENDIENTE',
                numero_equipo if numero_equipo is not None else 'N/A',
                firma or '', observaciones or ''
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
        
        self.edit_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        
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
        
        dialog = RoomEditDialog(
            parent=self, 
            title="Editar Préstamo de Sala", 
            loan_summary=loan_summary,
            loan_model=self.room_loan_model,
            personal_model=self.personal_model,
            student_model=self.student_model,
            profesor_model=self.profesor_model,
            room_model=self.room_model,
            equipos_model=self.equipos_model
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

class RoomReturnDialog(ctk.CTkToplevel):
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

class RoomEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, loan_summary, loan_model, personal_model, student_model, profesor_model, room_model, equipos_model):
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
        self.equipos_model = equipos_model
        
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

        if self.original_loan_type == 'student':
            self.idx = {'id': 0, 'fecha_entrada': 1, 'laboratorista': 2, 'monitor': 3, 'sala_id': 4, 'usuario_id': 5, 'hora_salida': 6, 'equipo_codigo': 7, 'numero_equipo': 8, 'firma': 9, 'observaciones': 10}
        else:
            self.idx = {'id': 0, 'fecha_entrada': 1, 'laboratorista': 2, 'monitor': 3, 'sala_id': 4, 'usuario_id': 5, 'hora_salida': 6, 'firma': 7, 'observaciones': 8}

        row_idx = 0
        ctk.CTkLabel(scrollable_frame, text="Tipo de Usuario:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(scrollable_frame, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly", command=self._on_user_type_change_edit)
        self.user_type_combo.set("Estudiante" if self.original_loan_type == "student" else "Profesor")
        self.user_type_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Código/Cédula Usuario:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.user_id_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        self.user_id_entry.insert(0, self.loan_details[self.idx['usuario_id']])
        self.user_id_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        self.user_id_entry.bind("<KeyRelease>", self._validate_user_id)
        row_idx += 1

        # Label para mostrar el estado de validación del usuario
        self.user_validation_label = ctk.CTkLabel(scrollable_frame, text="", font=get_font("small"))
        self.user_validation_label.grid(row=row_idx, column=1, padx=5, pady=(0, 10), sticky="w")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Fecha Entrada:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.fecha_entrada_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        self.fecha_entrada_entry.insert(0, datetime.fromisoformat(self.loan_details[self.idx['fecha_entrada']]).strftime('%Y-%m-%d %H:%M:%S'))
        self.fecha_entrada_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Hora Salida:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.hora_salida_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        if self.loan_details[self.idx['hora_salida']]:
            self.hora_salida_entry.insert(0, self.loan_details[self.idx['hora_salida']])
        self.hora_salida_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Sala:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        sala_names = ["Ninguna"] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(scrollable_frame, values=sala_names, font=get_font("normal"), state="readonly")
        current_sala_name = next((s[1] for s in self.salas_data if s[0] == self.loan_details[self.idx['sala_id']]), "Ninguna")
        self.sala_combo.set(current_sala_name)
        self.sala_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Identificador Equipo:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        equipo_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        equipo_frame.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=10)
        equipo_frame.columnconfigure((0, 2), weight=1)
        self.equipo_code_entry = ctk.CTkEntry(equipo_frame, placeholder_text="Código de Equipo")
        self.equipo_code_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(equipo_frame, text="Ó").grid(row=0, column=1, padx=5)
        self.equipo_number_entry = ctk.CTkEntry(equipo_frame, placeholder_text="Nro. Equipo en Sala")
        self.equipo_number_entry.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        if self.original_loan_type == 'student':
            if self.loan_details[self.idx['equipo_codigo']]: self.equipo_code_entry.insert(0, self.loan_details[self.idx['equipo_codigo']])
        else:
            self.equipo_code_entry.configure(state="disabled")
            self.equipo_number_entry.configure(state="disabled")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Laboratorista:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        lab_names = ["Ninguno"] + [p[1] for p in self.laboratoristas_data]
        self.lab_combo = ctk.CTkComboBox(scrollable_frame, values=lab_names, font=get_font("normal"), state="readonly")
        current_lab_name = next((p[1] for p in self.laboratoristas_data if p[0] == self.loan_details[self.idx['laboratorista']]), "Ninguno")
        self.lab_combo.set(current_lab_name)
        self.lab_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Monitor:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        monitor_names = ["Ninguno"] + [p[1] for p in self.monitores_data]
        self.monitor_combo = ctk.CTkComboBox(scrollable_frame, values=monitor_names, font=get_font("normal"), state="readonly")
        current_monitor_name = next((p[1] for p in self.monitores_data if p[0] == self.loan_details[self.idx['monitor']]), "Ninguno")
        self.monitor_combo.set(current_monitor_name)
        self.monitor_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Observaciones:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(scrollable_frame, height=100, font=get_font("normal"))
        if self.loan_details[self.idx['observaciones']]:
            self.obs_textbox.insert("1.0", self.loan_details[self.idx['observaciones']])
        self.obs_textbox.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        save_btn = ctk.CTkButton(button_frame, text="Guardar Cambios", command=self.save, font=get_font("normal", "bold"))
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self._center_dialog()
        self.wait_window(self)

    def _center_dialog(self):
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

    def _on_user_type_change_edit(self, event=None):
        """Maneja el cambio de tipo de usuario en el diálogo de edición."""
        user_type = self.user_type_combo.get()
        # Limpiar validación anterior
        self.user_validation_label.configure(text="")
        # Habilitar/deshabilitar campos de equipo según el tipo
        if user_type == "Profesor":
            self.equipo_code_entry.configure(state="disabled")
            self.equipo_number_entry.configure(state="disabled")
        else:  # Estudiante
            self.equipo_code_entry.configure(state="normal")
            self.equipo_number_entry.configure(state="normal")
        # Validar el código/cédula actual
        self._validate_user_id()

    def _validate_user_id(self, event=None):
        """Valida que el código/cédula ingresado existe en la base de datos correspondiente."""
        user_id = self.user_id_entry.get().strip()
        user_type = self.user_type_combo.get()
        if not user_id:
            self.user_validation_label.configure(text="", text_color=("gray", "gray"))
            return
        # Verificar si el usuario existe en la base de datos correspondiente
        user_exists = False
        if user_type == "Estudiante":
            user_exists = self.student_model.get_student_by_code_or_id(user_id) is not None
        else:  # Profesor
            user_exists = self.profesor_model.get_professor_by_id(user_id) is not None
        if user_exists:
            self.user_validation_label.configure(
                text="✓ Usuario válido", 
                text_color=("green", "lightgreen")
            )
        else:
            self.user_validation_label.configure(
                text="✗ Usuario no encontrado", 
                text_color=("red", "lightcoral")
            )

    def save(self):
        update_data = {}
        new_user_id = self.user_id_entry.get().strip()
        new_fecha_entrada = self.fecha_entrada_entry.get().strip()
        new_hora_salida = self.hora_salida_entry.get().strip()
        sala_nombre = self.sala_combo.get()
        lab_nombre = self.lab_combo.get()
        monitor_nombre = self.monitor_combo.get()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()

        # Validar usuario antes de guardar
        user_type = self.user_type_combo.get()
        if user_type == "Estudiante":
            user_exists = self.student_model.get_student_by_code_or_id(new_user_id) is not None
        else:
            user_exists = self.profesor_model.get_professor_by_id(new_user_id) is not None
        if not user_exists:
            messagebox.showerror("Error de Validación", f"El {user_type.lower()} con ID '{new_user_id}' no existe en la base de datos. No se puede guardar.", parent=self)
            return

        if not new_user_id or not new_fecha_entrada:
            messagebox.showerror("Error", "El ID de usuario y la fecha de entrada son obligatorios.", parent=self)
            return
        try:
            new_fecha_entrada_iso = datetime.strptime(new_fecha_entrada, '%Y-%m-%d %H:%M:%S').isoformat()
        except ValueError:
            messagebox.showerror("Formato Inválido", "La fecha debe estar en formato YYYY-MM-DD HH:MM:SS.", parent=self)
            return

        # Build update_data dictionary with changes
        if new_user_id != str(self.loan_details[self.idx['usuario_id']]): update_data['usuario_id'] = new_user_id
        if new_fecha_entrada_iso != self.loan_details[self.idx['fecha_entrada']]: update_data['fecha_entrada'] = new_fecha_entrada_iso
        if (new_hora_salida or None) != self.loan_details[self.idx['hora_salida']]: update_data['hora_salida'] = new_hora_salida or None
        
        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        if sala_id != self.loan_details[self.idx['sala_id']]: update_data['sala_id'] = sala_id

        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        if laboratorista_id != self.loan_details[self.idx['laboratorista']]: update_data['laboratorista'] = laboratorista_id

        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)
        if monitor_id != self.loan_details[self.idx['monitor']]: update_data['monitor'] = monitor_id

        obs_key = 'novedad' if self.original_loan_type == 'student' else 'observaciones'
        if observaciones != (self.loan_details[self.idx['observaciones']] or ''): update_data[obs_key] = observaciones

        if self.original_loan_type == 'student':
            equipo_code_str = self.equipo_code_entry.get().strip()
            equipo_number_str = self.equipo_number_entry.get().strip()
            new_equipo_codigo = None
            if equipo_code_str and equipo_number_str:
                messagebox.showwarning("Ambigüedad", "Proporcione solo el Código o el Número de Equipo, no ambos.", parent=self)
                return
            elif equipo_code_str or equipo_number_str:
                equipo_number_val = int(equipo_number_str) if equipo_number_str else None
                equipo_encontrado = self.equipos_model.get_equipo_by_identifier(sala_id, equipo_code_str, equipo_number_val)
                if not equipo_encontrado:
                    messagebox.showerror("No Encontrado", "El equipo no se encontró para la sala seleccionada.", parent=self)
                    return
                new_equipo_codigo = equipo_encontrado[0]
            
            if new_equipo_codigo != self.loan_details[self.idx['equipo_codigo']]:
                update_data['equipo_codigo'] = new_equipo_codigo

        if not update_data:
            messagebox.showinfo("Sin cambios", "No se detectaron cambios para guardar.", parent=self)
            return

        if self.loan_model.update_room_loan(self.loan_id, self.original_loan_type, update_data):
            self.result = True
            messagebox.showinfo("Éxito", "El préstamo ha sido actualizado.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el préstamo.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()
