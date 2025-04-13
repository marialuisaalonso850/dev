import sqlite3
from db import crear_tablas
from functions import registrar_paciente, iniciar_sesion, consultar_resultados, agendar_cita, ingresar_resultados_medicos,listar_pacientes
from db import conectar_db, cerrar_db

crear_tablas()
def menu_paciente(usuario_id):
    while True:
        print("\n--- Menú Paciente ---")
        print("1. Consultar Resultados Médicos")
        print("2. Agendar Cita")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            consultar_resultados(usuario_id)
        elif opcion == '2':
            agendar_cita(usuario_id)
        elif opcion == '3':
            break
        else:
            print("Opción inválida")
            
def ver_citas():
    conn, cursor = conectar_db()
    
    try:
        cursor.execute("SELECT * FROM citas")
        citas = cursor.fetchall()
        
        if citas:
            print("📅 Citas registradas:")
            for cita in citas:
                print(cita)
        else:
            print("⚠️ No hay citas registradas.")
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")

    cerrar_db(conn)           
            
def menu_medico(medico_id):
    while True:
        print("\n--- Menú Médico ---")
        print("1. Ingresar Resultados Médicos")
        print("2. Ver Pacientes")
        print("3. Ver Citas")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            ingresar_resultados_medicos(medico_id)
        elif opcion == '2':
            listar_pacientes()
        elif opcion == '3':
            ver_citas()  # Aquí la llamada
        elif opcion == '4':
            break
        else:
            print("Opción inválida")


def menu():
    while True:
        print("\n--- VitalApp ---")
        print("1. Iniciar Sesión")
        print("2. Registrar Paciente")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            usuario_id, rol = iniciar_sesion()
            if usuario_id:
                if rol == 'medico':
                    menu_medico(usuario_id)  # Redirigir al menú del médico
                elif rol == 'paciente':
                    menu_paciente(usuario_id)  # Redirigir al menú del paciente
        elif opcion == '2':
            registrar_paciente()
        elif opcion == '3':
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida")

menu()
