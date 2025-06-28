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

        self.new_loan_btn = ctk.CTkButton(self.nav_frame, text="Nuevo Préstamo", command=self._show_new_loan_view, font=get_font("normal", "bold"))
        self.new_loan_btn.pack(side="left", padx=(0, 5))

        self.history_btn = ctk.CTkButton(self.nav_frame, text="Historial de Préstamos", command=self._show_history_view, font=get_font("normal", "bold"))
        self.history_btn.pack(side="left", padx=5)

        # Frame principal para el contenido
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_new_loan_view(self):
        self._clear_content_frame()
        self.new_loan_btn.configure(fg_color=("#ffa154", "#c95414"))
        self.history_btn.configure(fg_color=("gray70", "gray30"))

        # Título independiente del formulario (similar a StudentsView)
        title = ctk.CTkLabel(self.content_frame, text="Registrar Nuevo Préstamo de Equipo", font=get_font("title", "bold"))
        title.pack(pady=(10, 20))

        # Frame del formulario con marco
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        # --- Formulario ---
        form_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_grid.pack(fill="x", expand=True, padx=20, pady=20)
        form_grid.columnconfigure(1, weight=1)

        # Tipo de usuario
        ctk.CTkLabel(form_grid, text="Tipo de Usuario:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.user_type_combo = ctk.CTkComboBox(form_grid, values=["Estudiante", "Profesor"], font=get_font("normal"), state="readonly")
        self.user_type_combo.set("Estudiante")
        self.user_type_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Equipo
        ctk.CTkLabel(form_grid, text="Equipo Disponible:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.equipos_data = self.inventory_model.get_available_equipment_for_dropdown()
        equipo_names = ["Seleccione un equipo..."] + [e[1] for e in self.equipos_data]
        self.equipo_combo = ctk.CTkComboBox(form_grid, values=equipo_names, font=get_font("normal"), state="readonly")
        self.equipo_combo.set(equipo_names[0])
        self.equipo_combo.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Sala
        ctk.CTkLabel(form_grid, text="Sala:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.salas_data = self.room_model.get_all_rooms_for_dropdown()
        sala_names = ["Seleccione una sala..."] + [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(form_grid, values=sala_names, font=get_font("normal"), state="readonly")
        self.sala_combo.set(sala_names[0])
        self.sala_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # ID Usuario (Código o Cédula)
        ctk.CTkLabel(form_grid, text="Código/Cédula:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=10, sticky="w")
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
        ctk.CTkLabel(form_grid, text="Laboratorista:", font=get_font("normal")).grid(row=6, column=0, padx=5, pady=10, sticky="w")
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
        equipo_nombre = self.equipo_combo.get()
        sala_nombre = self.sala_combo.get()
        user_id = self.user_id_entry.get().strip()
        num_estudiantes = self.num_estudiantes_entry.get().strip()
        titulo_practica = self.titulo_practica_entry.get().strip()
        lab_nombre = self.lab_combo.get()
        monitor_nombre = self.monitor_combo.get()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        # --- Validaciones ---
        if not all([user_type, equipo_nombre != "Seleccione un equipo...", sala_nombre != "Seleccione una sala...", 
                   user_id, titulo_practica, lab_nombre != "Seleccione...", monitor_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Todos los campos (excepto observaciones y número de estudiantes) son obligatorios.", parent=self)
            return

        # Validar número de estudiantes para estudiantes
        if user_type == "Estudiante" and not num_estudiantes:
            messagebox.showerror("Error de Validación", "El número de estudiantes es obligatorio para préstamos de estudiantes.", parent=self)
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
        equipo_codigo = next((e[0] for e in self.equipos_data if e[1] == equipo_nombre), None)
        sala_id = next((s[0] for s in self.salas_data if s[1] == sala_nombre), None)
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)
        fecha_entrega = datetime.now()

        # Guardar en la base de datos
        if user_type == "Estudiante":
            result = self.equipment_loan_model.add_loan_student(fecha_entrega, equipo_codigo, laboratorista_id, monitor_id, 
                                                              user_id, int(num_estudiantes), sala_id, titulo_practica, observaciones)
        else: # Profesor
            result = self.equipment_loan_model.add_loan_professor(fecha_entrega, equipo_codigo, laboratorista_id, monitor_id, 
                                                                user_id, sala_id, titulo_practica, observaciones)

        if result:
            messagebox.showinfo("Éxito", "Préstamo de equipo registrado correctamente.", parent=self)
            self._show_new_loan_view() # Recargar para limpiar formulario y actualizar equipos
        else:
            messagebox.showerror("Error en Base de Datos", "No se pudo registrar el préstamo de equipo.", parent=self)

    def _show_history_view(self):
        # ... (la configuración de la tabla y los scrollbars es la misma que en la respuesta anterior) ...
        self._clear_content_frame()
        self.history_btn.configure(fg_color=("#ffa154", "#c95414"))
        self.new_loan_btn.configure(fg_color=("gray70", "gray30"))
        title = ctk.CTkLabel(self.content_frame, text="Historial de Préstamos de Equipos", font=get_font("title", "bold"))
        title.pack(pady=(10, 20))
        table_main_container = ctk.CTkFrame(self.content_frame, corner_radius=8, border_width=1, border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0, 10), padx=0)
        table_container_frame = ctk.CTkFrame(table_main_container, corner_radius=15, fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)
        columns = ("tipo_usuario", "usuario_nombre", "equipo_desc", "fecha_entrega", "fecha_devolucion", "titulo_practica", "laboratorista_entrega", "monitor_entrega", "laboratorista_devolucion", "monitor_devolucion", "estado_prestamo", "observaciones")
        self.tree = ttk.Treeview(table_container_frame, columns=columns, show="headings", style="Modern.Treeview")
        self.tree.heading("tipo_usuario", text="👤 Tipo Usuario", anchor='w')
        self.tree.heading("usuario_nombre", text="👨‍💼 Nombre Usuario", anchor='w')
        self.tree.heading("equipo_desc", text="🔧 Equipo", anchor='w')
        self.tree.heading("fecha_entrega", text="📅 Fecha Entrega", anchor='w')
        self.tree.heading("fecha_devolucion", text="📅 Fecha Devolución", anchor='w')
        self.tree.heading("titulo_practica", text="📋 Título Práctica", anchor='w')
        self.tree.heading("laboratorista_entrega", text="👨‍🔬 Lab. Entrega", anchor='w')
        self.tree.heading("monitor_entrega", text="👥 Monitor Entrega", anchor='w')
        self.tree.heading("laboratorista_devolucion", text="👨‍🔬 Lab. Devolución", anchor='w')
        self.tree.heading("monitor_devolucion", text="👥 Monitor Devolución", anchor='w')
        self.tree.heading("estado_prestamo", text="📊 Estado", anchor='w')
        self.tree.heading("observaciones", text="📝 Observaciones", anchor='w')
        self.tree.column("tipo_usuario", width=100, stretch=False)
        self.tree.column("usuario_nombre", width=150)
        self.tree.column("equipo_desc", width=200)
        self.tree.column("fecha_entrega", width=150)
        self.tree.column("fecha_devolucion", width=150, anchor='center')
        self.tree.column("titulo_practica", width=200)
        self.tree.column("laboratorista_entrega", width=150)
        self.tree.column("monitor_entrega", width=150)
        self.tree.column("laboratorista_devolucion", width=150)
        self.tree.column("monitor_devolucion", width=150)
        self.tree.column("estado_prestamo", width=100)
        self.tree.column("observaciones", width=300)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        v_scroll = ctk.CTkScrollbar(table_container_frame, command=self.tree.yview, corner_radius=8, width=12)
        v_scroll.pack(side="right", fill="y", pady=5, padx=(0, 5))
        h_scroll = ctk.CTkScrollbar(table_container_frame, command=self.tree.xview, orientation="horizontal", corner_radius=8, height=12)
        h_scroll.pack(side="bottom", fill="x", padx=5, pady=(0, 5))
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self._populate_history_treeview()
        self.actions_frame = ctk.CTkFrame(self.content_frame, corner_radius=12)
        self.actions_frame.pack(pady=(15, 0), padx=0, fill="x")
        self.return_btn = ctk.CTkButton(self.actions_frame, text="Registrar Devolución", command=self._return_selected_equipment, state="disabled", font=get_font("normal"), corner_radius=8, height=35)
        self.return_btn.pack(side="left", padx=8, pady=8)
        self.edit_btn = ctk.CTkButton(self.actions_frame, text="Editar Préstamo", command=self._edit_selected_loan, state="disabled", font=get_font("normal"), corner_radius=8, height=35)
        self.edit_btn.pack(side="left", padx=8, pady=8)
        self.delete_btn = ctk.CTkButton(self.actions_frame, text="Eliminar Préstamo", command=self._delete_selected_loan, state="disabled", fg_color=("#b3261e", "#e4675f"), hover_color=("#8b1e17", "#b8514a"), font=get_font("normal"), corner_radius=8, height=35)
        self.delete_btn.pack(side="left", padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_loan_select)
        self._on_loan_select()

    def _populate_history_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        loans = self.equipment_loan_model.get_equipment_loans()
        
        current_mode = ctk.get_appearance_mode()
        tag_config = {'active_loan': ("#f59e0b",), 'alternate': ('#323232',) if current_mode == "Dark" else ('#f8f9fa',)}
        self.tree.tag_configure('active_loan', foreground=tag_config['active_loan'][0])
        self.tree.tag_configure('alternate', background=tag_config['alternate'][0])

        for i, loan in enumerate(loans):
            # Se añade sala_id al desempaquetado
            loan_id, tipo, nombre, equipo_desc, f_entrega, f_devolucion, lab_ent, mon_ent, lab_dev, mon_dev, titulo_practica, estado_prestamo, obs, user_id, loan_type, equipo_codigo, sala_id = loan
            
            f_entrega_str = datetime.fromisoformat(f_entrega).strftime('%Y-%m-%d %H:%M') if f_entrega else 'N/A'
            f_devolucion_str = datetime.fromisoformat(f_devolucion).strftime('%Y-%m-%d %H:%M') if f_devolucion else "PENDIENTE"
            
            values = (tipo, nombre, equipo_desc, f_entrega_str, f_devolucion_str, titulo_practica, 
                      lab_ent or 'N/A', mon_ent or 'N/A', lab_dev or 'N/A', mon_dev or 'N/A', 
                      estado_prestamo, obs or '')
            
            tags = ('alternate',) if i % 2 == 1 else ()
            if estado_prestamo == 'En Préstamo':
                tags += ('active_loan',)
            
            self.tree.insert("", "end", iid=f"{loan_type}_{loan_id}", values=values, tags=tags)
        
        # Guardar datos completos para usarlos después
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
        if not selected_iid or not (loan_details := self.loan_data.get(selected_iid)):
            messagebox.showwarning("Sin selección", "Por favor, seleccione un préstamo para editar.", parent=self)
            return
        
        # Abrir el nuevo diálogo de edición
        dialog = EquipmentEditDialog(self, "Editar Préstamo de Equipo", loan_details, self.equipment_loan_model, self.room_model)
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
        self.geometry("500x400")
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
        ctk.CTkLabel(main_frame, text="Fecha de Devolución:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.fecha_devolucion_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.fecha_devolucion_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.fecha_devolucion_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Laboratorista de devolución
        ctk.CTkLabel(main_frame, text="Laboratorista Devolución:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.laboratoristas_data = self.personal_model.get_laboratoristas()
        lab_names = ["Seleccione..."] + [p[1] for p in self.laboratoristas_data]
        self.lab_combo = ctk.CTkComboBox(main_frame, values=lab_names, font=get_font("normal"), state="readonly")
        self.lab_combo.set(lab_names[0])
        self.lab_combo.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Monitor de devolución
        ctk.CTkLabel(main_frame, text="Monitor Devolución:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.monitores_data = self.personal_model.get_monitores()
        monitor_names = ["Seleccione..."] + [p[1] for p in self.monitores_data]
        self.monitor_combo = ctk.CTkComboBox(main_frame, values=monitor_names, font=get_font("normal"), state="readonly")
        self.monitor_combo.set(monitor_names[0])
        self.monitor_combo.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Documento de quien devuelve
        ctk.CTkLabel(main_frame, text="Documento Devolvente:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.doc_devolvente_entry = ctk.CTkEntry(main_frame, placeholder_text="Cédula o código de quien devuelve", font=get_font("normal"))
        self.doc_devolvente_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        # Observaciones de devolución
        ctk.CTkLabel(main_frame, text="Observaciones\n(Devolución):", font=get_font("normal")).grid(row=4, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(main_frame, height=80, font=get_font("normal"))
        self.obs_textbox.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        if self.loan_data[12]: # Cargar observaciones existentes
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
        doc_devolvente = self.doc_devolvente_entry.get().strip()
        observaciones = self.obs_textbox.get("1.0", "end-1c").strip()
        
        # Validaciones
        if not all([fecha_devolucion, lab_nombre != "Seleccione...", monitor_nombre != "Seleccione..."]):
            messagebox.showerror("Error de Validación", "Fecha de devolución, laboratorista y monitor son obligatorios.", parent=self)
            return
        
        try:
            datetime.strptime(fecha_devolucion, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            messagebox.showerror("Formato incorrecto", "La fecha debe estar en formato YYYY-MM-DD HH:MM:SS (ej. 2023-12-01 14:30:00).", parent=self)
            return

        # Obtener IDs
        laboratorista_id = next((p[0] for p in self.laboratoristas_data if p[1] == lab_nombre), None)
        monitor_id = next((p[0] for p in self.monitores_data if p[1] == monitor_nombre), None)

        loan_id = self.loan_data[0]
        loan_type = self.loan_data[14]

        success = self.equipment_loan_model.update_equipment_loan_return(loan_id, loan_type, fecha_devolucion, 
                                                                       laboratorista_id, monitor_id, observaciones, doc_devolvente)
        
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "La devolución ha sido registrada.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro de la devolución.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()

# Diálogo para editar un préstamo
class EquipmentEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, loan_data, loan_model, room_model):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x350")
        self.transient(parent)
        self.grab_set()
        self.lift()
        self._set_app_icon()
        self._center_dialog()
        self.loan_data = loan_data
        self.loan_model = loan_model
        self.room_model = room_model
        self.result = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)

        # Título de la práctica
        ctk.CTkLabel(main_frame, text="Título de la Práctica:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.titulo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.titulo_entry.insert(0, self.loan_data[10]) # titulo_practica
        self.titulo_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Sala
        ctk.CTkLabel(main_frame, text="Sala:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.salas_data = self.room_model.get_all_rooms_for_dropdown()
        sala_names = [s[1] for s in self.salas_data]
        self.sala_combo = ctk.CTkComboBox(main_frame, values=sala_names, font=get_font("normal"), state="readonly")
        
        # Encontrar y seleccionar la sala actual
        current_sala_id = self.loan_data[16] # sala_id
        current_sala_name = next((s[1] for s in self.salas_data if s[0] == current_sala_id), sala_names[0] if sala_names else "")
        self.sala_combo.set(current_sala_name)
        self.sala_combo.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Observaciones
        ctk.CTkLabel(main_frame, text="Observaciones:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=10, sticky="nw")
        self.obs_textbox = ctk.CTkTextbox(main_frame, height=100, font=get_font("normal"))
        self.obs_textbox.insert("1.0", self.loan_data[12] or "") # observaciones
        self.obs_textbox.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")
        save_btn = ctk.CTkButton(button_frame, text="Guardar Cambios", command=self.save, font=get_font("normal"))
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
        new_titulo = self.titulo_entry.get().strip()
        new_sala_nombre = self.sala_combo.get()
        new_observaciones = self.obs_textbox.get("1.0", "end-1c").strip()

        if not new_titulo:
            messagebox.showerror("Error de Validación", "El título de la práctica no puede estar vacío.", parent=self)
            return
        
        # Obtener el ID de la sala seleccionada
        new_sala_id = next((s[0] for s in self.salas_data if s[1] == new_sala_nombre), None)
        if new_sala_id is None:
            messagebox.showerror("Error de Validación", "Debe seleccionar una sala válida.", parent=self)
            return

        loan_id = self.loan_data[0]
        loan_type = self.loan_data[14]

        success = self.loan_model.update_equipment_loan(loan_id, loan_type, new_titulo, new_sala_id, new_observaciones)
        
        if success:
            self.result = True
            messagebox.showinfo("Éxito", "El préstamo ha sido actualizado correctamente.", parent=self.master)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el préstamo en la base de datos.", parent=self)

    def cancel(self):
        self.result = None
        self.destroy()