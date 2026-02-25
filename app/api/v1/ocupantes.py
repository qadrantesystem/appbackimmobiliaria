"""
API de Ocupantes de Inmueble
Sistema Inmobiliario - Gestion de ocupantes normalizados
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.ocupante import Ocupante
from app.models.usuario import Usuario
from app.schemas.ocupante import (
    OcupanteCreate,
    OcupanteUpdate,
    OcupanteResponse,
    OcupanteBuscarResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# BUSCAR OCUPANTE POR DNI (Auto-fill)
# ============================================

@router.get("/{dni}", response_model=OcupanteBuscarResponse, status_code=status.HTTP_200_OK)
async def buscar_ocupante_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Buscar ocupante por DNI (auto-fill frontend)

    Si el ocupante existe, devuelve sus datos para auto-completar el formulario.
    Si no existe, el frontend permite crear uno nuevo.
    """
    logger.info(f"Buscando ocupante con DNI: {dni}")

    ocupante = db.query(Ocupante).filter(
        Ocupante.dni == dni,
        Ocupante.activo == True
    ).first()

    if not ocupante:
        logger.info(f"Ocupante con DNI {dni} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocupante no encontrado"
        )

    logger.info(f"Ocupante encontrado: {ocupante.nombre}")

    return OcupanteBuscarResponse(
        ocupante_id=ocupante.ocupante_id,
        dni=ocupante.dni,
        nombre=ocupante.nombre,
        telefono=ocupante.telefono,
        email=ocupante.email,
        tipo_persona=ocupante.tipo_persona,
        empresa=ocupante.empresa,
        existe=True
    )

# ============================================
# LISTAR OCUPANTES
# ============================================

@router.get("", response_model=List[OcupanteResponse], status_code=status.HTTP_200_OK)
async def listar_ocupantes(
    skip: int = 0,
    limit: int = 100,
    activo: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar todos los ocupantes activos

    - **skip**: Numero de registros a saltar (paginacion)
    - **limit**: Cantidad maxima de registros a devolver
    - **activo**: Filtrar por ocupantes activos/inactivos
    """
    logger.info(f"Listando ocupantes (skip={skip}, limit={limit}, activo={activo})")

    query = db.query(Ocupante)

    if activo is not None:
        query = query.filter(Ocupante.activo == activo)

    ocupantes = query.order_by(Ocupante.nombre).offset(skip).limit(limit).all()

    logger.info(f"Ocupantes encontrados: {len(ocupantes)}")

    return ocupantes

# ============================================
# CREAR OCUPANTE
# ============================================

@router.post("", response_model=OcupanteResponse, status_code=status.HTTP_201_CREATED)
async def crear_ocupante(
    ocupante: OcupanteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo ocupante

    El DNI debe ser unico en el sistema.
    """
    logger.info(f"Creando ocupante: {ocupante.nombre} - DNI: {ocupante.dni}")

    # Verificar si el DNI ya existe
    ocupante_existente = db.query(Ocupante).filter(
        Ocupante.dni == ocupante.dni
    ).first()

    if ocupante_existente:
        logger.warning(f"DNI {ocupante.dni} ya existe en ocupantes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El DNI {ocupante.dni} ya esta registrado como ocupante"
        )

    try:
        nuevo_ocupante = Ocupante(
            dni=ocupante.dni,
            nombre=ocupante.nombre,
            telefono=ocupante.telefono,
            email=ocupante.email,
            tipo_persona=ocupante.tipo_persona,
            empresa=ocupante.empresa,
            notas=ocupante.notas,
            created_by=current_user.usuario_id,
            updated_by=current_user.usuario_id
        )

        db.add(nuevo_ocupante)
        db.commit()
        db.refresh(nuevo_ocupante)

        logger.info(f"Ocupante creado exitosamente: ID {nuevo_ocupante.ocupante_id}")

        return nuevo_ocupante

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear ocupante: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear ocupante. Verifica que el DNI sea unico."
        )

# ============================================
# ACTUALIZAR OCUPANTE
# ============================================

@router.put("/{ocupante_id}", response_model=OcupanteResponse, status_code=status.HTTP_200_OK)
async def actualizar_ocupante(
    ocupante_id: int,
    ocupante_update: OcupanteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualizar datos de un ocupante existente

    No se puede cambiar el DNI (es unico e inmutable).
    """
    logger.info(f"Actualizando ocupante ID: {ocupante_id}")

    ocupante = db.query(Ocupante).filter(
        Ocupante.ocupante_id == ocupante_id
    ).first()

    if not ocupante:
        logger.warning(f"Ocupante ID {ocupante_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocupante no encontrado"
        )

    # Actualizar campos si estan presentes
    if ocupante_update.nombre is not None:
        ocupante.nombre = ocupante_update.nombre
    if ocupante_update.telefono is not None:
        ocupante.telefono = ocupante_update.telefono
    if ocupante_update.email is not None:
        ocupante.email = ocupante_update.email
    if ocupante_update.tipo_persona is not None:
        ocupante.tipo_persona = ocupante_update.tipo_persona
    if ocupante_update.empresa is not None:
        ocupante.empresa = ocupante_update.empresa
    if ocupante_update.notas is not None:
        ocupante.notas = ocupante_update.notas
    if ocupante_update.activo is not None:
        ocupante.activo = ocupante_update.activo

    ocupante.updated_by = current_user.usuario_id

    try:
        db.commit()
        db.refresh(ocupante)

        logger.info(f"Ocupante ID {ocupante_id} actualizado exitosamente")

        return ocupante

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error al actualizar ocupante: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar ocupante"
        )

# ============================================
# DESACTIVAR OCUPANTE (Soft Delete)
# ============================================

@router.delete("/{ocupante_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_ocupante(
    ocupante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Desactivar (soft delete) un ocupante

    No elimina el registro, solo lo marca como inactivo.
    """
    logger.info(f"Desactivando ocupante ID: {ocupante_id}")

    ocupante = db.query(Ocupante).filter(
        Ocupante.ocupante_id == ocupante_id
    ).first()

    if not ocupante:
        logger.warning(f"Ocupante ID {ocupante_id} no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocupante no encontrado"
        )

    ocupante.activo = False
    ocupante.updated_by = current_user.usuario_id

    db.commit()

    logger.info(f"Ocupante ID {ocupante_id} desactivado exitosamente")

    return None
