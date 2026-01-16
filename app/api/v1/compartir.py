"""
📤 Endpoints para Compartir Propiedades
Sistema Inmobiliario CUADRANTE
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.services.whatsapp_service import whatsapp_service
from app.database import get_db
from app.models.propiedad import Propiedad
from app.dependencies import get_current_active_user
from app.models.usuario import Usuario
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class CompartirWhatsAppRequest(BaseModel):
    """Schema para compartir por WhatsApp"""
    to_phone: str  # Formato: +51999999999
    message: Optional[str] = ""
    propiedad_ids: List[int]


@router.post("/whatsapp")
async def compartir_por_whatsapp(
    request: CompartirWhatsAppRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)  # ✅ Requiere autenticación
):
    """
    📱 Compartir propiedades por WhatsApp con PDFs adjuntos

    Perfiles permitidos:
    - Demandante (perfil_id = 1)
    - Ofertante (perfil_id = 2)
    - Corredor (perfil_id = 3)
    - Administrador (perfil_id = 4)

    Args:
        request: Datos para compartir (teléfono, mensaje, IDs de propiedades)
        current_user: Usuario autenticado

    Returns:
        Dict con resultado del envío
    """
    try:
        logger.info(f"📱 Usuario {current_user.usuario_id} compartiendo por WhatsApp a {request.to_phone}")

        # Validar que haya propiedades
        if not request.propiedad_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe seleccionar al menos una propiedad"
            )

        # Limitar a 3 propiedades por WhatsApp
        if len(request.propiedad_ids) > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo 3 propiedades por WhatsApp"
            )

        # Validar formato de teléfono (debe empezar con +)
        if not request.to_phone.startswith("+"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El teléfono debe incluir el código de país (ej: +51999999999)"
            )

        # Consultar propiedades
        propiedades = db.query(Propiedad).filter(
            Propiedad.registro_cab_id.in_(request.propiedad_ids)
        ).all()

        if not propiedades:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propiedades no encontradas"
            )

        # TODO: Generar PDFs (reutilizar lógica de email_service)
        # Por ahora, urls vacías (se implementará cuando se integre generador de PDFs)
        pdf_urls = []

        # Preparar datos de propiedades
        propiedades_data = []
        for p in propiedades:
            propiedades_data.append({
                "registro_cab_id": p.registro_cab_id,
                "titulo": p.titulo,
                "nombre_inmueble": p.nombre_inmueble,
                "area": float(p.area) if p.area else 0,
                "precio_venta": float(p.precio_venta) if p.precio_venta else None,
                "precio_alquiler": float(p.precio_alquiler) if p.precio_alquiler else None,
                "distrito": p.distrito.nombre if p.distrito else None
            })

        logger.info(f"📊 Preparando envío de {len(propiedades)} propiedades")

        # Enviar por WhatsApp
        result = await whatsapp_service.enviar_propiedades(
            to_phone=request.to_phone,
            propiedades_data=propiedades_data,
            pdf_urls=pdf_urls,
            mensaje_personal=request.message
        )

        if result.get("success"):
            logger.info(f"✅ WhatsApp enviado exitosamente a {request.to_phone}")
            return {
                "success": True,
                "message": "Propiedades compartidas por WhatsApp",
                "propiedades_enviadas": len(propiedades),
                "destinatario": request.to_phone,
                "nota": "Integración con WhatsApp API pendiente - mensaje simulado"
            }
        else:
            logger.error(f"❌ Error enviando WhatsApp: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Error enviando WhatsApp")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error compartiendo por WhatsApp: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
