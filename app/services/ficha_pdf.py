"""
📄 Ficha inmobiliaria A4 — Cuadrante
Genera un PDF profesional (oficinas corporativas) a partir de la ficha del inmueble.
Homologa: EDIFICIO (nivel 1) + UNIDAD (nivel 2) + COMERCIALIZACIÓN (nivel 3).
"""
import io
import os
import logging
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

import requests

logger = logging.getLogger(__name__)

# ---------------- Paleta ----------------
NAVY = colors.HexColor("#0B2A4A")
NAVY2 = colors.HexColor("#123E6B")
TEAL = colors.HexColor("#0E718D")
ORANGE = colors.HexColor("#FF9800")
GREY = colors.HexColor("#5F6F78")
DARK = colors.HexColor("#1F2937")
BORDER = colors.HexColor("#D6DEE6")
GREY_L = colors.HexColor("#EEF2F6")
WHITE = colors.white

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS, "logo-qadrante.png")


# ---------------- helpers ----------------
def _v(caract, *ids):
    """Primer valor no vacío entre los IDs de característica."""
    if not caract:
        return None
    for i in ids:
        val = caract.get(i)
        if val not in (None, "", "None"):
            return val
    return None


def _si(caract, *ids):
    val = _v(caract, *ids)
    if val is None:
        return "-"
    return "Sí" if str(val).strip().lower() in ("si", "sí", "1", "true", "yes") else str(val)


def _wrap(c, text, font, size, maxw):
    words = str(text or "").split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _title_bar(c, x, y, w, text, h=5.4 * mm):
    c.setFillColor(NAVY)
    c.rect(x, y - h, w, h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawString(x + 1.6 * mm, y - h + 1.7 * mm, text.upper())
    return y - h


def _kv(c, x, y, w, rows, rowh=4.9 * mm, labelw=0.55):
    for k, v in rows:
        c.setFillColor(WHITE)
        c.rect(x, y - rowh, w, rowh, fill=1, stroke=0)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.25)
        c.rect(x, y - rowh, w, rowh, fill=0, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 6.0)
        c.drawString(x + 1.3 * mm, y - rowh + 1.5 * mm, str(k)[:38])
        c.setFillColor(DARK)
        c.setFont("Helvetica", 6.0)
        c.drawRightString(x + w - 1.3 * mm, y - rowh + 1.5 * mm, str(v)[:24])
        y -= rowh
    return y


def _box_border(c, x, y, w, h):
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.4)
    c.rect(x, y, w, h, fill=0, stroke=1)


def _img(url, timeout=6):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200 and r.content:
            return ImageReader(io.BytesIO(r.content))
    except Exception as e:
        logger.warning(f"ficha: no se pudo cargar imagen {url}: {e}")
    return None


def cargar_contexto_ficha(db, propiedad):
    """Carga características (EAV) de la unidad + edificio y datos del edificio."""
    from app.models.propiedad import Propiedad
    from app.models.propiedad_detalle import PropiedadDetalle
    from app.models.tipo_inmueble import TipoInmueble

    def car(rid):
        try:
            rows = db.query(PropiedadDetalle).filter(PropiedadDetalle.registro_cab_id == rid).all()
            return {d.caracteristica_id: d.valor for d in rows}
        except Exception:
            return {}

    caract = car(propiedad.registro_cab_id)
    edif, edif_car = None, {}
    padre = getattr(propiedad, "padre_registro_cab_id", None)
    if padre:
        edif = db.query(Propiedad).filter(Propiedad.registro_cab_id == padre).first()
        if edif:
            edif_car = car(edif.registro_cab_id)

    tipo = None
    try:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == propiedad.tipo_inmueble_id).first()
    except Exception:
        pass

    distrito = None
    try:
        distrito = propiedad.distrito.nombre
    except Exception:
        pass

    edificio = {
        "nombre": (edif.titulo or edif.nombre_inmueble) if edif else (propiedad.titulo or propiedad.nombre_inmueble),
        "direccion": (edif.direccion if edif else propiedad.direccion),
        "distrito": distrito,
        "departamento": "Lima",
        "pais": "Perú",
        "descripcion": (edif.descripcion if edif else propiedad.descripcion),
        "tipo": tipo.nombre if tipo else "Oficina Corporativa",
    }
    return caract, edificio, edif_car


