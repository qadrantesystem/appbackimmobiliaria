"""
👤 API de Propietarios
Sistema Inmobiliario - Gestión de propietarios normalizados
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.propietario import Propietario
from app.models.usuario import Usuario
from app.schemas.propietario import (
    PropietarioCreate,
    PropietarioUpdate,
    PropietarioResponse,
    PropietarioBuscarResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 🔍 BUSCAR PROPIETARIO POR DNI (Auto-fill)
# ============================================

@router.get("/{dni}", response_model=PropietarioBuscarResponse, status_code=status.HTTP_200_OK)
async def buscar_propietario_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    🔍 Buscar propietario por DNI o RUC (auto-fill frontend)

    Si el propietario existe, devuelve sus datos para auto-completar el formulario.
    Si no existe, el frontend permite crear uno nuevo.
    Busca por DNI (8 dígitos) o por RUC (11 dígitos).
    """
    logger.info(f"Buscando propietario con documento: {dni}")

    # Buscar por DNI primero, luego por RUC
    propietario = db.query(Propietario).filter(
        Propietario.dni == dni,
        Propietario.activo == True
    ).first()

    if not propietario and len(dni) == 11:
        propietario = db.query(Propietario).filter(
            Propietario.ruc == dni,
            Propietario.activo == True
        ).first()

    if not propietario:
        logger.info(f"Propietario con documento {dni} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propietario no encontrado"
        )

    logger.info(f"Propietario encontrado: {propietario.nombre}")

    return PropietarioBuscarResponse(
        propietario_id=propietario.propietario_id,
        tipo_persona=propietario.tipo_persona or "natural",
        tipo_documento=propietario.tipo_documento or "DNI",
        dni=propietario.dni,
        nombre=propietario.nombre,
        razon_social=propietario.razon_social,
        ruc=propietario.ruc,
        representante_legal=propietario.representante_legal,
        telefono=propietario.telefono,
        email=propietario.email,
        existe=True
    )

# ============================================
# 📋 LISTAR PROPIETARIOS
# ============================================

@router.get("", response_model=List[PropietarioResponse], status_code=status.HTTP_200_OK)
async def listar_propietarios(
    skip: int = 0,
    limit: int = 100,
    activo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📋 Listar todos los propietarios activos

    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Cantidad máxima de registros a devolver
    - **activo**: Filtrar por propietarios activos/inactivos
    """
    logger.info(f"Listando propietarios (skip={skip}, limit={limit}, activo={activo})")

    query = db.query(Propietario)

    if activo is not None:
        query = query.filter(Propietario.activo == activo)

    propietarios = query.order_by(Propietario.nombre).offset(skip).limit(limit).all()

    logger.info(f"Propietarios encontrados: {len(propietarios)}")

    return propietarios

# ============================================
# ➕ CREAR PROPIETARIO
# ============================================

@router.post("", response_model=PropietarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_propietario(
    propietario: PropietarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    ➕ Crear un nuevo propietario

    El DNI debe ser único en el sistema.
    """
    logger.info(f"Creando propietario: {propietario.nombre} - DNI: {propietario.dni}")

    # Verificar si el DNI ya existe
    propietario_existente = db.query(Propietario).filter(
        Propietario.dni == propietario.dni
    ).first()

    if propietario_existente:
        logger.warning(f"DNI {propietario.dni} ya existe")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El DNI {propietario.dni} ya está registrado"
        )

    try:
        nuevo_propietario = Propietario(
            tipo_persona=propietario.tipo_persona or "natural",
            tipo_documento=propietario.tipo_documento or "DNI",
            dni=propietario.dni,
            nombre=propietario.nombre,
            razon_social=propietario.razon_social,
            ruc=propietario.ruc,
            representante_legal=propietario.representante_legal,
            telefono=propietario.telefono,
            email=propietario.email,
            notas=propietario.notas,
            created_by=current_user.usuario_id,
            updated_by=current_user.usuario_id
        )

        db.add(nuevo_propietario)
        db.commit()
        db.refresh(nuevo_propietario)

        logger.info(f"Propietario creado exitosamente: ID {nuevo_propietario.propietario_id}")

        return nuevo_propietario

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear propietario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear propietario. Verifica que el DNI sea único."
        )

# ============================================
# 🔄 ACTUALIZAR PROPIETARIO
# ============================================

@router.put("/{propietario_id}", response_model=PropietarioResponse, status_code=status.HTTP_200_OK)
async def actualizar_propietario(
    propietario_id: int,
    propietario_update: PropietarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    🔄 Actualizar datos de un propietario existente

    No se puede cambiar el DNI (es único e inmutable).
    """
    logger.info(f"Actualizando propietario ID: {propietario_id}")

    propietario = db.query(Propietario).filter(
        Propietario.propietario_id == propietario_id
    ).first()

    if not propietario:
        logger.warning(f"Propietario ID {propietario_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propietario no encontrado"
        )

    # Actualizar campos si están presentes
    if propietario_update.nombre is not None:
        propietario.nombre = propietario_update.nombre
    if propietario_update.telefono is not None:
        propietario.telefono = propietario_update.telefono
    if propietario_update.email is not None:
        propietario.email = propietario_update.email
    if propietario_update.notas is not None:
        propietario.notas = propietario_update.notas
    if propietario_update.activo is not None:
        propietario.activo = propietario_update.activo

    propietario.updated_by = current_user.usuario_id

    try:
        db.commit()
        db.refresh(propietario)

        logger.info(f"Propietario ID {propietario_id} actualizado exitosamente")

        return propietario

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error al actualizar propietario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar propietario"
        )

# ============================================
# ❌ DESACTIVAR PROPIETARIO (Soft Delete)
# ============================================

@router.delete("/{propietario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_propietario(
    propietario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    ❌ Desactivar (soft delete) un propietario

    No elimina el registro, solo lo marca como inactivo.
    """
    logger.info(f"Desactivando propietario ID: {propietario_id}")

    propietario = db.query(Propietario).filter(
        Propietario.propietario_id == propietario_id
    ).first()

    if not propietario:
        logger.warning(f"Propietario ID {propietario_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propietario no encontrado"
        )

    propietario.activo = False
    propietario.updated_by = current_user.usuario_id

    db.commit()

    logger.info(f"Propietario ID {propietario_id} desactivado exitosamente")

    return None
