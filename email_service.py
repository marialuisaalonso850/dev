import smtplib, json
from email.mime.text import MIMEText

class EmailService:
    def __init__(self, config_path='config_email.json'):
        with open(config_path, "r") as f:
            config = json.load(f)
        self.smtp_server = config["smtp_server"]
        self.smtp_port = config["smtp_port"]
        self.correo_emisor = config["correo_emisor"]
        self.contrasena = config["contrasena"]

    def enviar(self, destinatario, asunto, mensaje):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.correo_emisor, self.contrasena)

            msg = MIMEText(mensaje)
            msg['Subject'] = asunto
            msg['From'] = self.correo_emisor
            msg['To'] = destinatario

            server.sendmail(self.correo_emisor, destinatario, msg.as_string())
            server.quit()
            print(f"📧 Correo enviado a {destinatario}")
        except Exception as e:
            print(f"❌ Error al enviar correo: {e}")
