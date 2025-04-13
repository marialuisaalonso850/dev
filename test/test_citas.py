import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime
from controller.functions import agendar_cita

class TestAgendarCita(unittest.TestCase):

    @patch('functions.conectar_db')
    @patch('functions.enviar_correo')
    @patch('functions.consultar_medicos_en_db')
    @patch('builtins.input')
    def test_agendar_cita_exitosa(self, mock_input, mock_consultar_medicos, mock_enviar_correo, mock_conectar_db):
        # Mock de la lista de médicos disponibles
        mock_consultar_medicos.return_value = [
            (1, 'Carlos Gómez', 'carlos.gomez@hospital.com')
        ]

        # Simulamos las entradas del usuario
        mock_input.side_effect = [
            "1",                # Seleccionar médico 1
            "2025-05-01",       # Fecha válida
            "10:30"             # Hora válida
        ]

        # Mock de la conexión a base de datos
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conectar_db.return_value = (mock_conn, mock_cursor)

        # Simulamos que al buscar el correo, devuelve uno válido
        mock_cursor.fetchone.return_value = ['paciente@example.com']

        # Ejecutamos la función con paciente_id ficticio
        paciente_id = 7
        agendar_cita(paciente_id)

        # Verificar que se insertó la cita con los valores correctos
        mock_cursor.execute.assert_any_call(
            ANY,
            (paciente_id, 1, "2025-05-01", "10:30")
        )

        # Verificar que se haya hecho commit a la base de datos
        mock_conn.commit.assert_called()

        # Verificar que se envió el correo correctamente
        mock_enviar_correo.assert_called_with(
            'paciente@example.com',
            "Cita agendada - VitalApp",
            "Has agendado una cita para el 2025-05-01 a las 10:30."
        )

if __name__ == '__main__':
    unittest.main()

