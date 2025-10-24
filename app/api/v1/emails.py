"""
📧 Endpoint para envío de correos con fichas de propiedades
Sistema Inmobiliario - Envío de fichas PDF profesionales
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.services.email_service import email_service
from app.database import get_db
from app.models.propiedad import RegistroXInmuebleCab
import logging
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import base64
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


class EnviarFichasRequest(BaseModel):
    """Schema para solicitud de envío de fichas"""
    to_email: EmailStr
    subject: str = "Propiedades Quadrante"
    message: Optional[str] = ""
    propiedad_ids: List[int]
    send_copy: bool = False


@router.post("/enviar-fichas")
async def enviar_fichas_por_correo(
    request: EnviarFichasRequest,
    db: Session = Depends(get_db)
):
    """
    📧 Enviar fichas PDF de propiedades por correo

    - Recibe lista de IDs de propiedades
    - Genera fichas PDF profesionales (A4)
    - Construye correo HTML con la lista
    - Envía correo con PDFs adjuntos

    Args:
        request: Datos del correo (destinatario, asunto, mensaje, IDs)
        db: Sesión de base de datos

    Returns:
        Dict con resultado del envío
    """
    try:
        # Validar que haya propiedades
        if not request.propiedad_ids:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos una propiedad")

        # Limitar a 4 propiedades máximo (para no saturar el correo)
        if len(request.propiedad_ids) > 4:
            raise HTTPException(
                status_code=400,
                detail="Máximo 4 propiedades permitidas por correo"
            )

        # Consultar propiedades
        propiedades = db.query(RegistroXInmuebleCab).filter(
            RegistroXInmuebleCab.registro_cab_id.in_(request.propiedad_ids)
        ).all()

        if not propiedades:
            raise HTTPException(status_code=404, detail="No se encontraron las propiedades")

        logger.info(f"📧 Generando fichas para {len(propiedades)} propiedades")

        # Generar PDFs
        attachments = []
        for propiedad in propiedades:
            try:
                pdf_bytes = generar_ficha_pdf(propiedad)
                codigo = propiedad.codigo or f"PROP_{propiedad.registro_cab_id}"

                attachments.append({
                    "filename": f"Propiedad_{codigo}.pdf",
                    "content": base64.b64encode(pdf_bytes).decode('utf-8'),
                    "content_type": "application/pdf"
                })

                logger.info(f"✅ PDF generado para propiedad {codigo}")

            except Exception as e:
                logger.error(f"❌ Error generando PDF para propiedad {propiedad.registro_cab_id}: {e}")
                continue

        if not attachments:
            raise HTTPException(status_code=500, detail="No se pudieron generar los PDFs")

        # Construir HTML del correo
        html_content = construir_html_correo(propiedades, request.message)

        # Enviar correo
        result = await email_service.send_email_with_attachments(
            to_email=request.to_email,
            subject=request.subject,
            html_content=html_content,
            attachments=attachments
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Fichas enviadas correctamente",
                "propiedades_enviadas": len(attachments),
                "destinatario": request.to_email
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Error enviando correo"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en envío de fichas: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


def generar_ficha_pdf(propiedad: RegistroXInmuebleCab) -> bytes:
    """
    Generar ficha PDF profesional de una propiedad

    Args:
        propiedad: Modelo de propiedad

    Returns:
        PDF en bytes
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # 210mm x 297mm

    # Colores corporativos
    COLOR_AZUL = colors.HexColor('#2C5282')
    COLOR_GRIS = colors.HexColor('#6B7280')

    # Márgenes
    margin = 20 * mm
    y = height - margin

    # ===== HEADER CON LOGO =====
    c.setFillColor(COLOR_AZUL)
    c.rect(0, height - 50*mm, width, 50*mm, fill=1, stroke=0)

    # Título "QUADRANTE" (simulando logo)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, height - 35*mm, "QUADRANTE")

    # Código y fecha
    codigo = propiedad.codigo or f"PROP-{propiedad.registro_cab_id}"
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(width - margin, height - 30*mm, codigo)

    c.setFont("Helvetica", 10)
    fecha = datetime.now().strftime("%d/%m/%Y")
    c.drawRightString(width - margin, height - 40*mm, fecha)

    y = height - 60*mm

    # ===== TÍTULO Y UBICACIÓN =====
    c.setFillColor(COLOR_AZUL)
    c.setFont("Helvetica-Bold", 16)
    titulo = propiedad.nombre_inmueble or "Propiedad en Venta/Alquiler"
    c.drawString(margin, y, titulo[:60])  # Limitar longitud
    y -= 8*mm

    c.setFillColor(COLOR_GRIS)
    c.setFont("Helvetica", 11)
    ubicacion = f"📍 {propiedad.direccion or ''}, {propiedad.distrito.nombre if propiedad.distrito else ''}"
    c.drawString(margin, y, ubicacion[:80])
    y -= 15*mm

    # ===== DESCRIPCIÓN =====
    if propiedad.descripcion:
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Descripción")
        y -= 6*mm

        # Recortar descripción a 300 caracteres
        desc = propiedad.descripcion[:300] + "..." if len(propiedad.descripcion) > 300 else propiedad.descripcion

        # Texto multi-línea
        c.setFont("Helvetica", 9)
        text_width = width - 2 * margin
        lines = []
        words = desc.split()
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 9) < text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for line in lines[:4]:  # Máximo 4 líneas
            c.drawString(margin, y, line)
            y -= 4*mm

        y -= 5*mm

    # ===== TABLA DE CARACTERÍSTICAS =====
    c.setFillColor(COLOR_AZUL)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Características Principales")
    y -= 8*mm

    # Datos de la tabla
    data = [
        ['Área Total', f"{propiedad.area or 'N/A'} m²", 'Precio', f"$ {'{:,.0f}'.format(propiedad.precio_venta or 0)}"],
        ['Habitaciones', str(propiedad.habitaciones or 'N/A'), 'Baños', str(propiedad.banos or 'N/A')],
        ['Parqueos', str(propiedad.parqueos or '0'), 'Antigüedad', f"{propiedad.antiguedad or 'N/A'} años"],
    ]

    table = Table(data, colWidths=[40*mm, 40*mm, 40*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOT TOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    table_width, table_height = table.wrap(0, 0)
    table.drawOn(c, margin, y - table_height)
    y -= table_height + 10*mm

    # ===== FOOTER =====
    c.setFillColor(colors.lightgrey)
    c.rect(0, 0, width, 25*mm, fill=1, stroke=0)

    c.setFillColor(COLOR_GRIS)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, 15*mm, "QUADRANTE - Sistema Inmobiliario Profesional")

    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 10*mm, "www.quadrante.com | contacto@quadrante.com")

    # Finalizar PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


