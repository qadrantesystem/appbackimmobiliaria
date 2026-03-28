"""
API de Contactos/Leads/Oportunidades CRM
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models.contacto import Contacto
from app.models.propiedad import Propiedad
from app.models.usuario import Usuario
from app.models.tracking import Tracking
from app.dependencies import get_current_active_user, get_optional_user
from app.schemas.common import ResponseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contactos", tags=["Contactos/Leads"])


@router.get("/mis-oportunidades")
async def mis_oportunidades(
    estado: Optional[str] = Query(None, description="Filtrar por estado: nuevo, atendido, en_negociacion, cerrado"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtener oportunidades/leads según perfil:
    - Corredor: contactos de propiedades donde corredor_asignado_id = yo
    - Ofertante: contactos de propiedades donde usuario_id = yo
    - Admin: todos los contactos
    """
    query = db.query(Contacto).join(
        Propiedad, Contacto.registro_cab_id == Propiedad.registro_cab_id
    )

    # Filtrar según perfil
    if current_user.perfil_id == 4:
        pass  # Admin ve todo
    elif current_user.perfil_id == 3:
        # Corredor ve contactos de SUS propiedades asignadas
        query = query.filter(Propiedad.corredor_asignado_id == current_user.usuario_id)
    else:
        # Ofertante ve contactos de SUS propiedades
        query = query.filter(Propiedad.usuario_id == current_user.usuario_id)

    # Filtrar por estado
    if estado:
        query = query.filter(Contacto.estado == estado)

    # Contar totales por estado
    totales_query = db.query(
        Contacto.estado, func.count(Contacto.contacto_id)
    ).join(
        Propiedad, Contacto.registro_cab_id == Propiedad.registro_cab_id
    )

    if current_user.perfil_id == 4:
        pass
    elif current_user.perfil_id == 3:
        totales_query = totales_query.filter(Propiedad.corredor_asignado_id == current_user.usuario_id)
    else:
        totales_query = totales_query.filter(Propiedad.usuario_id == current_user.usuario_id)

    totales = dict(totales_query.group_by(Contacto.estado).all())

    # Paginación
    total = query.count()
    offset = (page - 1) * limit
    contactos = query.order_by(desc(Contacto.created_at)).offset(offset).limit(limit).all()

    # Serializar
    contactos_list = []
    for c in contactos:
        prop = db.query(Propiedad).filter(Propiedad.registro_cab_id == c.registro_cab_id).first()
        contactos_list.append({
            "contacto_id": c.contacto_id,
            "registro_cab_id": c.registro_cab_id,
            "propiedad_titulo": prop.titulo if prop else "Sin título",
            "propiedad_direccion": prop.direccion if prop else None,
            "propiedad_imagen": prop.imagen_principal if prop else None,
            "nombre": c.nombre,
            "email": c.email,
            "telefono": c.telefono,
            "mensaje": c.mensaje,
            "tipo_contacto": c.tipo_contacto,
            "estado": c.estado,
            "notas_corredor": c.notas_corredor,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "atendido_at": c.atendido_at.isoformat() if c.atendido_at else None
        })

    return {
        "success": True,
        "data": contactos_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        },
        "totales": {
            "nuevo": totales.get("nuevo", 0),
            "atendido": totales.get("atendido", 0),
            "en_negociacion": totales.get("en_negociacion", 0),
            "cerrado": totales.get("cerrado", 0),
            "total": sum(totales.values())
        }
    }


@router.patch("/{contacto_id}/estado")
async def actualizar_estado_contacto(
    contacto_id: int,
    estado: str = Query(..., description="nuevo, atendido, en_negociacion, cerrado"),
    notas: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cambiar estado de un contacto/lead"""
    estados_validos = ["nuevo", "atendido", "en_negociacion", "cerrado"]
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {estados_validos}")

    contacto = db.query(Contacto).filter(Contacto.contacto_id == contacto_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")

    estado_anterior = contacto.estado
    contacto.estado = estado
    contacto.updated_at = datetime.utcnow()

    if notas:
        contacto.notas_corredor = notas

    if estado == "atendido" and not contacto.atendido_at:
        contacto.atendido_at = datetime.utcnow()

    # Registrar en tracking
    tracking = Tracking(
        registro_cab_id=contacto.registro_cab_id,
        estado_anterior=f"contacto_{estado_anterior}",
        estado_nuevo=f"contacto_{estado}",
        usuario_id=current_user.usuario_id,
        corredor_id=current_user.usuario_id if current_user.perfil_id == 3 else None,
        motivo=notas or f"Lead cambiado a {estado}",
        metadata_json={"contacto_id": contacto_id}
    )
    db.add(tracking)
    db.commit()

    return ResponseModel(
        success=True,
        message=f"Contacto actualizado a '{estado}'",
        data={"contacto_id": contacto_id, "estado": estado}
    )


@router.get("/tracking/{registro_cab_id}")
async def tracking_propiedad(
    registro_cab_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Timeline de una propiedad: contactos + cambios CRM (para modal Seguimiento)"""
    # Contactos de esta propiedad
    contactos = db.query(Contacto).filter(
        Contacto.registro_cab_id == registro_cab_id
    ).order_by(desc(Contacto.created_at)).all()

    # Tracking CRM
    tracking = db.query(Tracking).filter(
        Tracking.registro_cab_id == registro_cab_id
    ).order_by(desc(Tracking.created_at)).all()

    # Propiedad
    prop = db.query(Propiedad).filter(Propiedad.registro_cab_id == registro_cab_id).first()

    # Construir timeline unificado
    timeline = []

    for c in contactos:
        timeline.append({
            "tipo": "contacto",
            "fecha": c.created_at.isoformat() if c.created_at else None,
            "titulo": f"{c.nombre} contactó",
            "detalle": c.mensaje or "",
            "email": c.email,
            "telefono": c.telefono,
            "estado": c.estado,
            "icono": "📞"
        })

    for t in tracking:
        usuario = db.query(Usuario).filter(Usuario.usuario_id == t.usuario_id).first() if t.usuario_id else None
        timeline.append({
            "tipo": "cambio_estado",
            "fecha": t.created_at.isoformat() if t.created_at else None,
            "titulo": f"Estado: {t.estado_anterior or '?'} → {t.estado_nuevo}",
            "detalle": t.motivo or "",
            "usuario": f"{usuario.nombre} {usuario.apellido}" if usuario else "Sistema",
            "icono": "🔄"
        })

    # Ordenar por fecha desc
    timeline.sort(key=lambda x: x["fecha"] or "", reverse=True)

    return {
        "success": True,
        "data": {
            "propiedad": {
                "titulo": prop.titulo if prop else None,
                "estado_crm": prop.estado_crm if prop else None,
                "vistas": prop.vistas if prop else 0,
                "contactos": prop.contactos if prop else 0
            },
            "timeline": timeline,
            "total_contactos": len(contactos),
            "total_cambios": len(tracking)
        }
    }
