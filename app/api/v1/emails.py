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
from app.models.propiedad import Propiedad
from app.dependencies import get_current_active_user
from app.models.usuario import Usuario
import logging
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import base64
from datetime import datetime
from app.services.imagekit_service import imagekit_service
import requests
from reportlab.lib.utils import ImageReader
from PIL import Image

logger = logging.getLogger(__name__)
router = APIRouter()


class EnviarFichasRequest(BaseModel):
    """Schema para solicitud de envío de fichas"""
    to_email: EmailStr
    subject: str = "Propiedades Quadrante"
    message: Optional[str] = ""
    propiedad_ids: List[int]
    send_copy: bool = False
    client_name: Optional[str] = None
    tabla_resumen: Optional[str] = None  # HTML de tabla resumen desde frontend


class GenerarFichasRequest(BaseModel):
    """Schema para generar fichas PDF y obtener URLs"""
    propiedad_ids: List[int]


@router.post("/enviar-fichas")
async def enviar_fichas_por_correo(
    request: EnviarFichasRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📧 Enviar fichas PDF de propiedades por correo

    Requiere autenticación.
    Perfiles permitidos: TODOS (demandante, ofertante, corredor, admin)

    - Recibe lista de IDs de propiedades
    - Genera fichas PDF profesionales (A4)
    - Construye correo HTML con la lista
    - Envía correo con PDFs adjuntos

    Args:
        request: Datos del correo (destinatario, asunto, mensaje, IDs)
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Dict con resultado del envío
    """
    try:
        # Validar que haya propiedades
        if not request.propiedad_ids:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos una propiedad")

        # Limitar a 10 propiedades máximo (para no saturar el correo)
        if len(request.propiedad_ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Máximo 10 propiedades permitidas por correo"
            )

        # Consultar propiedades
        propiedades = db.query(Propiedad).filter(
            Propiedad.registro_cab_id.in_(request.propiedad_ids)
        ).all()

        if not propiedades:
            raise HTTPException(status_code=404, detail="No se encontraron las propiedades")

        logger.info(f"📧 Generando fichas para {len(propiedades)} propiedades")

        # Generar PDFs
        attachments = []
        for propiedad in propiedades:
            try:
                pdf_bytes = generar_ficha_pdf(propiedad)
                codigo = f"PROP_{propiedad.registro_cab_id}"

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
        html_content = construir_html_correo(
            propiedades=propiedades,
            mensaje_personal=request.message,
            tabla_resumen=request.tabla_resumen,
            client_name=request.client_name
        )

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


@router.post("/generar-fichas-urls")
async def generar_fichas_urls(
    request: GenerarFichasRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📄 Generar fichas PDF y obtener URLs de descarga (para WhatsApp)

    Requiere autenticación.

    - Recibe lista de IDs de propiedades
    - Genera fichas PDF profesionales
    - Sube a ImageKit
    - Retorna URLs de descarga

    Args:
        request: Lista de IDs de propiedades
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Dict con URLs de descarga de los PDFs
    """
    try:
        # Validar que haya propiedades
        if not request.propiedad_ids:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos una propiedad")

        # Limitar a 10 propiedades máximo
        if len(request.propiedad_ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Máximo 10 propiedades permitidas"
            )

        # Consultar propiedades
        propiedades = db.query(Propiedad).filter(
            Propiedad.registro_cab_id.in_(request.propiedad_ids)
        ).all()

        if not propiedades:
            raise HTTPException(status_code=404, detail="No se encontraron las propiedades")

        logger.info(f"📄 Generando fichas PDF para WhatsApp: {len(propiedades)} propiedades")

        # Generar PDFs y subir a ImageKit
        fichas_urls = []
        for propiedad in propiedades:
            try:
                # Generar PDF
                pdf_bytes = generar_ficha_pdf(propiedad)
                codigo = f"PROP_{propiedad.registro_cab_id}"
                filename = f"Ficha_{codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                # Subir a ImageKit
                upload_result = imagekit_service.upload_image(
                    file_content=pdf_bytes,
                    file_name=filename,
                    folder="inmobiliaria/fichas-propiedades"
                )

                if upload_result and upload_result.get("url"):
                    fichas_urls.append({
                        "propiedad_id": propiedad.registro_cab_id,
                        "codigo": codigo,
                        "titulo": propiedad.titulo or propiedad.nombre_inmueble or f"Propiedad {codigo}",
                        "url": upload_result["url"],
                        "file_id": upload_result.get("file_id")
                    })
                    logger.info(f"✅ PDF subido a ImageKit: {filename}")
                else:
                    logger.warning(f"⚠️ Error subiendo PDF para {codigo}")

            except Exception as e:
                logger.error(f"❌ Error generando/subiendo PDF para propiedad {propiedad.registro_cab_id}: {e}")
                continue

        if not fichas_urls:
            raise HTTPException(status_code=500, detail="No se pudieron generar los PDFs")

        return {
            "success": True,
            "message": f"Se generaron {len(fichas_urls)} fichas PDF",
            "fichas": fichas_urls,
            "total": len(fichas_urls)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando fichas URLs: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


def generar_ficha_pdf(propiedad: Propiedad) -> bytes:
    """
    Generar ficha PDF profesional de una propiedad
    Diseño moderno y compacto con header elegante

    Args:
        propiedad: Modelo de propiedad

    Returns:
        PDF en bytes
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # 210mm x 297mm

    # Colores corporativos
    COLOR_AZUL_OSCURO = colors.HexColor('#1E3A5F')
    COLOR_AZUL = colors.HexColor('#2C5282')
    COLOR_AZUL_CLARO = colors.HexColor('#3182CE')
    COLOR_GRIS = colors.HexColor('#6B7280')
    COLOR_GRIS_CLARO = colors.HexColor('#F3F4F6')
    COLOR_VERDE = colors.HexColor('#10B981')
    COLOR_DORADO = colors.HexColor('#D4AF37')

    # Márgenes
    margin = 15 * mm
    content_width = width - 2 * margin

    # ===== HEADER ELEGANTE =====
    # Fondo degradado simulado (dos rectángulos)
    c.setFillColor(COLOR_AZUL_OSCURO)
    c.rect(0, height - 35*mm, width, 35*mm, fill=1, stroke=0)

    # Línea decorativa dorada
    c.setStrokeColor(COLOR_DORADO)
    c.setLineWidth(2)
    c.line(0, height - 35*mm, width, height - 35*mm)

    # Logo QUADRANTE estilizado
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin, height - 18*mm, "QUADRANTE")

    # Subtítulo
    c.setFont("Helvetica", 8)
    c.setFillColor(COLOR_DORADO)
    c.drawString(margin, height - 24*mm, "SISTEMA INMOBILIARIO PROFESIONAL")

    # Código de propiedad (badge)
    codigo = f"COD: {propiedad.registro_cab_id}"
    c.setFillColor(COLOR_DORADO)
    c.roundRect(width - margin - 45*mm, height - 22*mm, 45*mm, 10*mm, 2*mm, fill=1, stroke=0)
    c.setFillColor(COLOR_AZUL_OSCURO)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width - margin - 22.5*mm, height - 19*mm, codigo)

    # Fecha
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    fecha = datetime.now().strftime("%d de %B, %Y")
    c.drawRightString(width - margin, height - 30*mm, fecha)

    y = height - 45*mm

    # ===== TÍTULO Y UBICACIÓN =====
    # Nombre del edificio/propiedad
    c.setFillColor(COLOR_AZUL_OSCURO)
    c.setFont("Helvetica-Bold", 16)
    titulo = propiedad.titulo or propiedad.nombre_inmueble or "Oficina en Venta/Alquiler"
    c.drawString(margin, y, titulo[:55])
    y -= 7*mm

    # Ubicación con ícono
    try:
        distrito_nombre = propiedad.distrito.nombre if propiedad.distrito else ''
    except:
        distrito_nombre = ''

    c.setFillColor(COLOR_GRIS)
    c.setFont("Helvetica", 10)
    ubicacion = f"{propiedad.direccion or 'Sin dirección'}"
    if distrito_nombre:
        ubicacion += f" - {distrito_nombre}"
    c.drawString(margin + 5*mm, y, ubicacion[:70])

    # Ícono de ubicación (círculo con punto)
    c.setFillColor(COLOR_AZUL_CLARO)
    c.circle(margin + 2*mm, y + 1.5*mm, 1.5*mm, fill=1, stroke=0)

    y -= 10*mm

    # ===== GALERÍA DE FOTOS (hasta 3 en una fila) =====
    imagenes_urls = []

    # Agregar imagen principal si existe
    if propiedad.imagen_principal:
        imagenes_urls.append(propiedad.imagen_principal)

    # Agregar imágenes adicionales
    if propiedad.imagenes and isinstance(propiedad.imagenes, list):
        for img_url in propiedad.imagenes[:2]:  # Máximo 2 adicionales
            if img_url and img_url not in imagenes_urls:
                imagenes_urls.append(img_url)

    # Limitar a 3 imágenes
    imagenes_urls = imagenes_urls[:3]

    if imagenes_urls:
        img_height = 35*mm
        img_spacing = 3*mm
        num_images = len(imagenes_urls)
        img_width = (content_width - (num_images - 1) * img_spacing) / num_images

        for i, img_url in enumerate(imagenes_urls):
            try:
                # Descargar imagen
                response = requests.get(img_url, timeout=5)
                if response.status_code == 200:
                    img_data = io.BytesIO(response.content)
                    img = Image.open(img_data)

                    # Convertir a RGB si es necesario (para evitar errores con PNG transparentes)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')

                    # Guardar en buffer
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='JPEG', quality=85)
                    img_buffer.seek(0)

                    # Calcular posición
                    x_pos = margin + i * (img_width + img_spacing)

                    # Dibujar fondo gris claro como placeholder
                    c.setFillColor(COLOR_GRIS_CLARO)
                    c.roundRect(x_pos, y - img_height, img_width, img_height, 2*mm, fill=1, stroke=0)

                    # Dibujar imagen
                    c.drawImage(
                        ImageReader(img_buffer),
                        x_pos + 1*mm,
                        y - img_height + 1*mm,
                        width=img_width - 2*mm,
                        height=img_height - 2*mm,
                        preserveAspectRatio=True,
                        mask='auto'
                    )

                    logger.info(f"✅ Imagen {i+1} agregada al PDF")

            except Exception as img_error:
                logger.warning(f"⚠️ No se pudo cargar imagen {i+1}: {img_error}")
                # Dibujar placeholder
                x_pos = margin + i * (img_width + img_spacing)
                c.setFillColor(COLOR_GRIS_CLARO)
                c.roundRect(x_pos, y - img_height, img_width, img_height, 2*mm, fill=1, stroke=0)
                c.setFillColor(COLOR_GRIS)
                c.setFont("Helvetica", 8)
                c.drawCentredString(x_pos + img_width/2, y - img_height/2, "Sin imagen")

        y -= img_height + 8*mm
    else:
        y -= 2*mm

    # ===== INFORMACIÓN PRINCIPAL (Cards) =====
    # Card de Precio
    card_height = 22*mm
    card_width = (content_width - 5*mm) / 2

    # Card 1: Precio Venta
    c.setFillColor(COLOR_GRIS_CLARO)
    c.roundRect(margin, y - card_height, card_width, card_height, 3*mm, fill=1, stroke=0)

    c.setFillColor(COLOR_GRIS)
    c.setFont("Helvetica", 8)
    c.drawString(margin + 4*mm, y - 6*mm, "PRECIO VENTA")

    c.setFillColor(COLOR_AZUL_OSCURO)
    c.setFont("Helvetica-Bold", 16)
    precio_venta = propiedad.precio_venta or 0
    c.drawString(margin + 4*mm, y - 14*mm, f"USD {'{:,.0f}'.format(precio_venta)}")

    # Card 2: Precio Alquiler
    c.setFillColor(COLOR_GRIS_CLARO)
    c.roundRect(margin + card_width + 5*mm, y - card_height, card_width, card_height, 3*mm, fill=1, stroke=0)

    c.setFillColor(COLOR_GRIS)
    c.setFont("Helvetica", 8)
    c.drawString(margin + card_width + 9*mm, y - 6*mm, "PRECIO ALQUILER")

    c.setFillColor(COLOR_AZUL_OSCURO)
    c.setFont("Helvetica-Bold", 16)
    precio_alquiler = propiedad.precio_alquiler or 0
    c.drawString(margin + card_width + 9*mm, y - 14*mm, f"USD {'{:,.0f}'.format(precio_alquiler)}/mes")

    y -= card_height + 8*mm

    # ===== CARACTERÍSTICAS EN GRID =====
    c.setFillColor(COLOR_AZUL_OSCURO)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "CARACTERÍSTICAS")

    # Línea decorativa
    c.setStrokeColor(COLOR_DORADO)
    c.setLineWidth(2)
    c.line(margin, y - 2*mm, margin + 35*mm, y - 2*mm)

    y -= 10*mm

    # Grid de características (3 columnas x 2 filas)
    char_data = [
        ('Área Total', f"{propiedad.area or 0} m²"),
        ('Antigüedad', f"{propiedad.antiguedad or 'N/A'} años"),
        ('Transacción', (propiedad.transaccion or 'venta').capitalize()),
        ('Moneda', propiedad.moneda or 'USD'),
        ('Piso', f"{propiedad.piso or 'N/A'}"),
        ('Estado', 'Disponible'),
    ]

    col_width = content_width / 3
    row_height = 12*mm

    for i, (label, value) in enumerate(char_data):
        col = i % 3
        row = i // 3
        x = margin + col * col_width
        current_y = y - row * row_height

        # Fondo alternado
        if row % 2 == 0:
            c.setFillColor(COLOR_GRIS_CLARO)
            c.rect(x, current_y - row_height + 2*mm, col_width - 2*mm, row_height - 1*mm, fill=1, stroke=0)

        # Label
        c.setFillColor(COLOR_GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x + 3*mm, current_y - 4*mm, label)

        # Value
        c.setFillColor(COLOR_AZUL_OSCURO)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 3*mm, current_y - 9*mm, str(value)[:15])

    y -= 2 * row_height + 8*mm

    # ===== DESCRIPCIÓN =====
    if propiedad.descripcion:
        c.setFillColor(COLOR_AZUL_OSCURO)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, "DESCRIPCIÓN")

        # Línea decorativa
        c.setStrokeColor(COLOR_DORADO)
        c.setLineWidth(2)
        c.line(margin, y - 2*mm, margin + 28*mm, y - 2*mm)

        y -= 8*mm

        # Borde izquierdo decorativo
        c.setFillColor(COLOR_AZUL_CLARO)
        c.rect(margin, y - 25*mm, 2*mm, 25*mm, fill=1, stroke=0)

        # Texto de descripción
        desc = propiedad.descripcion[:400] + "..." if len(propiedad.descripcion) > 400 else propiedad.descripcion

        c.setFillColor(COLOR_GRIS)
        c.setFont("Helvetica", 9)

        # Wrap text
        text_width = content_width - 10*mm
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

        for line in lines[:6]:  # Máximo 6 líneas
            c.drawString(margin + 5*mm, y, line)
            y -= 4*mm

        y -= 5*mm

    # ===== FOOTER ELEGANTE =====
    footer_height = 20*mm

    # Fondo del footer
    c.setFillColor(COLOR_AZUL_OSCURO)
    c.rect(0, 0, width, footer_height, fill=1, stroke=0)

    # Línea dorada superior
    c.setStrokeColor(COLOR_DORADO)
    c.setLineWidth(1.5)
    c.line(0, footer_height, width, footer_height)

    # Texto del footer
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width/2, 12*mm, "QUADRANTE - Tu Socio Inmobiliario de Confianza")

    c.setFont("Helvetica", 7)
    c.setFillColor(COLOR_DORADO)
    c.drawCentredString(width/2, 7*mm, "www.quadrante.com  |  contacto@quadrante.com  |  Lima, Perú")

    # Pequeño detalle decorativo
    c.setFillColor(COLOR_DORADO)
    c.circle(margin, 10*mm, 2*mm, fill=1, stroke=0)
    c.circle(width - margin, 10*mm, 2*mm, fill=1, stroke=0)

    # Finalizar PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


def construir_html_correo(
    propiedades: List[Propiedad],
    mensaje_personal: str,
    tabla_resumen: str = None,
    client_name: str = None
) -> str:
    """
    Construir HTML del correo con lista de propiedades

    Args:
        propiedades: Lista de propiedades
        mensaje_personal: Mensaje con narrativa de búsqueda
        tabla_resumen: HTML de tabla resumen desde frontend
        client_name: Nombre del cliente para saludo

    Returns:
        HTML del correo
    """
    # Saludo personalizado
    saludo = f"Hola {client_name}," if client_name else "Hola,"

    # Convertir mensaje a HTML (reemplazar saltos de línea)
    mensaje_html = ""
    if mensaje_personal:
        # Convertir saltos de línea a <br> y preservar espacios
        mensaje_html = mensaje_personal.replace('\n', '<br>')
        # Convertir emojis de bullets a listas
        mensaje_html = mensaje_html.replace('• ', '&bull; ')
        mensaje_html = mensaje_html.replace('📋', '📋')
        mensaje_html = mensaje_html.replace('🔗', '🔗')
        mensaje_html = mensaje_html.replace('📍', '📍')
        mensaje_html = mensaje_html.replace('📐', '📐')
        mensaje_html = mensaje_html.replace('💰', '💰')
        mensaje_html = mensaje_html.replace('📎', '📎')

    # Usar tabla del frontend si existe, sino generar una básica
    tabla_html = ""
    if tabla_resumen:
        tabla_html = tabla_resumen
    else:
        # Generar tabla básica de propiedades
        props_html = ""
        for prop in propiedades:
            codigo = f"PROP-{prop.registro_cab_id}"
            titulo = prop.titulo or prop.nombre_inmueble or "Propiedad"
            precio = f"${'{:,.0f}'.format(prop.precio_venta or 0)}"
            area = f"{prop.area or 'N/A'} m²"
            try:
                distrito_nombre = prop.distrito.nombre if prop.distrito else ''
            except:
                distrito_nombre = ''

            props_html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{codigo}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{titulo}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{distrito_nombre}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{area}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{precio}</td>
            </tr>
            """

        tabla_html = f"""
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background: #0066CC; color: white;">
                    <th style="padding: 10px; border: 1px solid #0066CC;">Código</th>
                    <th style="padding: 10px; border: 1px solid #0066CC;">Propiedad</th>
                    <th style="padding: 10px; border: 1px solid #0066CC;">Distrito</th>
                    <th style="padding: 10px; border: 1px solid #0066CC;">Área</th>
                    <th style="padding: 10px; border: 1px solid #0066CC;">Precio</th>
                </tr>
            </thead>
            <tbody>
                {props_html}
            </tbody>
        </table>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 750px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2C5282 0%, #1e3a5f 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .message-section {{ background: #f8f9fa; border-radius: 10px; padding: 25px; margin: 20px 0; line-height: 1.8; font-size: 14px; color: #333; }}
            .table-section {{ margin: 25px 0; }}
            .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #6c757d; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">🏠 QUADRANTE</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Propiedades Seleccionadas para Ti</p>
            </div>

            <div class="content">
                <!-- Mensaje narrativo con formato -->
                <div class="message-section">
                    {mensaje_html if mensaje_html else f"<p>{saludo}</p><p>Te enviamos información de {len(propiedades)} propiedad(es) que podrían interesarte.</p>"}
                </div>

                <!-- Tabla resumen -->
                <div class="table-section">
                    <h3 style="color: #2C5282; margin-bottom: 15px;">📊 Resumen de Propiedades</h3>
                    {tabla_html}
                </div>

                <div style="background: #E8F5E9; border-radius: 8px; padding: 15px; margin-top: 25px; text-align: center;">
                    <p style="margin: 0; color: #2e7d32; font-weight: 600;">
                        📎 Revisa los archivos PDF adjuntos para ver las fichas detalladas de cada oficina
                    </p>
                </div>
            </div>

            <div class="footer">
                <p style="margin: 0;"><strong>QUADRANTE</strong> - Sistema Inmobiliario Profesional</p>
                <p style="margin: 5px 0;">www.quadrante.com | contacto@quadrante.com</p>
                <p style="margin-top: 15px; font-size: 11px; color: #999;">
                    Este es un correo automático generado desde el sistema Quadrante.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return html
