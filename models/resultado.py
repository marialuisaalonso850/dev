from db import conectar_db, cerrar_db
from datetime import datetime
from fastapi import HTTPException

class Resultado:
    def __init__(self, paciente_id, descripcion, fecha):
        self.paciente_id = paciente_id
        self.descripcion = descripcion
        self.fecha = fecha

    @staticmethod
    def ingresar_resultado(paciente_id, descripcion, fecha):
        # Validar si el paciente existe
        conn, cursor = conectar_db()
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        paciente = cursor.fetchone()

        if not paciente:
            cerrar_db(conn)
            raise HTTPException(status_code=404, detail="Paciente no encontrado.")

        # Insertar el resultado en la base de datos
        cursor.execute("""
            INSERT INTO resultados (paciente_id, descripcion, fecha)
            VALUES (?, ?, ?)
        """, (paciente_id, descripcion, fecha))
        conn.commit()
        cerrar_db(conn)

