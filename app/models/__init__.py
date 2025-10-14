# Importar todos los modelos en orden correcto para evitar errores de dependencias

# 1. Seguridad
from app.models.perfil import Perfil
from app.models.usuario import Usuario

# 2. Maestras
from app.models.plan import Plan
from app.models.distrito import Distrito
from app.models.tipo_inmueble import TipoInmueble
from app.models.caracteristica import Caracteristica
from app.models.caracteristica_inmueble import CaracteristicaInmueble
from app.models.estado_crm import EstadoCRM

# 3. Transaccionales
from app.models.suscripcion import Suscripcion
from app.models.propiedad import Propiedad
from app.models.propiedad_detalle import PropiedadDetalle
from app.models.busqueda import Busqueda
from app.models.favorito import Favorito
from app.models.tracking import Tracking

__all__ = [
    # Seguridad
    "Perfil",
    "Usuario",
    # Maestras
    "Plan",
    "Distrito",
    "TipoInmueble",
    "Caracteristica",
    "CaracteristicaInmueble",
    "EstadoCRM",
    # Transaccionales
    "Suscripcion",
    "Propiedad",
    "PropiedadDetalle",
    "Busqueda",
    "Favorito",
    "Tracking",
]
