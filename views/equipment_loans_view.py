import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import EquipmentLoanModel, InventoryModel, PersonalLaboratorioModel, StudentModel, ProfesorModel, RoomModel
from utils.font_config import get_font
from datetime import datetime
import os, sys
from PIL import Image, ImageTk

class EquipmentLoansView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15, fill="both", expand=True) # Padding general para la vista

        # Inicializar modelos
        self.equipment_loan_model = EquipmentLoanModel()
        self.inventory_model = InventoryModel()
        self.personal_model = PersonalLaboratorioModel()
        self.student_model = StudentModel()
        self.profesor_model = ProfesorModel()
        self.room_model = RoomModel()

        self.setup_ui()
        self._show_new_loan_view() # Mostrar la vista de nuevo préstamo por defecto

    def setup_ui(self):
        # Frame para los botones de navegación de la vista
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=(0, 15), padx=0, fill="x")

        self.new_loan_btn = ctk.CTkButton(self.nav_frame, text="Nuevo Préstamo", command=self._show_new_loan_view, font=get_font("normal", "bold"), text_color=("#222","#fff"))
        self.new_loan_btn.pack(side="left", padx=(0, 5))

        self.history_btn = ctk.CTkButton(self.nav_frame, text="Historial de Préstamos", command=self._show_history_view, font=get_font("normal", "bold"), text_color=("#222","#fff"))
        self.history_btn.pack(side="left", padx=5)

        # Frame principal para el contenido
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_new_loan_view(self):
        self._clear_content_frame()
        self.new_loan_btn.configure(fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"))
        self.history_btn.configure(fg_color=("#f5f5f5", "#232323"), hover_color=("#ffd3a8", "#9c6d41"))

        # Título independiente del formulario (similar a StudentsView)
        title = ctk.CTkLabel(self.content_frame, text="Registrar Nuevo Préstamo de Equipo", font=get_font("title", "bold"))
        title.pack(pady=(10, 30))

        # Frame del formulario con marco
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="both", expand=False, padx=0, pady=(0, 10))

        # --- Formulario ---
        form_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_grid.pack(fill="x", expand=True, padx=20, pady=20)
        form_grid.columnconfigure(1, weight=1)

        # Tipo de usuario
        ctk.CTkLabel(form_grid, text="Tipo de Usuario:*", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(form_grid, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly")
        self.user_type_combo.set("Estudiante")
        self.user_type_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Código del Equipo (Reemplazado ComboBox por Entry)
        ctk.CTkLabel(form_grid, text="Código del Equipo:*", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.equipo_code_entry = ctk.CTkEntry(form_grid, placeholder_text="Ingrese el código del equipo a prestar", font=get_font("normal"))
        self.equipo_code_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Sala
        ctk.CTkLabel(form_grid, text="Sala:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.salas_data = self.room_model.get_all_rooms_with_id_for_dropdown()
        sala_names = ["Seleccione una sala..."] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(form_grid, values=sala_names, font=get_font("normal"), state="readonly")
        self.sala_combo.set(sala_names[0])
        self.sala_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # ID Usuario (Código o Cédula)
        ctk.CTkLabel(form_grid, text="Código/Cédula:*", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.user_id_entry = ctk.CTkEntry(form_grid, placeholder_text="Código de estudiante o cédula de profesor", font=get_font("normal"))
        self.user_id_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        # Número de estudiantes (solo para estudiantes)
        ctk.CTkLabel(form_grid, text="Número de Estudiantes:", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=10, sticky="w")
        self.num_estudiantes_entry = ctk.CTkEntry(form_grid, placeholder_text="Solo para estudiantes", font=get_font("normal"))
        self.num_estudiantes_entry.grid(row=4, column=1, padx=5, pady=10, sticky="ew")

        # Título de la práctica
        ctk.CTkLabel(form_grid, text="Título de la Práctica:", font=get_font("normal")).grid(row=5, column=0, padx=5, pady=10, sticky="w")
        self.titulo_practica_entry = ctk.CTkEntry(form_grid, placeholder_text="Título de la práctica o actividad", font=get_font("normal"))
        self.titulo_practica_entry.grid(row=5, column=1, padx=5, pady=10, sticky="ew")

        # Laboratorista
        ctk.CTkLabel(form_grid, text="Laboratorista:*", font=get_font("normal")).grid(row=6, column=0, padx=5, pady=10, sticky="w")
        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        lab_names = ["Seleccione..."] + [p[1] for p in self.laboratoristas_data]
        self.lab_combo = ctk.CTkComboBox(form_grid, values=lab_names, font=get_font("normal"), state="readonly")
        self.lab_combo.set(lab_names[0])
        self.lab_combo.grid(row=6, column=1, padx=5, pady=10, sticky="ew")

        # Monitor
        ctk.CTkLabel(form_grid, text="Monitor:", font=get_font("normal")).grid(row=7, column=0, padx=5, pady=10, sticky="w")
        self.monitores_data = self.personal_model.get_monitores()
        monitor_names = ["Seleccione..."] + [p[1] for p in self.monitores_data]
        self.monitor_combo = ctk.CTkComboBox(form_grid, values=monitor_names, font=get_font("normal"), state="readonly")
        self.monitor_combo.set(monitor_names[0])
        self.monitor_combo.grid(row=7, column=1, padx=5, pady=10, sticky="ew")

        # Observaciones
        ctk.CTkLabel(form_grid, text="Observaciones:", font=get_font("normal")).grid(row=8, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(form_grid, height=120, font=get_font("normal"))
        self.obs_textbox.grid(row=8, column=1, padx=5, pady=10, sticky="ew")

        # Botón de guardar
        save_btn = ctk.CTkButton(form_grid, text="Guardar Préstamo", command=self._save_loan, font=get_font("normal", "bold"))
        save_btn.grid(row=9, column=0, columnspan=2, pady=20, padx=5, sticky="ew")

    def _save_loan(self):
        user_type = self.user_type_combo.get()
        equipo_codigo = self.equipo_code_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        lab_nombre = self.lab_combo.get()
        
        # --- Validaciones de campos obligatorios ---
        if not all([equipo_codigo, user_id, lab_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Código de Equipo, Código/Cédula de Usuario y Laboratorista son obligatorios.", parent=self)
            return

        # --- Validación de existencia de Equipo ---
        equipo_info = self.inventory_model.get_equipment_by_code(equipo_codigo)
        if not equipo_info:
            # Alerta de que no existe
            messagebox.showerror("Equipo no encontrado", f"El equipo con código '{equipo_codigo}' no existe en la base de datos.", parent=self)
            # Preguntar si se desea añadir
            if messagebox.askyesno("Crear Nuevo Equipo", f"¿Desea agregar '{equipo_codigo}' como un nuevo equipo al inventario?", parent=self):
                # Crear registro en blanco
                if not self.inventory_model.add_blank_equipment(equipo_codigo):
                    messagebox.showerror("Error", "No se pudo crear el nuevo equipo. El préstamo ha sido cancelado.", parent=self)
                    return # Cancelar si la creación falla
                # Si se crea, se puede continuar, ya que el estado por defecto es 'DISPONIBLE'
            else:
                # Si el usuario dice no, cancelar el préstamo
                return

        # Si el equipo ya existía, verificar su estado
        else:
            # El índice 6 corresponde al 'estado' del equipo
            if equipo_info[6] != 'DISPONIBLE':
                messagebox.showerror("Equipo no disponible", f"El equipo con código '{equipo_codigo}' se encuentra '{equipo_info[6]}'. No se puede prestar.", parent=self)
                return

        # --- Validación de existencia de Usuario ---
        user_exists = None
        if user_type == "Estudiante":
            user_exists = self.student_model.get_student_by_code_or_id(user_id)
        else: # Profesor
            user_exists = self.profesor_model.get_professor_by_id(user_id)
        
        if not user_exists:
            # Alerta de que no existe
            messagebox.showerror("Usuario no encontrado", f"El {user_type.lower()} con identificador '{user_id}' no existe en la base de datos.", parent=self)
            # Preguntar si se desea añadir
            if messagebox.askyesno("Crear Nuevo Usuario", f"¿Desea crear un nuevo perfil de {user_type.lower()} para '{user_id}'?", parent=self):
                # Crear registro en blanco según el tipo
                success = False
                if user_type == "Estudiante":
                    success = self.student_model.add_blank_student(user_id)
                else: # Profesor
                    success = self.profesor_model.add_blank_profesor(user_id)
                
                if not success:
                    messagebox.showerror("Error", f"No se pudo crear el nuevo perfil de {user_type.lower()}. El préstamo ha sido cancelado.", parent=self)
                    return # Cancelar si la creación falla
                # Si se crea, se puede continuar
            else:
                # Si el usuario dice no, cancelar el préstamo
                return

        # --- Si todas las validaciones pasan (o se crearon los registros), proceder a guardar ---
        sala_nombre = self.sala_combo.get()
        num_estudiantes_str = self.num_estudiantes_entry.get().strip()
        titulo_practica = self.titulo_practica_entry.get().strip()
        monitor_nombre = self.monitor_combo.get()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)
        
        num_estudiantes = None
        if user_type == "Estudiante" and num_estudiantes_str:
            try:
                num_estudiantes = int(num_estudiantes_str)
            except ValueError:
                messagebox.showerror("Error de Validación", "El número de estudiantes debe ser un valor numérico.", parent=self)
                return

        fecha_entrega = datetime.now()

        if user_type == "Estudiante":
            result = self.equipment_loan_model.add_loan_student(fecha_entrega, equipo_codigo, laboratorista_id, monitor_id, 
                                                              user_id, num_estudiantes, sala_id, titulo_practica, observaciones)
        else: # Profesor
            result = self.equipment_loan_model.add_loan_professor(fecha_entrega, equipo_codigo, laboratorista_id, monitor_id, 
                                                                user_id, sala_id, titulo_practica, observaciones)

        if result:
            messagebox.showinfo("Éxito", "Préstamo de equipo registrado correctamente.", parent=self)
            self._show_new_loan_view()
        else:
            messagebox.showerror("Error en Base de Datos", "No se pudo registrar el préstamo. Verifique los datos e intente de nuevo.", parent=self)

    def _show_history_view(self):
        self._clear_content_frame()
        self.history_btn.configure(fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"))
        self.new_loan_btn.configure(fg_color=("#f5f5f5", "#232323"), hover_color=("#ffd3a8", "#9c6d41"))
        
        title = ctk.CTkLabel(self.content_frame, text="Historial de Préstamos de Equipos", font=get_font("title", "bold"))
        title.pack(pady=(10, 10))
        
        # --- Filter Frame (Always Visible) ---
        self.filter_frame = ctk.CTkFrame(self.content_frame)
        self.filter_frame.pack(fill="x", pady=(0, 15), padx=0)

        # --- Widgets inside the filter frame ---
        ctk.CTkLabel(self.filter_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Usuario, equipo, práctica...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._apply_filters)
        
        ctk.CTkLabel(self.filter_frame, text="Tipo:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.user_type_filter = ctk.CTkComboBox(self.filter_frame, values=["Todos", "Estudiante", "Profesor"], font=get_font("normal"), command=self._apply_filters)
        self.user_type_filter.set("Todos")
        self.user_type_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.filter_frame, text="Estado:", font=get_font("normal")).grid(row=0, column=4, padx=(10,5), pady=10, sticky="w")
        self.status_filter = ctk.CTkComboBox(self.filter_frame, values=["Todos", "En Préstamo", "Devuelto"], font=get_font("normal"), command=self._apply_filters)
        self.status_filter.set("Todos")
        self.status_filter.grid(row=0, column=5, padx=(5,10), pady=10, sticky="ew")
        
        self.filter_frame.grid_columnconfigure(1, weight=3) # Give more space to search entry
        self.filter_frame.grid_columnconfigure(3, weight=1)
        self.filter_frame.grid_columnconfigure(5, weight=1)
        
        # --- Table and Actions ---
        table_main_container = ctk.CTkFrame(self.content_frame, corner_radius=8, border_width=1, border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0, 10), padx=0)
        
        table_container_frame = ctk.CTkFrame(table_main_container, corner_radius=15, fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        table_container_frame.grid_rowconfigure(0, weight=1)
        table_container_frame.grid_columnconfigure(0, weight=1)
        
        # Nuevo orden de columnas: tipo_usuario, fecha_entrega, estado_prestamo, usuario_id, usuario_nombre, ...
        columns = ("tipo_usuario", "fecha_entrega", "estado_prestamo", "usuario_id", "usuario_nombre", "equipo_desc", "titulo_practica", "laboratorista_entrega", "monitor_entrega", "fecha_devolucion", "laboratorista_devolucion", "monitor_devolucion", "firma", "observaciones")
        self.tree = ttk.Treeview(table_container_frame, columns=columns, show="headings", style="Modern.Treeview")
        
        # Configure headers in the new order
        self.tree.heading("tipo_usuario", text="👤 Usuario", anchor='w')
        self.tree.heading("fecha_entrega", text="📅 Fecha Entrega", anchor='w')
        self.tree.heading("estado_prestamo", text="📊 Estado", anchor='w')
        self.tree.heading("usuario_id", text="🆔 ID", anchor='w')
        self.tree.heading("usuario_nombre", text="👤 Nombre Usuario", anchor='w')
        self.tree.heading("equipo_desc", text="💻 Equipo", anchor='w')
        self.tree.heading("titulo_practica", text="📋 Título Práctica", anchor='w')
        self.tree.heading("laboratorista_entrega", text="👨‍🔬 Lab. Entrega", anchor='w')
        self.tree.heading("monitor_entrega", text="👥 Monitor Entrega", anchor='w')
        self.tree.heading("fecha_devolucion", text="📅 Fecha Devolución", anchor='w')
        self.tree.heading("laboratorista_devolucion", text="👨‍🔬 Lab. Devolución", anchor='w')
        self.tree.heading("monitor_devolucion", text="👥 Monitor Devolución", anchor='w')
        self.tree.heading("firma", text="✏️ Firma", anchor='w')
        self.tree.heading("observaciones", text="📝 Observaciones", anchor='w')
        
        # Configure column widths in the new order
        self.tree.column("tipo_usuario", width=100, stretch=False, minwidth=100)
        self.tree.column("fecha_entrega", width=150, stretch=False, minwidth=130, anchor='center')
        self.tree.column("estado_prestamo", width=100, stretch=False, minwidth=80)
        self.tree.column("usuario_id", width=110, stretch=False, minwidth=90)
        self.tree.column("usuario_nombre", width=230, stretch=False, minwidth=190)
        self.tree.column("equipo_desc", width=220, stretch=False, minwidth=180)
        self.tree.column("titulo_practica", width=190, stretch=False, minwidth=180)
        self.tree.column("laboratorista_entrega", width=260, stretch=False, minwidth=200)
        self.tree.column("monitor_entrega", width=260, stretch=False, minwidth=200)
        self.tree.column("fecha_devolucion", width=180, stretch=False, minwidth=150, anchor='center')
        self.tree.column("laboratorista_devolucion", width=260, stretch=False, minwidth=200)
        self.tree.column("monitor_devolucion", width=260, stretch=False, minwidth=200)
        self.tree.column("firma", width=120, stretch=False, minwidth=100)
        self.tree.column("observaciones", width=300, stretch=True, minwidth=200)
        
        v_scroll = ctk.CTkScrollbar(table_container_frame, command=self.tree.yview, corner_radius=8, width=16)
        h_scroll = ctk.CTkScrollbar(table_container_frame, command=self.tree.xview, orientation="horizontal", corner_radius=8, height=16)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=(5, 0))
        v_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=(5, 0))
        h_scroll.grid(row=1, column=0, sticky="ew", padx=(5, 0), pady=(0, 5))
        
        corner_frame = ctk.CTkFrame(table_container_frame, width=16, height=16, fg_color=("gray90", "gray25"))
        corner_frame.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))
        
        self._populate_history_treeview()
        
        self.actions_frame = ctk.CTkFrame(self.content_frame, corner_radius=12)
        self.actions_frame.pack(pady=(15, 0), padx=0, fill="x")
        self.return_btn = ctk.CTkButton(self.actions_frame, text="Registrar Devolución", command=self._return_selected_equipment, state="disabled", font=get_font("normal"), corner_radius=8, height=35, fg_color=("#ffa154", "#c95414"), hover_color=("#ff8c33", "#b34a0e"), text_color=("#222","#fff"))
        self.return_btn.pack(side="left", padx=8, pady=8)
        # Botones de editar y eliminar alineados a la derecha
        self.edit_btn = ctk.CTkButton(self.actions_frame, text="Editar Préstamo", command=self._edit_selected_loan, state="disabled", font=get_font("normal"), corner_radius=8, height=35, text_color=("#222","#fff"))
        self.delete_btn = ctk.CTkButton(self.actions_frame, text="Eliminar Préstamo", command=self._delete_selected_loan, state="disabled", fg_color=("#b3261e", "#e4675f"), hover_color=("#8b1e17", "#b8514a"), font=get_font("normal"), corner_radius=8, height=35, text_color=("#222","#fff"))
        self.delete_btn.pack(side="right", padx=8, pady=8)
        self.edit_btn.pack(side="right", padx=8, pady=8)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_loan_select)
        self._on_loan_select()

    def _apply_filters(self, event=None):
        if hasattr(self, 'tree'):
            self._populate_history_treeview()

    def _populate_history_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get current filter values
        search_term = self.search_entry.get()
        user_type = self.user_type_filter.get()
        status = self.status_filter.get()
        
        loans = self.equipment_loan_model.get_equipment_loans(
            search_term=search_term,
            user_type_filter=user_type,
            status_filter=status
        )
        
        current_mode = ctk.get_appearance_mode()
        tag_config = {'active_loan': ("#f59e0b",), 'alternate': ('#323232',) if current_mode == "Dark" else ('#f8f9fa',)}
        self.tree.tag_configure('active_loan', foreground=tag_config['active_loan'][0])
        self.tree.tag_configure('alternate', background=tag_config['alternate'][0])

        for i, loan in enumerate(loans):
            loan_id, tipo, nombre, equipo_desc, f_entrega, f_devolucion, lab_ent, mon_ent, lab_dev, mon_dev, titulo_practica, estado_prestamo, obs, user_id, loan_type, equipo_codigo, sala_id, firma_db = loan
            f_entrega_str = datetime.fromisoformat(f_entrega).strftime('%Y-%m-%d %H:%M') if f_entrega else 'N/A'
            f_devolucion_str = datetime.fromisoformat(f_devolucion).strftime('%Y-%m-%d %H:%M') if f_devolucion else "PENDIENTE"
            values = (
                tipo,
                f_entrega_str,
                estado_prestamo,
                user_id,
                nombre,
                equipo_desc,
                titulo_practica or '',
                lab_ent or 'N/A',
                mon_ent or 'N/A',
                f_devolucion_str,
                lab_dev or 'N/A',
                mon_dev or 'N/A',
                firma_db or '',
                obs or ''
            )
            
            tags = ('alternate',) if i % 2 == 1 else ()
            if estado_prestamo == 'En Préstamo':
                tags += ('active_loan',)
                
            iid = f"{loan_type}_{loan_id}"
            self.tree.insert("", "end", iid=iid, values=values, tags=tags)
        
        self.loan_data = {f"{loan[14]}_{loan[0]}": loan for loan in loans}

    def _on_loan_select(self, event=None):
        # --- MODIFICADO --- Actualiza el estado de los tres botones
        selected_iid = self.tree.focus()
        
        if not selected_iid:
            self.return_btn.configure(state="disabled")
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            return
        
        loan_details = self.loan_data.get(selected_iid)
        if not loan_details:
            self.return_btn.configure(state="disabled")
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            return

        # Habilitar editar y eliminar para cualquier préstamo seleccionado
        self.edit_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        
        # Habilitar "Registrar Devolución" solo si el préstamo está activo
        if loan_details[11] == 'En Préstamo': # estado_prestamo
            self.return_btn.configure(state="normal")
        else:
            self.return_btn.configure(state="disabled")

    def _return_selected_equipment(self):
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo activo para registrar la devolución.", parent=self)
            return

        loan_details = self.loan_data.get(selected_iid)
        if not loan_details: return

        dialog = EquipmentReturnDialog(self, "Registrar Devolución de Equipo", loan_details)
        if dialog.result:
            self.refresh_loans()

    # Placeholder para la función de edición
    def _edit_selected_loan(self):
        selected_iid = self.tree.focus()
        if not selected_iid or not (loan_summary := self.loan_data.get(selected_iid)):
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo para editar.", parent=self)
            return
        
        # Abrir el nuevo diálogo de edición, pasando todos los modelos necesarios
        dialog = EquipmentEditDialog(
            parent=self, 
            title="Editar Préstamo de Equipo", 
            loan_summary=loan_summary, 
            loan_model=self.equipment_loan_model,
            room_model=self.room_model,
            personal_model=self.personal_model,
            student_model=self.student_model,
            profesor_model=self.profesor_model
        )
        if dialog.result:
            self.refresh_loans() # Recargar la lista si la edición fue exitosa
            
    # Función para eliminar el préstamo seleccionado
    def _delete_selected_loan(self):
        selected_iid = self.tree.focus()
        if not selected_iid or not (loan_details := self.loan_data.get(selected_iid)):
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo para eliminar.", parent=self)
            return
            
        loan_id = loan_details[0]
        loan_type = loan_details[14]

        if messagebox.askyesno("Confirmar Eliminación", 
                               f"¿Está seguro de que desea eliminar permanentemente el préstamo ID: {loan_id}?\nEsta acción no se puede deshacer.",
                               parent=self, icon=messagebox.WARNING):
            
            success = self.equipment_loan_model.delete_loan(loan_id, loan_type)
            if success:
                messagebox.showinfo("Éxito", "El préstamo ha sido eliminado correctamente.", parent=self)
                self.refresh_loans()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el préstamo de la base de datos.", parent=self)
    
    def refresh_loans(self):
        if hasattr(self, 'tree'):
            self._populate_history_treeview()
            self._on_loan_select()
            self.update_idletasks()

    def on_theme_change(self, event=None):
        if hasattr(self, 'tree'):
            self.refresh_loans()
            self.update_idletasks()

    def set_app_icon(self):
        icon_path_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.ico")
        icon_path_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.png")
        final_icon_path = None
        if sys.platform == "win32" and os.path.exists(icon_path_ico):
            final_icon_path = icon_path_ico
        elif os.path.exists(icon_path_png):
            final_icon_path = icon_path_png
        if final_icon_path:
            try:
                if sys.platform == "win32" and final_icon_path.endswith(".ico"):
                    self.iconbitmap(default=final_icon_path)
                else:
                    icon_image = Image.open(final_icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo)
            except Exception as e:
                print(f"Error setting dialog icon: {e}")

class EquipmentReturnDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, loan_data):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x450")
        self.transient(parent)
        self.grab_set()
        self.lift()
        self._set_app_icon()
        self._center_dialog()
        self.loan_data = loan_data
        self.equipment_loan_model = EquipmentLoanModel()
        self.personal_model = PersonalLaboratorioModel()
        self.result = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)

        # Fecha de devolución
        ctk.CTkLabel(main_frame, text="Fecha de Devolución:*", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.fecha_devolucion_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.fecha_devolucion_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.fecha_devolucion_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Laboratorista de devolución
        ctk.CTkLabel(main_frame, text="Laboratorista Devolución:*", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        lab_names = ["Seleccione..."] + [p[1] for p in self.laboratoristas_data]
        self.lab_combo = ctk.CTkComboBox(main_frame, values=lab_names, font=get_font("normal"), state="readonly")
        self.lab_combo.set(lab_names[0])
        self.lab_combo.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Monitor de devolución (opcional)
        ctk.CTkLabel(main_frame, text="Monitor Devolución:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.monitores_data = self.personal_model.get_monitores()
        monitor_names = ["Seleccione..."] + [p[1] for p in self.monitores_data]
        self.monitor_combo = ctk.CTkComboBox(main_frame, values=monitor_names, font=get_font("normal"), state="readonly")
        self.monitor_combo.set(monitor_names[0])
        self.monitor_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Documento de quien devuelve (automático y no editable)
        borrower_id = self.loan_data[13] # Índice 13 es 'usuario_id'
        ctk.CTkLabel(main_frame, text="Documento Devolvente:*", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.doc_devolvente_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.doc_devolvente_entry.insert(0, borrower_id)
        self.doc_devolvente_entry.configure(state="disabled") # Hacer el campo de solo lectura
        self.doc_devolvente_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        # Observaciones de devolución
        ctk.CTkLabel(main_frame, text="Observaciones:", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(main_frame, height=80, font=get_font("normal"))
        self.obs_textbox.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        if self.loan_data[12]: # Cargar observaciones existentes si las hay
            self.obs_textbox.insert("1.0", self.loan_data[12])

        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

        save_btn = ctk.CTkButton(button_frame, text="Confirmar Devolución", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self.wait_window(self)

    def _set_app_icon(self):
        icon_path_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.ico")
        icon_path_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.png")
        final_icon_path = None
        if sys.platform == "win32" and os.path.exists(icon_path_ico):
            final_icon_path = icon_path_ico
        elif os.path.exists(icon_path_png):
            final_icon_path = icon_path_png
        if final_icon_path:
            try:
                if sys.platform == "win32" and final_icon_path.endswith(".ico"):
                    self.iconbitmap(default=final_icon_path)
                else:
                    icon_image = Image.open(final_icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo)
            except Exception as e:
                print(f"Error setting dialog icon: {e}")

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
        fecha_devolucion = self.fecha_devolucion_entry.get().strip()
        lab_nombre = self.lab_combo.get()
        monitor_nombre = self.monitor_combo.get()
        # El documento se obtiene directamente de los datos del préstamo, no del entry
        doc_devolvente = str(self.loan_data[13])
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        # Validaciones (Monitor ya no es obligatorio)
        if not all([fecha_devolucion, lab_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "La fecha de devolución y el laboratorista que recibe son obligatorios.", parent=self)
            return
        
        try:
            # Validar formato de fecha
            datetime.strptime(fecha_devolucion, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            messagebox.showerror("Formato incorrecto", "La fecha debe estar en formato YYYY-MM-DD HH:MM:SS (ej. 2023-12-01 14:30:00).", parent=self)
            return

        # Obtener IDs (monitor_id será None si no se selecciona)
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = None
        if monitor_nombre != "Seleccione...":
            monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)

        loan_id = self.loan_data[0]
        loan_type = self.loan_data[14]

        success = self.equipment_loan_model.update_equipment_loan_return(loan_id, loan_type, fecha_devolucion, 
                                                                       laboratorista_id, monitor_id, observaciones, doc_devolvente)
        
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "La devolución ha sido registrada correctamente.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro de la devolución en la base de datos.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()

# Diálogo para editar un préstamo
class EquipmentEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, loan_summary, loan_model, room_model, personal_model, student_model, profesor_model):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x700")
        self.transient(parent)
        self.grab_set()
        self.lift()
        self._set_app_icon()
        self._center_dialog()

        # Guardar modelos
        self.loan_model = loan_model
        self.room_model = room_model
        self.personal_model = personal_model
        self.student_model = student_model
        self.profesor_model = profesor_model
        
        # Guardar identificadores del préstamo
        self.loan_id = loan_summary[0]
        self.original_loan_type = loan_summary[14]
        
        # Obtener detalles completos del préstamo
        self.loan_details = self.loan_model.get_equipment_loan_details(self.loan_id, self.original_loan_type)
        self.result = None

        # --- Frame Principal Scrollable ---
        scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="Detalles del Préstamo")
        scrollable_frame.pack(expand=True, fill="both", padx=15, pady=15)
        scrollable_frame.columnconfigure(1, weight=1)

        # --- Cargar datos para los ComboBox ---
        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        self.monitores_data = self.personal_model.get_monitores()
        self.salas_data = self.room_model.get_all_rooms_with_id_for_dropdown()

        # --- Elementos de la UI ---
        row_idx = 0
        
        # Tipo de Usuario (para validación)
        ctk.CTkLabel(scrollable_frame, text="Tipo de Usuario:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(scrollable_frame, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly", command=self._on_user_type_change_edit)
        self.user_type_combo.set("Estudiante" if self.original_loan_type == "student" else "Profesor")
        self.user_type_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # ID de Usuario (Código/Cédula)
        ctk.CTkLabel(scrollable_frame, text="Código/Cédula Usuario:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.user_id_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        self.user_id_entry.insert(0, self.loan_details[6]) # estudiante_id o profesor_id
        self.user_id_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        self.user_id_entry.bind("<KeyRelease>", self._validate_user_id)
        row_idx += 1

        # Label para mostrar el estado de validación del usuario
        self.user_validation_label = ctk.CTkLabel(scrollable_frame, text="", font=get_font("small"))
        self.user_validation_label.grid(row=row_idx, column=1, padx=5, pady=(0, 10), sticky="w")
        row_idx += 1
        
        # Fechas de Entrega y Devolución
        ctk.CTkLabel(scrollable_frame, text="Fecha Entrega:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.fecha_entrega_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        self.fecha_entrega_entry.insert(0, datetime.fromisoformat(self.loan_details[1]).strftime('%Y-%m-%d %H:%M:%S')) # fecha_entrega
        self.fecha_entrega_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Fecha Devolución:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.fecha_devolucion_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        return_date = self.loan_details[2] # fecha_devolucion
        if return_date:
            self.fecha_devolucion_entry.insert(0, datetime.fromisoformat(return_date).strftime('%Y-%m-%d %H:%M:%S'))
        else:
            self.fecha_devolucion_entry.configure(placeholder_text="Préstamo activo (dejar vacío si no aplica)")
        self.fecha_devolucion_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Título de la práctica
        ctk.CTkLabel(scrollable_frame, text="Título Práctica:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.titulo_entry = ctk.CTkEntry(scrollable_frame, font=get_font("normal"))
        self.titulo_entry.insert(0, self.loan_details[9] or "")
        self.titulo_entry.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Sala
        ctk.CTkLabel(scrollable_frame, text="Sala:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        sala_names = ["Ninguna"] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(scrollable_frame, values=sala_names, font=get_font("normal"), state="readonly")
        current_sala_id = self.loan_details[8]
        current_sala_name = next((s[1] for s in self.salas_data if s[0] == current_sala_id), "Ninguna")
        self.sala_combo.set(current_sala_name)
        self.sala_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Personal (Entrega y Devolución)
        lab_names = ["Ninguno"] + [p[1] for p in self.laboratoristas_data]
        monitor_names = ["Ninguno"] + [p[1] for p in self.monitores_data]

        ctk.CTkLabel(scrollable_frame, text="Lab. Entrega:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.lab_entrega_combo = ctk.CTkComboBox(scrollable_frame, values=lab_names, font=get_font("normal"), state="readonly")
        current_lab_ent_name = next((p[1] for p in self.laboratoristas_data if p[0] == self.loan_details[4]), "Ninguno")
        self.lab_entrega_combo.set(current_lab_ent_name)
        self.lab_entrega_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Monitor Entrega:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.monitor_entrega_combo = ctk.CTkComboBox(scrollable_frame, values=monitor_names, font=get_font("normal"), state="readonly")
        current_mon_ent_name = next((p[1] for p in self.monitores_data if p[0] == self.loan_details[5]), "Ninguno")
        self.monitor_entrega_combo.set(current_mon_ent_name)
        self.monitor_entrega_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Lab. Devolución:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.lab_devolucion_combo = ctk.CTkComboBox(scrollable_frame, values=lab_names, font=get_font("normal"), state="readonly")
        current_lab_dev_name = next((p[1] for p in self.laboratoristas_data if p[0] == self.loan_details[11]), "Ninguno")
        self.lab_devolucion_combo.set(current_lab_dev_name)
        self.lab_devolucion_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        ctk.CTkLabel(scrollable_frame, text="Monitor Devolución:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="w")
        self.monitor_devolucion_combo = ctk.CTkComboBox(scrollable_frame, values=monitor_names, font=get_font("normal"), state="readonly")
        current_mon_dev_name = next((p[1] for p in self.monitores_data if p[0] == self.loan_details[12]), "Ninguno")
        self.monitor_devolucion_combo.set(current_mon_dev_name)
        self.monitor_devolucion_combo.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Observaciones
        ctk.CTkLabel(scrollable_frame, text="Observaciones:", font=get_font("normal")).grid(row=row_idx, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(scrollable_frame, height=100, font=get_font("normal"))
        self.obs_textbox.insert("1.0", self.loan_details[14] or "")
        self.obs_textbox.grid(row=row_idx, column=1, padx=5, pady=10, sticky="ew")
        row_idx += 1

        # Botones
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        save_btn = ctk.CTkButton(button_frame, text="Guardar Cambios", command=self.save, font=get_font("normal", "bold"))
        save_btn.pack(side="left", expand=True, padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)
        
        self.wait_window(self)

    def _set_app_icon(self):
        icon_path_ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.ico")
        icon_path_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "app_icon.png")
        final_icon_path = None
        if sys.platform == "win32" and os.path.exists(icon_path_ico):
            final_icon_path = icon_path_ico
        elif os.path.exists(icon_path_png):
            final_icon_path = icon_path_png
        if final_icon_path:
            try:
                if sys.platform == "win32" and final_icon_path.endswith(".ico"):
                    self.iconbitmap(default=final_icon_path)
                else:
                    icon_image = Image.open(final_icon_path)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    self.iconphoto(True, icon_photo)
            except Exception as e:
                print(f"Error setting dialog icon: {e}")

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

    def _on_user_type_change_edit(self, event):
        # This method is called when the user type combo box is changed.
        # We need to re-validate the user ID based on the new user type.
        self._validate_user_id()

    def _validate_user_id(self, event=None):
        user_id = self.user_id_entry.get().strip()
        user_type = self.user_type_combo.get()
        is_valid = False
        error_msg = ""

        if user_type == "Estudiante":
            is_valid = self.student_model.get_student_by_code_or_id(user_id)
            if not is_valid:
                error_msg = f"✗ El código '{user_id}' no corresponde a un estudiante válido."
        else: # Profesor
            is_valid = self.profesor_model.get_professor_by_id(user_id)
            if not is_valid:
                error_msg = f"✗ La cédula '{user_id}' no corresponde a un profesor válido."

        if is_valid:
            self.user_validation_label.configure(text="✓ Código/Cédula válido", text_color="green")
        else:
            self.user_validation_label.configure(text=error_msg, text_color="red")

    def save(self):
        update_data = {}
        
        # 1. Obtener nuevos valores de la UI
        selected_user_type_str = self.user_type_combo.get()
        new_user_id = self.user_id_entry.get().strip()
        new_fecha_entrega_str = self.fecha_entrega_entry.get().strip()
        new_fecha_devolucion_str = self.fecha_devolucion_entry.get().strip()

        # Validar usuario antes de guardar
        if selected_user_type_str == "Estudiante":
            user_exists = self.student_model.get_student_by_code_or_id(new_user_id)
        else:
            user_exists = self.profesor_model.get_professor_by_id(new_user_id)
        if not user_exists:
            messagebox.showerror("Error de Validación", f"El {selected_user_type_str.lower()} con ID '{new_user_id}' no existe en la base de datos. No se puede guardar.", parent=self)
            return

        # 2. Validar cambio de tipo y/o ID de usuario
        new_loan_type = "student" if selected_user_type_str == "Estudiante" else "professor"
        if new_loan_type != self.original_loan_type:
            messagebox.showerror("Operación no Soportada", "Cambiar el tipo de usuario (de Estudiante a Profesor o viceversa) no está permitido en esta versión.", parent=self)
            return

        original_user_id = str(self.loan_details[6])
        if new_user_id != original_user_id:
            user_exists = self.student_model.get_student_by_code_or_id(new_user_id) if new_loan_type == "student" else self.profesor_model.get_professor_by_id(new_user_id)
            if not user_exists:
                messagebox.showerror("Usuario no encontrado", f"El código/cédula '{new_user_id}' no corresponde a un {selected_user_type_str.lower()} válido.", parent=self)
                return
            update_data['usuario_id'] = new_user_id

        # 3. Validar y agregar fechas si cambiaron
        try:
            original_entrega_str = datetime.fromisoformat(self.loan_details[1]).strftime('%Y-%m-%d %H:%M:%S')
            if new_fecha_entrega_str != original_entrega_str:
                update_data['fecha_entrega'] = datetime.strptime(new_fecha_entrega_str, '%Y-%m-%d %H:%M:%S').isoformat()
            
            original_devolucion_str = datetime.fromisoformat(self.loan_details[2]).strftime('%Y-%m-%d %H:%M:%S') if self.loan_details[2] else ""
            if new_fecha_devolucion_str != original_devolucion_str:
                update_data['fecha_devolucion'] = datetime.strptime(new_fecha_devolucion_str, '%Y-%m-%d %H:%M:%S').isoformat() if new_fecha_devolucion_str else None
        except (ValueError, TypeError):
            messagebox.showerror("Formato de Fecha Inválido", "Las fechas deben estar en formato YYYY-MM-DD HH:MM:SS o dejarse vacías si aplica.", parent=self)
            return

        # 4. Procesar otros campos y agregarlos a update_data si cambiaron
        field_map = {
            'titulo_practica': (self.titulo_entry.get().strip(), self.loan_details[9]),
            'observaciones': (self.obs_textbox.get("1.0", "end-1c").strip(), self.loan_details[14]),
            'sala_id': (next((s[0] for s in self.salas_data if s[1] == self.sala_combo.get()), None), self.loan_details[8]),
            'laboratorista_entrega': (next((p[0] for p in self.laboratoristas_data if p[1] == self.lab_entrega_combo.get()), None), self.loan_details[4]),
            'monitor_entrega': (next((p[0] for p in self.monitores_data if p[1] == self.monitor_entrega_combo.get()), None), self.loan_details[5]),
            'laboratorista_devolucion': (next((p[0] for p in self.laboratoristas_data if p[1] == self.lab_devolucion_combo.get()), None), self.loan_details[11]),
            'monitor_devolucion': (next((p[0] for p in self.monitores_data if p[1] == self.monitor_devolucion_combo.get()), None), self.loan_details[12]),
        }

        for key, (new_val, old_val) in field_map.items():
            if new_val != (old_val or ("" if isinstance(new_val, str) else None)):
                update_data[key] = new_val

        # 5. Llamar al modelo para actualizar si hay cambios
        if not update_data:
            messagebox.showinfo("Sin cambios", "No se detectaron cambios para guardar.", parent=self)
            return

        success = self.loan_model.update_equipment_loan(self.loan_id, self.original_loan_type, update_data)
        
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "El préstamo ha sido actualizado correctamente.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el préstamo en la base de datos.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()