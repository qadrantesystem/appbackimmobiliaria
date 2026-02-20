"""
🏢 API de Pisos por Edificio
Sistema Inmobiliario - Configuración de pisos (tipo de uso y metraje)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user, require_ofertante
from app.models.propiedad import Propiedad
from app.models.piso import InmueblePiso
from app.models.usuario import Usuario
from app.schemas.piso import PisoCreate, PisoUpdate, PisoResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# 📋 ENDPOINTS
# ============================================

@router.get("/{propiedad_id}/pisos", response_model=List[PisoResponse])
async def listar_pisos(
    propiedad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Listar pisos de un edificio"""
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    pisos = db.query(InmueblePiso).filter(
        InmueblePiso.registro_cab_id == propiedad_id,
        InmueblePiso.activo == True
    ).order_by(InmueblePiso.numero_piso.asc()).all()

    return pisos


@router.post("/{propiedad_id}/pisos", response_model=List[PisoResponse], status_code=201)
async def crear_pisos(
    propiedad_id: int,
    pisos_data: List[PisoCreate],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_ofertante)
):
    """🏗️ Crear pisos en bulk para un edificio (upsert)"""
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    # Verificar permisos (dueño, corredor asignado, o admin)
    if current_user.perfil_id != 4:
        if propiedad.usuario_id != current_user.usuario_id and \
           propiedad.corredor_asignado_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta propiedad")

    pisos_creados = []
    for piso_data in pisos_data:
        # Verificar si ya existe el piso (upsert)
        existente = db.query(InmueblePiso).filter(
            InmueblePiso.registro_cab_id == propiedad_id,
            InmueblePiso.numero_piso == piso_data.numero_piso
        ).first()

        if existente:
            existente.tipo_uso = piso_data.tipo_uso or existente.tipo_uso
            if piso_data.area_total is not None:
                existente.area_total = piso_data.area_total
            if piso_data.area_comercializable is not None:
                existente.area_comercializable = piso_data.area_comercializable
            if piso_data.cantidad_unidades is not None:
                existente.cantidad_unidades = piso_data.cantidad_unidades
            existente.activo = piso_data.activo
            pisos_creados.append(existente)
        else:
            nuevo_piso = InmueblePiso(
                registro_cab_id=propiedad_id,
                numero_piso=piso_data.numero_piso,
                tipo_uso=piso_data.tipo_uso,
                area_total=piso_data.area_total,
                area_comercializable=piso_data.area_comercializable,
                cantidad_unidades=piso_data.cantidad_unidades,
                activo=piso_data.activo
            )
            db.add(nuevo_piso)
            pisos_creados.append(nuevo_piso)

    db.commit()
    for piso in pisos_creados:
        db.refresh(piso)

    return pisos_creados


@router.put("/{propiedad_id}/pisos/{piso_id}", response_model=PisoResponse)
async def actualizar_piso(
    propiedad_id: int,
    piso_id: int,
    piso_data: PisoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_ofertante)
):
    """✏️ Actualizar un piso específico"""
    piso = db.query(InmueblePiso).filter(
        InmueblePiso.piso_id == piso_id,
        InmueblePiso.registro_cab_id == propiedad_id
    ).first()
    if not piso:
        raise HTTPException(status_code=404, detail="Piso no encontrado")

    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    if current_user.perfil_id != 4:
        if propiedad.usuario_id != current_user.usuario_id and \
           propiedad.corredor_asignado_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta propiedad")

    update_data = piso_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(piso, field, value)

    db.commit()
    db.refresh(piso)
    return piso


@router.delete("/{propiedad_id}/pisos/{piso_id}", status_code=204)
async def eliminar_piso(
    propiedad_id: int,
    piso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_ofertante)
):
    """🗑️ Eliminar un piso (soft delete)"""
    piso = db.query(InmueblePiso).filter(
        InmueblePiso.piso_id == piso_id,
        InmueblePiso.registro_cab_id == propiedad_id
    ).first()
    if not piso:
        raise HTTPException(status_code=404, detail="Piso no encontrado")

    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    if current_user.perfil_id != 4:
        if propiedad.usuario_id != current_user.usuario_id and \
           propiedad.corredor_asignado_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta propiedad")

    piso.activo = False
    db.commit()
