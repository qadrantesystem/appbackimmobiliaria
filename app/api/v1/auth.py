from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UnauthorizedException, BadRequestException, ConflictException
from app.models import Usuario, Perfil
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.common import ResponseModel

router = APIRouter()

@router.post("/register", response_model=ResponseModel[dict], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario
    
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 6 caracteres)
    - **nombre**: Nombre del usuario
    - **apellido**: Apellido del usuario
    - **telefono**: Teléfono (opcional)
    - **dni**: DNI (opcional)
    """
    # Verificar si el email ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing_user:
        raise ConflictException("El email ya está registrado")
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    
    new_user = Usuario(
        email=user_data.email,
        password_hash=hashed_password,
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        telefono=user_data.telefono,
        dni=user_data.dni,
        perfil_id=1,  # Por defecto: demandante
        estado="activo"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Obtener nombre del perfil
    perfil = db.query(Perfil).filter(Perfil.perfil_id == new_user.perfil_id).first()
    
    return ResponseModel(
        success=True,
        message="Usuario registrado exitosamente",
        data={
            "usuario_id": new_user.usuario_id,
            "email": new_user.email,
            "nombre": new_user.nombre,
            "apellido": new_user.apellido,
            "perfil_id": new_user.perfil_id,
            "perfil_nombre": perfil.nombre if perfil else None,
            "estado": new_user.estado
        }
    )

@router.post("/login", response_model=ResponseModel[Token])
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Retorna un token JWT para autenticación
    """
    # Buscar usuario por email
    user = db.query(Usuario).filter(Usuario.email == credentials.email).first()
    
    if not user:
        raise UnauthorizedException("Credenciales incorrectas")
    
    # Verificar contraseña
    if not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Credenciales incorrectas")
    
    # Verificar que el usuario esté activo
    if user.estado != "activo":
        raise UnauthorizedException("Usuario inactivo o suspendido")
    
    # Obtener perfil
    perfil = db.query(Perfil).filter(Perfil.perfil_id == user.perfil_id).first()
    
    # Crear token JWT
    token_data = {
        "usuario_id": user.usuario_id,
        "email": user.email,
        "perfil_id": user.perfil_id
    }
    access_token = create_access_token(token_data)
    
    # Actualizar última sesión
    user.fecha_ultima_sesion = datetime.utcnow()
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Login exitoso",
        data=Token(
            access_token=access_token,
            token_type="bearer",
            usuario={
                "usuario_id": user.usuario_id,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "perfil_id": user.perfil_id,
                "perfil_nombre": perfil.nombre if perfil else None,
                "permisos": perfil.permisos if perfil else {}
            }
        )
    )

@router.post("/logout", response_model=ResponseModel[dict])
async def logout():
    """
    Cerrar sesión
    
    En una implementación con JWT, el logout se maneja en el cliente
    eliminando el token. Este endpoint es informativo.
    """
    return ResponseModel(
        success=True,
        message="Logout exitoso",
        data={"info": "Token debe ser eliminado del cliente"}
    )
