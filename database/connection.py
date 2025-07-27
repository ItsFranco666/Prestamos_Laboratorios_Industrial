import sqlite3
import os
import sys
import shutil

class DatabaseManager:
    def __init__(self, db_name='uso_de_espacios.db'):
        self.db_name = db_name
        self.db_path = self._get_database_path()
        self.init_database()
    
    def _get_database_path(self):
        '''
        Determines the appropriate path for the database file.
        In a PyInstaller bundle, it will be in a persistent user data directory.
        Otherwise, it will be in the current working directory.
        '''
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            # Use a persistent user data directory
            if sys.platform == 'win32':
                appdata = os.environ.get('APPDATA', '.')
                app_data_dir = os.path.join(appdata, 'Gestion_de_Laboratorios')
            elif sys.platform == 'darwin':
                app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support'), 'Gestion_de_Laboratorios')
            else: # Linux and other Unix-like systems
                app_data_dir = os.path.join(os.path.expanduser('~/.local/share'), 'Gestion_de_Laboratorios')
            
            os.makedirs(app_data_dir, exist_ok=True)
            db_file_path = os.path.join(app_data_dir, self.db_name)

            # Check if the database already exists in the persistent location
            if not os.path.exists(db_file_path):
                # If not, copy it from the bundled location (sys._MEIPASS)
                bundled_db_path = os.path.join(sys._MEIPASS, self.db_name)
                if os.path.exists(bundled_db_path):
                    shutil.copy2(bundled_db_path, db_file_path)
                    print(f'Copied initial database from {bundled_db_path} to {db_file_path}')
                else:
                    print(f'Bundled database not found at {bundled_db_path}. A new one will be created.')
            return db_file_path
        else:
            # Running as a script
            return self.db_name # Keep it in the current directory for development
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        ''' Database schema for initialization '''
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Initialize the database if not created
        cursor.executescript('''
            -- Enable foreign key constraints
            PRAGMA foreign_keys = ON;
            
            CREATE TABLE IF NOT EXISTS proyectos_curriculares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS salas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT,
                nombre TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'DISPONIBLE' CHECK (estado IN ('DISPONIBLE', 'OCUPADA'))
            );
            
            CREATE TABLE IF NOT EXISTS sedes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS personal_laboratorio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cargo INTEGER NOT NULL CHECK (cargo IN (0, 1))
            );
            
            CREATE TABLE IF NOT EXISTS estudiantes (
                codigo INTEGER PRIMARY KEY,
                nombre TEXT,
                cedula INTEGER,
                proyecto_curricular_id INTEGER REFERENCES proyectos_curriculares(id)
            );
            
            CREATE TABLE IF NOT EXISTS profesores (
                cedula INTEGER PRIMARY KEY,
                nombre TEXT,
                proyecto_curricular_id INTEGER REFERENCES proyectos_curriculares(id)
            );
            
            CREATE TABLE IF NOT EXISTS inventario (
                codigo TEXT PRIMARY KEY,
                marca_serie TEXT,
                documento_funcionario INTEGER,
                nombre_funcionario TEXT,
                descripcion TEXT,
                contenido TEXT,
                estado TEXT NOT NULL CHECK (estado IN ('DISPONIBLE', 'DAÑADO', 'EN USO')),
                sede_id INTEGER REFERENCES sedes(id)
            );
            
            CREATE TABLE IF NOT EXISTS equipos (
                codigo TEXT PRIMARY KEY,
                sala_id INTEGER REFERENCES salas(id),
                numero_equipo INTEGER,
                descripcion TEXT,
                estado INTEGER NOT NULL CHECK (estado IN (0, 1)),
                observaciones TEXT
            );
            
            CREATE TABLE IF NOT EXISTS prestamos_salas_profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_entrada TIMESTAMP NOT NULL,
                laboratorista INTEGER REFERENCES personal_laboratorio(id),
                monitor INTEGER REFERENCES personal_laboratorio(id),
                sala_id INTEGER REFERENCES salas(id) NOT NULL,
                profesor_id INTEGER REFERENCES profesores(cedula) NOT NULL,
                hora_salida TIME,
                firma_profesor INTEGER,
                observaciones TEXT
            );
            
            CREATE TABLE IF NOT EXISTS prestamos_salas_estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_entrada TIMESTAMP NOT NULL,
                laboratorista INTEGER REFERENCES personal_laboratorio(id),
                monitor INTEGER REFERENCES personal_laboratorio(id),
                sala_id INTEGER REFERENCES salas(id) NOT NULL,
                estudiante_id INTEGER REFERENCES estudiantes(codigo) NOT NULL,
                hora_salida TIME,
                equipo_codigo TEXT REFERENCES equipos(codigo),
                firma_estudiante INTEGER,
                novedad TEXT
            );
            
            CREATE TABLE IF NOT EXISTS prestamos_equipos_profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_entrega TIMESTAMP NOT NULL,
                fecha_devolucion TIMESTAMP,
                laboratorista_entrega INTEGER REFERENCES personal_laboratorio(id),
                monitor_entrega INTEGER REFERENCES personal_laboratorio(id),
                equipo_codigo TEXT REFERENCES inventario(codigo) NOT NULL,
                profesor_id INTEGER REFERENCES profesores(cedula) NOT NULL,
                sala_id INTEGER REFERENCES salas(id),
                titulo_practica TEXT,
                estado INTEGER NOT NULL CHECK (estado IN (0, 1)),
                laboratorista_devolucion INTEGER REFERENCES personal_laboratorio(id),
                monitor_devolucion INTEGER REFERENCES personal_laboratorio(id),
                documento_devolvente INTEGER,
                observaciones TEXT
            );
            
            CREATE TABLE IF NOT EXISTS prestamos_equipos_estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_entrega TIMESTAMP NOT NULL,
                fecha_devolucion TIMESTAMP,
                equipo_codigo TEXT REFERENCES inventario(codigo) NOT NULL,
                laboratorista_entrega INTEGER REFERENCES personal_laboratorio(id),
                monitor_entrega INTEGER REFERENCES personal_laboratorio(id),
                estudiante_id INTEGER REFERENCES estudiantes(codigo) NOT NULL,
                numero_estudiantes INTEGER,
                sala_id INTEGER REFERENCES salas(id),
                titulo_practica TEXT,
                estado INTEGER NOT NULL CHECK (estado IN (0, 1)),
                laboratorista_devolucion INTEGER REFERENCES personal_laboratorio(id),
                monitor_devolucion INTEGER REFERENCES personal_laboratorio(id),
                documento_devolvente INTEGER,
                observaciones TEXT
            );
        ''')
        
        # Create Triggers
        cursor.executescript('''
            -- When loaning something for a professor, it is set to in use state
            CREATE TRIGGER IF NOT EXISTS trg_prestamo_equipo_profesor
                AFTER INSERT ON prestamos_equipos_profesores
                FOR EACH ROW
            BEGIN
                UPDATE inventario 
                SET estado = 'EN USO'
                WHERE codigo = NEW.equipo_codigo;
            END;
            
            -- When returning something for a professor, its state is set to available
            CREATE TRIGGER IF NOT EXISTS trg_devolucion_equipo_profesor
                AFTER UPDATE ON prestamos_equipos_profesores
                FOR EACH ROW
                WHEN NEW.fecha_devolucion IS NOT NULL AND OLD.fecha_devolucion IS NULL
            BEGIN
                UPDATE inventario 
                SET estado = 'DISPONIBLE'
                WHERE codigo = NEW.equipo_codigo;
            END;
            
            -- When loaning something for a student, it is set to in use state
            CREATE TRIGGER IF NOT EXISTS trg_prestamo_equipo_estudiante
                AFTER INSERT ON prestamos_equipos_estudiantes
                FOR EACH ROW
            BEGIN
                UPDATE inventario 
                SET estado = 'EN USO'
                WHERE codigo = NEW.equipo_codigo;
            END;
            
            -- When returning something for a student, its state is set to available
            CREATE TRIGGER IF NOT EXISTS trg_devolucion_equipo_estudiante
                AFTER UPDATE ON prestamos_equipos_estudiantes
                FOR EACH ROW
                WHEN NEW.fecha_devolucion IS NOT NULL AND OLD.fecha_devolucion IS NULL
            BEGIN
                UPDATE inventario 
                SET estado = 'DISPONIBLE'
                WHERE codigo = NEW.equipo_codigo;
            END;
        ''')
        
        conn.commit()
        conn.close()