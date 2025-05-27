import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('university.db')
        return conn
    except Error as e:
        print(e)
    return conn

def setup_database(conn):
    sql_statements = [
        '''CREATE TABLE IF NOT EXISTS proyectos_curriculares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        );''',
        '''CREATE TABLE IF NOT EXISTS salas (
            codigo INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL
        );''',
        # ... All other tables ...
        '''CREATE TRIGGER IF NOT EXISTS trg_prestamo_equipo_profesor
           AFTER INSERT ON prestamos_equipos_profesores
           BEGIN
               UPDATE inventario SET estado = 'EN USO'
               WHERE codigo = NEW.equipo_codigo;
           END;''',
        # ... Other triggers ...
    ]
    
    try:
        c = conn.cursor()
        for statement in sql_statements:
            c.execute(statement)
        conn.commit()
    except Error as e:
        print(e)