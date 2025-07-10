import sqlite3
import os
import sys
import shutil

class DatabaseManager:
    def __init__(self, db_name="uso_de_espacios.db"):
        self.db_name = db_name
        self.db_path = self._get_database_path()
        self.init_database()
    
    def _get_database_path(self):
        """
        Determines the appropriate path for the database file.
        In a PyInstaller bundle, it will be in a persistent user data directory.
        Otherwise, it will be in the current working directory.
        """
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            # Use a persistent user data directory
            if sys.platform == "win32":
                appdata = os.environ.get('APPDATA', '.')
                app_data_dir = os.path.join(appdata, "GestionDeLaboratorios")
            elif sys.platform == "darwin":
                app_data_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), "GestionDeLaboratorios")
            else: # Linux and other Unix-like systems
                app_data_dir = os.path.join(os.path.expanduser("~/.local/share"), "GestionDeLaboratorios")
            
            os.makedirs(app_data_dir, exist_ok=True)
            db_file_path = os.path.join(app_data_dir, self.db_name)

            # Check if the database already exists in the persistent location
            if not os.path.exists(db_file_path):
                # If not, copy it from the bundled location (sys._MEIPASS)
                bundled_db_path = os.path.join(sys._MEIPASS, self.db_name)
                if os.path.exists(bundled_db_path):
                    shutil.copy2(bundled_db_path, db_file_path)
                    print(f"Copied initial database from {bundled_db_path} to {db_file_path}")
                else:
                    print(f"Bundled database not found at {bundled_db_path}. A new one will be created.")
            return db_file_path
        else:
            # Running as a script
            return self.db_name # Keep it in the current directory for development
    
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
                INSERT INTO proyectos_curriculares (id, nombre) VALUES 
                (1, 'Ingeniería Civil'),
                (2, 'Ingeniería de Produccion'),
                (3, 'Ingeniería Eléctrica'),
                (4, 'Ingeniería en Control y Automatización'),
                (5, 'Ingeniería en Telecomunicaciones'),
                (6, 'Ingeniería en Telematica'),
                (7, 'Ingeniería Mecánica'),
                (8, 'Tecnología en Construcciones Civiles'),
                (9, 'Tecnología en Electricidad de Media y Baja Tensión'),
                (10, 'Tecnología en Electrónica Industrial'),
                (11, 'Tecnología en Mecánica Industrial'),
                (12, 'Tecnología en Gestion de la Producción Industrial'),
                (13, 'Tecnología en Sistematización de Datos'),
                (14, 'Ingeniería Industrial'),
                (15, 'Comunicación social y periodismo '),
                (16, 'Tecnología Electrónica'),
                (17, 'Almacén'),
                (18, 'Laboratorio de Ciencias Basicas');
            ''')
        
        # Sedes
        cursor.execute("SELECT COUNT(*) FROM sedes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO sedes (nombre) VALUES 
                    ('Facultad Tecnológica'),
                    ('Sede Macarena A'),
                    ('Sede Macarena B'),
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
                INSERT INTO salas (id, codigo_interno, nombre) VALUES 
                (1, '320', 'FMS'),
                (2, '317', 'HAS'),
                (3, '321', 'GEIO'),
                (4, '416', 'SSA'),
                (5, '417', 'SSB'),
                (6, 'B1, 101', 'PLANTA DE EXTRACCIóN'),
                (7, '0', 'GRUPO INVESTIGACIÓN'),
                (8, 'N/A', 'OFICINAS LABORATORIO DE ELÉCTRICA'),
                (9, '318', 'DISEÑO DE PRODUCTO'),
                (10, 'N/A', 'SALA PROFESORES'),
                (11, 'N/A', 'AUDIOVISUALES 8VO'),
                (12, 'N/A', 'PLANTA TIBITOC'),
                (13, 'N/A', 'ALMACEN'),
                (14, 'N/A', 'LABORATORIO GESTIÓN P'),
                (15, 'N/A', 'SISTEMAS DE POTENCIA '),
                (16, 'N/A', 'LABORATORIO CIENCIAS BASICAS');
            ''')

        # Inventario
        cursor.execute("SELECT COUNT(*) FROM inventario")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO inventario (codigo, marca_serie, documento_funcionario, nombre_funcionario, descripcion, contenido, estado, sede_id) VALUES 
                    ('413533', '90V6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413534', '3TJ6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413535', '8VJ6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413536', 'FSJ6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413538', 'HXH6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413539', 'BXH6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413540', '1VJ6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413541', '2WH6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413542', '7WH6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('413543', 'B0M6XW1', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER', 'El Portátil Especial 2 LABORATORIOS corresponde a: DELL Latitud E5530; Procesador Intel Core i7 3520M 2.9Gb 4M; RAM 8.0 Gb DDR3 1600 Mhz; hdd 320GB; Bateria 6-Cell/60-WHr; QUEMADOR 8x DVD +/-RW; Ethernet 10/100/1000 Mbps; parlante interno; Tarjeta Inalámb', 'DISPONIBLE', 1),
                    ('2018061200000', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'VIDEO BEAM CABLE PODER CABLE HDMI', '1 VIDEO PROYECTOR EPSON X41 POWERLITE 3.600 LUMENS EN BLANCO Y COLOR-RESOLUCIÓN XGA V11H843022 - 1 CABLE DE PODER - 1 CABLE DE HDMI', 'DISPONIBLE', 1),
                    ('2018061200002', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'VIDEO BEAM CABLE PODER CABLE HDMI', '1 VIDEO PROYECTOR EPSON X41 POWERLITE 3.600 LUMENS EN BLANCO Y COLOR-RESOLUCIÓN XGA V11H843022 - 1 CABLE DE PODER - 1 CABLE DE HDMI', 'DISPONIBLE', 1),
                    ('2018061200003', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'VIDEO BEAM CABLE PODER CABLE HDMI', '1 VIDEO PROYECTOR EPSON X41 POWERLITE 3.600 LUMENS EN BLANCO Y COLOR-RESOLUCIÓN XGA V11H843022 - 1 CABLE DE PODER - 1 CABLE DE HDMI', 'DISPONIBLE', 1),
                    ('188690', 'PEAKTECH - 08102386', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SONOMETROS	1 SONOMETRO', 'DISPONIBLE', 1),
                    ('188691', 'PEAKTECH - 08102436', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SONOMETROS	1 SONOMETRO', 'DISPONIBLE', 1),
                    ('188692', 'PEAKTECH - 08102439', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SONOMETROS	1 SONOMETRO', 'DISPONIBLE', 1),
                    ('188693', 'PEAKTECH - 08102437', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SONOMETROS	1 SONOMETRO', 'DISPONIBLE', 1),
                    ('188694', 'PEAKTECH - 08102390', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SONOMETROS	1 SONOMETRO', 'DISPONIBLE', 1),
                    ('192186', 'GW INSTEK - GLX- 301/110449', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'ILUMINOMETRO', '1 ILUMINOMETRO', 'DISPONIBLE', 1),
                    ('192187', 'GW INSTEK - GLX- 301/110423', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'ILUMINOMETRO', '1 ILUMINOMETRO', 'DISPONIBLE', 1),
                    ('192188', 'GW INSTEK - GLX- 301/110440', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'ILUMINOMETRO', '1 ILUMINOMETRO', 'DISPONIBLE', 1),
                    ('192189', 'GW INSTEK - GLX- 301/110426', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'ILUMINOMETRO', '1 ILUMINOMETRO', 'DISPONIBLE', 1),
                    ('192190', 'GW INSTEK - GLX- 301/110409', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'ILUMINOMETRO', '1 ILUMINOMETRO', 'DISPONIBLE', 1),
                    ('2019040300001', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV3', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300002', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV4', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300003', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV5', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300004', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV6', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300005', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV7', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300006', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV8', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300007', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV9', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300008', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET LEGO MINDSTORM EV10', '1 set lego mindstorm EV3 con adaptador', 'DISPONIBLE', 1),
                    ('2019040300012', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES', '1 set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300013', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES', '1 set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300014', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES', '1 set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('415852', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CÁMARA TERMOGRÁFICA', '1 CAMARAS TERMOGRAFICAS MARCA FLIR. MODELO I 7. ACCESORIOS : ADAPTADOR MAS 4 CONECTORES, CABLE USB, MICROSD 26B MAS 2 CONECTORES, CD, CERTIFICADO DE CALIBRACION, MANUAL DE OPERACIÓN Y MANUAL DE SOPORTE CAJA Y PORTAFOLIO.', 'DISPONIBLE', 1),
                    ('416049', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CÁMARA TERMOGRÁFICA', '1 CAMARAS TERMOGRAFICAS MARCA FLIR. MODELO I 7. ACCESORIOS : ADAPTADOR MAS 4 CONECTORES, CABLE USB, MICROSD 26B MAS 2 CONECTORES, CD, CERTIFICADO DE CALIBRACION, MANUAL DE OPERACIÓN Y MANUAL DE SOPORTE CAJA Y PORTAFOLIO.', 'DISPONIBLE', 1),
                    ('416041', 'EXTECH. MODELO HD 500. - 12118569', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SICRONOMETRO CON TERMOMETRO', '1 SICROMETROS CON TERMOMETRO. ACCESORIOS: BATERIA 9V , CABLE USB, SONDA TIPO K, SOPORTE ENRROSCABLE, MANUAL DE USUARIO, CD SOFWARE Y ESTUCHE.', 'DISPONIBLE', 1),
                    ('416042', 'EXTECH. MODELO HD 500. - 12118570', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SICRONOMETRO CON TERMOMETRO', '1 SICROMETROS CON TERMOMETRO. ACCESORIOS: BATERIA 9V , CABLE USB, SONDA TIPO K, SOPORTE ENRROSCABLE, MANUAL DE USUARIO, CD SOFWARE Y ESTUCHE.', 'DISPONIBLE', 1),
                    ('416043', 'EXTECH. MODELO HD 500. - 12118578', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SICRONOMETRO CON TERMOMETRO', '1 SICROMETROS CON TERMOMETRO. ACCESORIOS: BATERIA 9V , CABLE USB, SONDA TIPO K, SOPORTE ENRROSCABLE, MANUAL DE USUARIO, CD SOFWARE Y ESTUCHE.', 'DISPONIBLE', 1),
                    ('416044', 'EXTECH. MODELO HD 500. - 12118583', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SICRONOMETRO CON TERMOMETRO', '1 SICROMETROS CON TERMOMETRO. ACCESORIOS: BATERIA 9V , CABLE USB, SONDA TIPO K, SOPORTE ENRROSCABLE, MANUAL DE USUARIO, CD SOFWARE Y ESTUCHE.', 'DISPONIBLE', 1),
                    ('416045', 'EXTECH. MODELO HD 500. - 12118609', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SICRONOMETRO CON TERMOMETRO', '1 SICROMETROS CON TERMOMETRO. ACCESORIOS: BATERIA 9V , CABLE USB, SONDA TIPO K, SOPORTE ENRROSCABLE, MANUAL DE USUARIO, CD SOFWARE Y ESTUCHE.', 'DISPONIBLE', 1),
                    ('416046', 'EXTECH. MODELO HD 500. - 12118612', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SICRONOMETRO CON TERMOMETRO', '1 SICROMETROS CON TERMOMETRO. ACCESORIOS: BATERIA 9V , CABLE USB, SONDA TIPO K, SOPORTE ENRROSCABLE, MANUAL DE USUARIO, CD SOFWARE Y ESTUCHE.', 'DISPONIBLE', 1),
                    ('416023', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TERMOMETRO INFRARROJO', '1 MINI TERMOMETRO INFRARROJO MODELO 42510A', 'DISPONIBLE', 1),
                    ('416026', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TERMOMETRO INFRARROJO', '1 MINI TERMOMETRO INFRARROJO MODELO 42510A', 'DISPONIBLE', 1),
                    ('416024', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TERMOMETRO INFRARROJO', '1 MINI TERMOMETRO INFRARROJO MODELO 42510A', 'DISPONIBLE', 1),
                    ('416028', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TERMOMETRO INFRARROJO', '1 MINI TERMOMETRO INFRARROJO MODELO 42510A', 'DISPONIBLE', 1),
                    ('416025', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TERMOMETRO INFRARROJO', '1 MINI TERMOMETRO INFRARROJO MODELO 42510A', 'DISPONIBLE', 1),
                    ('416027', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TERMOMETRO INFRARROJO', '1 MINI TERMOMETRO INFRARROJO MODELO 42510A', 'DISPONIBLE', 1),
                    ('2023080800009', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MINI TORNO', '1 CAJA CPN HERRAMIENTAS Y ELEMENTOS PARA EL ENSAMBLE DE DIFERENTES TIPOS DE TORNO', 'DISPONIBLE', 1),
                    ('2021072700121', 'COMPUMAX HALCÓN SERIES 700SN11475', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'COMPUMAX ', 'DISPONIBLE', 1),
                    ('2024050300031', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTATIL MOUSE CABLE DE PODER MALETÍN', 'ACER TRAVELMATE P Contiene mouse y cargador', 'DISPONIBLE', 1),
                    ('2021111200046', 'VIDEOBEAM EPSON', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'VIDEO BEAM CABLE PODER CABLE HDMI', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300059', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300069', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300060', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2016111600000', 'DELL - 4CZKK72', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL DELL CORPORATIVO LATITUD E5470', 'CARGADOR Y MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300067', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300068', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300063', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300066', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300062', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300065', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300061', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2024050300064', 'ACER TRAVELMATE P', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PORTÁTIL', 'MOUSE CON PILA RECARGABLE, CARGADOR, MALETÍN', 'DISPONIBLE', 1),
                    ('2018062200023', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200024', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200025', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200026', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200027', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200028', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200029', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200030', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200031', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200032', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200033', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200034', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200035', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200036', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200037', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200038', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200039', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200040', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200041', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200042', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200043', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200044', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018062200045', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2018061200001', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'VIDEO BEAM CABLE PODER CABLE HDMI', 'VIDEO PROYECTOR EPSON X41 POWERLITE 3.600 LUMENS EN BLANCO Y COLOR-RESOLUCIÓN XGA V11H843021', 'DISPONIBLE', 1),
                    ('2018062200021', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CRONOMETRO ANALOGO', 'CRONOMETRO ANALOGO', 'DISPONIBLE', 1),
                    ('2019040300009', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET EXPANSION PARA EV3 CON PROYECTOS DE INGENIERÌA', 'set expansion para EV3 con proyectos de ingenieria', 'DISPONIBLE', 1),
                    ('2019040300010', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET EXPANSION PARA EV3 CON PROYECTOS DE INGENIERÌA', 'set expansion para EV3 con proyectos de ingenieria', 'DISPONIBLE', 1),
                    ('2019040300011', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET EXPANSION PARA EV3 CON PROYECTOS DE INGENIERÌA', 'set expansion para EV3 con proyectos de ingenieria', 'DISPONIBLE', 1),
                    ('2019040300015', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300016', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300017', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300018', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300019', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300020', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300021', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300022', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE VEHÌCULOS DE LOGÌSTICA', 'set de vehiculos de logistica', 'DISPONIBLE', 1),
                    ('2019040300024', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES CON SOFTWARE DE MEDICIONES Y SENSOR', 'set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300025', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES CON SOFTWARE DE MEDICIONES Y SENSOR', 'set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300026', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES CON SOFTWARE DE MEDICIONES Y SENSOR', 'set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300027', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES CON SOFTWARE DE MEDICIONES Y SENSOR', 'set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300028', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE EXPANSION ENERGÍAS RENOVABLES CON SOFTWARE DE MEDICIONES Y SENSOR', 'set de expansion energias renovables con software de mediciones cientificas y sensor de temperatura', 'DISPONIBLE', 1),
                    ('2019040300029', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2019040300030', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2019040300031', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2019040300032', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2019040300033', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2019040300034', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2019040300035', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET DE PROTOTIPADO DE PLANTAS INDUSTRIALES', 'set de prototipado de plantas industriales', 'DISPONIBLE', 1),
                    ('2016051200002', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'L.VIDA VERTICAL 20 MT, MOSQ 2,1 KIT', 'l.vida vertical 20 MT, mosq 2.1 kit', 'DISPONIBLE', 1),
                    ('2016051200001', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'L.VIDA HORIZONTAL, CUERD, PORTAT, 30FT', 'l.vida horizontal, cuerd, portat,30ft', 'DISPONIBLE', 1),
                    ('2016051200000', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SISTEMA RESCATE ESTANDAR', 'sistema rescate estandar', 'DISPONIBLE', 1),
                    ('2122MH00GL29', 'Logitech', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'AUDIFONOS DIADEMA 4', 'Diadema de audifonos y usb', 'DISPONIBLE', 1),
                    ('2122MH00FSA9', 'Logitech', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'AUDIFONOS DIADEMA 1', 'Diadema de audifonos y usb', 'DISPONIBLE', 1),
                    ('MMM23', 'Logitech', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CAMARA COMPUTADOR', 'Camara de video para computador', 'DISPONIBLE', 1),
                    ('2019040300090', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET EXPANSION PARA MINDSTORMS EV3', 'SET LEGO MINDSTORM EV3 INCLUYE: ADAPTADOR DE CORRIENTE', 'DISPONIBLE', 1),
                    ('2019040300009', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET EXPANSION PARA MINDSTORMS EV3', 'SET LEGO MINDSTORM EV3 INCLUYE: ADAPTADOR DE CORRIENTE', 'DISPONIBLE', 1),
                    ('2019040300002', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'SET EXPANSION PARA MINDSTORMS EV3', 'SET LEGO MINDSTORM EV3 INCLUYE: ADAPTADOR DE CORRIENTE', 'DISPONIBLE', 1),
                    ('188598', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('158588', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188587', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188594', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188593', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH (El forro en el cual venía no se podía cerrar)', 'DISPONIBLE', 1),
                    ('188602', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188601', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188600', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DAÑADO', 1),
                    ('188599', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188595', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188597', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188596', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188589', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188590', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188592', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188591', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188606', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188605', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DAÑADO', 1),
                    ('188604', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188603', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('188588', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'MEDIDOR MULTIFUNCIONAL MARCA PEAKTECH', 'DISPONIBLE', 1),
                    ('9', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CASCO SST NUMERO 9', 'CASCO SST NUMERO 9', 'DISPONIBLE', 1),
                    ('ST-MO-91', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MOUSE INALAMBRICO', 'MOUSE INALAMBRICO', 'DISPONIBLE', 1),
                    ('2122MH00GL59', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'AUDIFONOS', 'AUDIFONOS CON CONECTAR USB', 'DISPONIBLE', 1),
                    ('CN0X146C', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'PARLANTES', 'PAR DE PARLANTES ', 'DISPONIBLE', 1),
                    ('30615', 'STANLEY', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'FLEXOMETRO', 'Flexometro Global 5Mts 30-615 Stanley', 'DISPONIBLE', 1),
                    ('14301', 'TRUPER', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'LENTES DE SEGURIDAD', 'LENTES DE SEGURIDAD TRANSPARENTES, TRUPER VISION, LEDE-ST POLICARBONATO', 'DISPONIBLE', 1),
                    ('30616', 'BOSCH', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'MEDIDOR LASER', 'Medidor Láser de Distancia GLM 20 – BOSCH', 'DISPONIBLE', 1),
                    ('1814380', 'TRUPER', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CALIBRADOR DIGITAL', 'Calibrador vernier digital 6" 14388 CALDI-6MP, acero inox, std y mm, TRUPER - 1 pila CR2032', 'DISPONIBLE', 1),
                    ('1814381', 'TRUPER', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CALIBRADOR DIGITAL', 'Calibrador vernier digital 6" 14388 CALDI-6MP, acero inox, std y mm, TRUPER - 1 pila CR2033', 'DISPONIBLE', 1),
                    ('1814382', 'TRUPER', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CALIBRADOR DIGITAL', 'Calibrador vernier digital 6" 14388 CALDI-6MP, acero inox, std y mm, TRUPER - 1 pila CR2034', 'DISPONIBLE', 1),
                    ('1814383', 'TRUPER', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CALIBRADOR DIGITAL', 'Calibrador vernier digital 6" 14388 CALDI-6MP, acero inox, std y mm, TRUPER - 1 pila CR2035', 'DISPONIBLE', 1),
                    ('1814384', 'TRUPER', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CALIBRADOR DIGITAL', 'Calibrador vernier digital 6" 14388 CALDI-6MP, acero inox, std y mm, TRUPER - 1 pila CR2036', 'DISPONIBLE', 1),
                    ('2120322121', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'BÁSCULA', 'CAJA ORGANIZADORA DE PIEZAS DE LEGO', 'DISPONIBLE', 1),
                    ('2020040400000', '-', 51953330, 'CLAUDIA MABEL MORENO PENAGOS', 'CAJA LEGOS', 'CAJA ORGANIZADORA DE PIEZAS DE LEGO', 'DISPONIBLE', 1);
            ''')

        # Equipos
        cursor.execute("SELECT COUNT(*) FROM equipos")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO equipos (codigo, sala_id, numero_equipo, descripcion, estado, observaciones) VALUES 
                    (41601, 4, 1, 'Equipo 01 / SSA', 1),	
                    (41602, 4, 2, 'Equipo 02 / SSA', 1),	
                    (41603, 4, 3, 'Equipo 03 / SSA', 1),	
                    (41604, 4, 4, 'Equipo 04 / SSA', 1),	
                    (41605, 4, 5, 'Equipo 05 / SSA', 1),	
                    (41606, 4, 6, 'Equipo 06 / SSA', 1),	
                    (41607, 4, 7, 'Equipo 07 / SSA', 1),	
                    (41608, 4, 8, 'Equipo 08 / SSA', 1),	
                    (41609, 4, 9, 'Equipo 09 / SSA', 1),	
                    (41610, 4, 10, 'Equipo 10 / SSA', 1),	
                    (41611, 4, 11, 'Equipo 11 / SSA', 1),	
                    (41612, 4, 12, 'Equipo 12 / SSA', 1),	
                    (41613, 4, 13, 'Equipo 13 / SSA', 1),	
                    (41614, 4, 14, 'Equipo 14 / SSA', 1),	
                    (41615, 4, 15, 'Equipo 15 / SSA', 1),	
                    (41616, 4, 16, 'Equipo 16 / SSA', 1),	
                    (41617, 4, 17, 'Equipo 17 / SSA', 1),	
                    (41701, 5, 1, 'Equipo 01 / SSB', 1),	
                    (41702, 5, 2, 'Equipo 02 / SSB', 1),	
                    (41703, 5, 3, 'Equipo 03 / SSB', 1),	
                    (41704, 5, 4, 'Equipo 04 / SSB', 1),	
                    (41705, 5, 5, 'Equipo 05 / SSB', 1),	
                    (41706, 5, 6, 'Equipo 06 / SSB', 1),	
                    (41707, 5, 7, 'Equipo 07 / SSB', 1),	
                    (41708, 5, 8, 'Equipo 08 / SSB', 1),	
                    (41709, 5, 9, 'Equipo 09 / SSB', 1),	
                    (41710, 5, 10, 'Equipo 10 / SSB', 1),	
                    (41711, 5, 11, 'Equipo 11 / SSB', 1),	
                    (41712, 5, 12, 'Equipo 12 / SSB', 1),	
                    (41713, 5, 13, 'Equipo 13 / SSB', 1),	
                    (41714, 5, 14, 'Equipo 14 / SSB', 1),	
                    (41715, 5, 15, 'Equipo 15 / SSB', 1),	
                    (41716, 5, 16, 'Equipo 16 / SSB', 1),	
                    (41717, 5, 17, 'Equipo 17 / SSB', 1),	
                    (41718, 5, 18, 'Equipo 18 / SSB', 1),	
                    (41719, 5, 19, 'Equipo 19 / SSB', 1),	
                    (41720, 5, 20, 'Equipo 20 / SSB', 1),	
                    (41721, 5, 21, 'Equipo 21 / SSB', 1),	
                    (41722, 5, 22, 'Equipo 22 / SSB', 1),	
                    (41723, 5, 23, 'Equipo 23 / SSB', 1),	
                    (41724, 5, 24, 'Equipo 24 / SSB', 1),	
                    (41725, 5, 25, 'Equipo 25 / SSB', 1),	
                    (32001, 1, 1, 'Equipo 01 / FMS', 1),	
                    (32002, 1, 2, 'Equipo 02 / FMS', 1),	
                    (32003, 1, 3, 'Equipo 03 / FMS', 1),	
                    (32004, 1, 4, 'Equipo 04 / FMS', 1),	
                    (32005, 1, 5, 'Equipo 05 / FMS', 1),	
                    (32006, 1, 6, 'Equipo 06 / FMS', 1),	
                    (32007, 1, 7, 'Equipo 07 / FMS', 1),	
                    (32008, 1, 8, 'Equipo 08 / FMS', 1),	
                    (32009, 1, 9, 'Equipo 09 / FMS', 1),	
                    (32010, 1, 10, 'Equipo 10 / FMS', 1),	
                    (32011, 1, 11, 'Equipo 11 / FMS', 1),	
                    (32012, 1, 12, 'Equipo 12 / FMS', 1),	
                    (32013, 1, 13, 'Equipo 13 / FMS', 1),	
                    (32014, 1, 14, 'Equipo 14 / FMS', 1),	
                    (32015, 1, 15, 'Equipo 15 / FMS', 1),	
                    (32016, 1, 16, 'Equipo 16 / FMS', 1),	
                    (32017, 1, 17, 'Equipo 17 / FMS', 1),	
                    (32018, 1, 18, 'Equipo 18 / FMS', 1),	
                    (31701, 2, 1, 'Equipo 01 / HAS', 1),	
                    (31702, 2, 2, 'Equipo 02 / HAS', 1),	
                    (31703, 2, 3, 'Equipo 03 / HAS', 1),	
                    (31704, 2, 4, 'Equipo 04 / HAS', 1),	
                    (31705, 2, 5, 'Equipo 05 / HAS', 1),	
                    (31706, 2, 6, 'Equipo 06 / HAS', 1),	
                    (31707, 2, 7, 'Equipo 07 / HAS', 1),	
                    (31708, 2, 8, 'Equipo 08 / HAS', 1),	
                    (31709, 2, 9, 'Equipo 09 / HAS', 1),	
                    (31710, 2, 10, 'Equipo 10 / HAS', 1),	
                    (31711, 2, 11, 'Equipo 11 / HAS', 1),	
                    (31712, 2, 12, 'Equipo 12 / HAS', 1),	
                    (31713, 2, 13, 'Equipo 13 / HAS', 1),	
                    (31714, 2, 14, 'Equipo 14 / HAS', 1),	
                    (31715, 2, 15, 'Equipo 15 / HAS', 1),	
                    (31716, 2, 16, 'Equipo 16 / HAS', 1),	
                    (31717, 2, 17, 'Equipo 17 / HAS', 1),	
                    (31718, 2, 18, 'Equipo 18 / HAS', 1),	
                    (31719, 2, 19, 'Equipo 19 / HAS', 1),	
                    (31720, 2, 20, 'Equipo 20 / HAS', 1),	
                    (31721, 2, 21, 'Equipo 21 / HAS', 1),	
                    (31722, 2, 22, 'Equipo 22 / HAS', 1);
            ''')

        # Estudiantes
        cursor.execute("SELECT COUNT(*) FROM estudiantes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO estudiantes (codigo, nombre, proyecto_curricular_id, cedula) VALUES 
                    (20251379118, 'Dana Camila Rojas Guzman', 8, 1013117834),
                    (20251379109, 'Laura Sofia Ruiz Rodriguez', 8, 1141317052),
                    (20242577009, 'Paula Andrea Guerrero Muñoz', 12, 1019604637),
                    (20242577067, 'Ana Valeria Gomez Velasquez', 12, 1019764697),
                    (20232377027, 'Juan Felipe Lopez Sanchez', 2, 1000724247),
                    (20232577137, 'Jaiver Jair Pinto Guevara', 12, 1001176532),
                    (20241377010, 'Daniel Steven Amalla', 2, 1007695357),
                    (20221577084, 'Melary Nicole Rozo Pinzon', 12, 0),
                    (20212574050, 'Juan Pablo Tuta Castro', 11, 1034656059),
                    (20202574085, 'Nixon Jussef Aguilera Wagner', 11, 1000835745),
                    (20221574031, 'Jackson Stiven Martinez Rodriguez', 11, 1117491758),
                    (20221574007, 'Sebastian Fernandez Aguirre', 11, 1014737587),
                    (20211574018, 'Juan Esteban Sanchez Bejarano', 11, 1032797259),
                    (20221574076, 'Juan Carlos Guevara Oicata', 10, 1070),
                    (20231377068, 'Billy Jhon Haner Delgadillo Malo', 2, 1033765148),
                    (20221977030, 'Liseth Tatiana Fernandez Jaramillo', 12, 10004063110),
                    (20231577081, 'Angie Lorena García Galindo', 12, 1121417018),
                    (20141383060, 'Juan Carlos Casas Bustos', 4, 80154113),
                    (20222577064, 'Sara Natalia Correa Villa', 12, 1013100344),
                    (20222577082, 'Stefanny Herrera Piñeros', 12, 1000007740),
                    (20241577111, 'Santiago Andres Pinzon Gil', 12, 1023866406),
                    (20232577070, 'Karol Tatiana Cabrera Davila', 12, 1012334522),
                    (20232577021, 'Righy hoyos Zuleta', 12, 1022928396),
                    (20232577025, 'Alex Felipe Yanquen', 12, 1050602144),
                    (20232577035, 'Maria Fernanda Arias Rodriguez', 12, 1034396573),
                    (20212577082, 'Dayron Manuel Alarcon Sierra', 12, 1023979881),
                    (20222375049, 'Brayan Esteban Velandia Arias', 7, 1023031598),
                    (20222577003, 'Dennis Juliana Herrera Villalobos', 12, 1027523091),
                    (20241577022, 'Angie Katherin Castillo Rozo', 12, 1023372612),
                    (20241577127, 'Laura Sofia Alarcon Torres', 12, 1031808827),
                    (20222577006, 'Johan Sebastian Prada Hernandez', 12, 1070385166),
                    (20241577044, 'Andrés Mauricio Quiñones Quiñones', 12, 1030553214),
                    (20241377040, 'Estiven Marin', 2, 1000326005),
                    (20241377011, 'Harryson Stick Niño', 2, 1000707362),
                    (20241377009, 'Natalia Cante Garzon', 2, 1000729417),
                    (20251379110, 'Stefanie Restrepo', 8, 1012363236),
                    (20251379131, 'ESTEFANY CARRILO', 8, 1067604718),
                    (20241577017, 'JULIETH ALEJANDRA GONZALES GONZALES', 12, 1000219865),
                    (20242377026, 'HEMILY ORIANA REYES LUNA', 12, 1000857901),
                    (20202577030, 'Danna Sofia Camargo Hernandez', 12, 1000786280),
                    (20231375059, 'ERIK SEBASTIAN BOJACA MALDONADO', 11, 1001065392),
                    (20221578137, 'Maira Alejandra Gomez Mejia', 12, 1022923707),
                    (20241377020, 'Cristian Camilo Cruz Sierra', 2, 1002265125),
                    (20232377017, 'Juan Pablo Martinez', 2, 1022445649),
                    (20211577124, 'David Santiago Rodriguez lozano', 12, 1000833940),
                    (20221379089, 'Jhon Lenin Prieto Valdes', 8, 1024416123),
                    (20221673031, 'Juan Camilo Reyes Baquero', 16, 1028780939),
                    (20192577032, 'Brayan Felipe Rivera Gomez', 12, 1000971676),
                    (20191577095, 'Karen Daniela Mayorga Sombredero', 12, 1000384721),
                    (20232377050, 'Angie Tatiana Muñoz Rojas', 12, 1000116900),
                    (20232377019, 'Julian Mauricio Jaimes Contreras', 12, 1005062754),
                    (20232377039, 'Andrey Oswaldo Diaz Quiñones', 12, 1001272242),
                    (20212377013, 'Sonia Esperanza Cruz León', 2, 1031171067),
                    (20192577048, 'Karen Lorena Perdomo Rodriguez', 12, 1000734233),
                    (20242377017, 'Danna Alonso Valencia', 2, 1000158337),
                    (20241377048, 'Nicolas Quevedo', 12, 1000493507),
                    (20242377063, 'Jesus Andres londoño Medina', 12, 1024577009),
                    (20231377049, 'Paula Viviana Alonzo', 12, 1000155387),
                    (20241377056, 'Valentina Mullon', 12, 1033818734),
                    (20241377001, 'Nicolas Alberto Puentes', 12, 1024569367),
                    (20232377044, 'Iris Daniela Coredor Nieto', 12, 1031158164),
                    (20232377003, 'Derian Rodrigo Tello Leon', 12, 1115917334),
                    (20201577102, 'Laura Stefania Cajamarca Beltran', 12, 1011201888),
                    (20202577022, 'Katherine Andrea Castillo Garcia', 2, 1014196918),
                    (20241377060, 'Bladimir Perdomo', 12, 1000781190),
                    (20242377007, 'laura Camila Vela', 12, 1073719828),
                    (20221577104, 'Ana Maria Olarte Anzola', 12, 1022934090),
                    (20221967031, 'Miguel Bedoza', 12, 1000621999),
                    (20201577082, 'Lina Maria Oliveros Orjuela', 12, 1193577440),
                    (1011201888, 'Laura Stefania Cajamarca Beltran', 12, 1011201888),
                    (20242377006, 'Paula Viviana Mogollon Mosquera', 2, 1026586892),
                    (20241377014, 'Mischell Kaory Forero pedraza', 12, 1001296234),
                    (20242673065, 'Emerson Damian Hernandez Beltran', 10, 1027525062),
                    (20222577075, 'Jenny Daniela Bohorquez Vega', 12, 1118166554),
                    (20221973008, 'Maira Stefanny Palacios Galindo ', 10, 1022932131),
                    (20221673071, 'Juan David Vargas', 10, 1033676283),
                    (20222673009, 'Jeisson Esteban Carmona Muñoz', 10, 1013109702),
                    (20222379019, 'Paula Lizeth Alvarez', 8, 1000363548),
                    (20241377068, 'Jhoanata Katerin Martin', 2, 1016102240),
                    (20171377007, 'Daniel Santiago Malaver', 2, 1023002436),
                    (20211377020, 'Miguel armando bermudez prieto', 2, 1015424852),
                    (20232377028, 'Dylan esteban aranda', 2, 1007648188),
                    (20171573135, 'Fabian Francisco Segura', 4, 1019137609),
                    (20201573158, 'Luis Alejandro Perez', 10, 1000626064),
                    (20251589016, 'Juan Sebastian Infante', 4, 1007702005),
                    (20221973029, 'Jaime Alejandro Carvajal Raigoso', 10, 1034658474),
                    (20232577121, 'Andres Felipe Albarracin Gomez', 12, 1001078144),
                    (20182873024, 'Kelluy Tatiana Cortes', 4, 1067749353),
                    (20242583013, 'Ospina Rojas Andres ', 4, 1018510066),
                    (20182573070, 'David Felipe Beltran', 4, 1016111151),
                    (20242583006, 'Yoiner David Castro', 4, 1042606086),
                    (20201573093, 'Duvan Santiago Vasquez', 4, 1000726987),
                    (20221673099, 'Lidier Alfonso Rocha', 10, 1122143069),
                    (20222673049, 'Leidy Alexandra Mena Ortiz', 10, 1073671271),
                    (20222673006, 'Samuel Santiago Ruiz Yepez', 10, 1085902307),
                    (20221673081, 'Angello Jefrey Gutierrez Rodriguez', 10, 1027524139),
                    (20221973011, 'Daniel Campos Rincon', 10, ,
                    (20161077720), 'iris Daniela Corredor Nieto', 12, 1031158164),
                    (20241377037, 'Sebastian Morales', 12, 3144898627),
                    (20231577065, 'DANNA CATALINA FORERO CEBALLOS', 12, 1022928061),
                    (20232577033, 'LAURA YINETH CHACON', 12, 1000621553),
                    (20232577038, 'ALEJANDRO ESTEBAN TORRES ZAMBRANO', 12, 1023370430),
                    (20251377042, 'John Sebastian Aya Prieto', 2, 1015478792),
                    (20202577060, 'Juan David Angel Hernandez', 12, 1000729021),
                    (20232577009, 'Deyber Giovanny Hernandez Cifuentes', 12, 1011085552),
                    (20212577101, 'Karen Daniela Guasca Florez', 12, 1014656611),
                    (20242377044, 'Julian Sebastian Gomez Paez', 2, 1000988515),
                    (20231577014, 'Juliana Luna Linares', 12, 1028880361),
                    (20241377039, 'Laura Stefania Cajamarca Beltran', 2, 1011201888),
                    (20221377047, 'Yenny Campo', 12, ,
                    (20192577012), 'Wenddy Balentina Patiño Camacho', 12, 1000122395),
                    (20192577045, 'Hernan Sebastian Candamil Parra', 12, 1000856854),
                    (20192577119, 'Nicolth Dayanne Romero Plazas', 12, 1015462109),
                    (20231377037, 'Isabella Blanco Buitrago', 12, 1193441531),
                    (20181577057, 'DILAN ESTEBAN ARANDA GUALTEROS', 12, 1007648188),
                    (20241577048, 'Nicol Daniela Castro', 11, ,
                    (20241574152), 'Johan David Tapias Lopez', 11, 1022948396),
                    (20241574112, 'Juan Sebastian Rodriguez Nuñez', 11, 1033098400),
                    (20212577409, 'Angel Santiago Espinoza Salcedo', 11, ,
                    (20241574115), 'Cristian David Gamboa Muñoz', 11, 1034396969),
                    (20241574160, 'Andres Felipe Pinilla Murcia', 11, 1033704554),
                    (20242577020, 'Allyson Daniela Navarrete Ramirez', 12, 1027150210),
                    (20241577056, 'Rafael Santiago Rodriguez Puentes', 11, 1011092568),
                    (20241574049, 'Luis Angel Sanchez Romero', 11, 1014665533),
                    (20241574058, 'Brayan Stif Barrera Perez', 11, 1014737718),
                    (20241574052, 'Luis Mario Diaz Salcedo', 11, 1023366241),
                    (20241574054, 'Heiddy Jineth Segura Ochoa', 11, 1016716114),
                    (20232574095, 'Carlos Samir Oyola', 11, 1005681806),
                    (20242574071, 'Michael Stiven Rey Gonzales', 11, 1073678951),
                    (20232574147, 'Jael Felipe Guasca Cortes', 11, 1021669597),
                    (20231379154, 'Wilmer Esteban Suares Marroquin', 8, 1027524837),
                    (20241574141, 'Maria Alejandra Torres Carrilo', 11, 1014662063),
                    (20221577106, 'Maira Yulisa Pinzón Bolivar', 12, 1034276409),
                    (20232577008, 'Katleen Ginnell Diaz Snachez', 12, 1025525911),
                    (20222379112, 'PIANNA LISETH YALANDA CUCHILLO', 8, 1061529854),
                    (20232377029, 'Jhon Alexander Puentes Galeano', 2, 1001204557),
                    (20222673067, 'Dana Marcela Pacheco Mejia', 10, 1019762805),
                    (20221578097, 'Joel Sanabria', 13, 1122918693),
                    (20221978003, 'Juan Sebastian Ospina Acosta', 13, 1014656168),
                    (20222577046, 'Katerin Alejandra Buitrago Ruiz', 12, 1016593002),
                    (20211577045, 'Julian Humberto Barrios', 2, 1005825280),
                    (20231577067, 'Miguel Angel Torres Medina', 12, 1014661488),
                    (20222577074, 'Paula Ximena Aguirre Gamez', 12, 1000225849),
                    (20231574013, 'Erick Steven Silva Sanchez', 11, 1025523002),
                    (20231574056, 'Samuel Sacristan Porras', 11, 1011091058),
                    (20241377049, 'Sandy Rocha', 2, 1010065832),
                    (20232377020, 'Yeferson Sneider Molano', 2, 1031172294),
                    (20231377066, 'Jeisson Iguera', 2, 1031181680),
                    (20232377069, 'Diego Alexander Muñoz Castillo', 2, 1016010800),
                    (20232377032, 'Miguel Alejandro Niño', 2, 1010005276),
                    (20241377028, 'Karen Lizeth Ortiz Rojas', 2, 1000139934),
                    (20221577044, 'Dayanna Calderon Mahecha', 12, 0) ,
                    (20201577035, 'Juan Pablo Camargo', 12, 0),
                    (20251377032, 'Maria Fernanda Quiebraolla', 2, 0),
                    (20221577023, 'Hanna Sofia Gonzalez Sanchez', 12, 1013104474),
                    (20231577063, 'Anguie Mishelle Duarte Duarte', 12, 1032678344),
                    (20231577056, 'Karen Sirley Cañon Paez', 12, 1053327387),
                    (20231577006, 'Valentina Ardila Roa', 12, 1000335243),
                    (20242377021, 'Cristian Palacios', 2, 1000004611),
                    (20241577006, 'Maria Alejandra Tovar Palma', 12, 1018512879),
                    (20222379068, 'Cristian Camilo Vargas Tello', 8, 1023365220),
                    (20242377069, 'Jose Camilo Ruiz Forero', 2, 1000576873),
                    (20241574128, 'Juan David Aranzalez Castañeda', 12, 1100182252),
                    (20241377005, 'Jonathan Camilo Martinez Lozano', 2, 1000327667),
                    (20212577050, 'Mónica Giseth Leal Moreno', 12, 1001203551),
                    (20241377013, 'DAVID RICARDO HERAZO MESA', 2, 1000787761),
                    (20201577072, 'EVELYN SOFIA CAÑON SANCHEZ', 12, 1000973575),
                    (20242577094, 'Andrés Felipe Ladino Santos', 12, 1121200761),
                    (20231377056, 'Nicolás Ochoa Tarazona', 2, 1001273492),
                    (20191573068, 'NICOLAS MENDEZ ROMERO', 10, 1000256924),
                    (20231577053, 'Jeimy Catalina Wilches Camargo', 12, 1023162756),
                    (20232574034, 'Tomas Esteban Díaz Romero', 11, 1000272604),
                    (20241673049, 'BARRAGAN GONZALES RODRIGO ALEJANDRO', 10, 1034313879),
                    (20241673077, 'FORERO CONDE NOCOLAY', 10, 1104940374),
                    (20221572036, 'ERIC SANTIAGO GARCIA SILVA', 9, 1011080865),
                    (20212577088, 'Juliana Sophia González Àvila', 12, 1030534340),
                    (20202577082, 'Juan Diego Cadenas Mancera', 12, 1001118499),
                    (20222577134, 'Erika Alejandra Obando Franco', 12, 1001344683),
                    (20212577095, 'Edgar Orlando Castellanos Ruiz', 12, 1015461751),
                    (20241574099, 'Angel Esteban Guerrero Manrique', 11, 1028881501),
                    (20241574728, 'Juan David Aranzalez Castañeda', 11, 1106482252),
                    (20162374161, 'Oscar Daniel Velásquez  Sánchez', 11, 1016099658),
                    (20232377052, 'Adriana Lucia Díaz Tique', 2, 1000123352),
                    (20232377025, 'Brayan Felipe Rivera Gomez', 2, 1000971676),
                    (20232377008, 'Harold Andrés Casallas Moreno', 2, 1001175350),
                    (20231377061, 'Andrés Felipe Vargas', 2, 1010236998),
                    (20231377043, 'Miguel Garcia', 12, 1001269793),
                    (20231377071, 'Carol Tatiana Vanegas Beleño', 12, 1000046404),
                    (20232377013, 'Laura Vela', 12, 1002587665),
                    (20171677030, 'Juan Sebastian Hernandez Benitez', 12, 1010231123),
                    (20222577093, 'Erick Stivent Rodríguez Rojas', 12, 1010062727),
                    (20232577093, 'Elvia Luz Machacon Pontón', 12, 1193360949),
                    (20232577135, 'Favian Estiven Gutierrez Murillo', 12, 1001285709),
                    (20231577058, 'Luna Mariana Chaparro', 12, 1141314063),
                    (20212577014, 'Jhulian David Montes Chibuque', 12, 1000253831),
                    (20221577080, 'Juan Eduardo Martínez Mancipe', 12, 1007107325),
                    (20202673118, 'Karol Tatiana Bautista Fajardo', 10, 1001296821),
                    (1013604453, 'Pulido Lemus Luis Alberto', 12, 1013604453),
                    (20241577003, 'Juan Sebastian Obando Moreno', 12, 1011094838),
                    (20221577006, 'Santiago Andrés Gil Duarte', 12, 1028660144),
                    (20231377008, 'Karoll Angelica Yarce Ruiz', 2, 1030701960),
                    (20242377014, 'Diomer Arbey Sanabria Pachón', 2, 0),
                    (20242377010, 'Maritza Andrea Cruz Rodríguez', 2, 0),
                    (20191577037, 'Maria Fernanda Parraga Hernandez', 12, 1007652277),
                    (202411377011, 'Harrison Estid Niño Muñoz', 2, 1000707362),
                    (20241377003, 'Aitken Julian Vasquez Silvera', 2, 1001203474),
                    (20192573001, 'Estefani Tapiero Guerra', 12, 1000224970),
                    (20222578140, 'Leidy Daniela Parra Vargas', 12, 1013258548),
                    (20222574033, 'Nicolás Galvis Carillo', 11, 1000698502),
                    (20181577087, 'Cristian Danilo Ramirez Maldonado', 2, 1032493626),
                    (20222577123, 'Fabian Eduardo Pedreros Diaz', 12, 1000378927),
                    (20232377071, 'Luis Camilo Garcia Lopez', 2, 1007648157),
                    (20241377030, 'Danna Ximena Sierra Aya', 2, 1000687876),
                    (20241377033, 'Daniel Vasquez', 2, 1007437470),
                    (20221673016, 'Joseph Nicolas Gomez Osorio', 10, 1034398166),
                    (20201577057, 'Andrés David López Pira', 12, 1007105062),
                    (20212574130, 'Jesús David Higuera', 11, 1001316242),
                    (20241379019, 'Jennifer Paola Castro Sua', 8, 1034659757),
                    (20241379013, 'Juan Andres Camargo Villa', 8, 1011098918),
                    (20232577028, 'Orjuela Reyes Harol Andres', 12, 1050090077),
                    (20241377006, 'Juan Pablo Sanchez Santana', 2, 1000614409),
                    (20192574104, 'Esteban Torres Molano', 11, 1000616760),
                    (20241577038, 'Linda Daniela Beltrán Torres', 12, 1140914253),
                    (20231574118, 'Juan David Santafe Leon', 11, 1101754658),
                    (20231377007, 'Javier Orrego Molina', 2, 1007303027),
                    (20221577031, 'Ximena Alexandra Cotreras Gomez', 12, 1077340124),
                    (20222577094, 'Diana Valeria Cifuentes Preciado', 12, 1087113294),
                    (20222377003, 'Mauricio Jose Beltran Perez', 2, 1012361891),
                    (20202577100, 'Jefereson Danjuver Moyano Manrique', 12, 1233512018),
                    (20222577090, 'Johan Nicolas Paez Salamanca', 12, 1019982746),
                    (20222577042, 'Leandro Peña Cifuentes', 12, 1001091757),
                    (20222577114, 'Angely Julieth Chavarro Gutierrez', 12, 1001286633),
                    (20221977034, 'Andrey Felipe Pineda Perez', 12, 1013099842),
                    (20211673003, 'Nicolas Mateo León Sierra', 10, 1001062353),
                    (20242577073, 'Nicol Sofia Amaya Villabon', 12, 1023378228),
                    (20242577075, 'Valeria Lemus Gomez', 12, 1013114765),
                    (20242577061, 'Daniela Jimenez Bareño', 12, 1140916418),
                    (20242577086, 'Monica Lorena Ramos Lopez', 12, 1014197631),
                    (20242577065, 'Valentina Africano', 12, 1028482208),
                    (20242577072, 'Manuel Jose Cifuentes', 12, 1011968270),
                    (20242577100, 'Pedro Estiben Soto Londoño', 12, 1012317469),
                    (20242577053, 'Yudi Noreli Vargas Gonzalez ', 12, 1024486825),
                    (20181577018, 'Tania Paola Aguilar Urrea', 12, 1024571478),
                    (20231377054, 'Ibeth Katherine Rodríguez castro', 2, 1012409019),
                    (20191577134, 'Gesther David Alfaro Ruíz', 12, 1002275590),
                    (20192577147, 'Santiago Torres Useche', 12, 1193562432),
                    (20201577020, 'Ivvo Imannol Betancur Perdomo', 12, 1077721178),
                    (20201573070, 'Walter Orduz Idarraga', 16, 1233504165),
                    (20202574082, 'Jerson Stiven Niño Chala', 11, 1000365927),
                    (20232377009, 'Adriana Calolina Munevar Cruz', 2, 1000252313),
                    (20201577047, 'aitken julian vazquez silvera', 12, 1001203474),
                    (20182577155, 'Alejandro Fernandez Delgado', 2, 1019119868),
                    (20231577075, 'Alison Natalia Rodriguez Mahecha', 12, 20231577075),
                    (20212673001, 'Anderson Camilo Pardo Gomez', 10, 1010246722),
                    (20211577079, 'Anderson Seyora', 12, 1000730264),
                    (20211574074, 'Andrea de Paula Morales Petit', 11, 30064101),
                    (20222577070, 'Andrés Alzedo', 12, 1018512125),
                    (20211574139, 'Andres David Beltran Martinez', 11, 1031120704),
                    (20241377012, 'Andres Felipe Rodriguez Rodriguez', 2, 1000139515),
                    (20192577008, 'Andres Felipe Rodriguez Rodriguez', 12, 1000139515),
                    (20221578067, 'Andrés Julián Barreto Puerto', 13, 1000286882),
                    (20221577095, 'Angela Maria Molina Rivera', 12, 1051954196),
                    (20241377044, 'Angela María Tovar R', 2, 1000018494),
                    (20202577027, 'Angie Benitez Castro', 12, 1000379092),
                    (20222577126, 'Angie Carolina Castellanos Acosta', 12, 1030695746),
                    (20212577109, 'Angie Sofia Gonzalez Ortiz', 12, 1023364141),
                    (20221577050, 'Angie Sofia Lagos Borda', 12, 1032797090),
                    (20241377023, 'Angie Vanesa Beltran Real', 2, 1000351195),
                    (20201577068, 'Anthony Emanuel Perilla Mora', 2, 1000212984),
                    (20222577008, 'Axel Sneyder Garzon Bello', 12, 1022933533),
                    (20212577063, 'Brallan Alexander Arguello Mancipe', 12, 1000695000),
                    (20221577089, 'Brallan Stiven Cruz Laguna', 12, 1027522333),
                    (20202577059, 'Brayan David Garzón Mantilla', 12, 1192793743),
                    (20241377046, 'Brayan Giobanny Lopez Coronado', 2, 1000592558),
                    (20241574135, 'Brayan Ospina Ospina', 11, 1013112691),
                    (20241377062, 'Brayan Steven Fandiño Pinilla', 2, 1007354557),
                    (20212577064, 'Brayhan Alberto Sua Cuy', 12, 1002480334),
                    (20202574051, 'Camilo Andrés Castillejo Ortíz', 11, 1001058365),
                    (20232377024, 'Carlos Andres Calderon Rojas', 2, 1001052813),
                    (20222577011, 'Carol Sofia Arango Barrios', 12, 1018411715),
                    (20231577017, 'Carol Yulieth Jimenez Ventura', 12, 1033687351),
                    (20221577018, 'Cesar Santiago Rodríguez Rojas', 12, 1027521651),
                    (20211574095, 'Cristian Camilo Mellizo Oliveros', 11, 1011200110),
                    (20222377042, 'Cristian Danilo Ramirez Galdonado', 2, 1032493626),
                    (20192573043, 'Cristian David Cangrejo Arias', 10, 1000226313),
                    (20221577039, 'Cristian David Montejo Daza', 12, 1034656923),
                    (20212577054, 'Cristian Sebastian Hernandez Salamanca', 12, 1001052257),
                    (20241377055, 'Dairon Andrey Carreño Parrado', 2, 1000227601),
                    (20232377002, 'Daniel Alejandro Usama Caes', 2, 1033784698),
                    (2022377066, 'Daniel Alfonso Rios Rueda', 2, 1023034519),
                    (20192577144, 'Daniel Esteban León Torres', 12, 1052409385),
                    (20201573067, 'Daniel Santiago Pinilla Reyes', 16, 1032501056),
                    (20212673118, 'Danilo Andres Cañon Palomino', 10, 1023242085),
                    (20231577070, 'Danna Valentina Quijano Sayago', 12, 1013591979),
                    (20221577109, 'Danna Yiseth Almanza Sastoque', 12, 1192736000),
                    (20212577092, 'David Alexander Cardenas Camelo', 12, 1000035693),
                    (20221973010, 'David Santiago Enciso Amorocho', 10, 1014659412),
                    (20221577037, 'David Santiago Martinez Peña', 12, 1000494481),
                    (20191577072, 'Dayana Lisbet Marin Cubides', 12, 1000001596),
                    (20231577078, 'Denisse Salome Gonzalez Posada', 12, 1019989379),
                    (20212577110, 'Derly Catherine Vargas Tamara', 12, 1023025846),
                    (20231577010, 'Diana Sofia Carvajal Ceron', 12, 1032367595),
                    (20202577092, 'Diana Sofia Caucayo Ochoa', 12, 1010133546),
                    (20231377022, 'Diego Andres Morales Riaño', 2, 1033809834),
                    (20242377028, 'Dilan Esteban Aranda Gualteros', 2, 1007648188),
                    (20191573107, 'Edgar Alfonso Duran Uriza', 10, 1001198997),
                    (20221577017, 'Erick Santiago Lopez Bustos', 12, 1019986529),
                    (20221577107, 'Erika Natalia Escarraga Castiblanco', 12, 1027521718),
                    (20222577048, 'Esteban Henao Ramirez', 12, 1025524196),
                    (20231577044, 'Estefania Pinzon Herreño', 12, 1005476537),
                    (20241377016, 'Eveyn Cañon', 2, 1000973575),
                    (20231577076, 'Fredy Alonso Mesa Granados', 12, 1019982580),
                    (20241377035, 'Gabriela Duarte Villamil', 2, 1024488655),
                    (20231673089, 'Gerson Samuel Castillo Parra', 10, 1013098999),
                    (20241377032, 'Gesther David Alfaro Ruiz', 2, 1002275590),
                    (20231577032, 'Gina Katerin Murcia Perez', 12, 1076648861),
                    (20152374067, 'ginna lorena torres vega', 12, 1012368718),
                    (20231377064, 'Ginneth Alejandra Quintero Romero', 2, 1024599792),
                    (20211577027, 'Hasbleidy Nava', 12, 1001272798),
                    (20221577011, 'Heidy Fernanda Lizarazo Salazar', 12, 1000775020),
                    (20221379086, 'Jeimmy Carolina Ramírez Poveda', 8, 1011081861),
                    (20211577053, 'Jheison estiben bernal cucaita', 12, 1007498307),
                    (20232379034, 'Jhon Jairo Rivera Lopez', 8, 1050220069),
                    (20231577005, 'Johan Andres Guerrero Barragan', 12, 1076242715),
                    (20212673053, 'Johan David Daza Palacios', 10, 1000626354),
                    (20192573145, 'Johan Sebastian Contreras Ariza', 16, 1013686509),
                    (20241377021, 'Johana Caterin Muñoz Callejas', 2, 1025520864),
                    (20212583018, 'Jordan Camilo Noguera Barahona', 4, 1233511928),
                    (20212577120, 'Jorge Andres Tique Ruje', 12, 1025520883),
                    (20211577030, 'Jorge David Castro Cordoba', 12, 1083865856),
                    (20222379154, 'José Miro Taquinas Achicue', 8, 1003373417),
                    (20212577094, 'Juan Andres Arango Rodriguez', 12, 1192782627),
                    (20182577005, 'Juan Andres Naranjo Pulido ', 12, 1001328352),
                    (20231577024, 'Juan Angel Mora Plata', 12, 1031421258),
                    (20232574025, 'Juan Camilo Valencia Mendez', 11, 1000625313),
                    (20232377070, 'Juan Carlos Vega Gonzalez', 2, 1033815896),
                    (20211579020, 'Juan David Bello Hernandez', 1, 1033814075),
                    (20221578058, 'Juan David López Marcelo', 13, 1012320944),
                    (20192573096, 'Juan Esteban Ovalle Cañon', 10, 1000335818),
                    (20211577127, 'Juan Felipe Sanchez Lozano', 12, 1000502494),
                    (20212577031, 'Juan Sebastian Ruiz', 12, 1023362637),
                    (20201052010, 'Juana Valentina Cespedes Blanco', 15, 1000733036),
                    (20222577009, 'Julian Andres Castañeda Guerrero', 12, 1000974023),
                    (20221577048, 'Julieth Alejandra Vanegas Lopez', 12, 1034657526),
                    (20221977018, 'Karen Dayana Poveda Poveda', 12, 1003977018),
                    (20221577040, 'Karen Juliana Arevalo Garcia', 12, 1032365364),
                    (20211577042, 'Karen Sofia Avila Garcia', 12, 1032796711),
                    (20222673087, 'Karen Tatiana Poveda Segura', 10, 1000940916),
                    (20231377020, 'Karen Yuranny Tellez Marinez', 12, 1002406453),
                    (20212577066, 'Katherin Lizeth Burgos Velasco', 12, 1000522533),
                    (20222577038, 'Kevin Camilo Barriga Vasquez', 12, 1007384369),
                    (20222377059, 'Kevin Ramiro Castro Bermudez', 2, 1024587124),
                    (20231574012, 'Kevin Santiago Daza Junco', 11, 1032938958),
                    (20231577021, 'Laura Daniela Rodriguez Cespedes', 12, 1000004540),
                    (20221577060, 'Laura Daniela Rojas Machado', 12, 1001202232),
                    (20241377022, 'Laura Daniela Rojas Machado', 2, 1001185562),
                    (20221577053, 'Laura Daniela Velandia Cortes', 12, 1001330184),
                    (20221577029, 'Laura Valentina Herrera Garzón', 12, 1031540322),
                    (20221977013, 'Laura Valentina Morales Riraquive', 12, 1022928614),
                    (20211577023, 'Laura Vanessa Gamba Garzon', 12, 1030698913),
                    (20221977006, 'Laura Ximena Herrera Segura', 12, 1032937526),
                    (20222577057, 'Liceth Lorena Montealegre Martinez', 12, 1029220200),
                    (20212577097, 'Lina Andrea Cardenas Rubiano', 12, 1000835435),
                    (20232377055, 'Loren Sofia Pantano', 2, 1001315776),
                    (20241377038, 'Luis Felipe Rincon', 2, 1193072039),
                    (20202577097, 'Mabel Estefany Malpica Mendivelso', 12, 1000997568),
                    (20231377039, 'Maira Alejandra Marin Ayala', 2, 1007423556),
                    (20241377007, 'Maria Fernanda Parraga Hernandez', 2, 1007652277),
                    (20202577020, 'Maria Fernanda Quebraolla Rincon ', 12, 1000687133),
                    (20212577045, 'Maria Fernanda Rodriguez Lopez', 11, 1024461482),
                    (20222577027, 'Maria Fernanda Rozo Gonzales', 12, 1000381504),
                    (20212574027, 'Maria Paula Peñaranda Avila', 11, 100574269),
                    (20222577084, 'Mariana Alejandra Reinoso Bastidas', 12, 1000005823),
                    (20212577093, 'Mariana Villamil Jimenez', 12, 1000695670),
                    (20221577069, 'Maribel Ovalle Segura', 12, 1117551520),
                    (20201577011, 'Mario Esteban Zarate Diaz', 12, 1000988050),
                    (20202577049, 'Marlon Alexis Palacios Vargas', 12, 1003766271),
                    (20191573047, 'Martín Julián Godoy Ramírez', 16, 1000785767),
                    (20181577078, 'Mayer Mauricio Bautista Rodríguez', 12, 1000781620),
                    (20222577069, 'Michael Guerrero', 12, 1000220685),
                    (20212574069, 'Michael Stiven Torres Aldana', 7, 1000942992),
                    (20221977031, 'Miguel Angel Bedoya Ospina', 12, 1000621999),
                    (20231577054, 'Miguel Angel Gutierrez Soto', 12, 1000790173),
                    (20222673106, 'Miguel Angel Pinto Rozo', 10, 1127610478),
                    (20221577077, 'Natalia Bedoyaa Monroy', 12, 1032937972),
                    (20222577036, 'Natalia Tibabuso Tribaldos', 12, 1015994502),
                    (20232377034, 'Nathaly Calvo Cepeda', 2, 1024587055),
                    (20202577079, 'Nicolas Felipe Sanchez Morales', 12, 1000465819),
                    (20221577010, 'Nicolas Henao Muñoz', 12, 1022931341),
                    (20191577047, 'Nicolas Ricardo Yanquen Jaime', 12, 1002332082),
                    (20211577112, 'Oscar Alejandro Casas Sopo', 12, 1003699881),
                    (20182574036, 'Oscar Santiago Acevedo Rodriguez', 11, 1033820107),
                    (20211577028, 'Oscar Yesid Hernandez Bermudez', 12, 1001174412),
                    (20221577105, 'Paula Sofia Gamba Arias', 12, 1022924784),
                    (20171779073, 'Ricardo Sosa', 8, 20171779073),
                    (20221577033, 'Santiago Alejandro González Gútierrez', 12, 1021664614),
                    (20202574129, 'Santiago Peña Rodríguez', 11, 1007708919),
                    (20222673028, 'Santiago Zuñiga Rodriguez', 10, 1122508542),
                    (20241377051, 'Sara Quimbayo Orozco', 2, 1000858067),
                    (20211577093, 'Sara Sofia Rico Vergara', 12, 1000991457),
                    (20231577030, 'Sara Valentina Rincón Córdoba', 12, 10960654371),
                    (20212577078, 'Slendy Tatiana Aguilar Correa', 12, 1000725474),
                    (20211577142, 'Sofia Junca Aguas', 12, 1000952566),
                    (20231377040, 'Stefany Pulga Zanguña', 2, 10263078252),
                    (20231377069, 'Tania Paola Aguilar Urrea', 2, 1024571478),
                    (20222577051, 'Valentina Parra García', 12, 1022930289),
                    (20221673052, 'Valentina Toro Rodriguez', 10, 1014658334),
                    (20231377025, 'Valentina Vera Quiroga', 2, 1000033994),
                    (20221577098, 'Valeria Estefania Avendaño Roa', 12, 1000493662),
                    (20241377024, 'Valeria Pamplona Gutierrez', 2, 1000973174),
                    (20231577007, 'Wilder Alexis Sarmiento Guerrero', 12, 1000036168),
                    (20212577133, 'Xiomara Quitian Martinez', 12, 1000727794),
                    (20221577045, 'Yady Xiomara Gaitan Achury', 12, 1002700091),
                    (20222577129, 'Yeimi constanza Tautiva', 12, 1074159611),
                    (20241574121, 'Jeimy Caterine Silva Silva', 11, 1029142582),
                    (20241377053, 'Yennifer Alexandra Huertas Triviño', 2, 1000519921),
                    (20182577085, 'Yerys Catalina Alvarez Morales', 12, 1000689480),
                    (20162577034, 'Yohana Caterin Ladino Martin', 2, 1016102240),
                    (20222377060, 'Yolima Marin Leon', 2, 1006902356),
                    (20212574112, 'Yosid Estevan Martinez Gonzalez', 11, 1006772787),
                    (20221577038, 'Zharinck Fernanda Feo Ruiz', 12, 1023363720),
                    (20202574079, 'Jorge Hernando Sarmiento Reyes', 11, 1004006241),
                    (20241377029, 'Anthony Emanuel Perilla Mora', 2, 1000212984),
                    (20192573055, 'Juan Camilo Castro', 10, 1001201521),
                    (20211673140, 'Nelson Sebastian Bajaca Acero', 10, 1000864455),
                    (20192577125, 'Santiago Romero Quevedo', 12, 1001193290),
                    (20242377047, 'Andres Felipe Ortiz Leon', 2, 0)
                    (20222577060), 'Geraldine Espitia Florido', 12, 1002523383),
                    (20222577080, 'Paula Alejandra Arroyo Mur', 12, 1030529181),
                    (20231574076, 'Javier Leonardo Tique Buenaventura', 11, 1028480566),
                    (20212577069, 'Michael Hernandez', 12, 1012433450);
            ''')

        # Profesores
        cursor.execute("SELECT COUNT(*) FROM profesores")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO profesores (cedula, nombre, proyecto_curricular_id) VALUES 
                    (80154113, 'Juan Carlos Casas Bustos', 12),
                    (1046874842, 'LOURDES CLARISSA DE LA ROSA SILVA', 8),
                    (19274281, 'Manuel Mayorga Morato', 12),
                    (80000901, 'Jhon Vladimir Acevedo Perez', 8),
                    (79703780, 'Freddy Eduardo Soler', 2),
                    (79430985, 'Wilfredo Ramirez Pretel', 12),
                    (797662077, 'EDWIN ALBERTO BULLA PEREIRA', 12),
                    (79616453, 'Nelsol Eduardo Garavito Leon', 2),
                    (79541666, 'Jose Eduardo Ustariz', 11),
                    (79529530, 'Eusebio Aventaño', 16),
                    (79527235, 'Alberto Delgadillo', 4),
                    (7169011, 'Mario Alberto Rodriguez Berrera', 9),
                    (79554816, 'Robinson Pacheco García', 12),
                    (80062068, 'Jorge Andrés Puerto Acosta', 4),
                    (1022339649, 'Digo Armando Giral Ramírez', 9),
                    (7140277, 'Jorge Andres Marulanda', 2),
                    (80172969, 'Jhon Rodrigo Hernandez Mora', 12),
                    (32841913, 'Astrid del Socorro Altamar Consuegra', 12),
                    (1,	'Javier Lopez Macias', 12),
                    (79055619, 'Jose David Cely Callejas', 18),
                    (1000973174, 'Valeria Pamplona Gutierrez', 2),
                    (51882539, 'Angela Pardo Heredia', 12),
                    (10178396, 'Albeiro Rubiano'),
                    (1000988323, 'Miguel Angel Bernal Gonzales', 9),
                    (80913205, 'Hector Ivan Tangarife Escobar', 11),
                    (52522772, 'Mariam  Elizabeth Vera Morales', 12),
                    (79627235, 'Alberto Delgadillo', 10),
                    (7181387, 'Alexander Alvarado Moreno', 7),
                    (1020808609, 'Carlos Arturo Gomez Jimenez', 1),
                    (79937984, 'Cesar Fernando Losada Figueroa', 1),
                    (51953330, 'Claudia Mabel Moreno Penagos', 12),
                    (73114432, 'David Rafael Navarro Mejia', 12),
                    (51563377, 'Doris Marlene Olea Suarez', 12),
                    (79114770, 'Edgar Antonio Pinto Cruz', 2),
                    (80437933, 'Edgar Arturo Chala Bustamante', 11),
                    (79380996, 'Edgar Humberto Sanchez Cotte', 8),
                    (79662344, 'Edgar Orlando Ladino Moreno', 1),
                    (80210579, 'Edward Hernando Bejarano', 10),
                    (79766207, 'Edwin Alberto Bulla Pereira', 12),
                    (1067880335, 'Emiliano Rodríguez Arango', 7),
                    (12977377, 'Ernesto Agreda Bastidas', 11),
                    (52715915, 'Evelyn Ivonne Diaz Montaño', 12),
                    (79526683, 'Fabio Hernando Castellanos Moreno', 10),
                    (19407823, 'Faolain Chaparro Chaparro', 12),
                    (79797695, 'Gustavo Andrés Romero Duque', 12),
                    (79312331, 'Humberto Guerrero Salas', 12),
                    (79457691, 'Jaime Francisco Pantoja Benavides', 12),
                    (1022350475, 'Javier Giovanny Rodriguez Quintero', 7),
                    (79617870, 'Javier Parra Peña', 12),
                    (79498320, 'Johan Alexander Rincon Gualdron', 2),
                    (79459303, 'Jorge Federico Ramirez Escobar', 4),
                    (79598913, 'Jorge Guzman Laverde', 12),
                    (19460176, 'Jose Ernesto Uribe Becerra', 12),
                    (80006862, 'Leonardo Andrés Hernández', 2),
                    (8006862, 'Leonardo Andrés Hernandez Beltrán', 2),
                    (79572667, 'Luini Leonardo Hurtado Cortes', 11),
                    (79286581, 'Luis Carlos Rojas Obando', 2),
                    (80062648, 'Luis Fernando Rodrígez Mondragón', 2),
                    (79576740, 'Luis Jorge Herrera', 2),
                    (52237734, 'Luz Dined Cardona Perdomo', 2),
                    (79799135, 'Marco Antonio Velasco Peña', 7),
                    (52051465, 'Martha Edith Pinzón Rueda', 12),
                    (65771052, 'Martha Lucia Tello Castañeda', 10),
                    (7226873, 'Mauricio Gonzales Colmenares', 7),
                    (79970934, 'Miguel Angel Ospina Usaquén', 12),
                    (52825393, 'Monica Yinette Suarez Serrano', 12),
                    (52990699, 'Nathaly Marin Medina', 8),
                    (79040266, 'Nelson Eduardo Rodriguez Montaña', 12),
                    (79852868, 'Norberto Chacón Cepeda', 2),
                    (52560428, 'Norvelys Celys Marin', 8),
                    (1033701075, 'Oscar Javier Martines Ricaurte', 5),
                    (79474810, 'Pablo Emilio Garzón Carreño', 2),
                    (8534496, 'Ricardo de Armas Costas', 6),
                    (19407114, 'Rodrigo Quintero Reyes', 12),
                    (79746738, 'Roman Leonardo Rodríguez Florian', 12),
                    (79938449, 'Ronald Gonzales Silva', 12),
                    (39750690, 'Ruth Esperanza Roman', 12),
                    (3154728, 'Urias Cendales Romero', 12),
                    (79502261, 'Victor Hugo Riveros Gomez', 12),
                    (79756323, 'Victor Ruiz', 7),
                    (79697945, 'William Alexander Murcia Rodriguez', 12),
                    (80472494, 'Wilson Alexander Pinzón Rueda', 2);
            ''')

        # Préstamos de salas a profesores
        cursor.execute("SELECT COUNT(*) FROM prestamos_salas_profesores")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO prestamos_salas_profesores 
                (fecha_entrada, laboratorista, monitor, sala_id, profesor_id, hora_salida, firma_profesor, observaciones) 
                VALUES 
                ('2024-03-15 08:00:00', 5, 1, 1, 80012345, NULL, NULL, 'Clase de laboratorio'),
                ('2024-03-15 10:30:00', 6, 2, 2, 80023456, NULL, NULL, 'Práctica de estudiantes');
            ''')
            
            cursor.executescript('''
                INSERT INTO prestamos_salas_profesores 
                (fecha_entrada, laboratorista, monitor, sala_id, profesor_id, hora_salida, firma_profesor, observaciones) 
                VALUES 
                ('2024-03-15 13:00:00', 7, 3, 3, 80034567, NULL, NULL, 'Investigación'),
                ('2024-03-15 15:30:00', 8, 4, 4, 80045678, NULL, NULL, 'Trabajo de grado');
            ''')

        # Préstamos de salas a estudiantes
        cursor.execute("SELECT COUNT(*) FROM prestamos_salas_estudiantes")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO prestamos_salas_estudiantes 
                (fecha_entrada, laboratorista, monitor, sala_id, estudiante_id, hora_salida, equipo_codigo, firma_estudiante, novedad) 
                VALUES 
                ('2024-03-15 08:00:00', 5, 1, 1, 2023001, NULL, NULL, NULL, NULL),
                ('2024-03-15 10:30:00', 6, 2, 2, 2023002, NULL, NULL, NULL, NULL),
                ('2024-03-15 13:00:00', 7, 3, 3, 2023003, NULL, NULL, NULL, NULL),
                ('2024-03-15 15:30:00', 8, 4, 4, 2023004, NULL, NULL, NULL, NULL);
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