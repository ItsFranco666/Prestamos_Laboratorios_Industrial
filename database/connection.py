import sqlite3
# from datetime import datetime
# import os

class DatabaseManager:
    def __init__(self, db_path="uso_de_espacios.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database with the required schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
            -- Enable foreign key constraints
            PRAGMA foreign_keys = ON;
            
            CREATE TABLE IF NOT EXISTS proyectos_curriculares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS salas (
                codigo INTEGER PRIMARY KEY,
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
                sala_id INTEGER REFERENCES salas(codigo),
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
                sala_id INTEGER REFERENCES salas(codigo) NOT NULL,
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
                sala_id INTEGER REFERENCES salas(codigo) NOT NULL,
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
                sala_id INTEGER REFERENCES salas(codigo),
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
                sala_id INTEGER REFERENCES salas(codigo) NOT NULL,
                titulo_practica TEXT,
                estado INTEGER NOT NULL CHECK (estado IN (0, 1)),
                laboratorista_devolucion INTEGER REFERENCES personal_laboratorio(id),
                monitor_devolucion INTEGER REFERENCES personal_laboratorio(id),
                documento_devolvente INTEGER,
                observaciones TEXT
            );
        ''')
        
        # Create triggers
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
        
        # Insert some initial data if tables are empty
        self._insert_initial_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_initial_data(self, cursor):
        """Insert initial data for testing"""
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM proyectos_curriculares")
        if cursor.fetchone()[0] == 0:
            cursor.executescript('''
                INSERT INTO proyectos_curriculares (nombre) VALUES 
                ('Ingeniería de Sistemas'),
                ('Ingeniería Electrónica'),
                ('Ingeniería Industrial');
                
                INSERT INTO sedes (nombre) VALUES 
                ('Sede Central'),
                ('Sede Norte');
                
                INSERT INTO personal_laboratorio (nombre, cargo) VALUES 
                ('Juan Pérez', 0),
                ('María González', 1),
                ('Carlos López', 0);
                
                INSERT INTO salas (codigo, nombre) VALUES 
                (101, 'Laboratorio de Sistemas 1'),
                (102, 'Laboratorio de Electrónica'),
                (103, 'Aula de Cómputo');
            ''')