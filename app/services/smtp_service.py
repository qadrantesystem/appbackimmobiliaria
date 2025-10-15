"""
📧 Servicio de Email con SMTP Propio
Sistema Inmobiliario - Usando servidor mail.qadrante2.com
"""
from typing import Optional, Dict, Any
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import random
import string

logger = logging.getLogger(__name__)

class SMTPService:
    """Servicio de email con SMTP propio"""
    
    def __init__(self):
        """Inicializar configuración SMTP"""
        try:
            self.smtp_host = settings.SMTP_HOST
            self.smtp_port = settings.SMTP_PORT
            self.smtp_user = settings.SMTP_USER
            self.smtp_password = settings.SMTP_PASSWORD
            self.from_email = settings.SMTP_FROM_EMAIL
            self.from_name = settings.SMTP_FROM_NAME
            
            logger.info(f"🔧 [SMTP] Configurado con servidor: {self.smtp_host}:{self.smtp_port}")
            logger.info(f"📧 [SMTP] Usuario: {self.smtp_user}")
            logger.info(f"📧 [SMTP] From Email: {self.from_email}")
            
        except Exception as e:
            logger.error(f"❌ [SMTP] Error en configuración: {e}")
    
    def generate_verification_code(self) -> str:
        """Generar código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    async def send_verification_email(
        self, 
        email: str, 
        name: str, 
        verification_code: str
    ) -> Dict[str, Any]:
        """
        Enviar email de verificación usando SMTP
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔐 Código de Verificación: {verification_code} - Sistema Inmobiliario"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email
            
            # Texto plano
            text_content = f"""
Hola {name},

Tu código de verificación es: {verification_code}

Este código es válido por 15 minutos.

Si no solicitaste este registro, puedes ignorar este mensaje.

---
Sistema Inmobiliario
Tu plataforma de confianza para compra, venta y alquiler de propiedades
            """
            
            # HTML
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ padding: 40px 30px; }}
        .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 25px; text-align: center; margin: 30px 0; }}
        .code {{ font-size: 36px; font-weight: bold; color: white; letter-spacing: 8px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Bienvenido a Sistema Inmobiliario</h1>
            <p>Verifica tu cuenta para comenzar</p>
        </div>
        <div class="content">
            <h2>Hola {name},</h2>
            <p>Gracias por registrarte en nuestro Sistema Inmobiliario.</p>
            <p><strong>Ingresa el siguiente código de verificación:</strong></p>
            <div class="code-box">
                <div class="code">{verification_code}</div>
            </div>
            <p><strong>⏰ Este código es válido por 15 minutos.</strong></p>
            <p>Si no solicitaste este registro, puedes ignorar este mensaje.</p>
        </div>
        <div class="footer">
            <p><strong>Sistema Inmobiliario</strong></p>
            <p>Tu plataforma de confianza para compra, venta y alquiler de propiedades</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Adjuntar partes
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar
            logger.info(f"📤 [SMTP] Enviando email a {email}")
            logger.info(f"   🔐 Código: {verification_code}")
            logger.info(f"   📧 Servidor: {self.smtp_host}:{self.smtp_port}")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Seguridad TLS
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ [SMTP] Email enviado exitosamente a {email}")
            
            return {
                "success": True,
                "message": "Código de verificación enviado correctamente",
                "email": email,
                "status_code": 200
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ [SMTP] Error de autenticación: {e}")
            return {
                "success": False,
                "message": "Error de autenticación SMTP",
                "error": str(e)
            }
        except smtplib.SMTPException as e:
            logger.error(f"❌ [SMTP] Error SMTP: {e}")
            return {
                "success": False,
                "message": "Error al enviar email",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ [SMTP] Error general: {e}")
            logger.exception(e)
            return {
                "success": False,
                "message": "Error inesperado",
                "error": str(e)
            }

# Instancia global
smtp_service = SMTPService()
