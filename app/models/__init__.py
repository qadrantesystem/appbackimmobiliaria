# Importar todos los modelos en orden correcto para evitar errores de dependencias

# 1. Seguridad
from app.models.perfil import Perfil
from app.models.usuario import Usuario
from app.models.verification_token import EmailVerificationToken, PasswordResetToken

# 2. Maestras
from app.models.plan import Plan
from app.models.distrito import Distrito
from app.models.tipo_inmueble import TipoInmueble
from app.models.caracteristica import Caracteristica
from app.models.caracteristica_x_inmueble import CaracteristicaXInmueble
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
    "EmailVerificationToken",
    "PasswordResetToken",
    # Maestras
    "Plan",
    "Distrito",
    "TipoInmueble",
    "Caracteristica",
    "CaracteristicaXInmueble",
    "EstadoCRM",
    # Transaccionales
    "Suscripcion",
    "Propiedad",
    "PropiedadDetalle",
    "Busqueda",
    "Favorito",
    "Tracking",
]
