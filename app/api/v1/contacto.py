from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service

router = APIRouter()


class ContactoRequest(BaseModel):
    nombre: str
    email: EmailStr
    mensaje: str


@router.post("", status_code=status.HTTP_200_OK)
async def enviar_contacto(datos: ContactoRequest):
    """Recibe mensaje de contacto desde la landing page y lo envía por email."""
    destinatario = "informes@qadrante2.com"
    asunto = f"Qadrante - Nuevo mensaje de {datos.nombre}"
    contenido_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0f4761;">Nuevo mensaje de contacto</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; font-weight: bold; color: #333;">Nombre:</td>
                <td style="padding: 8px;">{datos.nombre}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold; color: #333;">Email:</td>
                <td style="padding: 8px;"><a href="mailto:{datos.email}">{datos.email}</a></td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold; color: #333;">Mensaje:</td>
                <td style="padding: 8px;">{datos.mensaje}</td>
            </tr>
        </table>
        <hr style="border: 1px solid #e0e0e0; margin-top: 20px;">
        <p style="color: #666; font-size: 12px;">Enviado desde el formulario de contacto de Qadrante</p>
    </div>
    """

    try:
        await email_service.send_email_with_attachments(
            to_email=destinatario,
            subject=asunto,
            html_content=contenido_html
        )
        return {
            "success": True,
            "message": "Mensaje enviado correctamente"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar el mensaje. Intenta más tarde."
        )
