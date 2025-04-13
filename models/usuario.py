import sqlite3
from db import conectar_db, cerrar_db
from fastapi import HTTPException

class Usuario:
    def __init__(self, id, nombre, correo, rol):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.rol = rol

    @staticmethod
    def registrar(correo, nombre, contrasena, cedula, rol):
        # Verificar si el correo ya está registrado
        conn, cursor = conectar_db()
        cursor.execute("""SELECT id FROM usuarios WHERE correo = ?""", (correo,))
        existing_user = cursor.fetchone()

        if existing_user:
            cerrar_db(conn)
            raise HTTPException(status_code=400, detail="El correo ya está registrado.")
        
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
            WHERE correo = ? AND contrasena = ?
        """, (correo, contrasena))
        usuario = cursor.fetchone()
        
        if usuario:
            # Devolver el usuario encontrado
            return Usuario(usuario[0], usuario[1], correo, usuario[2])
        else:
            cerrar_db(conn)
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
        
        cerrar_db(conn)
