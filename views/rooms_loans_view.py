import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import RoomLoanModel, RoomModel, PersonalLaboratorioModel, StudentModel, ProfesorModel
from utils.font_config import get_font
from datetime import datetime

class RoomLoansView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        # Inicializar modelos
        self.room_loan_model = RoomLoanModel()
        self.room_model = RoomModel()
        self.personal_model = PersonalLaboratorioModel()
        self.student_model = StudentModel()
        self.profesor_model = ProfesorModel()

        self.setup_ui()
        self._show_new_loan_view() # Mostrar la vista de nuevo préstamo por defecto

    def setup_ui(self):
        # Frame para los botones de navegación de la vista
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=10, padx=20, fill="x")

        self.new_loan_btn = ctk.CTkButton(self.nav_frame, text="Nuevo Préstamo", command=self._show_new_loan_view, font=get_font("normal", "bold"))
        self.new_loan_btn.pack(side="left", padx=5)

        self.history_btn = ctk.CTkButton(self.nav_frame, text="Historial de Préstamos", command=self._show_history_view, font=get_font("normal", "bold"))
        self.history_btn.pack(side="left", padx=5)

        # Frame principal para el contenido
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_new_loan_view(self):
        self._clear_content_frame()
        self.new_loan_btn.configure(fg_color=("#ffa154", "#c95414"))
        self.history_btn.configure(fg_color=("gray70", "gray30"))

        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(form_frame, text="Registrar Nuevo Préstamo de Sala", font=get_font("title", "bold"))
        title.pack(anchor="w", pady=(0, 20))

        # --- Formulario ---
        form_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_grid.pack(fill="x", expand=True)
        form_grid.columnconfigure(1, weight=1)

        # Tipo de usuario
        ctk.CTkLabel(form_grid, text="Tipo de Usuario:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(form_grid, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly")
        self.user_type_combo.set("Estudiante")
        self.user_type_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Sala
        ctk.CTkLabel(form_grid, text="Sala Disponible:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.salas_data = self.room_model.get_available_rooms_for_dropdown()
        sala_names = ["Seleccione una sala..."] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(form_grid, values=sala_names, font=get_font("normal"), state="readonly")
        self.sala_combo.set(sala_names[0])
        self.sala_combo.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # ID Usuario (Código o Cédula)
        ctk.CTkLabel(form_grid, text="Código/Cédula:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.user_id_entry = ctk.CTkEntry(form_grid, placeholder_text="Código de estudiante o cédula de profesor", font=get_font("normal"))
        self.user_id_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Laboratorista
        ctk.CTkLabel(form_grid, text="Laboratorista:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        lab_names = ["Seleccione..."] + [p[1] for p in self.laboratoristas_data]
        self.lab_combo = ctk.CTkComboBox(form_grid, values=lab_names, font=get_font("normal"), state="readonly")
        self.lab_combo.set(lab_names[0])
        self.lab_combo.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        # Monitor
        ctk.CTkLabel(form_grid, text="Monitor:", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=10, sticky="w")
        self.monitores_data = self.personal_model.get_monitores()
        monitor_names = ["Seleccione..."] + [p[1] for p in self.monitores_data]
        self.monitor_combo = ctk.CTkComboBox(form_grid, values=monitor_names, font=get_font("normal"), state="readonly")
        self.monitor_combo.set(monitor_names[0])
        self.monitor_combo.grid(row=4, column=1, padx=5, pady=10, sticky="ew")

        # Observaciones
        ctk.CTkLabel(form_grid, text="Observaciones:", font=get_font("normal")).grid(row=5, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(form_grid, height=120, font=get_font("normal"))
        self.obs_textbox.grid(row=5, column=1, padx=5, pady=10, sticky="ew")

        # Botón de guardar
        save_btn = ctk.CTkButton(form_grid, text="Guardar Préstamo", command=self._save_loan, font=get_font("normal", "bold"))
        save_btn.grid(row=6, column=0, columnspan=2, pady=20, padx=5, sticky="ew")

    def _save_loan(self):
        user_type = self.user_type_combo.get()
        sala_nombre = self.sala_combo.get()
        user_id = self.user_id_entry.get().strip()
        lab_nombre = self.lab_combo.get()
        monitor_nombre = self.monitor_combo.get()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        # --- Validaciones ---
        if not all([user_type, sala_nombre != "Seleccione una sala...", user_id, lab_nombre != "Seleccione...", monitor_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Todos los campos (excepto observaciones) son obligatorios.", parent=self)
            return

        # Validar existencia de usuario
        user_exists = None
        if user_type == "Estudiante":
            user_exists = self.student_model.get_student_by_code_or_id(user_id)
        else:
            user_exists = self.profesor_model.get_professor_by_id(user_id)
        
        if not user_exists:
            messagebox.showerror("Usuario no encontrado", f"No se encontró un {user_type.lower()} con el identificador '{user_id}'.", parent=self)
            return

        # Obtener IDs
        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)
        fecha_entrada = datetime.now()

        # Guardar en la base de datos
        if user_type == "Estudiante":
            result = self.room_loan_model.add_loan_student(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, None, observaciones)
        else: # Profesor
            result = self.room_loan_model.add_loan_professor(fecha_entrada, laboratorista_id, monitor_id, sala_id, user_id, observaciones)

        if result:
            messagebox.showinfo("Éxito", "Préstamo registrado correctamente.", parent=self)
            self._show_new_loan_view() # Recargar para limpiar formulario y actualizar salas
        else:
            messagebox.showerror("Error en Base de Datos", "No se pudo registrar el préstamo.", parent=self)

    def _show_history_view(self):
        self._clear_content_frame()
        self.history_btn.configure(fg_color=("#ffa154", "#c95414"))
        self.new_loan_btn.configure(fg_color=("gray70", "gray30"))

        # --- Tabla de historial ---
        table_container = ctk.CTkFrame(self.content_frame)
        table_container.pack(fill="both", expand=True, padx=0, pady=10)

        columns = ("tipo_usuario", "usuario_nombre", "sala_nombre", "fecha_entrada", "hora_salida", "laboratorista", "monitor", "observaciones")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Modern.Treeview")
        
        # Cabeceras
        self.tree.heading("tipo_usuario", text="Tipo Usuario", anchor='w')
        self.tree.heading("usuario_nombre", text="Nombre Usuario", anchor='w')
        self.tree.heading("sala_nombre", text="Sala", anchor='w')
        self.tree.heading("fecha_entrada", text="Fecha Entrada", anchor='w')
        self.tree.heading("hora_salida", text="Hora Salida", anchor='w')
        self.tree.heading("laboratorista", text="Laboratorista", anchor='w')
        self.tree.heading("monitor", text="Monitor", anchor='w')
        self.tree.heading("observaciones", text="Observaciones", anchor='w')

        # Columnas
        self.tree.column("tipo_usuario", width=100, stretch=False)
        self.tree.column("usuario_nombre", width=200)
        self.tree.column("sala_nombre", width=150)
        self.tree.column("fecha_entrada", width=150)
        self.tree.column("hora_salida", width=100, anchor='center')
        self.tree.column("laboratorista", width=150)
        self.tree.column("monitor", width=150)
        self.tree.column("observaciones", width=300)

        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Scrollbars
        v_scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        v_scroll.pack(side="right", fill="y")
        h_scroll = ctk.CTkScrollbar(table_container, command=self.tree.xview, orientation="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self._populate_history_treeview()
        
        # --- Botones de acción ---
        actions_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=10)
        
        self.finalize_btn = ctk.CTkButton(actions_frame, text="Finalizar Préstamo Seleccionado", command=self._finalize_selected_loan, state="disabled", font=get_font("normal"))
        self.finalize_btn.pack(side="left")

        self.tree.bind("<<TreeviewSelect>>", self._on_loan_select)

    def _populate_history_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        loans = self.room_loan_model.get_room_loans()
        
        self.tree.tag_configure('active_loan', foreground=("#f59e0b"))

        for loan in loans:
            loan_id, tipo, nombre, sala, f_entrada, h_salida, lab, mon, obs, user_id, loan_type = loan
            
            # Formatear datos
            fecha_entrada_dt = datetime.fromisoformat(f_entrada)
            f_entrada_str = fecha_entrada_dt.strftime('%Y-%m-%d %H:%M')
            h_salida_str = h_salida if h_salida else "PENDIENTE"
            
            values = (tipo, nombre, sala, f_entrada_str, h_salida_str, lab or 'N/A', mon or 'N/A', obs or '')
            
            tags = ()
            if not h_salida:
                tags = ('active_loan',)
            
            self.tree.insert("", "end", iid=f"{loan_type}_{loan_id}", values=values, tags=tags)
        
        # Guardar datos completos para usarlos después
        self.loan_data = {f"{loan[10]}_{loan[0]}": loan for loan in loans}


    def _on_loan_select(self, event=None):
        selected_iid = self.tree.focus()
        if not selected_iid:
            self.finalize_btn.configure(state="disabled")
            return
        
        loan_details = self.loan_data.get(selected_iid)
        if loan_details and not loan_details[5]: # Si hora_salida (índice 5) es None
            self.finalize_btn.configure(state="normal")
        else:
            self.finalize_btn.configure(state="disabled")

    def _finalize_selected_loan(self):
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo activo para finalizar.", parent=self)
            return

        loan_details = self.loan_data.get(selected_iid)
        if not loan_details: return

        dialog = LoanFinalizationDialog(self, "Finalizar Préstamo", loan_details)
        if dialog.result:
            self.refresh_loans() # Recargar la lista de préstamos
    
    def refresh_loans(self):
        if hasattr(self, 'tree'):
            self._populate_history_treeview()
            self._on_loan_select()
            self.update_idletasks()

    def on_theme_change(self):
        self.refresh_loans()

class LoanFinalizationDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, loan_data):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x300")
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.loan_data = loan_data
        self.room_loan_model = RoomLoanModel()
        self.result = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)

        # Hora de salida
        ctk.CTkLabel(main_frame, text="Hora de Salida:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.hora_salida_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.hora_salida_entry.insert(0, datetime.now().strftime('%H:%M:%S'))
        self.hora_salida_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Observaciones de salida
        ctk.CTkLabel(main_frame, text="Observaciones\n(Salida):", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(main_frame, height=80, font=get_font("normal"))
        self.obs_textbox.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        if self.loan_data[8]: # Cargar observaciones existentes
            self.obs_textbox.insert("1.0", self.loan_data[8])

        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

        save_btn = ctk.CTkButton(button_frame, text="Confirmar Salida", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self.wait_window(self)

    def save(self):
        hora_salida = self.hora_salida_entry.get().strip()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        try:
            datetime.strptime(hora_salida, '%H:%M:%S')
        except ValueError:
            messagebox.showerror("Formato incorrecto", "La hora debe estar en formato HH:MM:SS (ej. 14:30:00).", parent=self)
            return

        loan_id = self.loan_data[0]
        loan_type = self.loan_data[10]
        user_id_for_signature = self.loan_data[9]

        success = self.room_loan_model.update_room_loan_exit(loan_id, loan_type, hora_salida, observaciones, firma=user_id_for_signature)
        
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "La salida ha sido registrada.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro del préstamo.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()