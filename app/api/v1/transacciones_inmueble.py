"""
💼 API de Transacciones por Inmueble
Sistema Inmobiliario - Historial de alquileres/ventas por unidad
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user, require_ofertante
from app.models.propiedad import Propiedad
from app.models.transaccion_inmueble import InmuebleTransaccion
from app.models.ocupante import Ocupante
from app.models.usuario import Usuario
from app.schemas.transaccion_inmueble import TransaccionCreate, TransaccionUpdate, TransaccionResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# 📋 ENDPOINTS
# ============================================

@router.get("/{propiedad_id}/transacciones-edificio", response_model=List[TransaccionResponse])
async def listar_transacciones_edificio(
    propiedad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Obtener transacciones vigentes de TODAS las oficinas de un edificio"""
    # Buscar todas las oficinas hijas del edificio
    oficinas = db.query(Propiedad.registro_cab_id).filter(
        Propiedad.padre_registro_cab_id == propiedad_id
    ).all()

    if not oficinas:
        return []

    ids_oficinas = [o.registro_cab_id for o in oficinas]

    transacciones = db.query(InmuebleTransaccion).filter(
        InmuebleTransaccion.registro_cab_id.in_(ids_oficinas),
        InmuebleTransaccion.es_vigente == True
    ).all()

    return transacciones


@router.get("/{propiedad_id}/transacciones", response_model=List[TransaccionResponse])
async def listar_transacciones(
    propiedad_id: int,
    solo_vigente: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Listar historial de transacciones de una unidad"""
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    query = db.query(InmuebleTransaccion).filter(
        InmuebleTransaccion.registro_cab_id == propiedad_id
    )

    if solo_vigente:
        query = query.filter(InmuebleTransaccion.es_vigente == True)

    transacciones = query.order_by(
        InmuebleTransaccion.es_vigente.desc(),
        InmuebleTransaccion.created_at.desc()
    ).all()

    return transacciones


@router.get("/{propiedad_id}/transaccion-vigente", response_model=Optional[TransaccionResponse])
async def obtener_transaccion_vigente(
    propiedad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🔍 Obtener la transacción vigente (actual) de una unidad"""
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    transaccion = db.query(InmuebleTransaccion).filter(
        InmuebleTransaccion.registro_cab_id == propiedad_id,
        InmuebleTransaccion.es_vigente == True
    ).first()

    return transaccion


@router.post("/{propiedad_id}/transacciones", response_model=TransaccionResponse, status_code=201)
async def crear_transaccion(
    propiedad_id: int,
    transaccion_data: TransaccionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_ofertante)
):
    """🏗️ Registrar nueva transacción (auto-marca la anterior como histórica)"""
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

    # Marcar transacción anterior como no vigente (historial)
    transaccion_anterior = db.query(InmuebleTransaccion).filter(
        InmuebleTransaccion.registro_cab_id == propiedad_id,
        InmuebleTransaccion.es_vigente == True
    ).first()

    if transaccion_anterior:
        transaccion_anterior.es_vigente = False
        transaccion_anterior.updated_by = current_user.usuario_id

    # Auto-crear ocupante si no hay ocupante_id pero si hay DNI
    if not transaccion_data.ocupante_id and transaccion_data.inquilino_ruc:
        ocupante_existente = db.query(Ocupante).filter(
            Ocupante.dni == transaccion_data.inquilino_ruc
        ).first()

        if ocupante_existente:
            # Ya existe, usar su ID
            transaccion_data.ocupante_id = ocupante_existente.ocupante_id
            logger.info(f"Ocupante existente encontrado: ID {ocupante_existente.ocupante_id} para DNI {transaccion_data.inquilino_ruc}")
        else:
            # Crear nuevo ocupante
            nuevo_ocupante = Ocupante(
                dni=transaccion_data.inquilino_ruc,
                nombre=transaccion_data.inquilino_nombre or "Sin nombre",
                empresa=transaccion_data.inquilino_contacto,
                telefono=transaccion_data.inquilino_telefono,
                email=transaccion_data.inquilino_email,
                tipo_persona=transaccion_data.tipo_persona or "natural",
                created_by=current_user.usuario_id
            )
            db.add(nuevo_ocupante)
            db.flush()  # Obtener ID sin commit
            transaccion_data.ocupante_id = nuevo_ocupante.ocupante_id
            logger.info(f"Ocupante auto-creado: ID {nuevo_ocupante.ocupante_id} para DNI {transaccion_data.inquilino_ruc}")

    # Crear nueva transacción vigente
    nueva_transaccion = InmuebleTransaccion(
        registro_cab_id=propiedad_id,
        tipo_transaccion=transaccion_data.tipo_transaccion,
        estado_ocupacion=transaccion_data.estado_ocupacion or "libre",
        inquilino_nombre=transaccion_data.inquilino_nombre,
        inquilino_ruc=transaccion_data.inquilino_ruc,
        inquilino_contacto=transaccion_data.inquilino_contacto,
        inquilino_telefono=transaccion_data.inquilino_telefono,
        inquilino_email=transaccion_data.inquilino_email,
        parqueos_simples=transaccion_data.parqueos_simples or 0,
        parqueos_dobles=transaccion_data.parqueos_dobles or 0,
        tipo_persona=transaccion_data.tipo_persona or "natural",
        ocupante_id=transaccion_data.ocupante_id,
        corredor_id=transaccion_data.corredor_id,
        comision_porcentaje=transaccion_data.comision_porcentaje,
        fecha_inicio=transaccion_data.fecha_inicio,
        fecha_fin=transaccion_data.fecha_fin,
        precio_oficina=transaccion_data.precio_oficina,
        precio_estacionamiento=transaccion_data.precio_estacionamiento,
        precio_venta=transaccion_data.precio_venta,
        moneda=transaccion_data.moneda or "USD",
        es_vigente=True,
        observaciones=transaccion_data.observaciones,
        created_by=current_user.usuario_id
    )

    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)

    return nueva_transaccion


@router.put("/{propiedad_id}/transacciones/{transaccion_id}", response_model=TransaccionResponse)
async def actualizar_transaccion(
    propiedad_id: int,
    transaccion_id: int,
    transaccion_data: TransaccionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_ofertante)
):
    """✏️ Actualizar una transacción existente"""
    transaccion = db.query(InmuebleTransaccion).filter(
        InmuebleTransaccion.transaccion_id == transaccion_id
    ).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    # Verificar permisos
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == transaccion.registro_cab_id
    ).first()
    if current_user.perfil_id != 4:
        if propiedad.usuario_id != current_user.usuario_id and \
           propiedad.corredor_asignado_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta propiedad")

    update_data = transaccion_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaccion, field, value)

    transaccion.updated_by = current_user.usuario_id
    db.commit()
    db.refresh(transaccion)
    return transaccion
