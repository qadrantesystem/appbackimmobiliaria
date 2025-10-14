from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_active_user, require_admin
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestException, NotFoundException
from app.models import Usuario, Perfil, Plan, Suscripcion
from app.schemas.usuario import UsuarioUpdate, UsuarioUpdatePassword, UsuarioResponse, UsuarioListResponse
from app.schemas.common import ResponseModel, PaginatedResponse

router = APIRouter()

@router.get("/me", response_model=ResponseModel[dict])
async def get_my_profile(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener perfil del usuario autenticado"""
    # Obtener perfil
    perfil = db.query(Perfil).filter(Perfil.perfil_id == current_user.perfil_id).first()
    
    # Obtener suscripción activa
    suscripcion_activa = db.query(Suscripcion).filter(
        Suscripcion.usuario_id == current_user.usuario_id,
        Suscripcion.estado == "activa"
    ).first()
    
    plan_actual = None
    if suscripcion_activa:
        plan = db.query(Plan).filter(Plan.plan_id == suscripcion_activa.plan_id).first()
        plan_actual = {
            "plan_id": plan.plan_id,
            "nombre": plan.nombre,
            "fecha_inicio": suscripcion_activa.fecha_inicio,
            "fecha_fin": suscripcion_activa.fecha_fin
        }
    
    return ResponseModel(
        success=True,
        data={
            "usuario_id": current_user.usuario_id,
            "email": current_user.email,
            "nombre": current_user.nombre,
            "apellido": current_user.apellido,
            "telefono": current_user.telefono,
            "dni": current_user.dni,
            "perfil": {
                "perfil_id": perfil.perfil_id,
                "nombre": perfil.nombre,
                "descripcion": perfil.descripcion,
                "permisos": perfil.permisos
            } if perfil else None,
            "suscripcion_activa": plan_actual,
            "estado": current_user.estado,
            "fecha_registro": current_user.fecha_registro
        }
    )

@router.put("/me", response_model=ResponseModel[UsuarioResponse])
async def update_my_profile(
    user_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar perfil del usuario autenticado"""
    # Actualizar campos
    if user_data.nombre:
        current_user.nombre = user_data.nombre
    if user_data.apellido:
        current_user.apellido = user_data.apellido
    if user_data.telefono:
        current_user.telefono = user_data.telefono
    if user_data.dni:
        current_user.dni = user_data.dni
    
    db.commit()
    db.refresh(current_user)
    
    # Obtener perfil
    perfil = db.query(Perfil).filter(Perfil.perfil_id == current_user.perfil_id).first()
    
    return ResponseModel(
        success=True,
        message="Perfil actualizado exitosamente",
        data=UsuarioResponse(
            usuario_id=current_user.usuario_id,
            email=current_user.email,
            nombre=current_user.nombre,
            apellido=current_user.apellido,
            telefono=current_user.telefono,
            dni=current_user.dni,
            perfil_id=current_user.perfil_id,
            perfil_nombre=perfil.nombre if perfil else None,
            estado=current_user.estado,
            fecha_registro=current_user.fecha_registro
        )
    )

@router.put("/me/password", response_model=ResponseModel[dict])
async def change_password(
    password_data: UsuarioUpdatePassword,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario autenticado"""
    # Verificar contraseña actual
    if not verify_password(password_data.password_actual, current_user.password_hash):
        raise BadRequestException("Contraseña actual incorrecta")
    
    # Verificar que las contraseñas coincidan
    if password_data.password_nueva != password_data.password_confirmacion:
        raise BadRequestException("Las contraseñas no coinciden")
    
    # Actualizar contraseña
    current_user.password_hash = get_password_hash(password_data.password_nueva)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Contraseña actualizada exitosamente",
        data={}
    )

@router.get("", response_model=PaginatedResponse[UsuarioListResponse])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    perfil_id: Optional[int] = None,
    estado: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Listar usuarios (Solo Admin)"""
    # Query base
    query = db.query(Usuario)
    
    # Filtros
    if perfil_id:
        query = query.filter(Usuario.perfil_id == perfil_id)
    if estado:
        query = query.filter(Usuario.estado == estado)
    if search:
        query = query.filter(
            or_(
                Usuario.nombre.ilike(f"%{search}%"),
                Usuario.apellido.ilike(f"%{search}%"),
                Usuario.email.ilike(f"%{search}%")
            )
        )
    
    # Total
    total = query.count()
    
    # Paginación
    offset = (page - 1) * limit
    usuarios = query.offset(offset).limit(limit).all()
    
    # Formatear respuesta
    usuarios_list = []
    for usuario in usuarios:
        perfil = db.query(Perfil).filter(Perfil.perfil_id == usuario.perfil_id).first()
        
        # Obtener plan actual
        suscripcion = db.query(Suscripcion).filter(
            Suscripcion.usuario_id == usuario.usuario_id,
            Suscripcion.estado == "activa"
        ).first()
        plan_actual = None
        if suscripcion:
            plan = db.query(Plan).filter(Plan.plan_id == suscripcion.plan_id).first()
            plan_actual = plan.nombre if plan else None
        
        usuarios_list.append(UsuarioListResponse(
            usuario_id=usuario.usuario_id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            telefono=usuario.telefono,
            perfil_nombre=perfil.nombre if perfil else "Sin perfil",
            estado=usuario.estado,
            fecha_registro=usuario.fecha_registro,
            plan_actual=plan_actual
        ))
    
    return PaginatedResponse(
        success=True,
        data=usuarios_list,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.patch("/{usuario_id}/estado", response_model=ResponseModel[dict])
async def update_user_status(
    usuario_id: int,
    estado: str,
    motivo: Optional[str] = None,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Actualizar estado de usuario (Solo Admin)"""
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
    if not usuario:
        raise NotFoundException("Usuario no encontrado")
    
    # Validar estado
    if estado not in ["activo", "inactivo", "suspendido"]:
        raise BadRequestException("Estado inválido")
    
    # Actualizar estado
    usuario.estado = estado
    db.commit()
    
    return ResponseModel(
        success=True,
        message=f"Estado actualizado a {estado}",
        data={"usuario_id": usuario_id, "estado": estado}
    )

@router.post("/{usuario_id}/perfil", response_model=ResponseModel[dict])
async def assign_profile(
    usuario_id: int,
    perfil_id: int,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Asignar perfil a usuario (Solo Admin)"""
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
    if not usuario:
        raise NotFoundException("Usuario no encontrado")
    
    # Verificar que el perfil existe
    perfil = db.query(Perfil).filter(Perfil.perfil_id == perfil_id).first()
    if not perfil:
        raise NotFoundException("Perfil no encontrado")
    
    # Asignar perfil
    usuario.perfil_id = perfil_id
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Perfil asignado exitosamente",
        data={"usuario_id": usuario_id, "perfil_id": perfil_id, "perfil_nombre": perfil.nombre}
    )
