import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import StudentModel
from utils.font_config import get_font
from utils.validators import *

class StudentsView(ctk.CTkFrame):
    def __init__(self, parent):
        # Hacer el frame principal transparente
        super().__init__(parent, fg_color="transparent")
        
        # Inicializa el modelo de datos para interactuar con la base de datos de estudiantes
        self.student_model = StudentModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15, fill="both", expand=True) # Padding general para la vista

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        # Creacion de UI y llenar datos de tabla
        self.setup_ui()
        self.refresh_students()
    
    def prevent_resize(self, event):
        """Impide que el usuario redimensione las columnas con el mouse"""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        '''Metodo para construir los componentes visuales de la vista (título, cuadro de búsqueda, filtro y botones)'''
        # Titulo
        title = ctk.CTkLabel(self, text="Gestión de Estudiantes", font=get_font("title", "bold"))
        title.pack(pady=(10, 20)) # Padding inferior para separar del siguiente frame
        
        # Frame para cuadro de busqueda
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0) # Padding inferior y sin padding horizontal interno al search_frame
        
        # Cuadro de busqueda 
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código, nombre o cédula...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Vincula el evento de liberación de tecla para llamar a la función de búsqueda
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filtro por proyectos
        ctk.CTkLabel(search_frame, text="Proyecto:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.project_filter = ctk.CTkComboBox(search_frame, 
                                             values=["Todos"] + [p[1] for p in self.student_model.get_curriculum_projects()],
                                             font=get_font("normal"))
        self.project_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.project_filter.set("Todos") # Establece "Todos" como valor por defecto
        # Configura el comando a ejecutar cuando cambia la selección del filtro
        self.project_filter.configure(command=self.on_filter_change)
        
        # Boton añadir estudiante
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Estudiante", command=self.add_student_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=4, padx=(10,10), pady=10)
        
        # Configura la expansión de las columnas en el grid del frame de búsqueda
        search_frame.grid_columnconfigure(1, weight=3) # Más peso a la búsqueda
        search_frame.grid_columnconfigure(3, weight=2) # Peso al filtro
        
        # Llama al método para crear la tabla de estudiantes
        self.create_students_treeview_table()
    
    def create_students_treeview_table(self):
        """
        Configurar el widget Treeview de ttk para mostrar datos de los
        estudiantes, incluyendo encabezados, columnas y scrollbar.
        """
        # Contenedor principal para la tabla con borde
        table_main_container = ctk.CTkFrame(self, corner_radius=8, 
                                          border_width=1,
                                          border_color=("gray80", "gray20"))
        table_main_container.pack(fill="both", expand=True, pady=(0,10), padx=0)

        # Frame interno para la tabla con fondo y padding
        table_container_frame = ctk.CTkFrame(table_main_container, 
                                           corner_radius=15,
                                           fg_color=("white", "gray15"))
        table_container_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Crear el Treeview APLICANDO el estilo global "Modern.Treeview"
        self.tree = ttk.Treeview(table_container_frame,
                               columns=("Codigo", "Nombre", "Cedula", "Proyecto"),
                               show="tree headings",
                               style="Modern.Treeview") # Se aplica el estilo definido en MainWindow

        # Encabezados de la tabla
        self.tree.heading("Codigo", text="📋 Código", anchor="w")
        self.tree.heading("Nombre", text="👤 Nombre", anchor="w")
        self.tree.heading("Cedula", text="🆔 Cédula", anchor="w")
        self.tree.heading("Proyecto", text="📁 Proyecto Curricular", anchor="w")

        # Columnas de la tabla (ancho y expansion)
        self.tree.column("#0", width=0, stretch=False) # Columna fantasma
        self.tree.column("Codigo", width=120, stretch=False, anchor="w")
        self.tree.column("Nombre", width=300, stretch=True, anchor="w")
        self.tree.column("Cedula", width=150, stretch=False, anchor="w")
        self.tree.column("Proyecto", width=350, stretch=True, anchor="w")

        # Empaqueta el Treeview para que se muestre
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Prevenir que el usuario redimensione las columnas
        self.tree.bind("<Button-1>", self.prevent_resize)
        self.tree.bind("<B1-Motion>", self.prevent_resize)
        
        # Scrollbar para la tabla
        scrollbar = ctk.CTkScrollbar(table_container_frame, 
                                   command=self.tree.yview,
                                   corner_radius=8,
                                   width=12)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0,5))
        
        # Configura el Treeview para que se desplace con la scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)

    def refresh_students(self):
        """
        Limpia la tabla, obtiene los estudiantes de la base de datos aplicando
        los filtros de búsqueda y proyecto, y vuelve a llenar la tabla.
        """
        # Elimina todos los items existentes en el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtiene los términos de búsqueda y el filtro de proyecto actuales
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        project_filter = self.project_filter.get() if hasattr(self, 'project_filter') and self.project_filter.get() != "Todos" else ""
        
        # Llama al modelo para obtener la lista de estudiantes filtrada
        students = self.student_model.get_all_students(search_term, project_filter_name=project_filter) 
        
        # Itera sobre los estudiantes obtenidos y los inserta en la tabla.
        for i, student_data in enumerate(students):
            # Simplificar la visualización sin iconos excesivos para mejor legibilidad
            codigo_display = str(student_data[0])
            nombre_display = student_data[1]
            cedula_display = str(student_data[2])
            proyecto_display = student_data[3] or 'Sin proyecto'
            
            # Inserta una nueva fila en el Treeview.
            item_id = self.tree.insert("", "end", iid=str(student_data[0]), values=(
                codigo_display,
                nombre_display, 
                cedula_display,
                proyecto_display
            ))
            
            # Alternar colores de fila para mejor legibilidad
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
        
        # Configurar el color de las filas alternas según el tema actual
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
        
        # Crea el frame y los botones de acciones (Editar/Eliminar) si no existen.
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                 text="Editar Seleccionado",
                                                 command=self.edit_selected_student, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_student, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Vincula el evento de selección en la tabla a la función on_student_select.
            self.tree.bind("<<TreeviewSelect>>", self.on_student_select)
        
        # Llama a on_student_select para establecer el estado inicial de los botones.
        self.on_student_select()

    def on_student_select(self, event=None):
        """
        Manejador de evento para la selección de un estudiante en la tabla.
        Habilita o deshabilita los botones de "Editar" y "Eliminar" según
        si hay un estudiante seleccionado o no.
        """
        if hasattr(self, 'edit_selected_btn'): # Check if buttons exist
            # Obtiene el identificador del item seleccionado.
            selected_item_iid = self.tree.focus() 
            if selected_item_iid:
                # Si hay selección, habilita los botones.
                self.edit_selected_btn.configure(state="normal")
                self.delete_selected_btn.configure(state="normal")
            else:
                # Si no hay selección, deshabilita los botones.
                self.edit_selected_btn.configure(state="disabled")
                self.delete_selected_btn.configure(state="disabled")

    def get_selected_student_data(self):
        """
        Obtiene los datos del estudiante actualmente seleccionado en la tabla.
        Retorna una tupla con los datos del estudiante o None si no hay selección.
        """
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un estudiante de la tabla.", parent=self)
            return None
        
        # Obtiene los valores de las columnas del item seleccionado.
        tree_values = self.tree.item(selected_item_iid, "values")
        # Los valores ahora están limpios, sin necesidad de remover iconos
        codigo = int(tree_values[0])
        nombre = tree_values[1]
        cedula = int(tree_values[2])
        proyecto = tree_values[3]
        
        return (codigo, nombre, cedula, proyecto)

    def edit_selected_student(self):
        """
        Abre un diálogo para editar la información del estudiante seleccionado.
        Si la edición es exitosa, actualiza la base de datos y refresca la tabla.
        """
        student_display_data = self.get_selected_student_data()
        if student_display_data:
            # Crea y muestra el diálogo de edición.
            dialog = StudentDialog(self, "Editar Estudiante", student_data_for_dialog=student_display_data, student_model=self.student_model)
            # Si el diálogo se cerró guardando cambios...
            if dialog.result: 
                original_codigo, nombre, cedula, proyecto_id, new_codigo = dialog.result
                # Llama al modelo para actualizar el estudiante.
                self.student_model.update_student(original_codigo, nombre, cedula, proyecto_id, new_codigo=new_codigo)
                # Refresca la tabla para mostrar los cambios.
                self.refresh_students()

    def delete_selected_student(self):
        """
        Elimina al estudiante seleccionado de la base de datos, previa confirmación.
        """
        student_display_data = self.get_selected_student_data()
        if student_display_data:
            codigo_to_delete = student_display_data[0]
            nombre_to_delete = student_display_data[1]
            # Muestra un cuadro de diálogo de confirmación.
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al estudiante {nombre_to_delete} (Cód: {codigo_to_delete})?", parent=self):
                # Llama al modelo para eliminar el estudiante.
                self.student_model.delete_student(codigo_to_delete)
                # Refresca la tabla.
                self.refresh_students()
    
    def on_search(self, event=None): 
        """
        Se ejecuta cada vez que el usuario escribe en el campo de búsqueda.
        Llama a refresh_students para filtrar los resultados.
        """
        self.refresh_students()
    
    def on_filter_change(self, value=None): 
        """
        Se ejecuta cuando el usuario cambia el valor del filtro de proyecto.
        Llama a refresh_students para aplicar el nuevo filtro.
        """
        self.refresh_students()
    
    def add_student_dialog(self):
        """
        Abre un diálogo para agregar un nuevo estudiante.
        Si se guarda el nuevo estudiante, lo agrega a la base de datos y refresca la tabla.
        """
        dialog = StudentDialog(self, "Agregar Estudiante", student_model=self.student_model)
        # Si el diálogo se cerró guardando...
        if dialog.result:
            codigo, nombre, cedula, proyecto_id = dialog.result
            # Llama al modelo para agregar el nuevo estudiante.
            self.student_model.add_student(codigo, nombre, cedula, proyecto_id)
            # Refresca la tabla para mostrar el nuevo registro.
            self.refresh_students()
    
    # --- MODIFICADO: Simplificar el método de cambio de tema ---
    def on_theme_change(self, event=None):
        """
        Actualiza la vista cuando cambia el tema. Los estilos ya fueron 
        actualizados globalmente por MainWindow.
        """
        if hasattr(self, 'tree'):
            # Solo necesitamos refrescar la lista de estudiantes para que 
            # los nuevos colores de las filas alternas se apliquen.
            # Los estilos base del Treeview se actualizan automáticamente.
            self.refresh_students()
            self.update_idletasks()

