from twilio.rest import Client
from app.core.config import settings

class SMSService:
    """Servicio para envío de SMS con Twilio"""
    
    @staticmethod
    def send_sms(to_phone: str, message: str) -> bool:
        """
        Enviar SMS
        
        Args:
            to_phone: Número de teléfono destinatario (formato: +51999888777)
            message: Mensaje a enviar
            
        Returns:
            bool indicando éxito
        """
        try:
            # Verificar que Twilio esté configurado
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                print("Twilio no configurado")
                return False
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            return message.sid is not None
        except Exception as e:
            print(f"Error enviando SMS: {e}")
            return False
    
    @staticmethod
    def send_property_contact_sms(propietario_telefono: str, propiedad_titulo: str, contacto_nombre: str) -> bool:
        """Notificar por SMS sobre contacto de propiedad"""
        message = f"Nuevo contacto para '{propiedad_titulo}' de {contacto_nombre}. Revisa tu email para más detalles."
        return SMSService.send_sms(propietario_telefono, message)
    
    @staticmethod
    def send_verification_code(phone: str, code: str) -> bool:
        """Enviar código de verificación"""
        message = f"Tu código de verificación es: {code}. Válido por 10 minutos."
        return SMSService.send_sms(phone, message)
