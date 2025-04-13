from controller.functions import (
    registrar_paciente, 
    agendar_cita, 
    consultar_resultados, 
    consultar_medicos_en_db,
    ingresar_resultados_medicos,
    iniciar_sesion,
    listar_pacientes,
    ver_citas
)
from models.cita import Cita
from models.usuario import Usuario
from models.resultado import Resultado

def menu_paciente(usuario_id):
    while True:
        print("\n--- Menú Paciente ---")
        print("1. Ver mis resultados médicos")
        print("2. Agendar una cita")
        print("3. Salir")

        seleccion = input("Seleccione una opción: ").strip()

        if seleccion == "1":
            consultar_resultados(usuario_id)
        elif seleccion == "2":
            agendar_cita(usuario_id)
        elif seleccion == "3":
            break
        else:
            print("❌ Opción inválida, intente nuevamente.")

def menu_medico(usuario_id):
    while True:
        print("\n--- Menú Médico ---")
        print("1. Ver citas programadas")
        print("2. Ingresar resultados médicos")
        print("3. Salir")

        seleccion = input("Seleccione una opción: ").strip()

        if seleccion == "1":
            ver_citas()
        elif seleccion == "2":
            ingresar_resultados_medicos(usuario_id)
        elif seleccion == "3":
            break
        else:
            print("❌ Opción inválida, intente nuevamente.")

def menu():
    while True:
        print("\n--- Menú Principal ---")
        print("1. Iniciar sesión")
        print("2. Registrar paciente")
        print("3. Salir")

        seleccion = input("Seleccione una opción: ").strip()

        if seleccion == "1":
            usuario_id, rol = iniciar_sesion()
            if usuario_id and rol == "paciente":
                menu_paciente(usuario_id)
            elif usuario_id and rol == "medico":
                menu_medico(usuario_id)
            else:
                print("❌ No se pudo iniciar sesión.")
        elif seleccion == "2":
            registrar_paciente()
        elif seleccion == "3":
            break
        else:
            print("❌ Opción inválida, intente nuevamente.")

if __name__ == "__main__":
    menu()
