import sqlite3

def conectar_db():
    conn = sqlite3.connect('vitalapp2.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Habilitar las restricciones de clave foránea
    return conn, cursor

def cerrar_db(conn):
    conn.close()

def crear_tablas():
    conn, cursor = conectar_db()
    
    # Crear tabla de usuarios (Usuarios pueden ser pacientes o médicos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT CHECK(rol IN ('paciente', 'medico')) NOT NULL
        )
    ''')

    # Crear tabla de pacientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL,
            FOREIGN KEY (id) REFERENCES usuarios(id)
        )
    ''')

    # Crear tabla de médicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            FOREIGN KEY (id) REFERENCES usuarios(id)
        )
    ''')

    # Crear tabla de citas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medico_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (medico_id) REFERENCES medicos(id)
        )
    ''')

    # Crear tabla de resultados médicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    ''')

    # Confirmar la creación de las tablas
    conn.commit()
    cerrar_db(conn)

# Llamar a la función para crear las tablas
crear_tablas()
