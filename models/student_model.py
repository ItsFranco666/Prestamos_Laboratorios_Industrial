from database import create_connection

class StudentModel:
    def __init__(self):
        self.conn = create_connection()
    
    def get_students(self, project_id=None):
        cur = self.conn.cursor()
        query = "SELECT * FROM estudiantes"
        params = ()
        if project_id:
            query += " WHERE proyecto_curricular_id = ?"
            params = (project_id,)
        cur.execute(query, params)
        return cur.fetchall()
    
    def add_student(self, code, name, cedula, project_id):
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO estudiantes VALUES (?, ?, ?, ?)",
                        (code, name, cedula, project_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding student: {e}")
            return False