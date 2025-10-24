"""
📧 Servicio de Email con SendGrid o SMTP
Sistema Inmobiliario - Verificación de cuenta y notificaciones
"""
from typing import Optional, Dict, Any
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent
from app.core.config import settings
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio de email con SendGrid o SMTP"""
    
    def __init__(self):
        """Inicializar cliente de email"""
        self.use_smtp = settings.USE_SMTP
        
        if self.use_smtp:
            # Usar SMTP propio
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
                self.sendgrid = True  # Flag para compatibilidad
                
            except Exception as e:
                logger.error(f"❌ [SMTP] Error en configuración: {e}")
                self.sendgrid = None
        else:
            # Usar SendGrid
            try:
                logger.info(f"🔧 [SENDGRID] Inicializando con API Key: {settings.SENDGRID_API_KEY[:10]}...")
                logger.info(f"📧 [SENDGRID] From Email: {settings.SENDGRID_FROM_EMAIL}")
                logger.info(f"👤 [SENDGRID] From Name: {settings.SENDGRID_FROM_NAME}")
                
                if not settings.SENDGRID_API_KEY or settings.SENDGRID_API_KEY == "":
                    logger.error("❌ [SENDGRID] API Key está vacía!")
                    self.sendgrid = None
                    return
                
                self.sendgrid = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                self.from_email = settings.SENDGRID_FROM_EMAIL
                self.from_name = settings.SENDGRID_FROM_NAME
                logger.info("✅ [SENDGRID] Inicializado correctamente")
            except Exception as e:
                logger.error(f"❌ [SENDGRID] Error inicializando: {e}")
                logger.exception(e)
                self.sendgrid = None
    
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
        Enviar email de verificación de cuenta
        
        Args:
            email: Email del usuario
            name: Nombre del usuario
            verification_code: Código de verificación de 6 dígitos
        
        Returns:
            Dict con success, message, etc.
        """
        if not self.sendgrid:
            logger.error("❌ SendGrid no está inicializado")
            return {
                "success": False,
                "message": "Servicio de email no disponible"
            }
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                    .content {{ padding: 40px 30px; }}
                    .content h2 {{ color: #333; margin-top: 0; }}
                    .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 25px; text-align: center; margin: 30px 0; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3); }}
                    .code {{ font-size: 36px; font-weight: bold; color: white; letter-spacing: 8px; font-family: 'Courier New', monospace; }}
                    .info-box {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px 20px; margin: 20px 0; border-radius: 5px; }}
                    .info-box p {{ margin: 5px 0; color: #555; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px 20px; margin: 20px 0; border-radius: 5px; }}
                    .warning p {{ margin: 5px 0; color: #856404; }}
                    .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #6c757d; font-size: 13px; }}
                    .footer p {{ margin: 5px 0; }}
                    .btn {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏠 Sistema Inmobiliario</h1>
                        <p>Verificación de Cuenta</p>
                    </div>
                    <div class="content">
                        <h2>¡Hola {name}! 👋</h2>
                        <p>Gracias por registrarte en nuestro Sistema Inmobiliario. Para activar tu cuenta, necesitamos verificar tu correo electrónico.</p>
                        
                        <div class="info-box">
                            <p><strong>📧 Email registrado:</strong> {email}</p>
                        </div>
                        
                        <p><strong>Ingresa el siguiente código de verificación:</strong></p>
                        
                        <div class="code-box">
                            <div class="code">{verification_code}</div>
                        </div>
                        
                        <div class="warning">
                            <p><strong>⏰ Este código es válido por 15 minutos.</strong></p>
                            <p>Si no solicitaste este registro, puedes ignorar este mensaje.</p>
                        </div>
                        
                        <p><strong>¿Qué podrás hacer una vez verificada tu cuenta?</strong></p>
                        <ul>
                            <li>🏠 Publicar propiedades</li>
                            <li>🔍 Buscar inmuebles</li>
                            <li>💬 Contactar propietarios</li>
                            <li>⭐ Guardar favoritos</li>
                            <li>📊 Gestionar tus publicaciones</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p><strong>Sistema Inmobiliario</strong></p>
                        <p>Tu plataforma de confianza para compra, venta y alquiler de propiedades</p>
                        <p style="margin-top: 15px; font-size: 11px;">Este es un correo automático, por favor no responder.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=From(self.from_email, self.from_name),
                to_emails=To(email),
                subject=Subject(f"🔐 Código de Verificación: {verification_code} - Sistema Inmobiliario"),
                plain_text_content=PlainTextContent(f"Tu código de verificación es: {verification_code}. Válido por 15 minutos."),
                html_content=HtmlContent(html_content)
            )
            
            logger.info(f"📤 [EMAIL] Enviando código de verificación a {email}")
            logger.info(f"   🔐 Código: {verification_code}")
            logger.info(f"   📧 From: {self.from_email} ({self.from_name})")
            
            # Enviar según el método configurado
            if self.use_smtp:
                # Enviar con SMTP
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"🔐 Código de Verificación: {verification_code} - Sistema Inmobiliario"
                msg['From'] = f"{self.from_name} <{self.from_email}>"
                msg['To'] = email
                
                part1 = MIMEText(f"Tu código de verificación es: {verification_code}. Válido por 15 minutos.", 'plain', 'utf-8')
                part2 = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(part1)
                msg.attach(part2)
                
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                logger.info(f"✅ [SMTP] Email enviado exitosamente a {email}")
                
                return {
                    "success": True,
                    "message": "Código de verificación enviado correctamente",
                    "email": email,
                    "status_code": 200
                }
            else:
                # Enviar con SendGrid
                response = self.sendgrid.send(message)
                
                logger.info(f"✅ [SENDGRID] Respuesta - Status: {response.status_code}")
                logger.info(f"   📨 Headers: {response.headers}")
                logger.info(f"   ✉️ Email enviado exitosamente a {email}")
                
                return {
                    "success": True,
                    "message": "Código de verificación enviado correctamente",
                    "email": email,
                    "status_code": response.status_code
                }
            
        except Exception as e:
            logger.error(f"❌ [EMAIL] Error enviando verificación a {email}")
            logger.error(f"   ⚠️ Error: {str(e)}")
            logger.exception(e)
            return {
                "success": False,
                "message": f"Error enviando email: {str(e)}",
                "email": email
            }
    
    async def send_welcome_email(
        self, 
        email: str, 
        name: str, 
        perfil: str = "Usuario"
    ) -> Dict[str, Any]:
        """
        Enviar email de bienvenida después de verificar cuenta
        
        Args:
            email: Email del usuario
            name: Nombre del usuario
            perfil: Tipo de perfil (Demandante, Ofertante, Corredor)
        
        Returns:
            Dict con success, message, etc.
        """
        if not self.sendgrid:
            logger.error("❌ SendGrid no está inicializado")
            return {
                "success": False,
                "message": "Servicio de email no disponible"
            }
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .content {{ padding: 40px 30px; }}
                    .welcome-box {{ background: linear-gradient(135deg, #e0f7fa 0%, #e1bee7 100%); border-radius: 10px; padding: 25px; margin: 20px 0; text-align: center; }}
                    .welcome-box h2 {{ margin: 0; color: #333; }}
                    .features {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; }}
                    .features ul {{ list-style: none; padding: 0; }}
                    .features li {{ padding: 10px 0; border-bottom: 1px solid #e0e0e0; }}
                    .features li:last-child {{ border-bottom: none; }}
                    .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #6c757d; font-size: 13px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏠 Sistema Inmobiliario</h1>
                        <p>¡Bienvenido a tu nueva plataforma!</p>
                    </div>
                    <div class="content">
                        <div class="welcome-box">
                            <h2>¡Hola {name}! 🎉</h2>
                            <p style="margin: 10px 0 0 0; font-size: 16px;">Tu cuenta ha sido verificada exitosamente</p>
                        </div>
                        
                        <p><strong>Perfil:</strong> {perfil}</p>
                        <p><strong>Email:</strong> {email}</p>
                        
                        <div class="features">
                            <h3 style="margin-top: 0;">✨ Ya puedes disfrutar de:</h3>
                            <ul>
                                <li>🏠 <strong>Publicar propiedades</strong> - Comparte tus inmuebles con miles de usuarios</li>
                                <li>🔍 <strong>Búsqueda avanzada</strong> - Encuentra la propiedad perfecta</li>
                                <li>💬 <strong>Contacto directo</strong> - Comunícate con propietarios y corredores</li>
                                <li>⭐ <strong>Favoritos</strong> - Guarda las propiedades que te interesan</li>
                                <li>📊 <strong>Panel de control</strong> - Gestiona todas tus publicaciones</li>
                                <li>🔔 <strong>Notificaciones</strong> - Recibe alertas de nuevas oportunidades</li>
                            </ul>
                        </div>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            <strong>¡Comienza a explorar ahora!</strong>
                        </p>
                    </div>
                    <div class="footer">
                        <p><strong>Sistema Inmobiliario</strong></p>
                        <p>Tu plataforma de confianza para compra, venta y alquiler de propiedades</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=From(self.from_email, self.from_name),
                to_emails=To(email),
                subject=Subject(f"🎉 ¡Bienvenido {name}! - Sistema Inmobiliario"),
                plain_text_content=PlainTextContent(f"Bienvenido {name}, tu cuenta ha sido verificada exitosamente."),
                html_content=HtmlContent(html_content)
            )
            
            response = self.sendgrid.send(message)
            
            logger.info(f"✅ [EMAIL] Email de bienvenida enviado a {email}")
            
            return {
                "success": True,
                "message": "Email de bienvenida enviado",
                "email": email
            }
            
        except Exception as e:
            logger.error(f"❌ [EMAIL] Error enviando bienvenida: {str(e)}")
            return {
                "success": False,
                "message": f"Error enviando email: {str(e)}",
                "email": email
            }
    
    async def send_password_reset_code(
        self, 
        email: str, 
        name: str, 
        reset_code: str
    ) -> Dict[str, Any]:
        """
        Enviar código de recuperación de contraseña
        
        Args:
            email: Email del usuario
            name: Nombre del usuario
            reset_code: Código de recuperación de 6 dígitos
        
        Returns:
            Dict con success, message, etc.
        """
        if not self.sendgrid:
            logger.error("❌ SendGrid no está inicializado")
            return {
                "success": False,
                "message": "Servicio de email no disponible"
            }
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .content {{ padding: 40px 30px; }}
                    .code-box {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; padding: 25px; text-align: center; margin: 30px 0; box-shadow: 0 5px 15px rgba(240, 147, 251, 0.3); }}
                    .code {{ font-size: 36px; font-weight: bold; color: white; letter-spacing: 8px; font-family: 'Courier New', monospace; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px 20px; margin: 20px 0; border-radius: 5px; }}
                    .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #6c757d; font-size: 13px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Recuperación de Contraseña</h1>
                        <p>Sistema Inmobiliario</p>
                    </div>
                    <div class="content">
                        <h2>Hola {name},</h2>
                        <p>Recibimos una solicitud para restablecer tu contraseña. Usa el siguiente código:</p>
                        
                        <div class="code-box">
                            <div class="code">{reset_code}</div>
                        </div>
                        
                        <div class="warning">
                            <p><strong>⏰ Este código es válido por 15 minutos.</strong></p>
                            <p>Si no solicitaste este cambio, ignora este mensaje y tu contraseña permanecerá sin cambios.</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p><strong>Sistema Inmobiliario</strong></p>
                        <p>Este es un correo automático, por favor no responder.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            logger.info(f"📤 [EMAIL] Enviando código de recuperación a {email}")
            logger.info(f"   🔐 Código: {reset_code}")
            
            # Enviar según el método configurado
            if self.use_smtp:
                # Enviar con SMTP
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"🔐 Código de Recuperación: {reset_code} - Sistema Inmobiliario"
                msg['From'] = f"{self.from_name} <{self.from_email}>"
                msg['To'] = email
                
                part1 = MIMEText(f"Tu código de recuperación es: {reset_code}. Válido por 15 minutos.", 'plain', 'utf-8')
                part2 = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(part1)
                msg.attach(part2)
                
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                logger.info(f"✅ [SMTP] Código de recuperación enviado a {email}")
                
                return {
                    "success": True,
                    "message": "Código de recuperación enviado",
                    "email": email
                }
            else:
                # Enviar con SendGrid
                message = Mail(
                    from_email=From(self.from_email, self.from_name),
                    to_emails=To(email),
                    subject=Subject(f"🔐 Código de Recuperación: {reset_code} - Sistema Inmobiliario"),
                    plain_text_content=PlainTextContent(f"Tu código de recuperación es: {reset_code}. Válido por 15 minutos."),
                    html_content=HtmlContent(html_content)
                )
                
                response = self.sendgrid.send(message)
                
                logger.info(f"✅ [SENDGRID] Código de recuperación enviado a {email}")
                
                return {
                    "success": True,
                    "message": "Código de recuperación enviado",
                    "email": email
                }
            
        except Exception as e:
            logger.error(f"❌ [EMAIL] Error enviando recuperación: {str(e)}")
            return {
                "success": False,
                "message": f"Error enviando email: {str(e)}",
                "email": email
            }


    # Alias para compatibilidad
    async def send_password_reset_email(self, email: str, name: str, reset_code: str):
        """Alias para send_password_reset_code"""
        return await self.send_password_reset_code(email, name, reset_code)

    async def send_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: list = None
    ) -> Dict[str, Any]:
        """
        Enviar email con archivos adjuntos (PDFs)

        Args:
            to_email: Email del destinatario
            subject: Asunto del correo
            html_content: Contenido HTML del correo
            attachments: Lista de diccionarios con:
                - filename: Nombre del archivo
                - content: Contenido en bytes o base64
                - content_type: Tipo MIME (default: 'application/pdf')

        Returns:
            Dict con success, message, etc.
        """
        if not self.sendgrid:
            logger.error("❌ Email service no está inicializado")
            return {
                "success": False,
                "message": "Servicio de email no disponible"
            }

        try:
            # Crear mensaje MIME
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Agregar contenido HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Agregar adjuntos si existen
            if attachments:
                from email.mime.base import MIMEBase
                from email import encoders
                import base64

                for attachment in attachments:
                    filename = attachment.get('filename', 'archivo.pdf')
                    content = attachment.get('content')
                    content_type = attachment.get('content_type', 'application/pdf')

                    # Si el contenido está en base64, decodificarlo
                    if isinstance(content, str):
                        try:
                            content = base64.b64decode(content)
                        except:
                            logger.warning(f"⚠️ No se pudo decodificar base64 para {filename}")
                            continue

                    # Crear parte del adjunto
                    part = MIMEBase('application', 'pdf')
                    part.set_payload(content)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)

                    logger.info(f"📎 [EMAIL] Adjunto agregado: {filename}")

            # Enviar según el método configurado
            if self.use_smtp:
                # Enviar con SMTP
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)

                logger.info(f"✅ [SMTP] Email con adjuntos enviado a {to_email}")
                logger.info(f"   📧 Asunto: {subject}")
                logger.info(f"   📎 Adjuntos: {len(attachments) if attachments else 0}")

                return {
                    "success": True,
                    "message": "Email enviado correctamente",
                    "email": to_email,
                    "attachments_count": len(attachments) if attachments else 0
                }
            else:
                # Enviar con SendGrid
                # TODO: Implementar envío con SendGrid usando adjuntos
                logger.warning("⚠️ [SENDGRID] Envío con adjuntos no implementado aún")
                return {
                    "success": False,
                    "message": "SendGrid con adjuntos no implementado, usar SMTP"
                }

        except Exception as e:
            logger.error(f"❌ [EMAIL] Error enviando con adjuntos: {str(e)}")
            logger.exception(e)
            return {
                "success": False,
                "message": f"Error enviando email: {str(e)}",
                "email": to_email
            }


# Instancia global del servicio
email_service = EmailService()
