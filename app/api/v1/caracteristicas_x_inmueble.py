"""
🔗 API de Características por Tipo de Inmueble
Sistema Inmobiliario - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import require_admin, get_optional_user
from app.models.caracteristica_x_inmueble import CaracteristicaXInmueble
from app.models.caracteristica import Caracteristica
from app.models.tipo_inmueble import TipoInmueble
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class CaracteristicaXInmuebleBase(BaseModel):
    tipo_inmueble_id: int
    caracteristica_id: int
    requerido: bool = False
    visible_en_filtro: bool = True
    orden: int = Field(default=0, ge=0, le=999)

class CaracteristicaXInmuebleCreate(CaracteristicaXInmuebleBase):
    pass

class CaracteristicaXInmuebleUpdate(BaseModel):
    requerido: Optional[bool] = None
    visible_en_filtro: Optional[bool] = None
    orden: Optional[int] = Field(None, ge=0, le=999)

class CaracteristicaXInmuebleResponse(CaracteristicaXInmuebleBase):
    id: int
    
    class Config:
        from_attributes = True

class CaracteristicaDetalle(BaseModel):
    caracteristica_id: int
    nombre: str
    descripcion: Optional[str]
    tipo_input: Optional[str]
    unidad: Optional[str]
    categoria: Optional[str]
    requerido: bool
    visible_en_filtro: bool
    orden: int
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/tipo-inmueble/{tipo_inmueble_id}", response_model=List[CaracteristicaDetalle])
async def listar_caracteristicas_por_tipo(
    tipo_inmueble_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📋 Listar características de un tipo de inmueble específico
    Retorna las características con sus detalles
    """
    try:
        # Verificar que el tipo de inmueble existe
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_inmueble_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        # Obtener características asociadas
        relaciones = db.query(
            CaracteristicaXInmueble, Caracteristica
        ).join(
            Caracteristica, CaracteristicaXInmueble.caracteristica_id == Caracteristica.caracteristica_id
        ).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id
        ).order_by(
            CaracteristicaXInmueble.orden, Caracteristica.nombre
        ).all()
        
        resultado = []
        for rel, car in relaciones:
            resultado.append({
                "caracteristica_id": car.caracteristica_id,
                "nombre": car.nombre,
                "descripcion": car.descripcion,
                "tipo_input": car.tipo_input,
                "unidad": car.unidad,
                "categoria": car.categoria,
                "requerido": rel.requerido,
                "visible_en_filtro": rel.visible_en_filtro,
                "orden": rel.orden
            })
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listando características del tipo {tipo_inmueble_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al listar características")

@router.post("/", response_model=CaracteristicaXInmuebleResponse, status_code=201)
async def asignar_caracteristica_a_tipo(
    data: CaracteristicaXInmuebleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """➕ Asignar una característica a un tipo de inmueble"""
    try:
        # Verificar que existen
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == data.tipo_inmueble_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")
        
        caracteristica = db.query(Caracteristica).filter(Caracteristica.caracteristica_id == data.caracteristica_id).first()
        if not caracteristica:
            raise HTTPException(status_code=404, detail="Característica no encontrada")
        
        # Verificar si ya existe la relación
        existe = db.query(CaracteristicaXInmueble).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == data.tipo_inmueble_id,
            CaracteristicaXInmueble.caracteristica_id == data.caracteristica_id
        ).first()
        
        if existe:
            raise HTTPException(status_code=400, detail="Esta característica ya está asignada a este tipo de inmueble")
        
        nueva_relacion = CaracteristicaXInmueble(**data.model_dump())
        db.add(nueva_relacion)
        db.commit()
        db.refresh(nueva_relacion)
        
        logger.info(f"✅ Característica {data.caracteristica_id} asignada al tipo {data.tipo_inmueble_id}")
        
        return nueva_relacion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error asignando característica: {e}")
        raise HTTPException(status_code=500, detail=f"Error al asignar característica: {str(e)}")

@router.put("/{relacion_id}", response_model=CaracteristicaXInmuebleResponse)
async def actualizar_caracteristica_tipo(
    relacion_id: int,
    data: CaracteristicaXInmuebleUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """✏️ Actualizar configuración de característica en tipo de inmueble"""
    try:
        relacion = db.query(CaracteristicaXInmueble).filter(CaracteristicaXInmueble.id == relacion_id).first()
        
        if not relacion:
            raise HTTPException(status_code=404, detail="Relación no encontrada")
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(relacion, field, value)
        
        db.commit()
        db.refresh(relacion)
        
        logger.info(f"✅ Relación actualizada (ID: {relacion_id})")
        
        return relacion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando relación {relacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")

@router.delete("/{relacion_id}")
async def eliminar_caracteristica_tipo(
    relacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🗑️ Eliminar asignación de característica a tipo de inmueble"""
    try:
        relacion = db.query(CaracteristicaXInmueble).filter(CaracteristicaXInmueble.id == relacion_id).first()

        if not relacion:
            raise HTTPException(status_code=404, detail="Relación no encontrada")

        # Hard delete intencional: tabla pivote de relación, no requiere soft delete
        db.delete(relacion)
        db.commit()
        
        logger.info(f"✅ Relación eliminada (ID: {relacion_id})")
        
        return {
            "success": True,
            "message": "Característica desasignada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando relación {relacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")

@router.get("/tipo-inmueble/{tipo_inmueble_id}/agrupadas")
async def listar_caracteristicas_agrupadas(
    tipo_inmueble_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📊 Listar características AGRUPADAS POR CATEGORÍA
    Retorna un objeto con categorías y sus características
    Ideal para renderizar filtros avanzados en frontend

    ✅ ACTUALIZADO: Usa tabla categorias_mae normalizada
    """
    try:
        # Verificar que el tipo de inmueble existe
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_inmueble_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")

        # ✅ NUEVA QUERY: Join con categorias_mae
        relaciones = db.query(
            CaracteristicaXInmueble,
            Caracteristica,
            Categoria
        ).join(
            Caracteristica,
            CaracteristicaXInmueble.caracteristica_id == Caracteristica.caracteristica_id
        ).outerjoin(
            Categoria,
            Caracteristica.categoria_id == Categoria.categoria_id
        ).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id,
            CaracteristicaXInmueble.visible_en_filtro == True  # Solo las visibles en filtro
        ).order_by(
            Categoria.orden,
            CaracteristicaXInmueble.orden,
            Caracteristica.nombre
        ).all()

        # Agrupar por categoría
        categorias_dict = {}
        for rel, car, cat in relaciones:
            # Usar categoría normalizada o 'General' como fallback
            categoria_nombre = cat.nombre if cat else 'General'
            categoria_id = cat.categoria_id if cat else None
            orden_cat = cat.orden if cat else 999

            if categoria_nombre not in categorias_dict:
                categorias_dict[categoria_nombre] = {
                    "categoria_id": categoria_id,
                    "nombre": categoria_nombre,
                    "orden": orden_cat,
                    "caracteristicas": []
                }

            categorias_dict[categoria_nombre]["caracteristicas"].append({
                "caracteristica_id": car.caracteristica_id,
                "nombre": car.nombre,
                "descripcion": car.descripcion,
                "tipo_input": car.tipo_input,
                "unidad": car.unidad,
                "requerido": rel.requerido,
                "orden": rel.orden
            })

        # Convertir a lista y ordenar por orden de categoría
        categorias_list = sorted(categorias_dict.values(), key=lambda x: x['orden'])

        return {
            "tipo_inmueble_id": tipo_inmueble_id,
            "tipo_inmueble_nombre": tipo.nombre,
            "categorias": categorias_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listando características agrupadas del tipo {tipo_inmueble_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al listar características agrupadas")

@router.get("/tipo-inmueble/{tipo_inmueble_id}/mantenimiento")
async def listar_todas_caracteristicas_para_mantenimiento(
    tipo_inmueble_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    🛠️ Listar TODAS las características agrupadas por categoría para MANTENIMIENTO
    Muestra todas las características (asignadas y no asignadas) con flag 'asignado'
    Ideal para tree view de asignación en módulo de mantenimiento
    """
    
    # Iconos monocromáticos elegantes con paleta azul/gris corporativa
    ICONOS = {
        # Edificio y estructura
        'ascensor': '▣',
        'elevador': '▣',
        'piso': '▢',
        
        # Áreas comunes
        'piscina': '◈',
        'gimnasio': '◐',
        'gym': '◐',
        'salon': '▭',
        'sala': '▭',
        'terraza': '▱',
        'azotea': '▱',
        'balcon': '▭',
        
        # Seguridad
        'seguridad': '◆',
        'vigilancia': '◆',
        'camaras': '◆',
        'alarma': '◆',
        'portero': '◆',
        
        # Estacionamiento
        'garaje': '▧',
        'estacionamiento': '▧',
        'cochera': '▧',
        'parking': '▧',
        
        # Servicios
        'agua': '◉',
        'luz': '◎',
        'gas': '◉',
        'internet': '◬',
        'wifi': '◬',
        'cable': '◭',
        
        # Espacios verdes
        'parque': '◈',
        'jardin': '◈',
        'area verde': '◈',
        
        # Clima
        'aire': '◐',
        'calefaccion': '◉',
        'ventilacion': '◎',
        
        # Espacios interiores
        'cocina': '▢',
        'baño': '▢',
        'dormitorio': '▢',
        'habitacion': '▢',
        'closet': '▢',
        
        # Servicios adicionales
        'lavanderia': '◫',
        'deposito': '▣',
        'bodega': '▣',
        
        # Características especiales
        'mascotas': '◇',
        'amoblado': '▦',
        'vista': '◈',
        'esquina': '◆',
    }
    
    def obtener_icono(nombre: str) -> str:
        """Retorna icono monocromático basado en palabras clave"""
        nombre_lower = nombre.lower()
        for palabra, icono in ICONOS.items():
            if palabra in nombre_lower:
                return icono
        return '▪'  # Icono por defecto (cuadrado pequeño)
    
    try:
        from sqlalchemy import func as sql_func
        
        # Verificar que el tipo de inmueble existe
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_inmueble_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de inmueble no encontrado")

        # Obtener IDs de características ya asignadas
        asignadas_ids = set(
            rel.caracteristica_id
            for rel in db.query(CaracteristicaXInmueble.caracteristica_id).filter(
                CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id
            ).all()
        )

        # Obtener TODAS las características activas con sus categorías
        caracteristicas = db.query(
            Caracteristica,
            Categoria
        ).outerjoin(
            Categoria,
            Caracteristica.categoria_id == Categoria.categoria_id
        ).filter(
            Caracteristica.activo == True
        ).order_by(
            sql_func.coalesce(Categoria.orden, 999),
            Caracteristica.nombre
        ).all()

        # Agrupar por categoría
        categorias_dict = {}
        for car, cat in caracteristicas:
            categoria_nombre = cat.nombre if cat else 'General'
            categoria_id = cat.categoria_id if cat else None
            orden_cat = cat.orden if cat else 999

            if categoria_nombre not in categorias_dict:
                categorias_dict[categoria_nombre] = {
                    "categoria_id": categoria_id,
                    "nombre": categoria_nombre,
                    "orden": orden_cat,
                    "caracteristicas": []
                }

            categorias_dict[categoria_nombre]["caracteristicas"].append({
                "caracteristica_id": car.caracteristica_id,
                "nombre": car.nombre,
                "icono": obtener_icono(car.nombre),  # ◆ Iconos monocromáticos elegantes
                "asignado": car.caracteristica_id in asignadas_ids
            })

        # Convertir a lista y ordenar
        categorias_list = sorted(categorias_dict.values(), key=lambda x: x['orden'])

        return {
            "tipo_inmueble_id": tipo_inmueble_id,
            "tipo_inmueble_nombre": tipo.nombre,
            "categorias": categorias_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listando características para mantenimiento del tipo {tipo_inmueble_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar características para mantenimiento: {str(e)}")

@router.delete("/tipo/{tipo_inmueble_id}/caracteristica/{caracteristica_id}")
async def eliminar_por_composite_key(
    tipo_inmueble_id: int,
    caracteristica_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🗑️ Eliminar relación usando tipo_inmueble_id + caracteristica_id"""
    try:
        relacion = db.query(CaracteristicaXInmueble).filter(
            CaracteristicaXInmueble.tipo_inmueble_id == tipo_inmueble_id,
            CaracteristicaXInmueble.caracteristica_id == caracteristica_id
        ).first()

        if not relacion:
            raise HTTPException(status_code=404, detail="Relación no encontrada")

        # Hard delete intencional: tabla pivote de relación, no requiere soft delete
        db.delete(relacion)
        db.commit()
        
        logger.info(f"✅ Relación eliminada (Tipo: {tipo_inmueble_id}, Característica: {caracteristica_id})")
        
        return {
            "success": True,
            "message": "Característica desasignada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando relación: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
