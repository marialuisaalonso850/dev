import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from email.mime.text import MIMEText
import json
import smtplib
import sqlite3
from db import conectar_db, cerrar_db
from datetime import datetime

sentry_sdk.init(
    dsn="https://d58338bc03b4c29351b1b01d3b602589@o4509147517550592.ingest.de.sentry.io/4509147520303184",
    integrations=[LoggingIntegration()],
    traces_sample_rate=1.0
)


# --- Funciones de Envío de Correos ---
def iniciar_sesion():
    correo = input("Ingrese su correo: ").strip()
    contrasena = input("Ingrese su contraseña: ").strip()

    conn, cursor = conectar_db()
    cursor.execute("""
        SELECT id, nombre, rol FROM usuarios
        WHERE correo=? AND contrasena=?
    """, (correo, contrasena))
    usuario = cursor.fetchone()
    cerrar_db(conn)

    if usuario:
        usuario_id, nombre, rol = usuario
        print(f"✅ Bienvenido, {nombre}. Rol: {rol}")
        return usuario_id, rol

    print("❌ Credenciales incorrectas.")
    return None, None


def enviar_correo(destinatario, asunto, mensaje):
    try:
        with open("config/config_email.json", "r") as f:
            config = json.load(f)

        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["correo_emisor"], config["contrasena"])

        msg = MIMEText(mensaje)
        msg['Subject'] = asunto
        msg['From'] = config["correo_emisor"]
        msg['To'] = destinatario

        server.sendmail(config["correo_emisor"], destinatario, msg.as_string())
        server.quit()
        print(f"📧 Correo enviado a {destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        sentry_sdk.capture_exception(e)

# --- Funciones de Registro y Gestión de Usuarios ---
def registrar_paciente():
    nombre = input("Ingrese su nombre: ").strip()
    correo = input("Ingrese su correo: ").strip()
    contrasena = input("Ingrese su contraseña: ").strip()
    cedula = input("Ingrese su cédula: ").strip()
    telefono = input("Ingrese su teléfono: ").strip()

    conn, cursor = conectar_db()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contrasena, cedula, rol)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, correo, contrasena, cedula, 'paciente'))

        usuario_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO pacientes (id, nombre, correo, telefono)
            VALUES (?, ?, ?, ?)
        """, (usuario_id, nombre, correo, telefono))

        conn.commit()
        print(f"✅ Paciente {nombre} registrado correctamente.")

        mensaje = f"Hola {nombre}, gracias por registrarte en VitalApp. Ya puedes agendar tus citas y consultar tus resultados."
        enviar_correo(correo, "Registro exitoso en VitalApp", mensaje)

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"❌ Error al registrar paciente: {e}")
        sentry_sdk.capture_exception(e)
    finally:
        cerrar_db(conn)
def listar_pacientes():
    conn, cursor = conectar_db()
    cursor.execute("""
        SELECT id, nombre, correo, telefono FROM pacientes
    """)
    pacientes = cursor.fetchall()
    cerrar_db(conn)

    if pacientes:
        print("\n--- Lista de Pacientes ---")
        for paciente in pacientes:
            paciente_id, nombre, correo, telefono = paciente
            print(f"ID: {paciente_id} | Nombre: {nombre} | Correo: {correo} | Teléfono: {telefono}")
    else:
        print("⚠️ No hay pacientes registrados.")
        
def insertar_medicos_en_db():
    medicos = leer_medicos_desde_txt()
    if not medicos:
        print("⚠️ No hay médicos para insertar.")
        return

    conn, cursor = conectar_db()
    try:
        for medico in medicos:
            cursor.execute("SELECT id FROM usuarios WHERE correo = ? AND rol = 'medico'", (medico['correo'],))
            existente = cursor.fetchone()

            if existente:
                print(f"ℹ️ El médico {medico['nombre']} ya existe en la base de datos.")
                continue

            cursor.execute('''INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (?, ?, ?, ?)''',
                           (medico['nombre'], medico['correo'], medico['contrasena'], 'medico'))

            usuario_id = cursor.lastrowid

            cursor.execute('''INSERT INTO medicos (id, nombre, correo) VALUES (?, ?, ?)''',
                           (usuario_id, medico['nombre'], medico['correo']))

            print(f"✅ Médico insertado: {medico['nombre']} - {medico['correo']}")

        conn.commit()
        print("✅ Médicos insertados correctamente en la base de datos.")
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"❌ Error al insertar médicos: {e}")
        sentry_sdk.capture_exception(e)
    finally:
        cerrar_db(conn)

def leer_medicos_desde_txt():
    medicos = []
    try:
        with open('medicos.txt', 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue

                partes = linea.split(',')
                if len(partes) == 3:
                    correo, nombre, contrasena = partes
                    medicos.append({'correo': correo.strip(), 'nombre': nombre.strip(), 'contrasena': contrasena.strip()})
                else:
                    print(f"❌ Línea mal formateada en el archivo de médicos: {linea}")
    except FileNotFoundError as e:
        print("❌ El archivo de médicos no se encontró.")
        sentry_sdk.capture_exception(e)

    return medicos

# --- Funciones de Gestión de Citas ---
def agendar_cita(paciente_id):
    medicos = consultar_medicos_en_db()

    if not medicos:
        print("❌ No hay médicos disponibles.")
        return

    print("\n📋 Doctores disponibles:")
    for idx, medico in enumerate(medicos, 1):
        doctor_id, nombre, correo = medico
        print(f"{idx}. Dr. {nombre} ({correo})")

    seleccion = input("Seleccione el número del doctor: ").strip()

    if not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(medicos):
        print("❌ Selección inválida.")
        return

    medico_seleccionado = medicos[int(seleccion) - 1]
    medico_id = medico_seleccionado[0]

    while True:
        fecha_str = input("Ingrese la fecha (YYYY-MM-DD): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("❌ Fecha inválida. Por favor, ingrese la fecha en formato YYYY-MM-DD.")

    while True:
        hora_str = input("Ingrese la hora (HH:MM): ").strip()
        try:
            hora = datetime.strptime(hora_str, "%H:%M").time()
            break
        except ValueError:
            print("❌ Hora inválida. Por favor, ingrese la hora en formato HH:MM.")

    fecha_hora_str = f"{fecha_str} {hora_str}"
    fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    if fecha_hora <= datetime.now():
        print("❌ La fecha y hora deben ser futuras. Intente de nuevo.")
        return

    conn, cursor = conectar_db()
    try:
        cursor.execute(""" 
            INSERT INTO citas (paciente_id, medico_id, fecha, hora)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, medico_id, fecha_str, hora_str))

        conn.commit()
        print("✅ Cita agendada correctamente.")

        cursor.execute("SELECT correo FROM pacientes WHERE id=?", (paciente_id,))
        correo = cursor.fetchone()[0]
        mensaje = f"Has agendado una cita para el {fecha_str} a las {hora_str}."
        enviar_correo(correo, "Cita agendada - VitalApp", mensaje)

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"❌ Error al agendar cita: {e}")
        sentry_sdk.capture_exception(e)
    finally:
        cerrar_db(conn)

