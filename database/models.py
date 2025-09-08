import sqlite3
from .connection import DatabaseManager

class StudentModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    # Lists all the students
    def get_all_students(self, search_term='', project_filter_name=''):
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
            query += ' AND pc.nombre = ?'
            params.append(project_filter_name)

        query += ' ORDER BY e.nombre ASC'
        cursor.execute(query, params)
        students = cursor.fetchall()
        conn.close()
        return students

    # A student can be located by code or id
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
            print(f'Error adding student: {e}')
            return False
        finally:
            conn.close()

    # Insert a student with code but no data, when a code is no found in a loan
    def add_blank_student(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO estudiantes (codigo, nombre, cedula, proyecto_curricular_id)
                VALUES (?, NULL, NULL, NULL)
            ''', (codigo,))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error adding blank student: {e}')
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
            print(f'Error updating student: {e}')
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
            print(f'Error deleting student: {e}') # Handle potential foreign key constraints if student has loans
        finally:
            conn.close()
    
    def get_curriculum_projects(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM proyectos_curriculares ORDER BY nombre ASC')
        projects = cursor.fetchall()
        conn.close()
        return projects

class ProfesorModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_profesores(self, search_term='', project_filter_name=''):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.cedula, p.nombre, pc.nombre as proyecto_nombre
            FROM profesores p
            LEFT JOIN proyectos_curriculares pc ON p.proyecto_curricular_id = pc.id
            WHERE (CAST(p.cedula AS TEXT) LIKE ? OR p.nombre LIKE ?)
        '''
        # Cedula is primary key, usually not searched with LIKE unless its a partial string search
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if project_filter_name:
            query += ' AND pc.nombre = ?'
            params.append(project_filter_name)
        
        query += ' ORDER BY p.nombre ASC'
        cursor.execute(query, params)
        profesores = cursor.fetchall()
        conn.close()
        return profesores

    def get_professor_by_id(self, cedula):
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
            print(f'Error adding professor: {e}')
            return False
        finally:
            conn.close()
    
    # Adds a professor with only the ID number. Other fields are null.
    def add_blank_profesor(self, cedula):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO profesores (cedula, nombre, proyecto_curricular_id)
                VALUES (?, NULL, NULL)
            ''', (cedula,))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error adding blank professor: {e}')
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
            print(f'Error updating professor: {e}')
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
            print(f'Error deleting professor: {e}')
        finally:
            conn.close()
    
    def get_curriculum_projects(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM proyectos_curriculares ORDER BY nombre ASC')
        projects = cursor.fetchall()
        conn.close()
        return projects

class RoomModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    # Lists if a room is occupied or available depending to loans
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
    
    ''' When a student asks for a room, it ill be ocuppied but available for another
        loan, but for a professor the occupied ones will not be displayed '''
    def get_available_rooms_for_dropdown(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.nombre
            FROM salas s
            WHERE NOT EXISTS (
                SELECT 1 FROM prestamos_salas_profesores psp
                WHERE psp.sala_id = s.id AND psp.hora_salida IS NULL
            ) AND NOT EXISTS (
                SELECT 1 FROM prestamos_salas_estudiantes pse
                WHERE pse.sala_id = s.id AND pse.hora_salida IS NULL
            )
            ORDER BY s.nombre ASC
        ''')
        rooms = cursor.fetchall()
        conn.close()
        return rooms
    
    # Fetches all rooms with their ID and name, suitable for foreign key relations
    def get_all_rooms_with_id_for_dropdown(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM salas ORDER BY nombre ASC')
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
            print(f'Error adding room: {e}')
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
            print(f'Error updating room: {e}')
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
            print(f'Error deleting room: {e}')
        finally:
            conn.close()

class InventoryModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    # Filters by status and serial
    def get_all_equipment(self, search_term='', status_filter='', brand_serial_filter=''):
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
            query += ' AND i.estado = ?'
            params.append(status_filter)
        if brand_serial_filter:
            query += ' AND i.marca_serie LIKE ?'
            params.append(f'%{brand_serial_filter}%')

        query += ' ORDER BY i.codigo ASC'
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
            print(f'Error adding equipment: {e}')
            return False
        finally:
            conn.close()
    
    # Adds an equipment with only the code and a 'DISPONIBLE' status
    def add_blank_equipment(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO inventario 
                (codigo, marca_serie, documento_funcionario, nombre_funcionario, 
                descripcion, contenido, estado, sede_id)
                VALUES (?, NULL, NULL, NULL, 'Nuevo equipo (detalles pendientes)', NULL, 'DISPONIBLE', NULL)
            ''', (codigo,))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error adding blank equipment: {e}')
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
            print(f'Error updating equipment: {e}')
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
            print(f'Error deleting equipment: {e}')
        finally:
            conn.close()

    # Fetches equipment thats available
    def get_available_equipment_for_dropdown(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT codigo, descripcion || " (" || estado || ")" FROM inventario WHERE estado = "DISPONIBLE" ORDER BY codigo ASC')
        equipment = cursor.fetchall()
        conn.close()
        return equipment

    # Fetches equipment regardless of the state
    def get_all_equipment_for_dropdown(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT codigo, descripcion || " (" || estado || ")" FROM inventario ORDER BY codigo ASC')
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

    # Checks if a equipmment is available for loan
    def check_equipment_availability(self, equipo_codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT estado FROM inventario WHERE codigo = ?', (equipo_codigo,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 'DISPONIBLE'

    def update_equipment_status(self, equipo_codigo, nuevo_estado):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE inventario SET estado = ? WHERE codigo = ?', (nuevo_estado, equipo_codigo))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error updating equipment status: {e}')
            return False
        finally:
            conn.close()

class PersonalLaboratorioModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    # Retrieves all staff with text-based roles for exporting
    def get_all_personal_for_export(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT id, nombre, 
                CASE cargo 
                    WHEN 0 THEN 'Laboratorista' 
                    ELSE 'Monitor' 
                END as cargo
            FROM personal_laboratorio 
            ORDER BY nombre ASC
        '''
        cursor.execute(query)
        personal = cursor.fetchall()
        conn.close()
        return personal
    
    def get_cargos(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre, CASE cargo WHEN 0 THEN "Laboratorista" ELSE "Monitor" END as cargo_nombre FROM personal_laboratorio ORDER BY nombre ASC')
        personal = cursor.fetchall()
        conn.close()
        return personal

    def get_all_personal(self, search_term='', cargo_filter_name=''):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, nombre, cargo
            FROM personal_laboratorio 
            WHERE (CAST(id AS TEXT) LIKE ? OR nombre LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if cargo_filter_name and cargo_filter_name != 'Todos':
            query += ' AND CASE cargo WHEN 0 THEN "Laboratorista" ELSE "Monitor" END = ?'
            params.append(cargo_filter_name)
        
        query += ' ORDER BY nombre ASC'
        cursor.execute(query, params)
        personal = cursor.fetchall()
        conn.close()
        return personal

    def add_personal(self, nombre, cargo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO personal_laboratorio (nombre, cargo) VALUES (?, ?)', (nombre, cargo))
            conn.commit()
            return True
        except Exception as e:
            print(f'Error adding personal: {e}')
            return False
        finally:
            conn.close()

    def update_personal(self, id, nombre, cargo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE personal_laboratorio SET nombre = ?, cargo = ? WHERE id = ?', (nombre, cargo, id))
            conn.commit()
            return True
        except Exception as e:
            print(f'Error updating personal: {e}')
            return False
        finally:
            conn.close()

    def delete_personal(self, id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM personal_laboratorio WHERE id = ?', (id,))
            conn.commit()
            return True
        except Exception as e:
            print(f'Error deleting personal: {e}')
            return False
        finally:
            conn.close()

    def get_laboratoristas(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM personal_laboratorio WHERE cargo = 0 ORDER BY nombre ASC') # 0 for Laboratorista
        personal = cursor.fetchall()
        conn.close()
        return personal

    def get_monitores(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre FROM personal_laboratorio WHERE cargo = 1 ORDER BY nombre ASC') # 1 for Monitor
        personal = cursor.fetchall()
        conn.close()
        return personal

class RoomLoanModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    # Generates a loan for a student
    def add_loan_student(self, fecha_entrada, laboratorista_id, monitor_id, sala_id, estudiante_id, equipo_codigo, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO prestamos_salas_estudiantes 
                (fecha_entrada, laboratorista, monitor, sala_id, estudiante_id, equipo_codigo, novedad)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_entrada, laboratorista_id, monitor_id, sala_id, estudiante_id, equipo_codigo, observaciones))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f'Error adding student room loan: {e}')
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
            print(f'Error adding professor room loan: {e}')
            return None
        finally:
            conn.close()

    ''' Fetches all room loans with comprehensive filtering capabilities.
    - sala_filter_id: Filters by a specific room ID. '''
    def get_room_loans(self, search_term='', user_type_filter='Todos', status_filter='Todos', date_filter=None, sala_filter_id=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        student_query = '''
            SELECT pse.id, 'Estudiante' as tipo_usuario, e.nombre as usuario_nombre, s.nombre as sala_nombre, 
                   pse.fecha_entrada, pse.hora_salida, pl_lab.nombre as laboratorista, pl_mon.nombre as monitor, 
                   pse.novedad as observaciones, pse.estudiante_id as usuario_id, 'student' as loan_type, 
                   eq.numero_equipo,
                   CASE WHEN pse.hora_salida IS NULL THEN 'En Préstamo' ELSE 'Finalizado' END as estado_prestamo,
                   pse.firma_estudiante,
                   pse.equipo_codigo
            FROM prestamos_salas_estudiantes pse
            JOIN estudiantes e ON pse.estudiante_id = e.codigo
            JOIN salas s ON pse.sala_id = s.id
            LEFT JOIN equipos eq ON pse.equipo_codigo = eq.codigo
            LEFT JOIN personal_laboratorio pl_lab ON pse.laboratorista = pl_lab.id
            LEFT JOIN personal_laboratorio pl_mon ON pse.monitor = pl_mon.id
        '''
        professor_query = '''
            SELECT psp.id, 'Profesor' as tipo_usuario, p.nombre as usuario_nombre, s.nombre as sala_nombre,
                   psp.fecha_entrada, psp.hora_salida, pl_lab.nombre as laboratorista, pl_mon.nombre as monitor, 
                   psp.observaciones, psp.profesor_id as usuario_id, 'professor' as loan_type, 
                   NULL as numero_equipo,
                   CASE WHEN psp.hora_salida IS NULL THEN 'En Préstamo' ELSE 'Finalizado' END as estado_prestamo,
                   psp.firma_profesor,
                   NULL as equipo_codigo
            FROM prestamos_salas_profesores psp
            JOIN profesores p ON psp.profesor_id = p.cedula
            JOIN salas s ON psp.sala_id = s.id
            LEFT JOIN personal_laboratorio pl_lab ON psp.laboratorista = pl_lab.id
            LEFT JOIN personal_laboratorio pl_mon ON psp.monitor = pl_mon.id
        '''

        student_where = []
        professor_where = []
        student_params = []
        professor_params = []

        if search_term:
            search_like = f'%{search_term}%'
            student_where.append('(e.nombre LIKE ? OR CAST(e.cedula AS TEXT) LIKE ? OR CAST(e.codigo AS TEXT) LIKE ? OR s.nombre LIKE ? OR CAST(eq.numero_equipo AS TEXT) LIKE ? OR pse.equipo_codigo LIKE ?)')
            professor_where.append('(p.nombre LIKE ? OR CAST(p.cedula AS TEXT) LIKE ? OR s.nombre LIKE ?)')
            student_params.extend([search_like, search_like, search_like, search_like, search_like, search_like])
            professor_params.extend([search_like, search_like, search_like])

        status_map = {'En Préstamo': 'IS NULL', 'Finalizado': 'IS NOT NULL'}
        if status_filter in status_map:
            student_where.append(f'pse.hora_salida {status_map[status_filter]}')
            professor_where.append(f'psp.hora_salida {status_map[status_filter]}')
        
        if date_filter:
            student_where.append('DATE(pse.fecha_entrada) = ?')
            professor_where.append('DATE(psp.fecha_entrada) = ?')
            student_params.append(date_filter)
            professor_params.append(date_filter)

        if sala_filter_id:
            student_where.append('pse.sala_id = ?')
            professor_where.append('psp.sala_id = ?')
            student_params.append(sala_filter_id)
            professor_params.append(sala_filter_id)

        if student_where:
            student_query += ' WHERE ' + ' AND '.join(student_where)
        if professor_where:
            professor_query += ' WHERE ' + ' AND '.join(professor_where)

        queries_to_run = []
        if user_type_filter == 'Estudiante':
            queries_to_run.append((student_query, student_params))
        elif user_type_filter == 'Profesor':
            queries_to_run.append((professor_query, professor_params))
        else: # 'Todos'
            queries_to_run.append((student_query, student_params))
            queries_to_run.append((professor_query, professor_params))

        all_loans = []
        for query, params in queries_to_run:
            try:
                cursor.execute(query, params)
                all_loans.extend(cursor.fetchall())
            except sqlite3.Error as e:
                print(f'Database error on room loan fetch: {e}')

        conn.close()
        all_loans.sort(key=lambda x: x[4], reverse=True) # Sort by fecha_entrada DESC
        return all_loans

    # Fetches a specific room loan
    def get_room_loan_details(self, loan_id, loan_type):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        if loan_type == 'student':
            cursor.execute('''
                SELECT pse.id, pse.fecha_entrada, pse.laboratorista, pse.monitor, pse.sala_id,
                       pse.estudiante_id, pse.hora_salida, pse.equipo_codigo, eq.numero_equipo,
                       pse.firma_estudiante, pse.novedad
                FROM prestamos_salas_estudiantes pse
                LEFT JOIN equipos eq ON pse.equipo_codigo = eq.codigo
                WHERE pse.id = ?
            ''', (loan_id,))
        elif loan_type == 'professor':
            cursor.execute('''
                SELECT id, fecha_entrada, laboratorista, monitor, sala_id, profesor_id, hora_salida, firma_profesor, observaciones 
                FROM prestamos_salas_profesores WHERE id = ?
            ''', (loan_id,))
        else:
            conn.close()
            return None
        details = cursor.fetchone()
        conn.close()
        return details

    # Method to close a loan when its returned
    def update_room_loan_exit(self, loan_id, loan_type, hora_salida, observaciones, firma=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if loan_type == 'student':
                cursor.execute('''
                    UPDATE prestamos_salas_estudiantes
                    SET hora_salida = ?, novedad = ?, firma_estudiante = ?
                    WHERE id = ?
                ''', (hora_salida, observaciones, firma, loan_id))
            elif loan_type == 'professor':
                 cursor.execute('''
                    UPDATE prestamos_salas_profesores
                    SET hora_salida = ?, observaciones = ?, firma_profesor = ?
                    WHERE id = ?
                ''', (hora_salida, observaciones, firma, loan_id))
            else:
                return False
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error updating room loan exit: {e}')
            return False
        finally:
            conn.close()

    def update_room_loan(self, loan_id, loan_type, update_data):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        table_name = 'prestamos_salas_estudiantes' if loan_type == 'student' else 'prestamos_salas_profesores'
        
        # Map generic 'usuario_id' to the correct DB column name
        if 'usuario_id' in update_data:
            if loan_type == 'student':
                update_data['estudiante_id'] = update_data.pop('usuario_id')
            else: # professor
                update_data['profesor_id'] = update_data.pop('usuario_id')
        
        if not update_data:
            return True # No changes to save

        set_clause = ', '.join([f'{key} = ?' for key in update_data.keys()])
        params = list(update_data.values())
        params.append(loan_id)
        
        query = f'UPDATE {table_name} SET {set_clause} WHERE id = ?'
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error updating room loan: {e}')
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_loan(self, loan_id, loan_type):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        table_name = 'prestamos_salas_estudiantes' if loan_type == 'student' else 'prestamos_salas_profesores'
        try:
            cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (loan_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error deleting room loan: {e}')
            conn.rollback()
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
            # Checks if the equipment is available
            if not self.inventory_model.check_equipment_availability(equipo_codigo):
                return None

            # State: 1 for 'En prestamo'
            cursor.execute('''
                INSERT INTO prestamos_equipos_estudiantes
                (fecha_entrega, equipo_codigo, laboratorista_entrega, monitor_entrega, estudiante_id,
                 numero_estudiantes, sala_id, titulo_practica, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?) 
            ''', (fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id, estudiante_id,
                  numero_estudiantes, sala_id, titulo_practica, observaciones))
            conn.commit()

            # Update to 'EN USO'
            self.inventory_model.update_equipment_status(equipo_codigo, 'EN USO')
            
            return cursor.lastrowid 
        except sqlite3.Error as e:
            print(f'Error adding student equipment loan: {e}')
            return None
        finally:
            conn.close()

    def add_loan_professor(self, fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id,
                           profesor_id, sala_id, titulo_practica, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Checks if the equipment is available
            if not self.inventory_model.check_equipment_availability(equipo_codigo):
                return None

            # State: 1 for 'En prestamo'
            cursor.execute('''
                INSERT INTO prestamos_equipos_profesores
                (fecha_entrega, equipo_codigo, laboratorista_entrega, monitor_entrega, profesor_id,
                 sala_id, titulo_practica, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            ''', (fecha_entrega, equipo_codigo, laboratorista_entrega_id, monitor_entrega_id, profesor_id,
                  sala_id, titulo_practica, observaciones))
            conn.commit()

            # Update to 'EN USO'
            self.inventory_model.update_equipment_status(equipo_codigo, 'EN USO')
            
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f'Error adding professor equipment loan: {e}')
            return None
        finally:
            conn.close()

    def get_equipment_loans(self, search_term='', user_type_filter='Todos', status_filter='Todos'):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        queries = []
        
        # Base student query with all necessary joins
        student_base_query = '''
            SELECT pee.id, 'Estudiante' as tipo_usuario, e.nombre as usuario_nombre, inv.descripcion as equipo_desc,
                   pee.fecha_entrega, pee.fecha_devolucion, 
                   pl_ent.nombre as laboratorista_entrega, pm_ent.nombre as monitor_entrega,
                   pl_dev.nombre as laboratorista_devolucion, pm_dev.nombre as monitor_devolucion,
                   pee.titulo_practica, CASE pee.estado WHEN 1 THEN 'En Préstamo' ELSE 'Devuelto' END as estado_prestamo,
                   pee.observaciones, pee.estudiante_id as usuario_id, 'student' as loan_type, pee.equipo_codigo, pee.sala_id,
                   pee.documento_devolvente as firma
            FROM prestamos_equipos_estudiantes pee
            JOIN estudiantes e ON pee.estudiante_id = e.codigo
            JOIN inventario inv ON pee.equipo_codigo = inv.codigo
            LEFT JOIN personal_laboratorio pl_ent ON pee.laboratorista_entrega = pl_ent.id
            LEFT JOIN personal_laboratorio pm_ent ON pee.monitor_entrega = pm_ent.id
            LEFT JOIN personal_laboratorio pl_dev ON pee.laboratorista_devolucion = pl_dev.id
            LEFT JOIN personal_laboratorio pm_dev ON pee.monitor_devolucion = pm_dev.id
        '''
        
        # Base professor query with all necessary joins
        professor_base_query = '''
            SELECT pep.id, 'Profesor' as tipo_usuario, p.nombre as usuario_nombre, inv.descripcion as equipo_desc,
                   pep.fecha_entrega, pep.fecha_devolucion,
                   pl_ent.nombre as laboratorista_entrega, pm_ent.nombre as monitor_entrega,
                   pl_dev.nombre as laboratorista_devolucion, pm_dev.nombre as monitor_devolucion,
                   pep.titulo_practica, CASE pep.estado WHEN 1 THEN 'En Préstamo' ELSE 'Devuelto' END as estado_prestamo,
                   pep.observaciones, pep.profesor_id as usuario_id, 'professor' as loan_type, pep.equipo_codigo, pep.sala_id,
                   pep.documento_devolvente as firma
            FROM prestamos_equipos_profesores pep
            JOIN profesores p ON pep.profesor_id = p.cedula
            JOIN inventario inv ON pep.equipo_codigo = inv.codigo
            LEFT JOIN personal_laboratorio pl_ent ON pep.laboratorista_entrega = pl_ent.id
            LEFT JOIN personal_laboratorio pm_ent ON pep.monitor_entrega = pm_ent.id
            LEFT JOIN personal_laboratorio pl_dev ON pep.laboratorista_devolucion = pl_dev.id
            LEFT JOIN personal_laboratorio pm_dev ON pep.monitor_devolucion = pm_dev.id
        '''
        
        # Dynamically build WHERE clauses based on filters
        student_where_clauses = []
        professor_where_clauses = []
        student_params = []
        professor_params = []

        if search_term:
            search_like = f'%{search_term}%'
            student_where_clauses.append('(e.nombre LIKE ? OR CAST(e.cedula AS TEXT) LIKE ? OR CAST(e.codigo AS TEXT) LIKE ? OR inv.descripcion LIKE ? OR inv.codigo LIKE ? OR pee.titulo_practica LIKE ?)')
            professor_where_clauses.append('(p.nombre LIKE ? OR CAST(p.cedula AS TEXT) LIKE ? OR inv.descripcion LIKE ? OR inv.codigo LIKE ? OR pep.titulo_practica LIKE ?)')
            student_params.extend([search_like, search_like, search_like, search_like, search_like, search_like])
            professor_params.extend([search_like, search_like, search_like, search_like, search_like])

        status_map = {'En Préstamo': 1, 'Devuelto': 0}
        if status_filter in status_map:
            status_val = status_map[status_filter]
            student_where_clauses.append('pee.estado = ?')
            professor_where_clauses.append('pep.estado = ?')
            student_params.append(status_val)
            professor_params.append(status_val)
        
        # Construct the final queries with WHERE clauses if they exist
        student_query = student_base_query
        if student_where_clauses:
            student_query += ' WHERE ' + ' AND '.join(student_where_clauses)

        professor_query = professor_base_query
        if professor_where_clauses:
            professor_query += ' WHERE ' + ' AND '.join(professor_where_clauses)
            
        # Decide which queries to execute based on the user type filter
        if user_type_filter == 'Estudiante':
            queries.append((student_query, student_params))
        elif user_type_filter == 'Profesor':
            queries.append((professor_query, professor_params))
        else:  # 'Todos'
            queries.append((student_query, student_params))
            queries.append((professor_query, professor_params))

        all_loans = []
        for query, param_list in queries:
            try:
                cursor.execute(query, param_list)
                all_loans.extend(cursor.fetchall())
            except sqlite3.Error as e:
                print(f'Database error: {e}')
                print(f'Query: {query}')
                print(f'Params: {param_list}')
                
        conn.close()
        
        # Sort the combined results in Python by delivery date
        all_loans.sort(key=lambda x: x[4] if x[4] else '', reverse=True)
        
        return all_loans

    def get_equipment_loan_details(self, loan_id, loan_type):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        details = None
        if loan_type == 'student':
            cursor.execute('''
                SELECT id, fecha_entrega, fecha_devolucion, equipo_codigo, laboratorista_entrega, monitor_entrega,
                       estudiante_id, numero_estudiantes, sala_id, titulo_practica, estado, 
                       laboratorista_devolucion, monitor_devolucion, documento_devolvente, observaciones
                FROM prestamos_equipos_estudiantes WHERE id = ?
            ''', (loan_id,))
            details = cursor.fetchone()
        elif loan_type == 'professor':
            # For nunmber of students it is added a NULL placeholder to maintain consistency in the indexes
            cursor.execute('''
                SELECT id, fecha_entrega, fecha_devolucion, equipo_codigo, laboratorista_entrega, monitor_entrega,
                       profesor_id, NULL as numero_estudiantes, sala_id, titulo_practica, estado,
                       laboratorista_devolucion, monitor_devolucion, documento_devolvente, observaciones
                FROM prestamos_equipos_profesores WHERE id = ?
            ''', (loan_id,))
            details = cursor.fetchone()

        conn.close()
        return details
    
    def update_equipment_loan(self, loan_id, loan_type, update_data):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        table_name = 'prestamos_equipos_estudiantes' if loan_type == 'student' else 'prestamos_equipos_profesores'
        
        # Fetch 'usuario_id' to the correct column name in the DB
        if 'usuario_id' in update_data:
            if loan_type == 'student':
                update_data['estudiante_id'] = update_data.pop('usuario_id')
            else: # professor
                update_data['profesor_id'] = update_data.pop('usuario_id')

        if not update_data:
            return True # No data to update

        set_clause = ', '.join([f'{key} = ?' for key in update_data.keys()])
        params = list(update_data.values())
        params.append(loan_id)
        
        query = f'UPDATE {table_name} SET {set_clause} WHERE id = ?'
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error updating equipment loan: {e}')
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def delete_loan(self, loan_id, loan_type):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        table_name = 'prestamos_equipos_estudiantes' if loan_type == 'student' else 'prestamos_equipos_profesores'
        
        try:
            # Obtain the code and state of the equipment BEFORE deleting the loan
            loan_info = self._get_equipment_code_for_loan(cursor, loan_id, loan_type)
            if not loan_info:
                return False # If loan doesnt exist

            equipo_codigo, estado_prestamo = loan_info

            cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (loan_id,))
            conn.commit()

            # Free the equipment if the loan was active
            if estado_prestamo == 1: # 1 is 'En Préstamo'
                self.inventory_model.update_equipment_status(equipo_codigo, 'DISPONIBLE')

            return True
        except sqlite3.Error as e:
            print(f'Error deleting equipment loan: {e}')
            conn.rollback() # Revert changes
            return False
        finally:
            conn.close()

    def _get_equipment_code_for_loan(self, cursor, loan_id, loan_type):
        table_name = 'prestamos_equipos_estudiantes' if loan_type == 'student' else 'prestamos_equipos_profesores'
        cursor.execute(f'SELECT equipo_codigo, estado FROM {table_name} WHERE id = ?', (loan_id,))
        return cursor.fetchone()
    
    def update_equipment_loan_return(self, loan_id, loan_type, fecha_devolucion, laboratorista_devolucion_id,
                                     monitor_devolucion_id, observaciones, documento_devolvente=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Retrieve equipment code
            if loan_type == 'student':
                cursor.execute('SELECT equipo_codigo FROM prestamos_equipos_estudiantes WHERE id = ?', (loan_id,))
            else:
                cursor.execute('SELECT equipo_codigo FROM prestamos_equipos_profesores WHERE id = ?', (loan_id,))
            
            equipo_codigo = cursor.fetchone()[0]

            # State: 0 for 'Devuelto'
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

            # Update to 'DISPONIBLE'
            self.inventory_model.update_equipment_status(equipo_codigo, 'DISPONIBLE')
            
            return True
        except sqlite3.Error as e:
            print(f'Error updating equipment loan return: {e}')
            return False
        finally:
            conn.close()

class EquiposModel:
    ''' Manages database operations for the 'equipos' table, which represents
    equipment located within specific rooms (salas) '''
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    # Retrieves all room equipment with text-based status for exporting
    def get_all_equipos_for_export(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT e.codigo, s.nombre as sala_nombre, e.numero_equipo,
                e.descripcion, 
                CASE e.estado 
                    WHEN 0 THEN 'En Mantenimiento' 
                    ELSE 'Operativo' 
                END as estado, 
                e.observaciones
            FROM equipos e
            LEFT JOIN salas s ON e.sala_id = s.id
            ORDER BY s.nombre, e.numero_equipo ASC
        '''
        cursor.execute(query)
        equipos = cursor.fetchall()
        conn.close()
        return equipos

    # Room devices with filters & status
    def get_all_equipos(self, search_term='', sala_filter_id=None, status_filter=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT e.codigo, s.nombre as sala_nombre, e.numero_equipo,
                   e.descripcion, e.estado, e.observaciones
            FROM equipos e
            LEFT JOIN salas s ON e.sala_id = s.id
            WHERE (e.codigo LIKE ? OR e.descripcion LIKE ?)
        '''
        params = [f'%{search_term}%', f'%{search_term}%']
        
        if sala_filter_id:
            query += ' AND e.sala_id = ?'
            params.append(sala_filter_id)
        
        if status_filter is not None and status_filter != -1: # -1 for 'Todos'
            query += ' AND e.estado = ?'
            params.append(status_filter)

        query += ' ORDER BY s.nombre, e.numero_equipo ASC'
        cursor.execute(query, params)
        equipos = cursor.fetchall()
        conn.close()
        return equipos

    # Equipment by just code (for loan)
    def get_equipo_by_code(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT codigo, sala_id, numero_equipo, descripcion, estado, observaciones
            FROM equipos WHERE codigo = ?
        ''', (codigo,))
        item = cursor.fetchone()
        conn.close()
        return item

    # Equipment by room & code or number (for table filter)
    def get_equipo_by_identifier(self, sala_id, codigo=None, numero_equipo=None):
        if not codigo and (numero_equipo is None):
            return None
            
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT codigo, sala_id, numero_equipo, descripcion, estado, observaciones FROM equipos WHERE '
        params = []

        if codigo:
            query += 'codigo = ?'
            params.append(codigo)
        elif numero_equipo is not None and sala_id:
            query += 'numero_equipo = ? AND sala_id = ?'
            params.extend([numero_equipo, sala_id])
        else:
            conn.close()
            return None

        cursor.execute(query, tuple(params))
        item = cursor.fetchone()
        conn.close()
        return item

    def add_equipo(self, codigo, sala_id, numero_equipo, descripcion, estado, observaciones):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO equipos (codigo, sala_id, numero_equipo, descripcion, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (codigo, sala_id, numero_equipo, descripcion, estado, observaciones))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error adding equipo: {e}')
            return False
        finally:
            conn.close()

    def update_equipo(self, original_codigo, sala_id, numero_equipo, descripcion, estado, observaciones, new_codigo=None): 
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            if new_codigo is None:
                new_codigo = original_codigo
            cursor.execute('''
                UPDATE equipos
                SET codigo = ?, sala_id = ?, numero_equipo = ?, descripcion = ?,
                    estado = ?, observaciones = ?
                WHERE codigo = ?
            ''', (new_codigo, sala_id, numero_equipo, descripcion, estado, observaciones, original_codigo))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error updating equipo: {e}')
            return False
        finally:
            conn.close()

    def delete_equipo(self, codigo):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM equipos WHERE codigo = ?', (codigo,))
            conn.commit()
        except sqlite3.Error as e:
            print(f'Error deleting equipo: {e}') # Handle potential FK constraints
        finally:
            conn.close()

class ProyectosCurricularesModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def get_all_proyectos(self, search_term=''):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, nombre FROM proyectos_curriculares WHERE nombre LIKE ? ORDER BY nombre ASC',
            (f'%{search_term}%',)
        )
        proyectos = cursor.fetchall()
        conn.close()
        return proyectos

    def add_proyecto(self, nombre):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO proyectos_curriculares (nombre) VALUES (?)', (nombre,))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error adding proyecto curricular: {e}')
            return False
        finally:
            conn.close()

    def update_proyecto(self, id, nombre):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE proyectos_curriculares SET nombre = ? WHERE id = ?', (nombre, id))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error updating proyecto curricular: {e}')
            return False
        finally:
            conn.close()

    def delete_proyecto(self, id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Note: This will fail if a student or professor is assigned to this project.
            # This is expected behavior to maintain data integrity.
            cursor.execute('DELETE FROM proyectos_curriculares WHERE id = ?', (id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error deleting proyecto curricular: {e}')
            return False
        finally:
            conn.close()

class SedesModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    # Retrieves all campus locations (sedes), with an optional search filter.
    def get_all_sedes(self, search_term=''):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, nombre FROM sedes WHERE nombre LIKE ? ORDER BY nombre ASC',
            (f'%{search_term}%',)
        )
        sedes = cursor.fetchall()
        conn.close()
        return sedes

    def add_sede(self, nombre):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO sedes (nombre) VALUES (?)', (nombre,))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error adding sede: {e}')
            return False
        finally:
            conn.close()

    def update_sede(self, id, nombre):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE sedes SET nombre = ? WHERE id = ?', (nombre, id))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f'Error updating sede: {e}')
            return False
        finally:
            conn.close()

    def delete_sede(self, id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Note: This will fail if inventory items are assigned to this location (EXPECTED BEHAVIOUR)
            cursor.execute('DELETE FROM sedes WHERE id = ?', (id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f'Error deleting sede: {e}')
            return False
        finally:
            conn.close()

class DashboardModel:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def get_room_metrics(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM salas')
            total_rooms = cursor.fetchone()[0]
            cursor.execute('''
                SELECT COUNT(DISTINCT sala_id) FROM (
                    SELECT sala_id FROM prestamos_salas_profesores 
                    WHERE hora_salida IS NULL
                    UNION
                    SELECT sala_id FROM prestamos_salas_estudiantes 
                    WHERE hora_salida IS NULL
                )
            ''')
            occupied_rooms = cursor.fetchone()[0]
            available_rooms = total_rooms - occupied_rooms
            return {
                'total': total_rooms,
                'occupied': occupied_rooms,
                'available': available_rooms
            }
        finally:
            conn.close()

    def get_equipment_metrics(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM inventario WHERE estado != "DAÑADO"')
            total_equipment = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM inventario WHERE estado = "EN USO"')
            in_use_equipment = cursor.fetchone()[0]
            return {
                'total': total_equipment,
                'in_use': in_use_equipment
            }
        finally:
            conn.close()

    def get_active_loans(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Profesores - equipos
            cursor.execute('''
                SELECT 'Equipo' as type, p.nombre as borrower, i.descripcion as item, 
                       pep.fecha_entrega as date, 'Activo' as status
                FROM prestamos_equipos_profesores pep
                JOIN profesores p ON pep.profesor_id = p.cedula
                JOIN inventario i ON pep.equipo_codigo = i.codigo
                WHERE pep.fecha_devolucion IS NULL
                ORDER BY pep.fecha_entrega DESC
                LIMIT 10
            ''')
            active_loans = cursor.fetchall()

            # Estudiantes - equipos
            cursor.execute('''
                SELECT 'Equipo' as type, e.nombre as borrower, i.descripcion as item, 
                       pee.fecha_entrega as date, 'Activo' as status
                FROM prestamos_equipos_estudiantes pee
                JOIN estudiantes e ON pee.estudiante_id = e.codigo
                JOIN inventario i ON pee.equipo_codigo = i.codigo
                WHERE pee.fecha_devolucion IS NULL
                ORDER BY pee.fecha_entrega DESC
                LIMIT 10
            ''')
            active_loans.extend(cursor.fetchall())

            # Profesores - salas
            cursor.execute('''
                SELECT 'Sala' as type, p.nombre as borrower, s.nombre as item, 
                       psp.fecha_entrada as date, 'Activo' as status
                FROM prestamos_salas_profesores psp
                JOIN profesores p ON psp.profesor_id = p.cedula
                JOIN salas s ON psp.sala_id = s.id
                WHERE psp.hora_salida IS NULL
                ORDER BY psp.fecha_entrada DESC
                LIMIT 10
            ''')
            active_loans.extend(cursor.fetchall())

            # Estudiantes - salas
            cursor.execute('''
                SELECT 'Sala' as type, e.nombre as borrower, s.nombre as item, 
                       pse.fecha_entrada as date, 'Activo' as status
                FROM prestamos_salas_estudiantes pse
                JOIN estudiantes e ON pse.estudiante_id = e.codigo
                JOIN salas s ON pse.sala_id = s.id
                WHERE pse.hora_salida IS NULL
                ORDER BY pse.fecha_entrada DESC
                LIMIT 10
            ''')
            active_loans.extend(cursor.fetchall())

            # Limit to the 10 most recent
            active_loans.sort(key=lambda x: x[3], reverse=True)
            return active_loans[:10]
        finally:
            conn.close()

    def get_alerts(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            # Damaged equipment
            cursor.execute('''
                SELECT codigo, descripcion, estado, marca_serie
                FROM inventario 
                WHERE estado = 'DAÑADO'
                ORDER BY codigo
            ''')
            damaged_equipment = cursor.fetchall()

            # Equipment to review
            cursor.execute('''
                SELECT DISTINCT i.codigo, i.descripcion, 'REVISAR' as estado, pep.observaciones
                FROM prestamos_equipos_profesores pep
                JOIN inventario i ON pep.equipo_codigo = i.codigo
                WHERE pep.observaciones IS NOT NULL 
                AND pep.observaciones != ''
                AND pep.fecha_devolucion IS NOT NULL
                AND pep.fecha_devolucion > datetime('now', '-7 days')
                AND i.estado != 'DAÑADO'
                LIMIT 5
            ''')
            review_equipment = cursor.fetchall()
            return {
                'damaged': damaged_equipment,
                'review': review_equipment
            }
        finally:
            conn.close()