class StudentDialog(ctk.CTkToplevel):
    """
    Clase para la ventana de diálogo (popup) que se usa tanto para agregar
    como para editar estudiantes.
    """
    def __init__(self, parent, title, student_data_for_dialog=None, student_model=None):
        """
        Constructor del diálogo de estudiante.
        :param parent: La ventana padre.
        :param title: El título de la ventana de diálogo.
        :param student_data_for_dialog: Datos del estudiante si se está editando, None si se agrega.
        :param student_model: La instancia del modelo de datos de estudiante.
        """
        super().__init__(parent)
        self.title(title) # Establece el título.
        self.geometry("800x300") # Establece el tamaño.
        self.transient(parent) # Hace que la ventana se mantenga sobre la principal.
        self.grab_set() # Captura todos los eventos, bloqueando la ventana principal.
        self.lift() # Asegura que la ventana esté al frente.
        
        self.result = None # Almacenará los datos del formulario si se guarda.
        self.student_model = student_model 
        self.editing = student_data_for_dialog is not None # Bandera para saber si es edición o creación.
        # Guarda el código original del estudiante en modo edición.
        self.original_student_code = student_data_for_dialog[0] if self.editing else None

        # Frame principal del diálogo.
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Creación de etiquetas y campos de entrada para los datos del estudiante.
        ctk.CTkLabel(main_frame, text="Código:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre Completo:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Cédula:", font=get_font("normal")).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.cedula_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.cedula_entry.grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Proyecto Curricular:", font=get_font("normal")).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.projects_data = self.student_model.get_curriculum_projects() 
        project_names = ["Seleccione un proyecto..."] + [p[1] for p in self.projects_data]
        self.proyecto_combo = ctk.CTkComboBox(main_frame, values=project_names, font=get_font("normal"), state="readonly")
        self.proyecto_combo.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        self.proyecto_combo.set(project_names[0]) # Valor por defecto.

        # Configura la columna de los campos de entrada para que se expanda.
        main_frame.grid_columnconfigure(1, weight=1)

        # Si estamos en modo de edición, llena los campos con los datos del estudiante.
        if self.editing:
            self.codigo_entry.insert(0, str(student_data_for_dialog[0]))
            self.nombre_entry.insert(0, student_data_for_dialog[1])
            self.cedula_entry.insert(0, str(student_data_for_dialog[2]))
            if student_data_for_dialog[3] and student_data_for_dialog[3] != "Sin proyecto":
                self.proyecto_combo.set(student_data_for_dialog[3])
            else:
                self.proyecto_combo.set("Seleccione un proyecto...")
        
        # Frame para los botones de acción.
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20,0), sticky="ew")
        
        # Botón para guardar los cambios.
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        # Botón para cancelar y cerrar el diálogo.
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)

        # Centrar el diálogo
        self._center_dialog()
        
        # Pone el foco en el campo de código al abrir el diálogo.
        self.codigo_entry.focus_set()
        # Espera a que la ventana de diálogo se cierre antes de continuar.
        self.wait_window(self) 

    def _center_dialog(self): # This method might not be strictly necessary if parent centering works well
        """
        Método auxiliar para centrar el diálogo en relación a la ventana principal.
        """
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
        """
        Se ejecuta al presionar el botón "Guardar".
        Valida los datos de entrada, los empaqueta en self.result y cierra el diálogo.
        """
        codigo_str = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        cedula_str = self.cedula_entry.get().strip()
        proyecto_nombre_seleccionado = self.proyecto_combo.get()

        # Validación de tipo de dato numérico.
        try:
            codigo = int(codigo_str)
        except ValueError:
            messagebox.showerror("Error de Validación", "El código debe ser un número entero.", parent=self)
            return
        
        # La cedula es originalmente cero por si no se define una en la creacion
        cedula = 0
        if cedula_str:
            # Validación de tipo de dato numérico.
            try:
                cedula = int(codigo_str)
            except ValueError:
                messagebox.showerror("Error de Validación", "La cédula debe ser un número entero.", parent=self)
                return
            
        # Obtiene el ID del proyecto a partir del nombre seleccionado.
        proyecto_id = None
        if proyecto_nombre_seleccionado != "Seleccione un proyecto...":
            for p_id, p_name in self.projects_data:
                if p_name == proyecto_nombre_seleccionado:
                    proyecto_id = p_id
                    break
        
        # Prepara el resultado dependiendo de si es edición o creación.
        if self.editing:
            new_codigo_val = codigo if codigo != self.original_student_code else self.original_student_code
            # El resultado incluye el código original y el nuevo código (pueden ser iguales).
            self.result = (self.original_student_code, nombre, cedula, proyecto_id, new_codigo_val)
        else:
            # El resultado para un nuevo estudiante.
            self.result = (codigo, nombre, cedula, proyecto_id)
        
        # Cierra la ventana de diálogo.
        self.destroy()
    
    def cancel(self):
        """
        Se ejecuta al presionar el botón "Cancelar".
        Establece el resultado como None y cierra el diálogo.
        """
        self.result = None
        self.destroy()