def consultar_medicos_en_db():
    conn, cursor = conectar_db()
    cursor.execute("SELECT id, nombre, correo FROM medicos")
    medicos = cursor.fetchall()
    cerrar_db(conn)
    return medicos

# --- Funciones de Consultas y Resultados Médicos ---
def ingresar_resultados_medicos(medico_id):
    conn, cursor = conectar_db()

    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT c.id, p.id AS paciente_id, p.nombre AS paciente_nombre, c.fecha, c.hora
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        WHERE c.medico_id = ? AND (c.fecha > ? OR (c.fecha = ? AND c.hora > ?))
        ORDER BY c.fecha, c.hora
    """, (medico_id, fecha_actual, fecha_actual, datetime.now().strftime("%H:%M")))

    citas = cursor.fetchall()

    if not citas:
        print("⚠️ No tiene citas futuras programadas.")
        cerrar_db(conn)
        return

    print("\n--- Citas Programadas ---")
    for idx, cita in enumerate(citas, 1):
        cita_id, paciente_id, paciente_nombre, fecha, hora = cita
        print(f"{idx}. Cita #{cita_id} | {paciente_nombre} | {fecha} | {hora}")

    seleccion = input("\nSeleccione el número de la cita para ingresar resultados (0 para cancelar): ").strip()

    if seleccion == "0":
        print("Operación cancelada.")
        cerrar_db(conn)
        return

    if not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(citas):
        print("❌ Selección inválida.")
        cerrar_db(conn)
        return

    cita_seleccionada = citas[int(seleccion) - 1]
    paciente_id = cita_seleccionada[1]
    paciente_nombre = cita_seleccionada[2]

    print(f"\nIngresando resultados para {paciente_nombre}")
    descripcion = input("Ingrese la descripción de los resultados médicos: ").strip()

    try:
        cursor.execute("""
            INSERT INTO resultados (paciente_id, descripcion, fecha)
            VALUES (?, ?, ?)
        """, (paciente_id, descripcion, fecha_actual))

        conn.commit()
        print(f"✅ Resultados médicos ingresados correctamente para {paciente_nombre}.")
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"❌ Error al ingresar resultados: {e}")
        sentry_sdk.capture_exception(e)
    finally:
        cerrar_db(conn)

def consultar_resultados(usuario_id):
    conn, cursor = conectar_db()
    cursor.execute("""
        SELECT r.descripcion, r.fecha 
        FROM resultados r
        JOIN pacientes p ON r.paciente_id = p.id
        WHERE p.id = ?
    """, (usuario_id,))
    resultados = cursor.fetchall()
    cerrar_db(conn)

    if resultados:
        print("\n📋 Resultados médicos:")
        for descripcion, fecha in resultados:
            print(f"Fecha: {fecha} | Descripción: {descripcion}")
    else:
        print("⚠️ No tiene resultados médicos registrados.")
        
    
