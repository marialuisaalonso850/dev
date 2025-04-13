import sqlite3

# Conexión a la base de datos
def conectar_db():
    conn = sqlite3.connect('vitalapp.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = 1")  # Habilitar las claves foráneas
    return conn, cursor

# Función para cerrar la conexión
def cerrar_db(conn):
    conn.close()

def crear_tablas():
    conn, cursor = conectar_db()
    
    
    
    
    # Crear tabla de pacientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        correo TEXT,
                        telefono TEXT)''')

    # Crear tabla de médicos
    cursor.execute('''CREATE TABLE IF NOT EXISTS medicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        correo TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    correo TEXT,
                    contrasena TEXT,
                    cedula TEXT UNIQUE,
                    rol TEXT)''')

    # Crear tabla de citas
    cursor.execute('''CREATE TABLE IF NOT EXISTS citas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paciente_id INTEGER,
                        medico_id INTEGER,
                        fecha TEXT,
                        hora TEXT,
                        doctor TEXT,
                        FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
                        FOREIGN KEY (medico_id) REFERENCES medicos(id))''')

    # Crear tabla de resultados médicos
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paciente_id INTEGER,
                        descripcion TEXT,
                        fecha TEXT,
                        FOREIGN KEY (paciente_id) REFERENCES pacientes(id))''')


        
    cerrar_db(conn)

crear_tablas()
