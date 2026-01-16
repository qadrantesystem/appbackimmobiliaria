"""
🔗 Mantenimiento - Características x Tipo de Inmueble
Gestión de la relación muchos a muchos entre características y tipos de inmueble
Solo accesible para Administradores (perfil_id = 4)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import require_admin
from app.models.caracteristica_x_inmueble import CaracteristicaXInmueble
from app.models.caracteristica import Caracteristica
from app.models.tipo_inmueble import TipoInmueble
from app.models.usuario import Usuario
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==========================================
# 📋 SCHEMAS
# ==========================================

class CaracteristicaSimple(BaseModel):
    caracteristica_id: int
    nombre: str
    tipo_input: Optional[str]
    orden: int

    class Config:
        from_attributes = True


class AsignarCaracteristicasRequest(BaseModel):
    tipo_inmueble_id: int
    caracteristica_ids: List[int]


class CaracteristicasXInmuebleResponse(BaseModel):
    tipo_inmueble_id: int
    tipo_inmueble_nombre: str
    caracteristicas: List[CaracteristicaSimple]


# ==========================================
# 🛠️ ENDPOINTS
# ==========================================

@router.get("/tipo-inmueble/{tipo_inmueble_id}", response_model=CaracteristicasXInmuebleResponse)
async def obtener_caracteristicas_por_tipo(
    tipo_inmueble_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    📋 Obtener todas las características asignadas a un tipo de inmueble
    """
    # Verificar que el tipo de inmueble existe
    tipo = db.query(TipoInmueble).filter(
        TipoInmueble.tipo_inmueble_id == tipo_inmueble_id
    ).first()

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de inmueble no encontrado"
        )

    # Obtener características asignadas
    relaciones = db.query(CaracteristicaXInmueble).filter(
        CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id
    ).order_by(CaracteristicaXInmueble.orden).all()

    # Obtener objetos de características
    caracteristicas = []
    for rel in relaciones:
        carac = db.query(Caracteristica).filter(
            Caracteristica.caracteristica_id == rel.caracteristica_id
        ).first()
        if carac:
            caracteristicas.append(CaracteristicaSimple(
                caracteristica_id=carac.caracteristica_id,
                nombre=carac.nombre,
                tipo_input=carac.tipo_input,
                orden=rel.orden
            ))

    return CaracteristicasXInmuebleResponse(
        tipo_inmueble_id=tipo_inmueble_id,
        tipo_inmueble_nombre=tipo.nombre,
        caracteristicas=caracteristicas
    )


@router.post("/asignar")
async def asignar_caracteristicas_a_tipo(
    request: AsignarCaracteristicasRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    🔗 Asignar características a un tipo de inmueble

    Reemplaza TODAS las asignaciones anteriores con las nuevas.
    Útil para reconfigurar completamente las características de un tipo.
    """
    try:
        # Verificar que el tipo existe
        tipo = db.query(TipoInmueble).filter(
            TipoInmueble.tipo_inmueble_id == request.tipo_inmueble_id
        ).first()

        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de inmueble no encontrado"
            )

        # Verificar que todas las características existen
        for carac_id in request.caracteristica_ids:
            carac = db.query(Caracteristica).filter(
                Caracteristica.caracteristica_id == carac_id
            ).first()
            if not carac:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Característica {carac_id} no encontrada"
                )

        # Eliminar asignaciones anteriores
        db.query(CaracteristicaXInmueble).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == request.tipo_inmueble_id
        ).delete()

        # Crear nuevas asignaciones
        for idx, carac_id in enumerate(request.caracteristica_ids):
            asignacion = CaracteristicaXInmueble(
                tipo_inmueble_id=request.tipo_inmueble_id,
                caracteristica_id=carac_id,
                orden=idx + 1
            )
            db.add(asignacion)

        db.commit()

        logger.info(f"✅ Admin {current_user.usuario_id} asignó {len(request.caracteristica_ids)} características al tipo {tipo.nombre}")

        return {
            "success": True,
            "message": f"{len(request.caracteristica_ids)} características asignadas exitosamente",
            "tipo_inmueble_id": request.tipo_inmueble_id,
            "tipo_inmueble_nombre": tipo.nombre
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error asignando características: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/tipo-inmueble/{tipo_inmueble_id}/caracteristica/{caracteristica_id}")
async def desasignar_caracteristica(
    tipo_inmueble_id: int,
    caracteristica_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    ❌ Desasignar una característica específica de un tipo de inmueble
    """
    try:
        relacion = db.query(CaracteristicaXInmueble).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id,
            CaracteristicaXInmueble.caracteristica_id == caracteristica_id
        ).first()

        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La asignación no existe"
            )

        db.delete(relacion)
        db.commit()

        logger.info(f"✅ Admin {current_user.usuario_id} desasignó característica {caracteristica_id} del tipo {tipo_inmueble_id}")

        return {
            "success": True,
            "message": "Característica desasignada exitosamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error desasignando característica: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/todas")
async def listar_todas_las_relaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    📊 Listar TODAS las relaciones características x tipo de inmueble
    """
    try:
        # Obtener todos los tipos de inmueble
        tipos = db.query(TipoInmueble).filter(TipoInmueble.activo == True).all()

        resultado = []
        for tipo in tipos:
            # Obtener características asignadas
            relaciones = db.query(CaracteristicaXInmueble).filter(
                CaracteristicaXInmueble.tipo_inmueble_id == tipo.tipo_inmueble_id
            ).order_by(CaracteristicaXInmueble.orden).all()

            caracteristicas = []
            for rel in relaciones:
                carac = db.query(Caracteristica).filter(
                    Caracteristica.caracteristica_id == rel.caracteristica_id
                ).first()
                if carac:
                    caracteristicas.append({
                        "caracteristica_id": carac.caracteristica_id,
                        "nombre": carac.nombre,
                        "tipo_input": carac.tipo_input,
                        "orden": rel.orden
                    })

            resultado.append({
                "tipo_inmueble_id": tipo.tipo_inmueble_id,
                "tipo_inmueble_nombre": tipo.nombre,
                "cantidad_caracteristicas": len(caracteristicas),
                "caracteristicas": caracteristicas
            })

        logger.info(f"✅ Admin {current_user.usuario_id} consultó todas las relaciones carac x inmueble")

        return {
            "success": True,
            "data": resultado
        }

    except Exception as e:
        logger.error(f"❌ Error listando relaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