def generar_ficha_pdf(propiedad, caracteristicas=None, edificio=None, edificio_caracteristicas=None) -> bytes:
    """
    Genera la ficha A4.
    - propiedad: objeto Propiedad (usa attributes con getattr)
    - caracteristicas: dict {caracteristica_id: valor} de la UNIDAD
    - edificio: dict {nombre, direccion, distrito, departamento, pais, descripcion, tipo}
    - edificio_caracteristicas: dict {caracteristica_id: valor} del EDIFICIO
    """
    caracteristicas = caracteristicas or {}
    edificio_caracteristicas = edificio_caracteristicas or {}
    edificio = edificio or {}

    g = lambda o, k, d=None: getattr(o, k, d)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    M = 9 * mm
    CW = W - 2 * M

    # ============ HEADER ============
    hh = 26 * mm
    c.setFillColor(NAVY)
    c.rect(0, H - hh, W, hh, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H - hh, W * 0.62, hh, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.rect(0, H - hh, W * 0.56, hh, fill=1, stroke=0)

    c.setFillColor(ORANGE)
    c.rect(M, H - 9 * mm, 4 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M + 6 * mm, H - 8.4 * mm, "FICHA DE INMUEBLE")
    c.setFont("Helvetica-Bold", 20)
    c.drawString(M, H - 19 * mm, "OFICINAS CORPORATIVAS")

    # logo (transparente)
    try:
        if os.path.isfile(LOGO_PATH):
            c.drawImage(LOGO_PATH, W - M - 52 * mm, H - 20 * mm, width=52 * mm, height=17 * mm,
                        preserveAspectRatio=True, anchor='e', mask='auto')
    except Exception as e:
        logger.warning(f"ficha: logo no dibujado: {e}")

    # ============ INFO GENERAL DEL EDIFICIO + IMÁGENES ============
    y = H - hh - 4 * mm
    right_w = CW * 0.40
    left_w = CW - right_w - 3 * mm
    rows = [
        ("Nombre del Edificio", edificio.get("nombre") or g(propiedad, "titulo") or "-"),
        ("Dirección", edificio.get("direccion") or g(propiedad, "direccion") or "-"),
        ("Numeración", _v(edificio_caracteristicas, 106) or "-"),
        ("Urbanización", _v(edificio_caracteristicas, 107) or "-"),
        ("Distrito", edificio.get("distrito") or "-"),
        ("Departamento", _v(edificio_caracteristicas, 108) or edificio.get("departamento") or "Lima"),
        ("País", _v(edificio_caracteristicas, 109) or "Perú"),
    ]
    y_after = _title_bar(c, M, y, left_w, "Información General del Edificio")
    y_after = _kv(c, M, y_after, left_w, rows, rowh=5.4 * mm)
    _box_border(c, M, y_after, left_w, y - y_after)

    # imágenes (principal + hasta 3)
    imgs = []
    if g(propiedad, "imagen_principal"):
        imgs.append(g(propiedad, "imagen_principal"))
    arr = g(propiedad, "imagenes") or []
    if isinstance(arr, (list, tuple)):
        for u in arr:
            if u and u not in imgs:
                imgs.append(u)
    imgs = imgs[:4]

    ix = M + left_w + 3 * mm
    if imgs:
        big_h = 26 * mm
        big = _img(imgs[0])
        if big:
            c.drawImage(big, ix, y - big_h, width=right_w, height=big_h, preserveAspectRatio=True,
                        anchor='c', mask='auto')
        small = imgs[1:4]
        if small:
            sh = 9 * mm
            sw = (right_w - 2 * (1.5 * mm)) / 3
            for i, u in enumerate(small):
                ir = _img(u)
                if ir:
                    c.drawImage(ir, ix + i * (sw + 1.5 * mm), y - big_h - 2 * mm - sh, width=sw, height=sh,
                                preserveAspectRatio=True, anchor='c', mask='auto')
        y = y - big_h - (11 * mm if small else 2 * mm)
    else:
        y = y - 2 * mm

    # ============ DESCRIPCIÓN ============
    desc = edificio.get("descripcion") or g(propiedad, "descripcion") or ""
    y = _title_bar(c, M, y, CW, "Descripción General del Edificio")
    yy = y - 1.5 * mm
    lines = _wrap(c, desc, "Helvetica", 6.4, CW - 4 * mm)[:3]
    for ln in lines:
        yy -= 3.6 * mm
        c.setFillColor(DARK)
        c.setFont("Helvetica", 6.4)
        c.drawString(M + 2 * mm, yy, ln)
    y = yy - 3 * mm
    _box_border(c, M, y, CW, (y if False else 0) or 0)  # noop container (visual handled below)

    # ============ FILA 3 COLUMNAS ============
    colgap = 3 * mm
    cw3 = (CW - 2 * colgap) / 3
    x1 = M
    x2 = M + cw3 + colgap
    x3 = M + 2 * (cw3 + colgap)

    # Col 1: GENERALES
    y1 = _title_bar(c, x1, y, cw3, "Generales")
    gen = [
        ("Año de construcción", _v(edificio_caracteristicas, 170) or "-"),
        ("Cantidad de pisos", _v(edificio_caracteristicas, 110) or "-"),
        ("Cantidad de sótanos", _v(edificio_caracteristicas, 111) or "-"),
        ("Locales comerciales", _si(edificio_caracteristicas, 7)),
        ("Cafetería", _si(edificio_caracteristicas, 8)),
        ("Gym", _si(edificio_caracteristicas, 9)),
        ("Of. Trámite Documentos", _si(edificio_caracteristicas, 10)),
        ("Sala de Reuniones", _si(edificio_caracteristicas, 11)),
        ("SUM", _si(edificio_caracteristicas, 12)),
        ("Comedor", _si(edificio_caracteristicas, 13)),
        ("Depósito", _si(edificio_caracteristicas, 14)),
        ("RoofTop", _si(edificio_caracteristicas, 15)),
        ("Area After Office", _si(edificio_caracteristicas, 16)),
        ("Duchas y Vestuarios", _si(edificio_caracteristicas, 17)),
        ("Helipuerto", _si(edificio_caracteristicas, 18)),
    ]
    y1 = _kv(c, x1, y1, cw3, gen, rowh=4.4 * mm)
    _box_border(c, x1, y1, cw3, y - y1)

    # Col 2: EQUIPAMIENTO + SOPORTE
    y2 = _title_bar(c, x2, y, cw3, "Equipamiento")
    eq = [
        ("Ascensores (total)", _v(edificio_caracteristicas, 119) or "-"),
        ("Montacarga", _si(edificio_caracteristicas, 19)),
        ("De sótano a piso 1", _si(edificio_caracteristicas, 21)),
        ("De sótano a oficina VIP", _si(edificio_caracteristicas, 20)),
        ("Parqueo bicicletas", _si(edificio_caracteristicas, 4)),
        ("Carga veh. eléctricos", _si(edificio_caracteristicas, 5)),
    ]
    y2 = _kv(c, x2, y2, cw3, eq, rowh=4.4 * mm)
    y2 = _title_bar(c, x2, y2 - 1.5 * mm, cw3, "Soporte del Edificio")
    sop = [
        ("Grupo electrógeno", _si(edificio_caracteristicas, 32)),
        ("Encendido automático", _si(edificio_caracteristicas, 34)),
        ("Chiller para AACC", _si(edificio_caracteristicas, 35)),
        ("Cuarto técnico", _si(edificio_caracteristicas, 36)),
        ("Fibra óptica", _si(edificio_caracteristicas, 37)),
        ("Recepción / Seguridad", _si(edificio_caracteristicas, 38)),
    ]
    y2 = _kv(c, x2, y2, cw3, sop, rowh=4.4 * mm)
    _box_border(c, x2, y2, cw3, y - y2)

    # Col 3: SEGURIDAD
    y3 = _title_bar(c, x3, y, cw3, "Seguridad")
    seg = [
        ("Seguridad 24H", _v(edificio_caracteristicas, 38)),
        ("CCTV", _v(edificio_caracteristicas, 171)),
        ("Contra incendios", _v(edificio_caracteristicas, 172) or _v(caracteristicas, 125)),
        ("Generador eléctrico", _v(edificio_caracteristicas, 32)),
        ("Chiller para AACC", _v(edificio_caracteristicas, 35)),
    ]
    ys = y3 - 2 * mm
    for label, val in seg:
        ys -= 6.6 * mm
        c.setFillColor(GREY_L)
        c.roundRect(x3, ys - 6 * mm, cw3, 6 * mm, 1 * mm, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 5.6)
        c.drawString(x3 + 2 * mm, ys - 4 * mm, str(label).upper())
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 6)
        c.drawRightString(x3 + cw3 - 2 * mm, ys - 4 * mm, str(val)[:10])
    _box_border(c, x3, ys - 1 * mm, cw3, y - (ys - 1 * mm))
    y = min(y1, y2, ys - 2 * mm) - 3 * mm

    # ============ CERCANÍA + DISPONIBILIDAD ============
    half = (CW - colgap) / 2
    yc = _title_bar(c, M, y, half, "Cercanía Estratégica")
    cer = [
        ("Avenida importante", _si(edificio_caracteristicas, 39)),
        ("Tren Eléctrico / Metropolitano", _si(edificio_caracteristicas, 40, 182)),
        ("Bancos y financieras", _si(edificio_caracteristicas, 41)),
        ("Parque público", _si(edificio_caracteristicas, 42, 183)),
        ("Hoteles", _si(edificio_caracteristicas, 43)),
        ("Restaurantes / servicios", _si(edificio_caracteristicas, 44)),
    ]
    yc = _kv(c, M, yc, half, cer, rowh=4.6 * mm)
    _box_border(c, M, yc, half, y - yc)

    xr = M + half + colgap
    yd = _title_bar(c, xr, y, half, "Disponibilidad - Tiempo Estimado")
    disp = [
        ("Edificio listo y operativo", _si(edificio_caracteristicas, 181)),
        ("Oficina disponible desde", _si(caracteristicas, 181) if _v(caracteristicas, 181) else "-"),
        ("Meses de adelanto", _v(caracteristicas, 178) or "-"),
        ("Meses de garantía", _v(caracteristicas, 179) or "-"),
        ("Tiempo mínimo de alquiler", _v(caracteristicas, 180) or "-"),
    ]
    yd = _kv(c, xr, yd, half, disp, rowh=4.6 * mm)
    _box_border(c, xr, yd, half, y - yd)
    y = min(yc, yd) - 3 * mm

    # ============ SOBRE LA OFICINA + NIVEL EQUIP + VALORES ============
    y1 = _title_bar(c, x1, y, cw3, "Sobre la Oficina")
    ofi = [
        ("Número de oficina", _v(caracteristicas, 113) or g(propiedad, "nombre_inmueble") or "-"),
        ("Área neta", f"{g(propiedad,'area') or '-'} m²"),
        ("Área ocupada", _v(caracteristicas, 140) or "-"),
        ("Parqueo simple", _v(caracteristicas, 1, 115) or "-"),
        ("Parqueo doble", _v(caracteristicas, 2) or "-"),
        ("Depósito (m²)", _v(caracteristicas, 3, 14) or "-"),
    ]
    y1 = _kv(c, x1, y1, cw3, ofi, rowh=4.6 * mm)
    _box_border(c, x1, y1, cw3, y - y1)

    y2 = _title_bar(c, x2, y, cw3, "Nivel de Equipamiento")
    niv = [
        ("Pisos", _si(caracteristicas, 22)),
        ("Falso techo", _si(caracteristicas, 23, 122)),
        ("Luminarias", _si(caracteristicas, 24, 123)),
        ("Aire acondicionado", _si(caracteristicas, 25, 124, 116)),
        ("Tabiques y mamparas", _si(caracteristicas, 28, 127)),
        ("Mobiliario / escritorios", _si(caracteristicas, 29, 128)),
        ("Sillas", _si(caracteristicas, 30, 129)),
        ("Fibra óptica / telefonía", _si(caracteristicas, 27, 126)),
    ]
    y2 = _kv(c, x2, y2, cw3, niv, rowh=4.6 * mm)
    _box_border(c, x2, y2, cw3, y - y2)

    y3 = _title_bar(c, x3, y, cw3, "Valores de Renta")
    val = [
        ("Venta oficina", _v(caracteristicas, 161) or "-"),
        ("Renta depósito", _v(caracteristicas, 166, 162) or "-"),
        ("Venta parqueo simple", _v(caracteristicas, 163) or "-"),
        ("Venta parqueo doble", _v(caracteristicas, 164) or "-"),
        ("Alquiler oficina", _v(caracteristicas, 165) or "-"),
        ("Alquiler parqueo simple", _v(caracteristicas, 167) or "-"),
        ("Alquiler parqueo doble", _v(caracteristicas, 168) or "-"),
    ]
    y3 = _kv(c, x3, y3, cw3, val, rowh=4.6 * mm)
    _box_border(c, x3, y3, cw3, y - y3)
    y = min(y1, y2, y3) - 3 * mm

    # ============ OPCIÓN COMERCIAL + VISTA ============
    tr = (g(propiedad, "transaccion") or "").lower()
    y1 = _title_bar(c, x1, y, cw3, "Opción Comercial")
    com = [
        ("Venta", "Sí" if tr in ("venta", "ambos") else "-"),
        ("Alquiler", "Sí" if tr in ("alquiler", "ambos") else "-"),
    ]
    y1 = _kv(c, x1, y1, cw3, com, rowh=4.6 * mm)
    _box_border(c, x1, y1, cw3, y - y1)

    y2 = _title_bar(c, x2, y, cw3, "Vista de la Oficina")
    vis = [
        ("Vista frontal", _si(caracteristicas, 49)),
        ("Vista posterior", _si(caracteristicas, 50)),
        ("Vista interior", _si(caracteristicas, 48)),
        ("Doble frente (esquina)", _si(caracteristicas, 46, 45)),
    ]
    y2 = _kv(c, x2, y2, cw3, vis, rowh=4.6 * mm)
    _box_border(c, x2, y2, cw3, y - y2)
    y = min(y1, y2) - 4 * mm

    # ============ BARRA INFERIOR ============
    bh = 14 * mm
    by = max(M, y - bh)
    c.setFillColor(NAVY)
    c.rect(M, by, CW, bh, fill=1, stroke=0)
    items = [
        ("UBICACIÓN", f"{edificio.get('distrito') or '-'}, {edificio.get('departamento') or 'Lima'}"),
        ("TIPO DE INMUEBLE", edificio.get("tipo") or "Oficina Corporativa"),
        ("ÁREA TOTAL", f"{g(propiedad,'area') or '-'} m²"),
        ("ESTACIONAMIENTOS", str(g(propiedad, "estacionamientos") or _v(caracteristicas, 115) or "-")),
    ]
    colw = CW / 4
    for i, (t, v) in enumerate(items):
        cx = M + i * colw + 3 * mm
        c.setFillColor(ORANGE)
        c.setFont("Helvetica-Bold", 5.6)
        c.drawString(cx, by + bh - 4.6 * mm, t)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(cx, by + bh - 9.6 * mm, str(v)[:26])

    # footer pequeño
    c.setFillColor(GREY)
    c.setFont("Helvetica", 5.6)
    c.drawCentredString(W / 2, M - 2 * mm, f"Qadrante — Servicios Inmobiliarios Integrales  ·  Código {g(propiedad,'registro_cab_id')}  ·  {datetime.now().strftime('%d/%m/%Y')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
