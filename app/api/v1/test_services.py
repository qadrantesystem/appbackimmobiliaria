"""
🧪 Endpoint de prueba para servicios externos
Sistema Inmobiliario - Testing SendGrid e ImageKit
"""
from fastapi import APIRouter, HTTPException
from app.services.email_service import email_service
from app.services.imagekit_service import imagekit_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/sendgrid")
async def test_sendgrid():
    """
    🧪 Probar conexión con SendGrid
    """
    try:
        # Verificar configuración
        config_info = {
            "api_key_configured": bool(settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != ""),
            "api_key_prefix": settings.SENDGRID_API_KEY[:10] if settings.SENDGRID_API_KEY else "NO CONFIGURADA",
            "from_email": settings.SENDGRID_FROM_EMAIL,
            "from_name": settings.SENDGRID_FROM_NAME,
            "sendgrid_initialized": email_service.sendgrid is not None
        }
        
        # Intentar enviar email de prueba
        if email_service.sendgrid:
            result = await email_service.send_verification_email(
                email="test@example.com",
                name="Test User",
                verification_code="123456"
            )
            
            return {
                "success": True,
                "message": "SendGrid configurado correctamente",
                "config": config_info,
                "test_result": result
            }
        else:
            return {
                "success": False,
                "message": "SendGrid NO está inicializado",
                "config": config_info
            }
            
    except Exception as e:
        logger.error(f"❌ Error en test de SendGrid: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "config": config_info if 'config_info' in locals() else {}
        }

@router.get("/imagekit")
async def test_imagekit():
    """
    🧪 Probar conexión con ImageKit
    """
    try:
        config_info = {
            "private_key_configured": bool(settings.IMAGEKIT_PRIVATE_KEY),
            "private_key_prefix": settings.IMAGEKIT_PRIVATE_KEY[:15] if settings.IMAGEKIT_PRIVATE_KEY else "NO CONFIGURADA",
            "public_key": settings.IMAGEKIT_PUBLIC_KEY[:15] if settings.IMAGEKIT_PUBLIC_KEY else "NO CONFIGURADA",
            "url_endpoint": settings.IMAGEKIT_URL_ENDPOINT,
            "imagekit_initialized": imagekit_service.imagekit is not None
        }
        
        return {
            "success": True,
            "message": "ImageKit configurado correctamente" if imagekit_service.imagekit else "ImageKit NO inicializado",
            "config": config_info
        }
        
    except Exception as e:
        logger.error(f"❌ Error en test de ImageKit: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

@router.post("/send-email")
async def send_test_email(email: str):
    """
    📧 Enviar email de prueba a una dirección específica
    """
    try:
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Email inválido")
        
        result = await email_service.send_verification_email(
            email=email,
            name="Usuario de Prueba",
            verification_code="TEST123"
        )
        
        if result:
            return {
                "success": True,
                "message": f"Email de prueba enviado exitosamente a {email}",
                "email": email
            }
        else:
            return {
                "success": False,
                "message": "Error al enviar email",
                "email": email
            }
            
    except Exception as e:
        logger.error(f"❌ Error enviando email de prueba: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/all")
async def test_all_services():
    """
    🧪 Probar todos los servicios
    """
    sendgrid_test = await test_sendgrid()
    imagekit_test = await test_imagekit()
    
    return {
        "sendgrid": sendgrid_test,
        "imagekit": imagekit_test,
        "summary": {
            "sendgrid_ok": sendgrid_test.get("success", False),
            "imagekit_ok": imagekit_test.get("success", False),
            "all_ok": sendgrid_test.get("success", False) and imagekit_test.get("success", False)
        }
    }
