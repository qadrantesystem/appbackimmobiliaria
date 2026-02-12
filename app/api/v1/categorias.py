"""
📁 API de Categorías de Características
Sistema Inmobiliario - CRUD completo con paginación
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from app.database import get_db
from app.dependencies import require_admin, get_optional_user
from app.models.categoria import Categoria
from app.models.caracteristica import Caracteristica
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
from app.schemas.common import ResponseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    orden: int = 0
    activo: bool = True

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    orden: Optional[int] = None
    activo: Optional[bool] = None

class CategoriaResponse(CategoriaBase):
    categoria_id: int

    class Config:
        from_attributes = True

class CategoriaPaginada(BaseModel):
    """Respuesta paginada de categorías"""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[CategoriaResponse]

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[CategoriaResponse])
async def listar_categorias(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📋 Listar todas las categorías (sin paginación)

    - **activo**: Filtrar por categorías activas/inactivas (opcional)
    - **search**: Buscar por nombre (opcional)
    - Ordenadas por 'orden' y 'nombre'
    """
    try:
        query = db.query(Categoria)

        if activo is not None:
            query = query.filter(Categoria.activo == activo)

        if search:
            query = query.filter(Categoria.nombre.ilike(f"%{search}%"))

        categorias = query.order_by(Categoria.orden, Categoria.nombre).all()

        logger.info(f"✅ Listadas {len(categorias)} categorías")

        return categorias

    except Exception as e:
        logger.error(f"❌ Error listando categorías: {e}")
        raise HTTPException(status_code=500, detail="Error al listar categorías")


# Schema para característica en respuesta agrupada
class CaracteristicaEnGrupo(BaseModel):
    caracteristica_id: int
    nombre: str
    icono: Optional[str] = None
    activo: bool
    
    class Config:
        from_attributes = True

# Schema para categoría agrupada con características
class CategoriaAgrupada(BaseModel):
    categoria_id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    orden: Optional[int] = None
    caracteristicas: List[CaracteristicaEnGrupo] = []
    
    class Config:
        from_attributes = True


@router.get("/paginado", response_model=CategoriaPaginada)
async def listar_categorias_paginado(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(5, ge=1, le=100, description="Tamaño de página"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📄 Listar categorías con paginación (por defecto 5 registros)

    - **page**: Número de página (comienza en 1)
    - **page_size**: Cantidad de registros por página (default: 5, max: 100)
    - **activo**: Filtrar por categorías activas/inactivas (opcional)
    - **search**: Buscar por nombre (opcional)
    """
    try:
        # Query base
        query = db.query(Categoria)

        # Filtros
        if activo is not None:
            query = query.filter(Categoria.activo == activo)

        if search:
            query = query.filter(Categoria.nombre.ilike(f"%{search}%"))

        # Total de registros
        total = query.count()

        # Paginación
        offset = (page - 1) * page_size
        categorias = query.order_by(Categoria.orden, Categoria.nombre)\
                          .offset(offset)\
                          .limit(page_size)\
                          .all()

        # Calcular total de páginas
        total_pages = (total + page_size - 1) // page_size

        logger.info(f"✅ Página {page}/{total_pages} - {len(categorias)} categorías de {total} totales")

        return CategoriaPaginada(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=categorias
        )

    except Exception as e:
        logger.error(f"❌ Error listando categorías paginadas: {e}")
        raise HTTPException(status_code=500, detail="Error al listar categorías")

@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(get_db)
):
    """
    🔍 Obtener una categoría por ID
    """
    try:
        categoria = db.query(Categoria).filter(Categoria.categoria_id == categoria_id).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return categoria

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo categoría {categoria_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener categoría")

@router.post("/", response_model=CategoriaResponse, status_code=201)
async def crear_categoria(
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    ➕ Crear una nueva categoría

    **Requiere rol Admin**
    """
    try:
        # Verificar si ya existe una categoría con el mismo nombre
        existe = db.query(Categoria).filter(
            func.lower(Categoria.nombre) == categoria_data.nombre.lower()
        ).first()

        if existe:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{categoria_data.nombre}'"
            )

        # Crear nueva categoría
        nueva_categoria = Categoria(**categoria_data.model_dump())

        db.add(nueva_categoria)
        db.commit()
        db.refresh(nueva_categoria)

        logger.info(f"✅ Categoría creada: {nueva_categoria.nombre} (ID: {nueva_categoria.categoria_id})")

        return nueva_categoria

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando categoría: {e}")
        raise HTTPException(status_code=500, detail="Error al crear categoría")

@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def actualizar_categoria(
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    ✏️ Actualizar una categoría

    **Requiere rol Admin**
    """
    try:
        categoria = db.query(Categoria).filter(Categoria.categoria_id == categoria_id).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Verificar nombre único (si se está actualizando)
        if categoria_data.nombre:
            existe = db.query(Categoria).filter(
                Categoria.categoria_id != categoria_id,
                func.lower(Categoria.nombre) == categoria_data.nombre.lower()
            ).first()

            if existe:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe otra categoría con el nombre '{categoria_data.nombre}'"
                )

        # Actualizar campos
        update_data = categoria_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(categoria, field, value)

        db.commit()
        db.refresh(categoria)

        logger.info(f"✅ Categoría actualizada: {categoria.nombre} (ID: {categoria_id})")

        return categoria

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando categoría {categoria_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar categoría")

@router.delete("/{categoria_id}", status_code=204)
async def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    🗑️ Eliminar una categoría (soft delete - marca como inactivo)

    **Requiere rol Admin**

    Nota: No elimina físicamente, solo marca como inactivo para mantener integridad referencial
    """
    try:
        categoria = db.query(Categoria).filter(Categoria.categoria_id == categoria_id).first()

        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Soft delete - marcar como inactivo
        categoria.activo = False

        db.commit()

        logger.info(f"✅ Categoría eliminada (soft delete): {categoria.nombre} (ID: {categoria_id})")

        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando categoría {categoria_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar categoría")

@router.get("/agrupadas", response_model=ResponseModel[List[CategoriaAgrupada]])
async def listar_categorias_agrupadas(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📋 Listar categorías con sus características agrupadas
    Útil para tree views y selección dinámica
    """
    try:
        # Query base de categorías
        query = db.query(Categoria)
        
        if activo is not None:
            query = query.filter(Categoria.activo == activo)
        
        categorias = query.order_by(Categoria.orden, Categoria.nombre).all()
        
        # Formatear respuesta con características incluidas
        resultado = []
        for categoria in categorias:
            # Obtener características de esta categoría
            caracteristicas = db.query(Caracteristica).filter(
                Caracteristica.categoria_id == categoria.categoria_id,
                Caracteristica.activo == True
            ).order_by(Caracteristica.nombre).all()
            
            resultado.append(CategoriaAgrupada(
                categoria_id=categoria.categoria_id,
                nombre=categoria.nombre,
                descripcion=categoria.descripcion,
                activo=categoria.activo,
                orden=categoria.orden,
                caracteristicas=[
                    CaracteristicaEnGrupo(
                        caracteristica_id=c.caracteristica_id,
                        nombre=c.nombre,
                        icono=c.icono,
                        activo=c.activo
                    )
                    for c in caracteristicas
                ]
            ))
        
        return ResponseModel(
            success=True,
            message="Categorías agrupadas obtenidas exitosamente",
            data=resultado
        )
    
    except Exception as e:
        logger.error(f"❌ Error listando categorías agrupadas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar categorías agrupadas: {str(e)}"
        )

