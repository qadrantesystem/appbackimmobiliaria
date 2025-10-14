# Schemas module
from app.schemas.auth import UserRegister, UserLogin, Token, TokenData
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioUpdatePassword,
    UsuarioResponse, UsuarioListResponse
)
from app.schemas.propiedad import (
    PropiedadCreate, PropiedadUpdate, PropiedadEstadoUpdate,
    PropiedadResponse, PropiedadDetalleResponse, PropiedadListResponse
)
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse
from app.schemas.suscripcion import (
    SuscripcionCreate, SuscripcionAprobar,
    SuscripcionResponse, SuscripcionDetalleResponse
)
from app.schemas.busqueda import (
    BusquedaCreate, BusquedaGuardar, BusquedaAlertaUpdate,
    BusquedaResponse, BusquedaGuardadaResponse
)
from app.schemas.favorito import FavoritoCreate, FavoritoUpdate, FavoritoResponse
from app.schemas.common import ResponseModel, PaginationParams, PaginatedResponse

__all__ = [
    # Auth
    "UserRegister", "UserLogin", "Token", "TokenData",
    # Usuario
    "UsuarioCreate", "UsuarioUpdate", "UsuarioUpdatePassword",
    "UsuarioResponse", "UsuarioListResponse",
    # Propiedad
    "PropiedadCreate", "PropiedadUpdate", "PropiedadEstadoUpdate",
    "PropiedadResponse", "PropiedadDetalleResponse", "PropiedadListResponse",
    # Plan
    "PlanCreate", "PlanUpdate", "PlanResponse",
    # Suscripción
    "SuscripcionCreate", "SuscripcionAprobar",
    "SuscripcionResponse", "SuscripcionDetalleResponse",
    # Búsqueda
    "BusquedaCreate", "BusquedaGuardar", "BusquedaAlertaUpdate",
    "BusquedaResponse", "BusquedaGuardadaResponse",
    # Favorito
    "FavoritoCreate", "FavoritoUpdate", "FavoritoResponse",
    # Common
    "ResponseModel", "PaginationParams", "PaginatedResponse",
]
