import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import PersonalLaboratorioModel
from utils.font_config import get_font
from utils.validators import *

class PersonalView(ctk.CTkFrame):
    def __init__(self, parent):
        # Hacer el frame principal transparente
        super().__init__(parent, fg_color="transparent")
        
        # Inicializa el modelo de datos para interactuar con la base de datos de Personal
        self.personal_model = PersonalLaboratorioModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15, fill="both", expand=True) # Padding general para la vista

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        # Creacion de UI y llenar datos de tabla
        self.setup_ui()
        self.refresh_personal()
    
    def prevent_resize(self, event):
        """Impide que el usuario redimensione las columnas con el mouse"""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        '''Metodo para construir los componentes visuales de la vista (título, cuadro de búsqueda, filtro y botones)'''
        # Titulo
        title = ctk.CTkLabel(self, text="Gestión de Personal de Laboratorio", font=get_font("title", "bold"))
        title.pack(pady=(10, 20)) # Padding inferior para separar del siguiente frame
        
        # Frame para cuadro de busqueda
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0) # Padding inferior y sin padding horizontal interno al search_frame
        
        # Cuadro de busqueda 
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Nombre", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Vincula el evento de liberación de tecla para llamar a la función de búsqueda
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Filtro por Cargo
        ctk.CTkLabel(search_frame, text="Cargo:", font=get_font("normal")).grid(row=0, column=2, padx=(10,5), pady=10, sticky="w")
        self.cargo_filter = ctk.CTkComboBox(search_frame, 
                                          values=["Todos", "Monitor", "Laboratorista"],
                                          font=get_font("normal"))
        self.cargo_filter.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        self.cargo_filter.set("Todos") # Establece "Todos" como valor por defecto
        # Configura el comando a ejecutar cuando cambia la selección del filtro
        self.cargo_filter.configure(command=self.on_filter_change)
        
        # Boton añadir personal
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Personal", command=self.add_personal_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=4, padx=(10,10), pady=10)
        
        # Configura la expansión de las columnas en el grid del frame de búsqueda
        search_frame.grid_columnconfigure(1, weight=3) # Más peso a la búsqueda
        search_frame.grid_columnconfigure(3, weight=2) # Peso al filtro
        
        # Llama al método para crear la tabla de Personal
        self.create_personal_treeview_table()
    
    def create_personal_treeview_table(self):
        """
        Configurar el widget Treeview de ttk para mostrar datos de los
        Personal, incluyendo encabezados, columnas y scrollbar.
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
                               columns=("Nombre", "Cargo"),
                               show="tree headings",
                               style="Modern.Treeview")

        # Encabezados de la tabla
        self.tree.heading("Nombre", text="👤 Nombre", anchor="w")
        self.tree.heading("Cargo", text="💼 Cargo", anchor="w")

        # Columnas de la tabla (ancho y expansion)
        self.tree.column("#0", width=0, stretch=False) # Columna fantasma
        self.tree.column("Nombre", width=400, stretch=True, anchor="w")
        self.tree.column("Cargo", width=200, stretch=False, anchor="w")

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

    def refresh_personal(self):
        """
        Limpia la tabla, obtiene los Personal de la base de datos aplicando
        los filtros de búsqueda y cargo, y vuelve a llenar la tabla.
        """
        # Elimina todos los items existentes en el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtiene los términos de búsqueda y el filtro de cargo actuales
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        cargo_filter = self.cargo_filter.get() if hasattr(self, 'cargo_filter') and self.cargo_filter.get() != "Todos" else ""
        
        # Llama al modelo para obtener la lista de Personal filtrada
        personal = self.personal_model.get_all_personal(search_term, cargo_filter_name=cargo_filter) 
        
        # Itera sobre los Personal obtenidos y los inserta en la tabla
        for i, personal_data in enumerate(personal):
            nombre_display = personal_data[1]
            # Convertir el valor numérico del cargo a texto
            cargo_display = "Monitor" if personal_data[2] == 1 else "Laboratorista"
            
            # Inserta una nueva fila en el Treeview
            item_id = self.tree.insert("", "end", iid=str(personal_data[0]), values=(
                nombre_display,
                cargo_display
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
                                                 command=self.edit_selected_professor, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_professor, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Vincula el evento de selección en la tabla a la función on_professor_select.
            self.tree.bind("<<TreeviewSelect>>", self.on_professor_select)
        
        # Llama a on_professor_select para establecer el estado inicial de los botones.
        self.on_professor_select()

    def on_professor_select(self, event=None):
        """
        Manejador de evento para la selección de un profesor en la tabla.
        Habilita o deshabilita los botones de "Editar" y "Eliminar" según
        si hay un profesor seleccionado o no.
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

    def get_selected_professor_data(self):
        """
        Obtiene los datos del personal actualmente seleccionado en la tabla.
        Retorna una tupla con los datos del personal o None si no hay selección.
        """
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un personal de la tabla.", parent=self)
            return None
        
        # Obtiene los valores de las columnas del item seleccionado.
        tree_values = self.tree.item(selected_item_iid, "values")
        # Los valores ahora están limpios, sin necesidad de remover iconos
        nombre = tree_values[0]
        cargo = tree_values[1]
        
        # Obtener el ID del personal desde la base de datos
        personal_list = self.personal_model.get_all_personal()
        for p in personal_list:
            if p[1] == nombre:  # Comparar por nombre
                return (p[0], nombre, cargo)  # ID, nombre, cargo
        
        return None

    def edit_selected_professor(self):
        """
        Abre un diálogo para editar la información del personal seleccionado.
        Si la edición es exitosa, actualiza la base de datos y refresca la tabla.
        """
        personal_display_data = self.get_selected_professor_data()
        if personal_display_data:
            # Crea y muestra el diálogo de edición.
            dialog = PersonalDialog(self, "Editar Personal", personal_data=personal_display_data)
            # Si el diálogo se cerró guardando cambios...
            if dialog.result: 
                nombre, cargo_value = dialog.result
                personal_id = personal_display_data[0]
                # Llama al modelo para actualizar el personal.
                if self.personal_model.update_personal(personal_id, nombre, cargo_value):
                    messagebox.showinfo("Éxito", "Personal actualizado correctamente.", parent=self)
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el personal.", parent=self)
                # Refresca la tabla para mostrar los cambios.
                self.refresh_personal()

    def delete_selected_professor(self):
        """
        Elimina al personal seleccionado de la base de datos, previa confirmación.
        """
        personal_display_data = self.get_selected_professor_data()
        if personal_display_data:
            personal_id = personal_display_data[0]
            nombre_to_delete = personal_display_data[1]
            # Muestra un cuadro de diálogo de confirmación.
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al personal {nombre_to_delete}?", parent=self):
                # Llama al modelo para eliminar el personal.
                if self.personal_model.delete_personal(personal_id):
                    messagebox.showinfo("Éxito", "Personal eliminado correctamente.", parent=self)
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el personal.", parent=self)
                # Refresca la tabla.
                self.refresh_personal()
    
    def on_search(self, event=None): 
        """
        Se ejecuta cada vez que el usuario escribe en el campo de búsqueda.
        Llama a refresh_personal para filtrar los resultados.
        """
        self.refresh_personal()
    
    def on_filter_change(self, _=None):
        """Actualiza la tabla cuando cambia el filtro"""
        self.refresh_personal()

    def add_personal_dialog(self):
        """
        Abre un diálogo para agregar un nuevo personal.
        Si se guarda el nuevo personal, lo agrega a la base de datos y refresca la tabla.
        """
        dialog = PersonalDialog(self, "Agregar Personal")
        # Si el diálogo se cerró guardando...
        if dialog.result:
            nombre, cargo_value = dialog.result
            # Llama al modelo para agregar el nuevo personal.
            if self.personal_model.add_personal(nombre, cargo_value):
                messagebox.showinfo("Éxito", "Personal agregado correctamente.", parent=self)
            else:
                messagebox.showerror("Error", "No se pudo agregar el personal.", parent=self)
            # Refresca la tabla para mostrar el nuevo registro.
            self.refresh_personal()
    
    # --- MODIFICADO: Simplificar el método de cambio de tema ---
    def on_theme_change(self, event=None):
        """
        Actualiza la vista cuando cambia el tema. Los estilos ya fueron 
        actualizados globalmente por MainWindow.
        """
        if hasattr(self, 'tree'):
            # Solo necesitamos refrescar la lista de Personal para que 
            # los nuevos colores de las filas alternas se apliquen.
            # Los estilos base del Treeview se actualizan automáticamente.
            self.refresh_personal()
            self.update_idletasks()

class PersonalDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, personal_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x300")
        self.transient(parent)
        self.grab_set()
        self.lift()

        self.result = None
        self.editing = personal_data is not None

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Campos del formulario
        ctk.CTkLabel(main_frame, text="Nombre Completo:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="Cargo:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.cargo_combo = ctk.CTkComboBox(main_frame, 
                                         values=["Monitor", "Laboratorista"],
                                         font=get_font("normal"),
                                         state="readonly")
        self.cargo_combo.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        self.cargo_combo.set("Monitor")

        # Configurar la columna de entrada para que se expanda
        main_frame.grid_columnconfigure(1, weight=1)

        # Si estamos editando, llenar los campos con los datos existentes
        if self.editing:
            self.nombre_entry.insert(0, personal_data[1])
            self.cargo_combo.set("Monitor" if personal_data[2] == 1 else "Laboratorista")

        # Frame para botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20,0), sticky="ew")

        # Botones de acción
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, 
                                 fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)

        # Centrar el diálogo
        self._center_dialog()
        
        # Poner el foco en el campo de nombre
        self.nombre_entry.focus_set()
        
        # Esperar a que la ventana se cierre
        self.wait_window(self)

    def _center_dialog(self):
        """Centra el diálogo en relación a la ventana principal"""
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
        """Guarda los datos del formulario"""
        nombre = self.nombre_entry.get().strip()
        cargo = self.cargo_combo.get()

        # Validación de campos obligatorios
        if not nombre:
            messagebox.showerror("Error de Validación", 
                               "El nombre es un campo obligatorio.", 
                               parent=self)
            return

        # Convertir cargo a valor numérico (0 para Laboratorista, 1 para Monitor)
        cargo_value = 1 if cargo == "Monitor" else 0

        # Preparar el resultado
        self.result = (nombre, cargo_value)
        self.destroy()

    def cancel(self):
        """Cancela la operación y cierra el diálogo"""
        self.result = None
        self.destroy()
