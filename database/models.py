from database.connection import DatabaseManager
from datetime import datetime

class StudentModel:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_students(self, search_term="", project_filter=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT e.codigo, e.nombre, e.cedula, pc.nombre as proyecto
            FROM estudiantes e
            LEFT JOIN proyectos_curriculares pc ON e.proyecto_curricular_id = pc.id
            WHERE (e.codigo LIKE ? OR e.nombre LIKE ? OR e.cedula LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%', f'%{search_term}%']
        
        if project_filter:
            query += " AND pc.nombre = ?"
            params.append(project_filter)
        
        cursor.execute(query, params)
        students = cursor.fetchall()
        conn.close()
        return students
    
    def add_student(self, codigo, nombre, cedula, proyecto_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO estudiantes (codigo, nombre, cedula, proyecto_curricular_id)
                VALUES (?, ?, ?, ?)
            ''', (codigo, nombre, cedula, proyecto_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_student(self, codigo, nombre, cedula, proyecto_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE estudiantes 
                SET nombre = ?, cedula = ?, proyecto_curricular_id = ?
                WHERE codigo = ?
            ''', (nombre, cedula, proyecto_id, codigo))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_student(self, codigo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM estudiantes WHERE codigo = ?', (codigo,))
        conn.commit()
        conn.close()
    
    def get_curriculum_projects(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM proyectos_curriculares')
        projects = cursor.fetchall()
        conn.close()
        return projects

class Profesor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_profesores(self, search_term="", project_filter=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.cedula, p.nombre, pc.nombre as proyecto
            FROM profesores p
            LEFT JOIN proyectos_curriculares pc ON .proyecto_curricular_id = pc.id
            WHERE (p.codigo LIKE ? OR p.nombre LIKE ? OR p.cedula LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%', f'%{search_term}%']
        
        if project_filter:
            query += " AND pc.nombre = ?"
            params.append(project_filter)
        
        cursor.execute(query, params)
        students = cursor.fetchall()
        conn.close()
        return students
    
    def add_profesor(self, cedula, nombre, proyecto_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO profesores (cedula, nombre, proyecto_curricular_id)
                VALUES (?, ?, ?)
            ''', (cedula, nombre, proyecto_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_profesor(self, cedula, nombre, proyecto_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE profesores 
                SET nombre = ?, proyecto_curricular_id = ?
                WHERE cedula = ?
            ''', (nombre, proyecto_id, cedula))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_profesor(self, cedula):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM profesores WHERE cedula = ?', (cedula))
        conn.commit()
        conn.close()
    
    def get_proyectos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM proyectos_curriculares')
        proyectos = cursor.fetchall()
        conn.close()
        return proyectos
    
class RoomModel:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_rooms(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.codigo, s.nombre,
                   CASE 
                       WHEN EXISTS (
                           SELECT 1 FROM prestamos_salas_profesores 
                           WHERE sala_id = s.codigo AND hora_salida IS NULL
                       ) OR EXISTS (
                           SELECT 1 FROM prestamos_salas_estudiantes 
                           WHERE sala_id = s.codigo AND hora_salida IS NULL
                       ) THEN 'Ocupada'
                       ELSE 'Disponible'
                   END as estado
            FROM salas s
        ''')
        rooms = cursor.fetchall()
        conn.close()
        return rooms
    
    def add_room(self, codigo, nombre):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO salas (codigo, nombre) VALUES (?, ?)', (codigo, nombre))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_room(self, codigo, nombre):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE salas SET nombre = ? WHERE codigo = ?', (nombre, codigo))
        conn.commit()
        conn.close()

class InventoryModel:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_equipment(self, search_term="", status_filter=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT codigo, marca_serie, nombre_funcionario, 
                   COALESCE(s.nombre, 'Sin sede') as ubicacion,
                   descripcion, contenido, estado
            FROM inventario i
            LEFT JOIN sedes s ON i.sede_id = s.id
            WHERE (codigo LIKE ? OR marca_serie LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if status_filter:
            query += " AND estado = ?"
            params.append(status_filter)
        
        cursor.execute(query, params)
        equipment = cursor.fetchall()
        conn.close()
        return equipment
    
    def add_equipment(self, codigo, marca_serie, documento_funcionario, 
                     nombre_funcionario, descripcion, contenido, estado, sede_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO inventario 
                (codigo, marca_serie, documento_funcionario, nombre_funcionario, 
                 descripcion, contenido, estado, sede_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codigo, marca_serie, documento_funcionario, nombre_funcionario,
                  descripcion, contenido, estado, sede_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_available_equipment(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT codigo, descripcion FROM inventario WHERE estado = "DISPONIBLE"')
        equipment = cursor.fetchall()
        conn.close()
        return equipment
    
    def get_sedes(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM sedes')
        sedes = cursor.fetchall()
        conn.close()
        return sedes