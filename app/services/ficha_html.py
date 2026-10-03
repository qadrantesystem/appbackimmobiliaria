"""
📄 Ficha A4 — Cuadrante (WeasyPrint: HTML/CSS -> PDF)
Replica el diseño del mock. Datos homologados: EDIFICIO / UNIDAD / COMERCIALIZACIÓN.
"""
import os
import base64
import html as _html
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS, "logo-qadrante.png")
ICONS_DIR = os.path.join(ASSETS, "icons")
ICON_FILES = {
    "seguridad24h": "seguridad24h.webp",
    "cctv": "cctv.webp",
    "incendios": "incendios.webp",
    "generador": "generador.webp",
    "chiller": "chiller.webp",
}


def _logo_datauri():
    try:
        with open(LOGO_PATH, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def _icon(key):
    path = os.path.join(ICONS_DIR, ICON_FILES.get(key, ""))
    try:
        with open(path, "rb") as f:
            return "data:image/webp;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def _v(caract, *ids):
    if not caract:
        return None
    for i in ids:
        val = caract.get(i)
        if val not in (None, "", "None"):
            return val
    return None


_TRUE = ("si", "sí", "1", "true", "yes")


def _yn(val):
    if val is None or str(val).strip() == "":
        return "-"
    return "Sí" if str(val).strip().lower() in _TRUE else "No"


def _si(caract, *ids):
    return _yn(_v(caract, *ids))


def _e(x):
    return _html.escape(str(x if x not in (None, "") else "-"))


def _cls(value):
    s = str(value).strip().lower()
    if s in ("sí", "si"):
        return "si"
    if s == "no":
        return "no"
    if s in ("-", "", "none"):
        return "na"
    return "val"


def _rows(pairs):
    out = []
    for label, value in pairs:
        v = value if value not in (None, "") else "-"
        out.append(f'<div class="kv"><span>{_e(label)}</span><b class="{_cls(v)}">{_e(v)}</b></div>')
    return "".join(out)


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin:0; font-family: 'Helvetica','Arial',sans-serif; color:#1F2937; }
.page { width:210mm; min-height:297mm; padding:0 8mm 8mm; }
.hdr { margin:0 -8mm 4mm; background:#1E5E86; color:#fff; padding:6mm 8mm 5mm; display:flex; align-items:center; justify-content:space-between; }
.hdr .badge { background:#FF9800; color:#fff; font-size:7px; font-weight:bold; padding:1mm 2mm; display:inline-block; }
.hdr .t { font-size:26px; font-weight:800; letter-spacing:.5px; margin-top:1.5mm; }
.hdr img { height:16mm; }
.sec-title { background:#1E5E86; color:#fff; font-size:7.5px; font-weight:bold; letter-spacing:.4px; padding:1.2mm 2mm; margin-bottom:0; }
.kv { display:flex; justify-content:space-between; border:0.3pt solid #D6DEE6; border-top:0; padding:0.85mm 1.6mm; font-size:6.4px; }
.kv span { color:#1E5E86; font-weight:600; }
.kv b { color:#1F2937; font-weight:500; }
.kv:nth-child(even) { background:#F2F6FA; }
.row { display:flex; gap:3mm; margin-bottom:3mm; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:3mm; margin-bottom:3mm; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:3mm; margin-bottom:3mm; }
.col-file { flex:1; }
.top-left { flex:0 0 58%; }
.top-right { flex:1; display:flex; gap:1.5mm; }
.img-main { flex:1; }
.img-main img { width:100%; height:42mm; object-fit:cover; border-radius:1mm; }
.img-stack { flex:1; }
.img-stack img { display:block; width:100%; height:13mm; object-fit:cover; border-radius:1mm; }
.img-stack img + img { margin-top:1.5mm; }
.desc { border:0.3pt solid #D6DEE6; border-top:0; font-size:6.4px; padding:1.6mm; line-height:1.35; }
.pills { display:flex; flex-direction:column; gap:1.2mm; }
.pill { display:flex; justify-content:space-between; background:#EEF2F6; border-radius:1mm; padding:1.1mm 1.6mm; font-size:6.2px; }
.pill span { color:#1E5E86; font-weight:bold; }
.pill b { color:#0E718D; }
.seg-list { display:flex; flex-direction:column; gap:1.2mm; padding-top:1.5mm; }
.seg-item { display:flex; align-items:center; gap:1.6mm; background:#EEF2F6; border-radius:1mm; padding:1mm 1.6mm; font-size:6.2px; }
.seg-item img { width:4.2mm; height:4.2mm; object-fit:contain; }
.seg-item .lbl { color:#1E5E86; font-weight:bold; flex:1; }
.kv b.si, .seg-item b.si { color:#16A34A; font-weight:700; }
.kv b.no, .seg-item b.no { color:#9AA6B2; font-weight:500; }
.kv b.na, .seg-item b.na { color:#BCC6D0; font-weight:500; }
.bottom { display:flex; background:#1E5E86; color:#fff; margin-top:2mm; }
.bottom > div { flex:1; padding:2.2mm 3mm; }
.bottom .k { color:#FF9800; font-size:5.8px; font-weight:bold; letter-spacing:.3px; }
.bottom .v { font-size:9px; font-weight:bold; margin-top:.6mm; }
.foot { text-align:center; color:#8A98A4; font-size:6px; margin-top:2mm; }
"""


def generar_ficha_pdf(propiedad, caracteristicas=None, edificio=None, edificio_caracteristicas=None) -> bytes:
    from weasyprint import HTML

    caracteristicas = caracteristicas or {}
    edificio_caracteristicas = edificio_caracteristicas or {}
    edificio = edificio or {}
    g = lambda o, k, d=None: getattr(o, k, d)

    logo = _logo_datauri()

    # imágenes
    imgs = []
    if g(propiedad, "imagen_principal"):
        imgs.append(g(propiedad, "imagen_principal"))
    arr = g(propiedad, "imagenes") or []
    if isinstance(arr, (list, tuple)):
        for u in arr:
            if u and u not in imgs:
                imgs.append(u)
    imgs = imgs[:4]
    big_img = imgs[0] if imgs else ""
    minis = imgs[1:4]

    info_rows = _rows([
        ("Nombre del Edificio", edificio.get("nombre") or g(propiedad, "titulo")),
        ("Dirección", edificio.get("direccion") or g(propiedad, "direccion")),
        ("Numeración", _v(edificio_caracteristicas, 106)),
        ("Urbanización", _v(edificio_caracteristicas, 107)),
        ("Distrito", edificio.get("distrito")),
        ("Departamento", _v(edificio_caracteristicas, 108) or edificio.get("departamento") or "Lima"),
        ("País", _v(edificio_caracteristicas, 109) or "Perú"),
    ])

    generales = _rows([
        ("Año de construcción", _v(edificio_caracteristicas, 170)),
        ("Cantidad de pisos", _v(edificio_caracteristicas, 110)),
        ("Cantidad de sótanos", _v(edificio_caracteristicas, 111)),
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
    ])
    equipamiento = _rows([
        ("Ascensores (total)", _v(edificio_caracteristicas, 119)),
        ("Montacarga", _si(edificio_caracteristicas, 19)),
        ("De sótano a piso 1", _si(edificio_caracteristicas, 21)),
        ("De sótano a oficina VIP", _si(edificio_caracteristicas, 20)),
        ("Parqueo bicicletas", _si(edificio_caracteristicas, 4)),
        ("Carga veh. eléctricos", _si(edificio_caracteristicas, 5)),
    ])
    soporte = _rows([
        ("Grupo electrógeno", _si(edificio_caracteristicas, 32)),
        ("Encendido automático", _si(edificio_caracteristicas, 34)),
        ("Chiller para AACC", _si(edificio_caracteristicas, 35)),
        ("Cuarto técnico", _si(edificio_caracteristicas, 36)),
        ("Fibra óptica", _si(edificio_caracteristicas, 37)),
        ("Recepción / Seguridad", _si(edificio_caracteristicas, 38)),
    ])
    seguridad = "".join(
        f'<div class="seg-item"><img src="{_icon(icon)}"><span class="lbl">{_e(k)}</span><b class="{_cls(v)}">{_e(v)}</b></div>'
        for k, v, icon in [
            ("SEGURIDAD 24H", _yn(_v(edificio_caracteristicas, 38)), "seguridad24h"),
            ("CCTV", _yn(_v(edificio_caracteristicas, 171)), "cctv"),
            ("CONTRA INCENDIOS", _yn(_v(edificio_caracteristicas, 172) or _v(caracteristicas, 125)), "incendios"),
            ("GENERADOR ELÉCTRICO", _yn(_v(edificio_caracteristicas, 32)), "generador"),
            ("CHILLER PARA AACC", _yn(_v(edificio_caracteristicas, 35)), "chiller"),
        ]
    )
    cercania = _rows([
        ("Avenida importante", _si(edificio_caracteristicas, 39)),
        ("Tren Eléctrico / Metropolitano", _si(edificio_caracteristicas, 40, 182)),
        ("Bancos y financieras", _si(edificio_caracteristicas, 41)),
        ("Parque público", _si(edificio_caracteristicas, 42, 183)),
        ("Hoteles", _si(edificio_caracteristicas, 43)),
        ("Restaurantes / servicios", _si(edificio_caracteristicas, 44)),
    ])
    disponibilidad = _rows([
        ("Edificio listo y operativo", _si(edificio_caracteristicas, 181)),
        ("Meses de adelanto", _v(caracteristicas, 178)),
        ("Meses de garantía", _v(caracteristicas, 179)),
        ("Tiempo mínimo de alquiler", _v(caracteristicas, 180)),
    ])
    sobre_oficina = _rows([
        ("Número de oficina", _v(caracteristicas, 113) or g(propiedad, "nombre_inmueble")),
        ("Área neta", f"{g(propiedad,'area')} m²" if g(propiedad, "area") else "-"),
        ("Área ocupada", _v(caracteristicas, 140)),
        ("Parqueo simple", _v(caracteristicas, 1, 115)),
        ("Parqueo doble", _v(caracteristicas, 2)),
        ("Depósito (m²)", _v(caracteristicas, 3, 14)),
    ])
    nivel_eq = _rows([
        ("Pisos", _si(caracteristicas, 22)),
        ("Falso techo", _si(caracteristicas, 23, 122)),
        ("Luminarias", _si(caracteristicas, 24, 123)),
        ("Aire acondicionado", _si(caracteristicas, 25, 124, 116)),
        ("Tabiques y mamparas", _si(caracteristicas, 28, 127)),
        ("Mobiliario / escritorios", _si(caracteristicas, 29, 128)),
        ("Sillas", _si(caracteristicas, 30, 129)),
        ("Fibra óptica / telefonía", _si(caracteristicas, 27, 126)),
    ])
    valores = _rows([
        ("Venta oficina", _v(caracteristicas, 161)),
        ("Renta depósito", _v(caracteristicas, 166, 162)),
        ("Venta parqueo simple", _v(caracteristicas, 163)),
        ("Venta parqueo doble", _v(caracteristicas, 164)),
        ("Alquiler oficina", _v(caracteristicas, 165)),
        ("Alquiler parqueo simple", _v(caracteristicas, 167)),
        ("Alquiler parqueo doble", _v(caracteristicas, 168)),
    ])
    tr = (g(propiedad, "transaccion") or "").lower()
    opcion = _rows([
        ("Venta", "Sí" if tr in ("venta", "ambos") else "-"),
        ("Alquiler", "Sí" if tr in ("alquiler", "ambos") else "-"),
    ])
    vista = _rows([
        ("Vista frontal", _si(caracteristicas, 49)),
        ("Vista posterior", _si(caracteristicas, 50)),
        ("Vista interior", _si(caracteristicas, 48)),
        ("Doble frente (esquina)", _si(caracteristicas, 46, 45)),
    ])

    minis_html = "".join(f'<img src="{u}">' for u in minis)
    desc = _e(edificio.get("descripcion") or g(propiedad, "descripcion") or "")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  <div class="hdr">
    <div><div class="badge">FICHA DE INMUEBLE</div><div class="t">OFICINAS CORPORATIVAS</div></div>
    {f'<img src="{logo}">' if logo else ''}
  </div>

  <div class="row">
    <div class="top-left">
      <div class="sec-title">INFORMACIÓN GENERAL DEL EDIFICIO</div>
      {info_rows}
    </div>
    <div class="top-right">
      <div class="img-main">{f'<img src="{big_img}">' if big_img else ''}</div>
      <div class="img-stack">{minis_html}</div>
    </div>
  </div>

  <div class="sec-title">DESCRIPCIÓN GENERAL DEL EDIFICIO</div>
  <div class="desc">{desc}</div>

  <div style="height:3mm"></div>
  <div class="grid3">
    <div><div class="sec-title">GENERALES</div>{generales}</div>
    <div><div class="sec-title">EQUIPAMIENTO</div>{equipamiento}<div class="sec-title" style="margin-top:2mm">SOPORTE DEL EDIFICIO</div>{soporte}</div>
    <div><div class="sec-title">SEGURIDAD</div><div class="seg-list">{seguridad}</div></div>
  </div>

  <div class="grid2">
    <div><div class="sec-title">CERCANÍA ESTRATÉGICA</div>{cercania}</div>
    <div><div class="sec-title">DISPONIBILIDAD - TIEMPO ESTIMADO</div>{disponibilidad}</div>
  </div>

  <div class="grid3">
    <div><div class="sec-title">SOBRE LA OFICINA</div>{sobre_oficina}</div>
    <div><div class="sec-title">NIVEL DE EQUIPAMIENTO</div>{nivel_eq}</div>
    <div><div class="sec-title">VALORES DE RENTA</div>{valores}</div>
  </div>

  <div class="grid2">
    <div><div class="sec-title">OPCIÓN COMERCIAL</div>{opcion}</div>
    <div><div class="sec-title">VISTA DE LA OFICINA</div>{vista}</div>
  </div>

  <div class="bottom">
    <div><div class="k">UBICACIÓN</div><div class="v">{_e(edificio.get('distrito'))}, {_e(edificio.get('departamento') or 'Lima')}</div></div>
    <div><div class="k">TIPO DE INMUEBLE</div><div class="v">{_e(edificio.get('tipo') or 'Oficina Corporativa')}</div></div>
    <div><div class="k">ÁREA TOTAL</div><div class="v">{_e(str(g(propiedad,'area'))+' m²' if g(propiedad,'area') else '-')}</div></div>
    <div><div class="k">ESTACIONAMIENTOS</div><div class="v">{_e(g(propiedad,'estacionamientos') or _v(caracteristicas,115))}</div></div>
  </div>
  <div class="foot">Qadrante — Servicios Inmobiliarios Integrales · Código {_e(g(propiedad,'registro_cab_id'))} · {datetime.now().strftime('%d/%m/%Y')}</div>
</div></body></html>"""

    return HTML(string=html, base_url=ASSETS).write_pdf()
