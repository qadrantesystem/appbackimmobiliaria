from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

class EmailService:
    """Servicio para envío de emails con SendGrid"""
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        Enviar email
        
        Args:
            to_email: Email destinatario
            subject: Asunto del email
            html_content: Contenido HTML del email
            
        Returns:
            bool indicando éxito
        """
        try:
            message = Mail(
                from_email=(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
    
    @staticmethod
    def send_welcome_email(to_email: str, nombre: str) -> bool:
        """Enviar email de bienvenida"""
        subject = "¡Bienvenido al Sistema Inmobiliario!"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Hola {nombre}!</h2>
                <p>Bienvenido al Sistema Inmobiliario.</p>
                <p>Tu cuenta ha sido creada exitosamente.</p>
                <p>Ahora puedes:</p>
                <ul>
                    <li>Buscar propiedades</li>
                    <li>Guardar favoritos</li>
                    <li>Contactar propietarios</li>
                </ul>
                <p>¡Gracias por unirte!</p>
            </body>
        </html>
        """
        return EmailService.send_email(to_email, subject, html_content)
    
    @staticmethod
    def send_property_contact_notification(
        propietario_email: str,
        propietario_nombre: str,
        propiedad_titulo: str,
        contacto_nombre: str,
        contacto_email: str,
        contacto_telefono: str,
        mensaje: str
    ) -> bool:
        """Notificar al propietario sobre contacto de propiedad"""
        subject = f"Nuevo contacto para: {propiedad_titulo}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Hola {propietario_nombre}!</h2>
                <p>Tienes un nuevo contacto interesado en tu propiedad:</p>
                <h3>{propiedad_titulo}</h3>
                <hr>
                <p><strong>Datos del interesado:</strong></p>
                <ul>
                    <li><strong>Nombre:</strong> {contacto_nombre}</li>
                    <li><strong>Email:</strong> {contacto_email}</li>
                    <li><strong>Teléfono:</strong> {contacto_telefono}</li>
                </ul>
                <p><strong>Mensaje:</strong></p>
                <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                    {mensaje}
                </p>
                <p>Te recomendamos contactarlo lo antes posible.</p>
            </body>
        </html>
        """
        return EmailService.send_email(propietario_email, subject, html_content)
    
    @staticmethod
    def send_new_properties_alert(
        usuario_email: str,
        usuario_nombre: str,
        busqueda_nombre: str,
        cantidad_propiedades: int,
        propiedades: list
    ) -> bool:
        """Enviar alerta de nuevas propiedades"""
        subject = f"Nuevas propiedades: {busqueda_nombre}"
        
        propiedades_html = ""
        for prop in propiedades[:5]:  # Máximo 5 propiedades
            propiedades_html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h4>{prop['titulo']}</h4>
                <p><strong>Precio:</strong> {prop['precio']}</p>
                <p><strong>Ubicación:</strong> {prop['distrito']}</p>
                <a href="{prop['url']}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Propiedad</a>
            </div>
            """
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>¡Hola {usuario_nombre}!</h2>
                <p>Tenemos {cantidad_propiedades} nuevas propiedades que coinciden con tu búsqueda:</p>
                <h3>{busqueda_nombre}</h3>
                <hr>
                {propiedades_html}
                <p style="margin-top: 20px;">
                    <a href="https://tu-app.com/busquedas" style="color: #007bff;">Ver todas las propiedades</a>
                </p>
            </body>
        </html>
        """
        return EmailService.send_email(usuario_email, subject, html_content)
