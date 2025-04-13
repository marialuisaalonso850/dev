import sqlite3
from db import conectar_db, cerrar_db

class Usuario:
    def __init__(self, id, nombre, correo, rol):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.rol = rol

    @staticmethod
    def registrar(correo, nombre, contrasena, cedula, rol):
        conn, cursor = conectar_db()
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contrasena, cedula, rol)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, correo, contrasena, cedula, rol))
        conn.commit()
        cerrar_db(conn)
    
    @staticmethod
    def iniciar_sesion(correo, contrasena):
        conn, cursor = conectar_db()
        cursor.execute("""
            SELECT id, nombre, rol FROM usuarios
            WHERE correo=? AND contrasena=?
        """, (correo, contrasena))
        usuario = cursor.fetchone()
        cerrar_db(conn)
        return usuario
