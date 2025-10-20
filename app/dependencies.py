from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models import Usuario, Perfil

# Configurar esquema de seguridad
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtener usuario actual desde el token JWT
    """
    token = credentials.credentials
    
    # Decodificar token
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedException("Token inválido o expirado")
    
    usuario_id: int = payload.get("usuario_id")
    if usuario_id is None:
        raise UnauthorizedException("Token inválido")
    
    # Buscar usuario en BD
    usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
    if usuario is None:
        raise UnauthorizedException("Usuario no encontrado")
    
    if usuario.estado != "activo":
        raise ForbiddenException("Usuario inactivo o suspendido")
    
    return usuario

def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Verificar que el usuario esté activo
    """
    if current_user.estado != "activo":
        raise ForbiddenException("Usuario inactivo")
    return current_user

def require_perfil(*perfiles_permitidos: str):
    """
    Decorator para requerir perfiles específicos
    Uso: @require_perfil("admin", "corredor")
    """
    def perfil_checker(
        current_user: Usuario = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> Usuario:
        # Obtener nombre del perfil
        perfil = db.query(Perfil).filter(Perfil.perfil_id == current_user.perfil_id).first()
        
        if perfil and perfil.nombre in perfiles_permitidos:
            return current_user
        
        raise ForbiddenException(
            f"Acceso denegado. Se requiere perfil: {', '.join(perfiles_permitidos)}"
        )
    
    return perfil_checker

# Dependencias específicas por perfil
def require_admin(current_user: Usuario = Depends(require_perfil("admin"))) -> Usuario:
    """Requiere perfil Admin"""
    return current_user

def require_corredor(current_user: Usuario = Depends(require_perfil("corredor", "admin"))) -> Usuario:
    """Requiere perfil Corredor o Admin"""
    return current_user

def require_ofertante(current_user: Usuario = Depends(require_perfil("ofertante", "corredor", "admin"))) -> Usuario:
    """Requiere perfil Ofertante, Corredor o Admin"""
    return current_user

# Dependencia opcional de usuario (para endpoints públicos que pueden tener usuario logueado)
def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """
    Obtener usuario actual si existe token, sino None
    Útil para endpoints públicos que pueden personalizar respuesta si hay usuario
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        if payload is None:
            return None
        
        usuario_id: int = payload.get("usuario_id")
        if usuario_id is None:
            return None
        
        usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
        return usuario
    except:
        return None
