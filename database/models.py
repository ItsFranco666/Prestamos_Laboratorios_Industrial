# In university_management/database/models.py
import sqlite3
from .connection import DatabaseManager # Corrected import
from datetime import datetime

class StudentModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def get_all_students(self, search_term="", project_filter_name=""):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT e.codigo, e.nombre, e.cedula, pc.nombre as proyecto_nombre
            FROM estudiantes e
            LEFT JOIN proyectos_curriculares pc ON e.proyecto_curricular_id = pc.id
            WHERE (CAST(e.codigo AS TEXT) LIKE ? OR e.nombre LIKE ? OR CAST(e.cedula AS TEXT) LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%', f'%{search_term}%']
        
        if project_filter_name:
            query += " AND pc.nombre = ?"
            params.append(project_filter_name)
        
        query += " ORDER BY e.nombre ASC"
        cursor.execute(query, params)
        students = cursor.fetchall()
        conn.close()
        return students

    def get_student_by_code_or_id(self, identifier):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT codigo, nombre, cedula, proyecto_curricular_id 
            FROM estudiantes 
            WHERE codigo = ? OR cedula = ?
        ''', (identifier, identifier))
        student = cursor.fetchone()
        conn.close()
        return student
    
    def add_student(self, codigo, nombre, cedula, proyecto_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO estudiantes (codigo, nombre, cedula, proyecto_curricular_id)
                VALUES (?, ?, ?, ?)
            ''', (codigo, nombre, cedula, proyecto_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error adding student: {e}")
            return False
        finally:
            conn.close()
    
    def update_student(self, original_codigo, nombre, cedula, proyecto_id, new_codigo=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if new_codigo is None:
                new_codigo = original_codigo
            cursor.execute('''
                UPDATE estudiantes 
                SET codigo = ?, nombre = ?, cedula = ?, proyecto_curricular_id = ?
                WHERE codigo = ?
            ''', (new_codigo, nombre, cedula, proyecto_id, original_codigo))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error updating student: {e}")
            return False
        finally:
            conn.close()
    
    def delete_student(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM estudiantes WHERE codigo = ?', (codigo,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting student: {e}") # Handle potential foreign key constraints if student has loans
        finally:
            conn.close()
    
    def get_curriculum_projects(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM proyectos_curriculares ORDER BY nombre ASC')
        projects = cursor.fetchall()
        conn.close()
        return projects

class ProfesorModel: # Renamed from Profesor for consistency
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_profesores(self, search_term="", project_filter_name=""):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.cedula, p.nombre, pc.nombre as proyecto_nombre
            FROM profesores p
            LEFT JOIN proyectos_curriculares pc ON p.proyecto_curricular_id = pc.id
            WHERE (CAST(p.cedula AS TEXT) LIKE ? OR p.nombre LIKE ?)
        '''
        # Cedula is primary key, usually not searched with LIKE unless it's a partial string search
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if project_filter_name:
            query += " AND pc.nombre = ?"
            params.append(project_filter_name)
        
        query += " ORDER BY p.nombre ASC"
        cursor.execute(query, params)
        profesores = cursor.fetchall()
        conn.close()
        return profesores

    def get_professor_by_id(self, cedula): # Changed from get_professor_by_code_or_id
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cedula, nombre, proyecto_curricular_id 
            FROM profesores 
            WHERE cedula = ?
        ''', (cedula,))
        professor = cursor.fetchone()
        conn.close()
        return professor
    
    def add_profesor(self, cedula, nombre, proyecto_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO profesores (cedula, nombre, proyecto_curricular_id)
                VALUES (?, ?, ?)
            ''', (cedula, nombre, proyecto_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error adding professor: {e}")
            return False
        finally:
            conn.close()
    
    def update_profesor(self, original_cedula, nombre, proyecto_id, new_cedula=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if new_cedula is None:
                new_cedula = original_cedula
            cursor.execute('''
                UPDATE profesores 
                SET cedula = ?, nombre = ?, proyecto_curricular_id = ?
                WHERE cedula = ?
            ''', (new_cedula, nombre, proyecto_id, original_cedula))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error updating professor: {e}")
            return False
        finally:
            conn.close()
    
    def delete_profesor(self, cedula):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM profesores WHERE cedula = ?', (cedula,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting professor: {e}") # Handle potential foreign key constraints
        finally:
            conn.close()
    
    def get_curriculum_projects(self): # Same as StudentModel, could be refactored
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM proyectos_curriculares ORDER BY nombre ASC')
        projects = cursor.fetchall()
        conn.close()
        return projects

class RoomModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_rooms_with_status(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                s.id,
                s.codigo_interno, 
                s.nombre,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM prestamos_salas_profesores psp
                        WHERE psp.sala_id = s.id AND psp.hora_salida IS NULL
                    ) OR EXISTS (
                        SELECT 1 FROM prestamos_salas_estudiantes pse
                        WHERE pse.sala_id = s.id AND pse.hora_salida IS NULL
                    ) THEN 'Ocupada'
                    ELSE 'Disponible'
                END as estado
            FROM salas s
            ORDER BY s.nombre ASC
        ''')
        rooms = cursor.fetchall()
        conn.close()
        return rooms

    def get_all_rooms_for_dropdown(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT codigo_interno, nombre FROM salas ORDER BY nombre ASC')
        rooms = cursor.fetchall()
        conn.close()
        return rooms
        
    def get_room_by_code(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT codigo_interno, nombre FROM salas WHERE codigo_interno = ?', (codigo,))
        room = cursor.fetchone()
        conn.close()
        return room

    def add_room(self, codigo, nombre):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO salas (codigo_interno, nombre) VALUES (?, ?)', (codigo, nombre))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error adding room: {e}")
            return False
        finally:
            conn.close()
    
    def update_room(self, original_codigo, nombre, new_codigo=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if new_codigo is None:
                new_codigo = original_codigo
            cursor.execute('UPDATE salas SET codigo_interno = ?, nombre = ? WHERE codigo_interno = ?', (new_codigo, nombre, original_codigo))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error updating room: {e}")
            return False
        finally:
            conn.close()

    def delete_room(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM salas WHERE codigo_interno = ?', (codigo,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting room: {e}") # Handle FK constraints
        finally:
            conn.close()

class InventoryModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_equipment(self, search_term="", status_filter="", brand_serial_filter=""):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT i.codigo, i.marca_serie, 
                   i.nombre_funcionario || ' (' || CAST(i.documento_funcionario AS TEXT) || ')' as responsable, 
                   COALESCE(s.nombre, 'N/A') as ubicacion_sede,
                   i.descripcion, i.contenido, i.estado
            FROM inventario i
            LEFT JOIN sedes s ON i.sede_id = s.id
            WHERE (i.codigo LIKE ? OR i.descripcion LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if status_filter:
            query += " AND i.estado = ?"
            params.append(status_filter)
        if brand_serial_filter:
            query += " AND i.marca_serie LIKE ?"
            params.append(f'%{brand_serial_filter}%')

        query += " ORDER BY i.codigo ASC"
        cursor.execute(query, params)
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    def get_equipment_by_code(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT codigo, marca_serie, documento_funcionario, nombre_funcionario, 
                   descripcion, contenido, estado, sede_id 
            FROM inventario WHERE codigo = ?
        ''', (codigo,))
        item = cursor.fetchone()
        conn.close()
        return item

    def add_equipment(self, codigo, marca_serie, documento_funcionario, 
                     nombre_funcionario, descripcion, contenido, estado, sede_id):
        conn = self.db_manager.get_connection()
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
        except sqlite3.IntegrityError as e:
            print(f"Error adding equipment: {e}")
            return False
        finally:
            conn.close()

    def update_equipment(self, original_codigo, marca_serie, documento_funcionario,
                         nombre_funcionario, descripcion, contenido, estado, sede_id, new_codigo=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if new_codigo is None:
                new_codigo = original_codigo
            cursor.execute('''
                UPDATE inventario 
                SET codigo = ?, marca_serie = ?, documento_funcionario = ?, nombre_funcionario = ?,
                    descripcion = ?, contenido = ?, estado = ?, sede_id = ?
                WHERE codigo = ?
            ''', (new_codigo, marca_serie, documento_funcionario, nombre_funcionario,
                  descripcion, contenido, estado, sede_id, original_codigo))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error updating equipment: {e}")
            return False
        finally:
            conn.close()

    def delete_equipment(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM inventario WHERE codigo = ?', (codigo,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting equipment: {e}") # Handle FK constraints
        finally:
            conn.close()
            
    def get_available_equipment_for_dropdown(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        # Fetches equipment that is 'DISPONIBLE'
        cursor.execute("SELECT codigo, descripcion || ' (' || estado || ')' FROM inventario WHERE estado = 'DISPONIBLE' ORDER BY codigo ASC")
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    def get_all_equipment_for_dropdown(self): # Includes status
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, descripcion || ' (' || estado || ')' FROM inventario ORDER BY codigo ASC")
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    def get_sedes(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM sedes ORDER BY nombre ASC')
        sedes = cursor.fetchall()
        conn.close()
        return sedes

class PersonalLaboratorioModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def get_all_personal(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, CASE cargo WHEN 0 THEN 'Laboratorista' ELSE 'Monitor' END as cargo_nombre FROM personal_laboratorio ORDER BY nombre ASC")
        personal = cursor.fetchall()
        conn.close()
        return personal

    def get_laboratoristas(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM personal_laboratorio WHERE cargo = 0 ORDER BY nombre ASC") # 0 for Laboratorista
        personal = cursor.fetchall()
        conn.close()
        return personal

    def get_monitores(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM personal_laboratorio WHERE cargo = 1 ORDER BY nombre ASC") # 1 for Monitor
        personal = cursor.fetchall()
        conn.close()
        return personal

class RoomLoanModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def add_loan_student(self, fecha_entrada, laboratorista_id, monitor_id, sala_id, estudiante_id, numero_equipo, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO prestamos_salas_estudiantes 
                (fecha_entrada, laboratorista, monitor, sala_id, estudiante_id, numero_equipo, novedad)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_entrada, laboratorista_id, monitor_id, sala_id, estudiante_id, numero_equipo, observaciones))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding student room loan: {e}")
            return None
        finally:
            conn.close()

    def add_loan_professor(self, fecha_entrada, laboratorista_id, monitor_id, sala_id, profesor_id, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO prestamos_salas_profesores
                (fecha_entrada, laboratorista, monitor, sala_id, profesor_id, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fecha_entrada, laboratorista_id, monitor_id, sala_id, profesor_id, observaciones))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding professor room loan: {e}")
            return None
        finally:
            conn.close()

    def get_room_loans(self, date_filter=None): # YYYY-MM-DD
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        base_query_student = '''
            SELECT pse.id, 'Estudiante' as tipo_usuario, e.nombre as usuario_nombre, s.nombre as sala_nombre, 
                   pse.fecha_entrada, pse.hora_salida, pl_lab.nombre as laboratorista, pl_mon.nombre as monitor, pse.novedad as observaciones, pse.estudiante_id as usuario_id, 'student' as loan_type
            FROM prestamos_salas_estudiantes pse
            JOIN estudiantes e ON pse.estudiante_id = e.codigo
            JOIN salas s ON pse.sala_id = s.codigo
            LEFT JOIN personal_laboratorio pl_lab ON pse.laboratorista = pl_lab.id
            LEFT JOIN personal_laboratorio pl_mon ON pse.monitor = pl_mon.id
        '''
        base_query_professor = '''
            SELECT psp.id, 'Profesor' as tipo_usuario, p.nombre as usuario_nombre, s.nombre as sala_nombre,
                   psp.fecha_entrada, psp.hora_salida, pl_lab.nombre as laboratorista, pl_mon.nombre as monitor, psp.observaciones, psp.profesor_id as usuario_id, 'professor' as loan_type
            FROM prestamos_salas_profesores psp
            JOIN profesores p ON psp.profesor_id = p.cedula
            JOIN salas s ON psp.sala_id = s.codigo
            LEFT JOIN personal_laboratorio pl_lab ON psp.laboratorista = pl_lab.id
            LEFT JOIN personal_laboratorio pl_mon ON psp.monitor = pl_mon.id
        '''
        params = []
        if date_filter:
            date_condition = " WHERE DATE(fecha_entrada) = ?"
            base_query_student += date_condition
            base_query_professor += date_condition
            params.extend([date_filter, date_filter])
        
        query = f"({base_query_student}) UNION ALL ({base_query_professor}) ORDER BY fecha_entrada DESC"
        
        cursor.execute(query, params)
        loans = cursor.fetchall()
        conn.close()
        return loans

    def get_room_loan_details(self, loan_id, loan_type):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        if loan_type == 'student':
            cursor.execute('''
                SELECT id, fecha_entrada, laboratorista, monitor, sala_id, estudiante_id, hora_salida, numero_equipo, novedad 
                FROM prestamos_salas_estudiantes WHERE id = ?
            ''', (loan_id,))
        elif loan_type == 'professor':
            cursor.execute('''
                SELECT id, fecha_entrada, laboratorista, monitor, sala_id, profesor_id, hora_salida, observaciones 
                FROM prestamos_salas_profesores WHERE id = ?
            ''', (loan_id,))
        else:
            conn.close()
            return None
        details = cursor.fetchone()
        conn.close()
        return details

    def update_room_loan_exit(self, loan_id, loan_type, hora_salida, observaciones, firma=None, numero_equipo=None): # firma not used yet
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if loan_type == 'student':
                cursor.execute('''
                    UPDATE prestamos_salas_estudiantes
                    SET hora_salida = ?, novedad = ?, numero_equipo = ?
                    WHERE id = ?
                ''', (hora_salida, observaciones, numero_equipo, loan_id))
            elif loan_type == 'professor':
                 cursor.execute('''
                    UPDATE prestamos_salas_profesores
                    SET hora_salida = ?, observaciones = ?
                    WHERE id = ?
                ''', (hora_salida, observaciones, loan_id))
            else:
                return False
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating room loan exit: {e}")
            return False
        finally:
            conn.close()

class EquipmentLoanModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.inventory_model = InventoryModel()  # Agregamos referencia al modelo de inventario

    def add_loan_student(self, fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id,
                         estudiante_id, numero_estudiantes, sala_id, titulo_practica, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Verificar si el equipo está disponible
            if not self.inventory_model.check_equipment_availability(equipo_codigo):
                return None

            # Estado: 1 for "En prestamo"
            cursor.execute('''
                INSERT INTO prestamos_equipos_estudiantes
                (fecha_entrega, equipo_codigo, laboratorista_entrega, monitor_entrega, estudiante_id,
                 numero_estudiantes, sala_id, titulo_practica, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?) 
            ''', (fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id, estudiante_id,
                  numero_estudiantes, sala_id, titulo_practica, observaciones))
            conn.commit()

            # Actualizar el estado del equipo a 'EN USO'
            self.inventory_model.update_equipment_status(equipo_codigo, 'EN USO')
            
            return cursor.lastrowid 
        except sqlite3.Error as e:
            print(f"Error adding student equipment loan: {e}")
            return None
        finally:
            conn.close()

    def add_loan_professor(self, fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id,
                           profesor_id, sala_id, titulo_practica, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Verificar si el equipo está disponible
            if not self.inventory_model.check_equipment_availability(equipo_codigo):
                return None

            # Estado: 1 for "En prestamo"
            cursor.execute('''
                INSERT INTO prestamos_equipos_profesores
                (fecha_entrega, equipo_codigo, laboratorista_entrega, monitor_entrega, profesor_id,
                 sala_id, titulo_practica, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            ''', (fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id, profesor_id,
                  sala_id, titulo_practica, observaciones))
            conn.commit()

            # Actualizar el estado del equipo a 'EN USO'
            self.inventory_model.update_equipment_status(equipo_codigo, 'EN USO')
            
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding professor equipment loan: {e}")
            return None
        finally:
            conn.close()

    def get_equipment_loans(self, date_filter=None): # YYYY-MM-DD
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        base_query_student = '''
            SELECT pee.id, 'Estudiante' as tipo_usuario, e.nombre as usuario_nombre, inv.descripcion as equipo_desc,
                   pee.fecha_entrega, pee.fecha_devolucion, 
                   pl_ent.nombre as laboratorista_entrega, pm_ent.nombre as monitor_entrega,
                   pl_dev.nombre as laboratorista_devolucion, pm_dev.nombre as monitor_devolucion,
                   pee.titulo_practica, CASE pee.estado WHEN 1 THEN 'En Préstamo' ELSE 'Devuelto' END as estado_prestamo,
                   pee.observaciones, pee.estudiante_id as usuario_id, 'student' as loan_type, pee.equipo_codigo
            FROM prestamos_equipos_estudiantes pee
            JOIN estudiantes e ON pee.estudiante_id = e.codigo
            JOIN inventario inv ON pee.equipo_codigo = inv.codigo
            LEFT JOIN personal_laboratorio pl_ent ON pee.laboratorista_entrega = pl_ent.id
            LEFT JOIN personal_laboratorio pm_ent ON pee.monitor_entrega = pm_ent.id
            LEFT JOIN personal_laboratorio pl_dev ON pee.laboratorista_devolucion = pl_dev.id
            LEFT JOIN personal_laboratorio pm_dev ON pee.monitor_devolucion = pm_dev.id
        '''
        base_query_professor = '''
            SELECT pep.id, 'Profesor' as tipo_usuario, p.nombre as usuario_nombre, inv.descripcion as equipo_desc,
                   pep.fecha_entrega, pep.fecha_devolucion,
                   pl_ent.nombre as laboratorista_entrega, pm_ent.nombre as monitor_entrega,
                   pl_dev.nombre as laboratorista_devolucion, pm_dev.nombre as monitor_devolucion,
                   pep.titulo_practica, CASE pep.estado WHEN 1 THEN 'En Préstamo' ELSE 'Devuelto' END as estado_prestamo,
                   pep.observaciones, pep.profesor_id as usuario_id, 'professor' as loan_type, pep.equipo_codigo
            FROM prestamos_equipos_profesores pep
            JOIN profesores p ON pep.profesor_id = p.cedula
            JOIN inventario inv ON pep.equipo_codigo = inv.codigo
            LEFT JOIN personal_laboratorio pl_ent ON pep.laboratorista_entrega = pl_ent.id
            LEFT JOIN personal_laboratorio pm_ent ON pep.monitor_entrega = pm_ent.id
            LEFT JOIN personal_laboratorio pl_dev ON pep.laboratorista_devolucion = pl_dev.id
            LEFT JOIN personal_laboratorio pm_dev ON pep.monitor_devolucion = pm_dev.id
        '''
        params = []
        if date_filter:
            date_condition = " WHERE DATE(fecha_entrega) = ?" # Filter by delivery date
            base_query_student += date_condition
            base_query_professor += date_condition
            params.extend([date_filter, date_filter])
            
        query = f"({base_query_student}) UNION ALL ({base_query_professor}) ORDER BY fecha_entrega DESC"
        
        cursor.execute(query, params)
        loans = cursor.fetchall()
        conn.close()
        return loans

    def get_equipment_loan_details(self, loan_id, loan_type):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        if loan_type == 'student':
            cursor.execute('''
                SELECT id, fecha_entrega, fecha_devolucion, equipo_codigo, laboratorista_entrega, monitor_entrega,
                       estudiante_id, numero_estudiantes, sala_id, titulo_practica, estado, 
                       laboratorista_devolucion, monitor_devolucion, observaciones
                FROM prestamos_equipos_estudiantes WHERE id = ?
            ''', (loan_id,))
        elif loan_type == 'professor':
            cursor.execute('''
                SELECT id, fecha_entrega, fecha_devolucion, equipo_codigo, laboratorista_entrega, monitor_entrega,
                       profesor_id, sala_id, titulo_practica, estado,
                       laboratorista_devolucion, monitor_devolucion, observaciones
                FROM prestamos_equipos_profesores WHERE id = ?
            ''', (loan_id,))
        else:
            conn.close()
            return None
        details = cursor.fetchone()
        conn.close()
        return details

    def update_equipment_loan_return(self, loan_id, loan_type, fecha_devolucion, laboratorista_devolucion_id,
                                     monitor_devolucion_id, observaciones, documento_devolvente=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Primero obtenemos el código del equipo
            if loan_type == 'student':
                cursor.execute('SELECT equipo_codigo FROM prestamos_equipos_estudiantes WHERE id = ?', (loan_id,))
            else:
                cursor.execute('SELECT equipo_codigo FROM prestamos_equipos_profesores WHERE id = ?', (loan_id,))
            
            equipo_codigo = cursor.fetchone()[0]

            # Estado: 0 for "Devuelto"
            if loan_type == 'student':
                cursor.execute('''
                    UPDATE prestamos_equipos_estudiantes
                    SET fecha_devolucion = ?, laboratorista_devolucion = ?, monitor_devolucion = ?,
                        estado = 0, observaciones = ?, documento_devolvente = ?
                    WHERE id = ?
                ''', (fecha_devolucion, laboratorista_devolucion_id, monitor_devolucion_id,
                      observaciones, documento_devolvente, loan_id))
            elif loan_type == 'professor':
                cursor.execute('''
                    UPDATE prestamos_equipos_profesores
                    SET fecha_devolucion = ?, laboratorista_devolucion = ?, monitor_devolucion = ?,
                        estado = 0, observaciones = ?, documento_devolvente = ?
                    WHERE id = ?
                ''', (fecha_devolucion, laboratorista_devolucion_id, monitor_devolucion_id,
                      observaciones, documento_devolvente, loan_id))
            else:
                return False

            conn.commit()

            # Actualizar el estado del equipo a 'DISPONIBLE'
            self.inventory_model.update_equipment_status(equipo_codigo, 'DISPONIBLE')
            
            return True
        except sqlite3.Error as e:
            print(f"Error updating equipment loan return: {e}")
            return False
        finally:
            conn.close()
