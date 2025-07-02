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
                cedula INTEGER UNIQUE,
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
                    ('Sede Central'),
                    ('Sede Macarena A'),
                    ('Sede Macarena B'),
                    ('Facultad Tecnológica'),
                    ('Facultad de Artes ASAB'),
                    ('Facultad de Medio Ambiente y Recursos Naturales'),
                    ('Sede Vivero'),
                    ('Ciudadela Universitaria Bosa Porvenir'),
                    ('Sede Aduanilla de Paiba'),
                    ('Facultad de Ciencias de la Salud');
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

        # Inventario
        cursor.execute("SELECT COUNT(*) FROM inventario")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO inventario (codigo, marca_serie, documento_funcionario, nombre_funcionario, 
                                      descripcion, contenido, estado, sede_id) VALUES 
                ('EQ001', 'HP-2023-001', 12345678, 'Juan Pérez', 'Laptop HP ProBook', 'Laptop con Windows 11', 'DISPONIBLE', 1),
                ('EQ002', 'DELL-2023-002', 87654321, 'María López', 'Laptop Dell Latitude', 'Laptop con Ubuntu', 'DISPONIBLE', 1),
                ('EQ003', 'LEN-2023-003', 23456789, 'Carlos Ruiz', 'Laptop Lenovo ThinkPad', 'Laptop con Windows 10', 'DISPONIBLE', 1),
                ('EQ004', 'MSI-2023-004', 34567890, 'Ana Martínez', 'Laptop MSI Gaming', 'Laptop con Windows 11', 'DAÑADO', 1),
                ('EQ005', 'ASU-2023-005', 45678901, 'Pedro Gómez', 'Laptop Asus ZenBook', 'Laptop con Linux Mint', 'DISPONIBLE', 1),
                ('EQ006', 'MAC-2023-006', 56789012, 'Laura Torres', 'MacBook Pro', 'Laptop con macOS', 'DISPONIBLE', 1),
                ('EQ007', 'HP-2023-007', 67890123, 'Roberto Díaz', 'Laptop HP EliteBook', 'Laptop con Windows 11', 'DISPONIBLE', 1),
                ('EQ008', 'DELL-2023-008', 78901234, 'Sofía Vargas', 'Laptop Dell XPS', 'Laptop con Ubuntu', 'DISPONIBLE', 1);
            ''')

        # Equipos
        cursor.execute("SELECT COUNT(*) FROM equipos")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO equipos (codigo, sala_id, numero_equipo, descripcion, estado, observaciones) VALUES 
                ('PC001', 1, 1, 'Computador de escritorio HP', 1, 'Equipo en buen estado'),
                ('PC002', 1, 2, 'Computador de escritorio Dell', 1, 'Equipo en buen estado'),
                ('PC003', 2, 1, 'Computador de escritorio Lenovo', 0, 'Equipo en mantenimiento'),
                ('PC004', 2, 2, 'Computador de escritorio Asus', 1, 'Equipo en buen estado'),
                ('PC005', 3, 1, 'Computador de escritorio MSI', 1, 'Equipo en buen estado'),
                ('PC006', 3, 2, 'Computador de escritorio Acer', 0, 'Equipo en reparación'),
                ('PC007', 4, 1, 'Computador de escritorio HP', 1, 'Equipo en buen estado'),
                ('PC008', 4, 2, 'Computador de escritorio Dell', 1, 'Equipo en buen estado');
            ''')

        # Estudiantes
        cursor.execute("SELECT COUNT(*) FROM estudiantes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO estudiantes (codigo, nombre, cedula, proyecto_curricular_id) VALUES 
                (2023001, 'Juan Carlos Rodríguez', 1001234567, 1),
                (2023002, 'María Fernanda López', 1002345678, 2),
                (2023003, 'Carlos Andrés Martínez', 1003456789, 3),
                (2023004, 'Ana Sofía Gómez', 1004567890, 4),
                (2023005, 'Pedro José Torres', 1005678901, 5),
                (2023006, 'Laura Camila Vargas', 1006789012, 6),
                (2023007, 'Roberto Alejandro Díaz', 1007890123, 7),
                (2023008, 'Sofía Isabel Ruiz', 1008901234, 8);
            ''')

        # Profesores
        cursor.execute("SELECT COUNT(*) FROM profesores")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO profesores (cedula, nombre, proyecto_curricular_id) VALUES 
                (80012345, 'Dr. José Manuel Pérez', 1),
                (80023456, 'Dra. María Elena Sánchez', 2),
                (80034567, 'Dr. Carlos Eduardo Ramírez', 3),
                (80045678, 'Dra. Ana Patricia Torres', 4),
                (80056789, 'Dr. Pedro Antonio Gómez', 5),
                (80067890, 'Dra. Laura Beatriz Martínez', 6),
                (80078901, 'Dr. Roberto Carlos Díaz', 7),
                (80089012, 'Dra. Sofía Alejandra Vargas', 8);
            ''')

        # Préstamos de salas a profesores
        cursor.execute("SELECT COUNT(*) FROM prestamos_salas_profesores")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO prestamos_salas_profesores 
                (fecha_entrada, laboratorista, monitor, sala_id, profesor_id, hora_salida, firma_profesor, observaciones) 
                VALUES 
                ('2024-03-15 08:00:00', 5, 1, 1, 80012345, '10:00:00', 80012345, 'Clase de laboratorio'),
                ('2024-03-15 10:30:00', 6, 2, 2, 80023456, '12:30:00', 80023456, 'Práctica de estudiantes');
            ''')
            
            cursor.executescript('''
                INSERT INTO prestamos_salas_profesores 
                (fecha_entrada, laboratorista, monitor, sala_id, profesor_id, observaciones) 
                VALUES 
                ('2024-03-15 13:00:00', 7, 3, 3, 80034567, 'Investigación'),
                ('2024-03-15 15:30:00', 8, 4, 4, 80045678, 'Trabajo de grado');
            ''')

        # Préstamos de salas a estudiantes
        cursor.execute("SELECT COUNT(*) FROM prestamos_salas_estudiantes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO prestamos_salas_estudiantes 
                (fecha_entrada, laboratorista, monitor, sala_id, estudiante_id, hora_salida, numero_equipo, firma_estudiante, novedad) 
                VALUES 
                ('2024-03-15 08:00:00', 5, 1, 1, 2023001, '10:00:00', 1, 2023001, NULL),
                ('2024-03-15 10:30:00', 6, 2, 2, 2023002, '12:30:00', 2, 2023002, 'Equipo 2 con problemas de conexión'),
                ('2024-03-15 13:00:00', 7, 3, 3, 2023003, '15:00:00', 1, 2023003, NULL),
                ('2024-03-15 15:30:00', 8, 4, 4, 2023004, '17:30:00', 2, 2023004, NULL);
            ''')

        # Préstamos de equipos a profesores
        cursor.execute("SELECT COUNT(*) FROM prestamos_equipos_profesores")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO prestamos_equipos_profesores 
                (fecha_entrega, fecha_devolucion, laboratorista_entrega, monitor_entrega, 
                equipo_codigo, profesor_id, sala_id, titulo_practica, estado, 
                laboratorista_devolucion, monitor_devolucion, documento_devolvente, observaciones) 
                VALUES 
                ('2024-03-15 10:30:00', NULL, 6, 2, 'EQ002', 80023456, 2, 'Investigación de Tesis', 1, NULL, NULL, NULL, 'Préstamo activo'),
                ('2024-03-15 13:00:00', '2024-03-15 15:00:00', 7, 3, 'EQ003', 80034567, 3, 'Laboratorio de Control', 0, 7, 3, 80034567, 'Equipo con fallas menores')
            ''')

        # Préstamos de equipos a estudiantes
        cursor.execute("SELECT COUNT(*) FROM prestamos_equipos_estudiantes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO prestamos_equipos_estudiantes 
                (fecha_entrega, fecha_devolucion, equipo_codigo, laboratorista_entrega, monitor_entrega,
                estudiante_id, numero_estudiantes, sala_id, titulo_practica, estado,
                laboratorista_devolucion, monitor_devolucion, documento_devolvente, observaciones) 
                VALUES 
                ('2024-03-15 08:00:00', '2024-03-15 10:00:00', 'EQ005', 5, 1, 2023001, 3, 1, 'Práctica de Laboratorio', 0, 5, 1, 2023001, 'Equipo devuelto correctamente'),
                ('2024-03-15 10:30:00', NULL, 'EQ006', 6, 2, 2023002, 2, 2, 'Trabajo de Grado', 1, NULL, NULL, NULL, 'Préstamo activo'),
                ('2024-03-15 13:00:00', '2024-03-15 15:00:00', 'EQ007', 7, 3, 2023003, 4, 3, 'Práctica de Electrónica', 0, 7, 3, 2023003, 'Equipo con daños menores'),
                ('2024-03-15 15:30:00', NULL, 'EQ008', 8, 4, 2023004, 2, 4, 'Proyecto Final', 1, NULL, NULL, NULL, 'Préstamo activo');
            ''')