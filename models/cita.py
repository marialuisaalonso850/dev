from db import conectar_db, cerrar_db
from datetime import datetime
from fastapi import HTTPException

class Cita:
    def __init__(self, paciente_id, medico_id, fecha, hora):
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.fecha = fecha
        self.hora = hora

    @staticmethod
    def agendar(paciente_id, medico_id, fecha, hora):
        # Validar formato de fecha y hora
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha incorrecto. Use YYYY-MM-DD.")
        
        try:
            hora_obj = datetime.strptime(hora, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de hora incorrecto. Use HH:MM.")

        # Insertar la cita en la base de datos
        conn, cursor = conectar_db()
        cursor.execute("""
            INSERT INTO citas (paciente_id, medico_id, fecha, hora)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, medico_id, fecha, hora))
        conn.commit()
        cerrar_db(conn)

    @staticmethod
    def consultar_citas():
        conn, cursor = conectar_db()
        cursor.execute("""
            SELECT c.id, p.nombre AS paciente, m.nombre AS medico, c.fecha, c.hora
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN medicos m ON c.medico_id = m.id
        """)
        citas = cursor.fetchall()
        cerrar_db(conn)
        return citas
