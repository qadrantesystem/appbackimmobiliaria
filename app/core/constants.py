"""
Constantes centralizadas del sistema Qadrante.
Evita strings hardcodeados en endpoints y lógica de negocio.
"""


class EstadoPropiedad:
    BORRADOR = "borrador"
    PUBLICADO = "publicado"
    PAUSADO = "pausado"
    CERRADO = "cerrado"
    RECHAZADO = "rechazado"


class TipoTransaccion:
    VENTA = "venta"
    ALQUILER = "alquiler"
    AMBOS = "ambos"


class EstadoCRM:
    LEAD = "lead"
    CONTACTO = "contacto"
    PROPUESTA = "propuesta"
    NEGOCIACION = "negociacion"
    PRE_CIERRE = "pre_cierre"
    CERRADO_GANADO = "cerrado_ganado"
    CERRADO_PERDIDO = "cerrado_perdido"


class PerfilUsuario:
    DEMANDANTE = 1
    OFERTANTE = 2
    CORREDOR = 3
    ADMIN = 4


class TipoInmuebleID:
    OFICINA_EN_EDIFICIO = 1
    CASA = 2
    DEPARTAMENTO = 3
    LOCAL_COMERCIAL = 4
    TERRENO = 5
    ALMACEN = 6
    COCHERA = 7
    HABITACION = 8
    OFICINA_INDEPENDIENTE = 9
    CONSULTORIO = 10
    DEPOSITO = 11
    EDIFICIO_OFICINAS = 12
    EDIFICIO_DEPARTAMENTOS = 13
    CONDOMINIO = 14


# Margen de tolerancia para búsquedas (±15%)
MARGEN_BUSQUEDA = 0.15