def construir_html_correo(propiedades: List[RegistroXInmuebleCab], mensaje_personal: str) -> str:
    """
    Construir HTML del correo con lista de propiedades

    Args:
        propiedades: Lista de propiedades
        mensaje_personal: Mensaje opcional del usuario

    Returns:
        HTML del correo
    """
    # Lista de propiedades
    props_html = ""
    for prop in propiedades:
        codigo = prop.codigo or f"PROP-{prop.registro_cab_id}"
        titulo = prop.nombre_inmueble or "Propiedad"
        precio = f"${'{:,.0f}'.format(prop.precio_venta or 0)}"
        area = f"{prop.area or 'N/A'} m²"
        ubicacion = f"{prop.direccion or ''}, {prop.distrito.nombre if prop.distrito else ''}"

        props_html += f"""
        <tr>
            <td style="padding: 15px; border-bottom: 1px solid #e0e0e0;">
                <div style="display: flex; gap: 15px; align-items: start;">
                    <div style="flex: 1;">
                        <div style="font-size: 16px; font-weight: 600; color: #2C5282; margin-bottom: 5px;">
                            {codigo} - {titulo}
                        </div>
                        <div style="font-size: 14px; color: #6B7280; margin-bottom: 8px;">
                            📍 {ubicacion}
                        </div>
                        <div style="display: flex; gap: 15px; font-size: 13px; color: #374151;">
                            <span><strong>Precio:</strong> {precio}</span>
                            <span><strong>Área:</strong> {area}</span>
                        </div>
                    </div>
                </div>
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2C5282 0%, #1e3a5f 100%); color: white; padding: 40px 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .message-box {{ background: #f9fafb; border-left: 4px solid #2C5282; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .properties-list {{ margin: 20px 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }}
            .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #6c757d; font-size: 13px; }}
            .btn {{ display: inline-block; background: #2C5282; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">🏠 QUADRANTE</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Propiedades Seleccionadas para Ti</p>
            </div>
            <div class="content">
                <p>Hola,</p>
                <p>Te enviamos la información detallada de <strong>{len(propiedades)} {'propiedad' if len(propiedades) == 1 else 'propiedades'}</strong> que podrían interesarte.</p>

                {f'<div class="message-box"><p style="margin: 0; color: #374151;">{mensaje_personal}</p></div>' if mensaje_personal else ''}

                <h3 style="color: #2C5282; margin-top: 25px;">Propiedades Adjuntas:</h3>
                <table class="properties-list" style="width: 100%; border-collapse: collapse;">
                    {props_html}
                </table>

                <p style="margin-top: 25px; text-align: center;">
                    <strong>📎 Revisa los archivos PDF adjuntos para más detalles</strong>
                </p>

                <p style="text-align: center; margin-top: 30px; color: #6B7280; font-size: 14px;">
                    ¿Tienes preguntas? Contáctanos, estamos para ayudarte.
                </p>
            </div>
            <div class="footer">
                <p style="margin: 0;"><strong>QUADRANTE</strong> - Sistema Inmobiliario Profesional</p>
                <p style="margin: 5px 0;">www.quadrante.com | contacto@quadrante.com</p>
                <p style="margin-top: 15px; font-size: 11px;">Este es un correo automático, por favor no responder directamente.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html
