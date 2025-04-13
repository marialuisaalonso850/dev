import unittest
from unittest.mock import patch, MagicMock, ANY
from controller.functions import ingresar_resultados_medicos
from datetime import datetime

class TestIngresarResultadosMedicos(unittest.TestCase):

    @patch('controller.functions.conectar_db')
    @patch('controller.functions.enviar_correo')
    @patch('builtins.input')
    def test_ingresar_resultados_exitosa(self, mock_input, mock_enviar_correo, mock_conectar_db):
        # Mock de conexión y cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conectar_db.return_value = (mock_conn, mock_cursor)

        # Mock de citas futuras disponibles
        mock_cursor.fetchall.return_value = [
            (1, 1, 'Ana Martínez', '2025-06-15', '10:00')
        ]

        # Mock de correo del paciente
        mock_cursor.fetchone.return_value = ['ana.martinez@correo.com']

        # Simular inputs: seleccionar cita, descripción, fecha válida
        mock_input.side_effect = [
            "1",                            # Selecciona cita 1
            "Examen de sangre normal",      # Descripción
            "2025-06-15"                    # Fecha válida
        ]

        # Ejecutar función con medico_id simulado
        ingresar_resultados_medicos(3)

        # Verificar que se hizo INSERT en resultados correctamente
        mock_cursor.execute.assert_any_call(
            'INSERT INTO resultados (paciente_id, descripcion, fecha)',  # Comprobación de la consulta de inserción
            (1, "Examen de sangre normal", "2025-06-15")
        )

        # Verificar que commit fue llamado
        mock_conn.commit.assert_called()

        # Verificar que se envió el correo con contenido esperado
        mock_enviar_correo.assert_called_with(
            'ana.martinez@correo.com',
            "Nuevos Resultados Médicos",
            "Tienes nuevos resultados médicos disponibles en VitalApp: Examen de sangre normal (2025-06-15)."
        )

if __name__ == '__main__':
    unittest.main()
