import sqlite3

class DatabaseManager:
    def __init__(self, db_path="uso_de_espacios.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """ inicializar la base de datos si no esta creada """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Creacion de tablas
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
                nombre TEXT NOT NULL
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
                nombre TEXT NOT NULL,
                cedula INTEGER NOT NULL UNIQUE,
                proyecto_curricular_id INTEGER REFERENCES proyectos_curriculares(id)
            );
            
            CREATE TABLE IF NOT EXISTS profesores (
                cedula INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
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
                numero_equipo INTEGER,
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
                equipo_codigo TEXT REFERENCES inventario(codigo),
                laboratorista_entrega INTEGER REFERENCES personal_laboratorio(id),
                monitor_entrega INTEGER REFERENCES personal_laboratorio(id),
                estudiante_id INTEGER REFERENCES estudiantes(codigo) NOT NULL,
                numero_estudiantes INTEGER,
                sala_id INTEGER REFERENCES salas(id) NOT NULL,
                titulo_practica TEXT,
                estado INTEGER NOT NULL CHECK (estado IN (0, 1)),
                laboratorista_devolucion INTEGER REFERENCES personal_laboratorio(id),
                monitor_devolucion INTEGER REFERENCES personal_laboratorio(id),
                documento_devolvente INTEGER,
                observaciones TEXT
            );
        ''')
        
        # Triggers
        cursor.executescript('''
            -- Trigger for equipment loan to professors
            CREATE TRIGGER IF NOT EXISTS trg_prestamo_equipo_profesor
                AFTER INSERT ON prestamos_equipos_profesores
                FOR EACH ROW
            BEGIN
                UPDATE inventario 
                SET estado = 'EN USO'
                WHERE codigo = NEW.equipo_codigo;
            END;
            
            -- Trigger for equipment return from professors
            CREATE TRIGGER IF NOT EXISTS trg_devolucion_equipo_profesor
                AFTER UPDATE ON prestamos_equipos_profesores
                FOR EACH ROW
                WHEN NEW.fecha_devolucion IS NOT NULL AND OLD.fecha_devolucion IS NULL
            BEGIN
                UPDATE inventario 
                SET estado = 'DISPONIBLE'
                WHERE codigo = NEW.equipo_codigo;
            END;
            
            -- Trigger for equipment loan to students
            CREATE TRIGGER IF NOT EXISTS trg_prestamo_equipo_estudiante
                AFTER INSERT ON prestamos_equipos_estudiantes
                FOR EACH ROW
            BEGIN
                UPDATE inventario 
                SET estado = 'EN USO'
                WHERE codigo = NEW.equipo_codigo;
            END;
            
            -- Trigger for equipment return from students
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
        
        # Si las tablas estan vacias inserta datos iniciales
        self._insert_initial_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_initial_data(self, cursor):
        # Comprueba que no hayan datos previos en la tabla de proyectos_curriculares
        cursor.execute("SELECT COUNT(*) FROM proyectos_curriculares")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO proyectos_curriculares (nombre) VALUES 
                ('Ingeniería Civil'),
                ('Ingeniería de Produccion'),
                ('Ingeniería Eléctrica'),
                ('Ingeniería en Control y Automatización'),
                ('Ingeniería en Telecomunicaciones'),
                ('Ingeniería en Telematica'),
                ('Ingeniería Mecánica'),
                ('Tecnología en Construcciones Civiles'),
                ('Tecnología en Electricidad de Media y Baja Tensión'),
                ('Tecnología en Electrónica Industrial'),
                ('Tecnología en Mecánica Industrial'),
                ('Tecnología en Gestion de la Producción Industrial'),
                ('Tecnología en Sistematización de Datos'),
                ('Ingeniería Industrial'),
                ('Comunicación social y periodismo '),
                ('Tecnología Electrónica'),
                ('Almacén'),
                ('Laboratorio de Ciencias Basicas');
            ''')
        
        # Sedes
        cursor.execute("SELECT COUNT(*) FROM sedes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO sedes (nombre) VALUES 
                ('Facultad Tecnológica');
            ''')
        
        # Personal de laboratorio (laboratoristas y monitores)
        cursor.execute("SELECT COUNT(*) FROM personal_laboratorio")
        if cursor.fetchone()[0] == 0:
            # 1 para monitores, 0 para laboratoristas
            cursor.executescript('''
                INSERT INTO personal_laboratorio (nombre, cargo) VALUES 
                ('Andres Felipe Franco Tellez', 1),
                ('Evelyn Sofìa Cañon Sanchez', 1),
                ('Allyson Daniela Navarrete Ramirez', 1),
                ('David Santiago Duarte Urueña', 1),
                ('Mariam Elizabeth Vera Morales', 0),
                ('Wilfredo Ramirez Pretel', 0),
                ('José Jesús Barajas Sotero', 0),
                ('Valeria Pamplona Gutierrez', 0);
            ''')
        
        # Salas // Laboratorios
        cursor.execute("SELECT COUNT(*) FROM salas")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''                
                INSERT INTO salas (codigo_interno, nombre) VALUES 
                ('320', 'FMS'),
                ('317', 'HAS'),
                ('321', 'GEIO'),
                ('416', 'SSA'),
                ('417', 'SSB'),
                ('B1, 101', 'PLANTA DE EXTRACCIóN'),
                ('0', 'GRUPO INVESTIGACIÓN'),
                ('N/A', 'OFICINAS LABORATORIO DE ELÉCTRICA'),
                ('318', 'DISEÑO DE PRODUCTO'),
                ('N/A', 'SALA PROFESORES'),
                ('N/A', 'AUDIOVISUALES 8VO'),
                ('N/A', 'PLANTA TIBITOC'),
                ('N/A', 'ALMACEN'),
                ('N/A', 'LABORATORIO GESTIÓN P'),
                ('N/A', 'SISTEMAS DE POTENCIA '),
                ('N/A', 'LABORATORIO CIENCIAS BASICAS');
            ''')