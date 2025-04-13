import unittest
from unittest.mock import patch, MagicMock, call
from controller.functions import registrar_paciente

class TestRegistrarPaciente(unittest.TestCase):

    @patch('functions.input', side_effect=["Juan Pérez", "juan.perez@example.com", "123456", "123456789", "987654321"])
    @patch('functions.conectar_db')
    @patch('functions.enviar_correo')
    def test_registrar_paciente(self, mock_enviar_correo, mock_conectar_db, mock_input):
        # Simular conexión y cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conectar_db.return_value = (mock_conn, mock_cursor)

        # Simular ID generado
        mock_cursor.lastrowid = 1

        # Ejecutar función
        registrar_paciente()

        # Capturar todas las llamadas a execute
        calls = mock_cursor.execute.call_args_list

        # Función para limpiar query
        def clean_query(q):
            return ' '.join(q.strip().split())

        # Construimos las consultas esperadas, normalizadas
        expected_insert_usuarios_query = clean_query("""
            INSERT INTO usuarios (nombre, correo, contrasena, cedula, rol)
            VALUES (?, ?, ?, ?, ?)
        """)
        expected_insert_pacientes_query = clean_query("""
            INSERT INTO pacientes (id, nombre, correo, telefono)
            VALUES (?, ?, ?, ?)
        """)

        # Validar que se llamó con la consulta esperada
        usuarios_call_found = any(
            clean_query(args[0]) == expected_insert_usuarios_query and args[1] == (
                "Juan Pérez", "juan.perez@example.com", "123456", "123456789", 'paciente'
            )
            for args, kwargs in calls
        )
        pacientes_call_found = any(
            clean_query(args[0]) == expected_insert_pacientes_query and args[1] == (
                1, "Juan Pérez", "juan.perez@example.com", "987654321"
            )
            for args, kwargs in calls
        )

        self.assertTrue(usuarios_call_found, f"La consulta a usuarios no fue llamada correctamente. Llamadas: {calls}")
        self.assertTrue(pacientes_call_found, f"La consulta a pacientes no fue llamada correctamente. Llamadas: {calls}")

        # Verificar que se envió el correo correctamente
        mock_enviar_correo.assert_called_with(
            "juan.perez@example.com", "Registro exitoso en VitalApp",
            "Hola Juan Pérez, gracias por registrarte en VitalApp. Ya puedes agendar tus citas y consultar tus resultados."
        )

        # Verificar que se hizo commit
        mock_conn.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
