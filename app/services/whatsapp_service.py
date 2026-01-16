"""
📱 Servicio de WhatsApp
Sistema Inmobiliario CUADRANTE
"""
import requests
import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Servicio para envío por WhatsApp Web API"""

    def __init__(self):
        """Inicializar servicio de WhatsApp"""
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', '')
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
        self.from_number = getattr(settings, 'WHATSAPP_FROM_NUMBER', '+51999999999')

    async def enviar_propiedades(
        self,
        to_phone: str,
        propiedades_data: List[Dict],
        pdf_urls: List[str],
        mensaje_personal: str = ""
    ) -> Dict[str, Any]:
        """
        Envía mensaje de WhatsApp con propiedades y PDFs

        Args:
            to_phone: Número de teléfono destino (formato: +51999999999)
            propiedades_data: Lista de propiedades con datos
            pdf_urls: Lista de URLs de PDFs generados
            mensaje_personal: Mensaje opcional del usuario

        Returns:
            Dict con success, message, etc.
        """
        try:
            # Construir mensaje
            mensaje = self._construir_mensaje_whatsapp(
                propiedades_data,
                mensaje_personal
            )

            # Enviar mensaje de texto
            result_text = await self._enviar_mensaje_texto(to_phone, mensaje)

            if not result_text.get("success"):
                return result_text

            # Enviar PDFs como documentos
            for idx, pdf_url in enumerate(pdf_urls):
                await self._enviar_documento(
                    to_phone,
                    pdf_url,
                    f"Propiedad_{idx + 1}.pdf"
                )

            return {
                "success": True,
                "message": "Propiedades enviadas por WhatsApp exitosamente",
                "phone": to_phone,
                "propiedades_enviadas": len(propiedades_data)
            }

        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp: {e}")
            return {
                "success": False,
                "message": f"Error enviando WhatsApp: {str(e)}"
            }

    def _construir_mensaje_whatsapp(
        self,
        propiedades: List[Dict],
        mensaje_personal: str
    ) -> str:
        """Construye el mensaje de texto para WhatsApp"""

        mensaje = "🏠 *QUADRANTE - Propiedades Seleccionadas*\n\n"

        if mensaje_personal:
            mensaje += f"_{mensaje_personal}_\n\n"

        mensaje += f"Te envío *{len(propiedades)} {'propiedad' if len(propiedades) == 1 else 'propiedades'}* que podrían interesarte:\n\n"

        for idx, prop in enumerate(propiedades, 1):
            codigo = f"PROP-{prop['registro_cab_id']}"
            titulo = prop.get('titulo') or prop.get('nombre_inmueble') or "Propiedad"
            area = prop.get('area', 'N/A')
            precio = prop.get('precio_venta') or prop.get('precio_alquiler') or 0
            distrito = prop.get('distrito', '')

            mensaje += f"*{idx}. {codigo}*\n"
            mensaje += f"📍 {titulo}\n"
            mensaje += f"   {distrito} | {area} m²\n"
            mensaje += f"   💰 ${precio:,.0f}\n\n"

        mensaje += "📎 *Revisa los PDF adjuntos para más detalles*\n\n"
        mensaje += "¿Tienes preguntas? ¡Contáctanos!\n"
        mensaje += "www.quadrante.com"

        return mensaje

    async def _enviar_mensaje_texto(
        self,
        to_phone: str,
        mensaje: str
    ) -> Dict[str, Any]:
        """Envía mensaje de texto por WhatsApp API"""

        # TODO: Implementar según proveedor (Twilio, Meta Business API, etc.)
        # Ejemplo con Twilio:
        """
        payload = {
            "from": f"whatsapp:{self.from_number}",
            "to": f"whatsapp:{to_phone}",
            "body": mensaje
        }

        response = requests.post(
            self.api_url,
            auth=(self.api_token, ""),
            data=payload
        )

        if response.status_code == 201:
            return {"success": True}
        else:
            return {
                "success": False,
                "message": f"Error API: {response.text}"
            }
        """

        logger.warning("⚠️ WhatsApp Service: Implementar integración con proveedor")
        logger.info(f"📱 [SIMULADO] Enviando WhatsApp a {to_phone}")
        logger.info(f"📝 Mensaje:\n{mensaje}")

        # Por ahora retornar mock success
        return {
            "success": True,
            "message": "WhatsApp simulado (implementar integración real)"
        }

    async def _enviar_documento(
        self,
        to_phone: str,
        pdf_url: str,
        filename: str
    ) -> Dict[str, Any]:
        """Envía documento PDF por WhatsApp"""

        # TODO: Implementar según proveedor
        logger.info(f"📎 [SIMULADO] Enviando PDF: {filename} a {to_phone}")

        return {"success": True}


# Instancia global
whatsapp_service = WhatsAppService()
