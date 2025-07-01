import customtkinter as ctk
from tkinter import messagebox, ttk
from database.models import RoomModel
from utils.font_config import get_font
from utils.validators import *

class RoomsView(ctk.CTkFrame):
    def __init__(self, parent):
        # Hacer el frame principal transparente
        super().__init__(parent, fg_color="transparent")
        
        # Inicializa el modelo de datos para interactuar con la base de datos de salas
        self.room_model = RoomModel()
        
        # Configurar padding para el frame principal de la vista
        self.pack_propagate(False) # Evitar que los widgets hijos controlen el tamaño del frame principal
        self.pack(padx=15, pady=15, fill="both", expand=True) # Padding general para la vista

        # Vincular el cambio de tema
        self.bind("<<ThemeChanged>>", self.on_theme_change)

        # Creacion de UI y llenar datos de tabla
        self.setup_ui()
        self.refresh_rooms()
    
    def prevent_resize(self, event):
        """Impide que el usuario redimensione las columnas con el mouse"""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def setup_ui(self):
        '''Metodo para construir los componentes visuales de la vista (título, cuadro de búsqueda y botones)'''
        # Titulo
        title = ctk.CTkLabel(self, text="Gestión de Salas", font=get_font("title", "bold"))
        title.pack(pady=(10, 20)) # Padding inferior para separar del siguiente frame
        
        # Frame para cuadro de busqueda
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=(0, 15), padx=0) # Padding inferior y sin padding horizontal interno al search_frame
        
        # Cuadro de busqueda 
        ctk.CTkLabel(search_frame, text="Buscar:", font=get_font("normal")).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Código o nombre de la sala...", font=get_font("normal"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Vincula el evento de liberación de tecla para llamar a la función de búsqueda
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Boton añadir sala
        add_btn = ctk.CTkButton(search_frame, text="+ Agregar Sala", command=self.add_room_dialog, font=get_font("normal"))
        add_btn.grid(row=0, column=2, padx=(10,10), pady=10)
        
        # Configura la expansión de las columnas en el grid del frame de búsqueda
        search_frame.grid_columnconfigure(1, weight=3) # Más peso a la búsqueda
        
        # Llama al método para crear la tabla de salas
        self.create_rooms_treeview_table()
    
    def create_rooms_treeview_table(self):
        """
        Configurar el widget Treeview de ttk para mostrar datos de las
        salas, incluyendo encabezados, columnas y scrollbar.
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
                               columns=("Codigo", "Nombre", "Estado"),
                               show="tree headings",
                               style="Modern.Treeview") # Se aplica el estilo definido en MainWindow

        # Encabezados de la tabla
        self.tree.heading("Codigo", text="🔑 Código", anchor="w")
        self.tree.heading("Nombre", text="🏢 Nombre", anchor="w")
        self.tree.heading("Estado", text="📊 Estado", anchor="w")

        # Columnas de la tabla (ancho y expansion)
        self.tree.column("#0", width=0, stretch=False) # Columna fantasma
        self.tree.column("Codigo", width=150, stretch=False, anchor="w")
        self.tree.column("Nombre", width=300, stretch=True, anchor="w")
        self.tree.column("Estado", width=150, stretch=False, anchor="w")

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

    def refresh_rooms(self):
        """
        Limpia la tabla, obtiene las salas de la base de datos y vuelve a llenar la tabla.
        """
        # Elimina todos los items existentes en el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtiene los términos de búsqueda actuales
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        
        # Llama al modelo para obtener la lista de salas
        rooms = self.room_model.get_all_rooms_with_status()
        
        # Itera sobre las salas obtenidas y las inserta en la tabla.
        for i, room_data in enumerate(rooms):
            # Simplificar la visualización sin iconos excesivos para mejor legibilidad
            codigo_display = str(room_data[1])  # codigo_interno
            nombre_display = room_data[2]       # nombre
            estado_display = room_data[3]       # estado
            
            # Inserta una nueva fila en el Treeview.
            item_id = self.tree.insert("", "end", iid=str(room_data[0]), values=(
                codigo_display,
                nombre_display, 
                estado_display
            ))
            
            # Alternar colores de fila para mejor legibilidad
            if i % 2 == 1:
                self.tree.item(item_id, tags=('alternate',))
            
            # Colorear el estado
            if estado_display == "Ocupada":
                self.tree.item(item_id, tags=('occupied',))
            else:
                self.tree.item(item_id, tags=('available',))
        
        # Configurar el color de las filas alternas según el tema actual
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.tree.tag_configure('alternate', background='#323232')
            self.tree.tag_configure('occupied', foreground='#ef4444')
            self.tree.tag_configure('available', foreground='#22c55e')
        else:
            self.tree.tag_configure('alternate', background='#f8f9fa')
            self.tree.tag_configure('occupied', foreground='#dc2626')
            self.tree.tag_configure('available', foreground='#16a34a')
        
        # Crea el frame y los botones de acciones (Editar/Eliminar) si no existen.
        if not hasattr(self, 'selected_actions_frame'):
            self.selected_actions_frame = ctk.CTkFrame(self, corner_radius=12)
            self.selected_actions_frame.pack(pady=(15,0), padx=0, fill="x")

            self.edit_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                 text="Editar Seleccionado",
                                                 command=self.edit_selected_room, 
                                                 state="disabled", 
                                                 font=get_font("normal"),
                                                 corner_radius=8,
                                                 height=35)
            self.edit_selected_btn.pack(side="left", padx=8, pady=8)

            self.delete_selected_btn = ctk.CTkButton(self.selected_actions_frame, 
                                                   text="Eliminar Seleccionado",
                                                   command=self.delete_selected_room, 
                                                   state="disabled", 
                                                   fg_color=("#ef4444", "#dc2626"),
                                                   hover_color=("#dc2626", "#b91c1c"),
                                                   font=get_font("normal"),
                                                   corner_radius=8,
                                                   height=35)
            self.delete_selected_btn.pack(side="right", padx=8, pady=8)
            
            # Vincula el evento de selección en la tabla a la función on_room_select.
            self.tree.bind("<<TreeviewSelect>>", self.on_room_select)
        
        # Llama a on_room_select para establecer el estado inicial de los botones.
        self.on_room_select()

    def on_room_select(self, event=None):
        """
        Manejador de evento para la selección de una sala en la tabla.
        Habilita o deshabilita los botones de "Editar" y "Eliminar" según
        si hay una sala seleccionada o no.
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

    def get_selected_room_data(self):
        """
        Obtiene los datos de la sala actualmente seleccionada en la tabla.
        Retorna una tupla con los datos de la sala o None si no hay selección.
        """
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una sala de la tabla.", parent=self)
            return None
        
        # Obtiene los valores de las columnas del item seleccionado.
        tree_values = self.tree.item(selected_item_iid, "values")
        # Los valores ahora están limpios, sin necesidad de remover iconos
        codigo = tree_values[0]
        nombre = tree_values[1]
        estado = tree_values[2]
        
        return (codigo, nombre, estado)

    def edit_selected_room(self):
        """
        Abre un diálogo para editar la información de la sala seleccionada.
        Si la edición es exitosa, actualiza la base de datos y refresca la tabla.
        """
        room_display_data = self.get_selected_room_data()
        if room_display_data:
            # Crea y muestra el diálogo de edición.
            dialog = RoomDialog(self, "Editar Sala", room_data_for_dialog=room_display_data, room_model=self.room_model)
            # Si el diálogo se cerró guardando cambios...
            if dialog.result: 
                original_codigo, nombre, new_codigo = dialog.result
                # Llama al modelo para actualizar la sala.
                self.room_model.update_room(original_codigo, nombre, new_codigo=new_codigo)
                # Refresca la tabla para mostrar los cambios.
                self.refresh_rooms()

    def delete_selected_room(self):
        """
        Elimina la sala seleccionada de la base de datos, previa confirmación.
        """
        room_display_data = self.get_selected_room_data()
        if room_display_data:
            codigo_to_delete = room_display_data[0]
            nombre_to_delete = room_display_data[1]
            # Muestra un cuadro de diálogo de confirmación.
            if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar la sala {nombre_to_delete} (Cód: {codigo_to_delete})?", parent=self):
                # Llama al modelo para eliminar la sala.
                self.room_model.delete_room(codigo_to_delete)
                # Refresca la tabla.
                self.refresh_rooms()
    
    def on_search(self, event=None): 
        """
        Se ejecuta cada vez que el usuario escribe en el campo de búsqueda.
        Llama a refresh_rooms para filtrar los resultados.
        """
        self.refresh_rooms()
    
    def add_room_dialog(self):
        """
        Abre un diálogo para agregar una nueva sala.
        Si se guarda la nueva sala, la agrega a la base de datos y refresca la tabla.
        """
        dialog = RoomDialog(self, "Agregar Sala", room_model=self.room_model)
        # Si el diálogo se cerró guardando...
        if dialog.result:
            codigo, nombre = dialog.result #type: ignore
            # Llama al modelo para agregar la nueva sala.
            self.room_model.add_room(codigo, nombre)
            # Refresca la tabla para mostrar el nuevo registro.
            self.refresh_rooms()
    
    # --- MODIFICADO: Simplificar el método de cambio de tema ---
    def on_theme_change(self, event=None):
        """
        Actualiza la vista cuando cambia el tema. Los estilos ya fueron 
        actualizados globalmente por MainWindow.
        """
        if hasattr(self, 'tree'):
            # Solo necesitamos refrescar la lista de salas para que 
            # los nuevos colores de las filas alternas se apliquen.
            # Los estilos base del Treeview se actualizan automáticamente.
            self.refresh_rooms()
            self.update_idletasks()

