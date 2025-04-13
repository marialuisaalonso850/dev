from db import conectar_db, cerrar_db

class Resultado:
    def __init__(self, paciente_id, descripcion, fecha):
        self.paciente_id = paciente_id
        self.descripcion = descripcion
        self.fecha = fecha

    @staticmethod
    def ingresar_resultado(paciente_id, descripcion, fecha):
        conn, cursor = conectar_db()
        cursor.execute("""
            INSERT INTO resultados (paciente_id, descripcion, fecha)
            VALUES (?, ?, ?)
        """, (paciente_id, descripcion, fecha))
        conn.commit()
        cerrar_db(conn)
