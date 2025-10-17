from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UnauthorizedException, BadRequestException, ConflictException
from app.models import Usuario, Perfil, EmailVerificationToken, PasswordResetToken
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.common import ResponseModel
from app.services.email_service import email_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
    - **tipo_persona**: Tipo de persona (natural/juridica)
    - **tipo_documento**: Tipo de documento (DNI/RUC/CE/PAS)
    - **razon_social**: Razón social para personas jurídicas (opcional)
    - **ruc**: RUC para personas jurídicas (opcional)
    - **representante_legal**: Representante legal para personas jurídicas (opcional)
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
        tipo_persona=user_data.tipo_persona,
        tipo_documento=user_data.tipo_documento,
        razon_social=user_data.razon_social,
        ruc=user_data.ruc,
        representante_legal=user_data.representante_legal,
        perfil_id=1,  # Por defecto: demandante
        estado="pendiente",  # Pendiente hasta verificar email
        email_verificado=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Crear token de verificación
    verification_token = EmailVerificationToken.create_token(
        usuario_id=new_user.usuario_id,
        email=new_user.email
    )
    db.add(verification_token)
    db.commit()
    
    # Enviar email de verificación
    try:
        email_result = await email_service.send_verification_email(
            email=new_user.email,
            name=f"{new_user.nombre} {new_user.apellido}",
            verification_code=verification_token.token
        )
        logger.info(f"✅ [REGISTRO] Email de verificación enviado a {new_user.email}")
        logger.info(f"   🔐 Token ID: {verification_token.id}, Código: {verification_token.token}")
    except Exception as e:
        logger.error(f"❌ [REGISTRO] Error enviando email: {str(e)}")
        # No fallar el registro si falla el email
    
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

@router.post("/verify-email", response_model=ResponseModel[dict])
async def verify_email(
    email: str,
    codigo: str,
    db: Session = Depends(get_db)
):
    """
    Verificar email con código de 6 dígitos
    
    - **email**: Email del usuario
    - **codigo**: Código de verificación de 6 dígitos
    """
    # Buscar usuario
    user = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not user:
        raise BadRequestException("Usuario no encontrado")
    
    # Verificar si ya está verificado
    if user.email_verificado:
        raise BadRequestException("El email ya está verificado")
    
    # Buscar token válido
    token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.email == email,
        EmailVerificationToken.token == codigo,
        EmailVerificationToken.used == False
    ).order_by(EmailVerificationToken.created_at.desc()).first()
    
    if not token:
        raise BadRequestException("Código de verificación incorrecto")
    
    # Verificar si el token es válido
    if not token.is_valid():
        raise BadRequestException("El código de verificación ha expirado. Solicita uno nuevo.")
    
    # Marcar token como usado
    token.used = True
    
    # Marcar usuario como verificado
    user.email_verificado = True
    user.estado = "activo"
    
    db.commit()
    db.refresh(user)
    
    # Enviar email de bienvenida
    try:
        perfil = db.query(Perfil).filter(Perfil.perfil_id == user.perfil_id).first()
        await email_service.send_welcome_email(
            email=user.email,
            name=f"{user.nombre} {user.apellido}",
            perfil=perfil.nombre if perfil else "Usuario"
        )
        logger.info(f"✅ [VERIFICACIÓN] Email de bienvenida enviado a {user.email}")
    except Exception as e:
        logger.error(f"❌ [VERIFICACIÓN] Error enviando bienvenida: {str(e)}")
    
    return ResponseModel(
        success=True,
        message="Email verificado exitosamente. Ya puedes iniciar sesión.",
        data={
            "usuario_id": user.usuario_id,
            "email": user.email,
            "email_verificado": user.email_verificado,
            "estado": user.estado
        }
    )

@router.post("/resend-verification", response_model=ResponseModel[dict])
async def resend_verification(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Reenviar código de verificación
    
    - **email**: Email del usuario
    """
    # Buscar usuario
    user = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not user:
        raise BadRequestException("Usuario no encontrado")
    
    # Verificar si ya está verificado
    if user.email_verificado:
        raise BadRequestException("El email ya está verificado")
    
    # Crear nuevo token
    verification_token = EmailVerificationToken.create_token(
        usuario_id=user.usuario_id,
        email=user.email
    )
    db.add(verification_token)
    db.commit()
    
    # Enviar email
    try:
        await email_service.send_verification_email(
            email=user.email,
            name=f"{user.nombre} {user.apellido}",
            verification_code=verification_token.token
        )
        logger.info(f"✅ [REENVÍO] Código reenviado a {user.email}")
    except Exception as e:
        logger.error(f"❌ [REENVÍO] Error enviando email: {str(e)}")
        raise BadRequestException("Error enviando email de verificación")
    
    return ResponseModel(
        success=True,
        message="Código de verificación reenviado. Revisa tu email.",
        data={
            "email": user.email,
            "mensaje": "Código válido por 15 minutos"
        }
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

@router.post("/forgot-password", response_model=ResponseModel[dict])
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    🔐 Solicitar recuperación de contraseña
    Envía un código de 6 dígitos al email del usuario
    """
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            # Por seguridad, no revelar si el email existe o no
            return ResponseModel(
                success=True,
                message="Si el email existe, recibirás un código de recuperación",
                data={}
            )
        
        # Generar código de 6 dígitos
        codigo = email_service.generate_verification_code()
        
        # Eliminar tokens anteriores
        db.query(PasswordResetToken).filter(
            PasswordResetToken.usuario_id == usuario.usuario_id
        ).delete()
        
        # Crear nuevo token
        nuevo_token = PasswordResetToken(
            usuario_id=usuario.usuario_id,
            email=usuario.email,
            token=codigo,
            expires_at=datetime.now() + timedelta(minutes=15)
        )
        db.add(nuevo_token)
        db.commit()
        
        # Enviar email
        await email_service.send_password_reset_email(
            email=usuario.email,
            name=usuario.nombre,
            reset_code=codigo
        )
        
        logger.info(f"✅ Código de recuperación enviado a {email}")
        
        return ResponseModel(
            success=True,
            message="Si el email existe, recibirás un código de recuperación",
            data={}
        )
        
    except Exception as e:
        logger.error(f"❌ Error en forgot-password: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar solicitud")

@router.post("/reset-password", response_model=ResponseModel[dict])
async def reset_password(
    email: str,
    codigo: str,
    nueva_password: str,
    db: Session = Depends(get_db)
):
    """
    🔐 Restablecer contraseña con código
    """
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Buscar token válido
        token = db.query(PasswordResetToken).filter(
            PasswordResetToken.usuario_id == usuario.usuario_id,
            PasswordResetToken.token == codigo,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.now()
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=400, 
                detail="Código inválido o expirado"
            )
        
        # Actualizar contraseña
        usuario.password_hash = get_password_hash(nueva_password)
        
        # Marcar token como usado
        token.used = True
        
        db.commit()
        
        logger.info(f"✅ Contraseña restablecida para {email}")
        
        return ResponseModel(
            success=True,
            message="Contraseña restablecida exitosamente. Ya puedes iniciar sesión.",
            data={"email": email}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error en reset-password: {e}")
        raise HTTPException(status_code=500, detail="Error al restablecer contraseña")