class RoomDialog(ctk.CTkToplevel):
    """
    Clase para la ventana de diálogo (popup) que se usa tanto para agregar
    como para editar salas.
    """
    def __init__(self, parent, title, room_data_for_dialog=None, room_model=None):
        """
        Constructor del diálogo de sala.
        :param parent: La ventana padre.
        :param title: El título de la ventana de diálogo.
        :param room_data_for_dialog: Datos de la sala si se está editando, None si se agrega.
        :param room_model: La instancia del modelo de datos de sala.
        """
        super().__init__(parent)
        self.title(title) # Establece el título.
        self.geometry("800x200") # Establece el tamaño.
        self.transient(parent) # Hace que la ventana se mantenga sobre la principal.
        self.grab_set() # Captura todos los eventos, bloqueando la ventana principal.
        self.lift() # Asegura que la ventana esté al frente.
        self._center_dialog()

        self.result = None # Almacenará los datos del formulario si se guarda.
        self.room_model = room_model 
        self.editing = room_data_for_dialog is not None # Bandera para saber si es edición o creación.
        # Guarda el código original de la sala en modo edición.
        self.original_room_code = room_data_for_dialog[0] if self.editing else None

        # Frame principal del diálogo.
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Creación de etiquetas y campos de entrada para los datos de la sala.
        ctk.CTkLabel(main_frame, text="Código Interno:", font=get_font("normal")).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.codigo_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="Nombre:", font=get_font("normal")).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.nombre_entry = ctk.CTkEntry(main_frame, font=get_font("normal"))
        self.nombre_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        # Configura la columna de los campos de entrada para que se expanda.
        main_frame.grid_columnconfigure(1, weight=1)

        # Si estamos en modo de edición, llena los campos con los datos de la sala.
        if self.editing:
            self.codigo_entry.insert(0, str(room_data_for_dialog[0]))
            self.nombre_entry.insert(0, room_data_for_dialog[1])
        
        # Frame para los botones de acción.
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20,0), sticky="ew")
        
        # Botón para guardar los cambios.
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=self.save, font=get_font("normal"))
        save_btn.pack(side="left", expand=True, padx=5)
        
        # Botón para cancelar y cerrar el diálogo.
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="gray", font=get_font("normal"))
        cancel_btn.pack(side="right", expand=True, padx=5)

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
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()

        # Validación de campos obligatorios.
        if not codigo or not nombre:
            messagebox.showerror("Error de Validación", "Código y Nombre son obligatorios.", parent=self)
            return
        
        # Prepara el resultado dependiendo de si es edición o creación.
        if self.editing:
            new_codigo_val = codigo if codigo != self.original_room_code else self.original_room_code
            # El resultado incluye el código original y el nuevo código (pueden ser iguales).
            self.result = (self.original_room_code, nombre, new_codigo_val)
        else:
            # El resultado para una nueva sala.
            self.result = (codigo, nombre)
        
        # Cierra la ventana de diálogo.
        self.destroy()
    
    def cancel(self):
        """
        Se ejecuta al presionar el botón "Cancelar".
        Establece el resultado como None y cierra el diálogo.
        """
        self.result = None
        self.destroy()