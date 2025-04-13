from db import conectar_db, cerrar_db
from datetime import datetime

# Registrar un paciente
def registrar_paciente():
    nombre = input("Ingrese su nombre: ").strip()
    correo = input("Ingrese su correo: ").strip()
    contrasena = input("Ingrese su contraseña: ").strip()
    cedula = input("Ingrese su cédula: ").strip()

    conn, cursor = conectar_db()
    cursor.execute("INSERT INTO usuarios (nombre, correo, contrasena, cedula, rol) VALUES (?, ?, ?, ?, ?)",
                   (nombre, correo, contrasena, cedula, 'paciente'))
    conn.commit()
    cerrar_db(conn)
    print(f"✅ Paciente {nombre} registrado correctamente.")


def leer_medicos_desde_txt():
    medicos = []
    with open('medicos.txt', 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue  # Saltar líneas vacías

            partes = linea.split(',')

            if len(partes) == 3:
                correo, nombre, contrasena = partes
                medicos.append({
                    'correo': correo.strip(),
                    'nombre': nombre.strip(),
                    'contrasena': contrasena.strip()
                })
            else:
                print(f"❌ Línea mal formateada en el archivo de médicos: {linea}")
    return medicos


def iniciar_sesion():
    correo = input("Ingrese su correo: ").strip()
    contrasena = input("Ingrese su contraseña: ").strip()

    # Revisar en médicos
    medicos = leer_medicos_desde_txt()
    for medico in medicos:
        if medico['correo'] == correo and medico['contrasena'] == contrasena:
            print(f"✅ Bienvenido, Dr. {medico['nombre']}. Rol: Médico")
            return correo, 'medico'  # Retorna correo y rol

    # Revisar en pacientes
    conn, cursor = conectar_db()
    cursor.execute("SELECT id, nombre, rol FROM usuarios WHERE correo=? AND contrasena=?", (correo, contrasena))
    usuario = cursor.fetchone()

    if usuario:
        usuario_id, nombre, rol = usuario
        print(f"✅ Bienvenido, {nombre}. Rol: {rol}")
        cerrar_db(conn)
        return usuario_id, rol
    else:
        print("❌ Credenciales incorrectas.")
        cerrar_db(conn)
        return None, None


def listar_pacientes():
    conn, cursor = conectar_db()
    cursor.execute("SELECT id, nombre, correo, telefono FROM pacientes")
    pacientes = cursor.fetchall()

    if pacientes:
        print("\n📋 Lista de Pacientes Registrados:")
        for paciente in pacientes:
            id_paciente, nombre, correo, telefono = paciente
            print(f"ID: {id_paciente} - Nombre: {nombre} - Correo: {correo} - Teléfono: {telefono}")
    else:
        print("❌ No hay pacientes registrados.")
    cerrar_db(conn)

# Consultar resultados médicos
def consultar_resultados(paciente_id):
    conn, cursor = conectar_db()
    cursor.execute("SELECT descripcion, fecha FROM resultados WHERE paciente_id=?", (paciente_id,))
    resultados = cursor.fetchall()

    if resultados:
        print("\n🩺 Resultados médicos:")
        for resultado in resultados:
            descripcion = resultado[0]
            fecha = resultado[1]
            print(f"📅 Fecha: {fecha} - Resultado: {descripcion}")
    else:
        print("❌ No hay resultados médicos registrados para este paciente.")
    cerrar_db(conn)

def agendar_cita(paciente_id):
    medicos = leer_medicos_desde_txt()

    print("\n📋 Doctores disponibles:")
    for idx, medico in enumerate(medicos, 1):
        print(f"{idx}. Dr. {medico['nombre']} ({medico['correo']})")

    seleccion = input("Seleccione el número del doctor: ").strip()

    if not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(medicos):
        print("❌ Selección inválida.")
        return

    doctor_seleccionado = medicos[int(seleccion) - 1]['nombre']
    medico_id = medicos[int(seleccion) - 1]['correo']  # O lo que utilices para obtener el médico

    # Validar la fecha
    while True:
        fecha_str = input("Ingrese la fecha (YYYY-MM-DD): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            break  # Si es válida, salir del bucle
        except ValueError:
            print("❌ Fecha inválida. Por favor, ingrese la fecha en formato YYYY-MM-DD.")

    # Validar la hora
    while True:
        hora_str = input("Ingrese la hora (HH:MM): ").strip()
        try:
            hora = datetime.strptime(hora_str, "%H:%M").time()
            break  # Si es válida, salir del bucle
        except ValueError:
            print("❌ Hora inválida. Por favor, ingrese la hora en formato HH:MM.")

    # Verificar si la fecha y hora son válidas y no están en el pasado
    fecha_hora_str = f"{fecha_str} {hora_str}"
    fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")

    if fecha_hora <= datetime.now():
        print("❌ La fecha y hora deben ser futuras. Intente de nuevo.")
        return

    # Agendar la cita en la base de datos
    conn, cursor = conectar_db()
    cursor.execute("""
        INSERT INTO citas (paciente_id, medico_id, fecha, hora, doctor)
        VALUES (?, ?, ?, ?, ?)
    """, (paciente_id, medico_id, fecha_str, hora_str, doctor_seleccionado))

    conn.commit()
    cerrar_db(conn)
    print("✅ Cita agendada correctamente.")


def ver_citas_medico(medico_id):
    conn, cursor = conectar_db()

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
        SELECT c.id, u.nombre, c.fecha, c.hora
        FROM citas c
        JOIN usuarios u ON c.paciente_id = u.id
        WHERE c.medico_id = ? AND (c.fecha || ' ' || c.hora) > ?
    """, (medico_id, ahora))

    citas = cursor.fetchall()
    cerrar_db(conn)
    return citas

# Ingresar resultados médicos
def ingresar_resultados_medicos(medico_id):
    citas = ver_citas_medico(medico_id)

    if not citas:
        print("❌ No hay citas pendientes para usted.")
        return

    print("\n📋 Citas pendientes:")
    for idx, (cita_id, paciente_nombre, fecha, hora) in enumerate(citas, 1):
        print(f"{idx}. {paciente_nombre} - {fecha} {hora}")

    seleccion = input("Seleccione el número de la cita: ").strip()

    if not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(citas):
        print("❌ Selección inválida.")
        return

    cita_seleccionada = citas[int(seleccion)-1]
    cita_id, paciente_nombre, fecha, hora = cita_seleccionada

    descripcion = input("Ingrese los resultados (descripción): ").strip()

    conn, cursor = conectar_db()

    cursor.execute("""
        INSERT INTO resultados (paciente_id, descripcion, fecha)
        VALUES ((SELECT paciente_id FROM citas WHERE id = ?), ?, ?)
    """, (cita_id, descripcion, fecha))

    conn.commit()
    cerrar_db(conn)
    print("✅ Resultado ingresado correctamente.")

# Crear alerta para el paciente
def crear_alerta(paciente_id, mensaje, fecha):
    # Insertar una alerta en la base de datos
    conn, cursor = conectar_db()
    cursor.execute("INSERT INTO alertas (paciente_id, mensaje, fecha) VALUES (?, ?, ?)",
                   (paciente_id, mensaje, str(fecha)))
    conn.commit()
    cerrar_db(conn)
    print("✅ Alerta generada correctamente.")

# Ver alertas de salud
def ver_alertas(paciente_id):
    conn, cursor = conectar_db()
    cursor.execute("SELECT id, mensaje, fecha, leida FROM alertas WHERE paciente_id=? AND leida=0", (paciente_id,))
    alertas = cursor.fetchall()

    if alertas:
        print("\n📢 **Tus alertas de salud:**")
        for alerta in alertas:
            alerta_id, mensaje, fecha, leida = alerta
            print(f"📅 Fecha: {fecha} - Alerta: {mensaje}")
        # Marcar alertas como leídas
        cursor.execute("UPDATE alertas SET leida=1 WHERE paciente_id=?", (paciente_id,))
        conn.commit()
    else:
        print("❌ No tienes alertas pendientes.")
    cerrar_db(conn)

# Función para verificar si el paciente existe en la base de datos
def paciente_existe(paciente_id):
    conn, cursor = conectar_db()
    cursor.execute("SELECT id FROM pacientes WHERE id=?", (paciente_id,))
    paciente = cursor.fetchone()
    cerrar_db(conn)
    return paciente is not None

