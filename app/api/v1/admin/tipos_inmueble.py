"""
🏢 CRUD Mantenimiento - Tipos de Inmueble
Solo accesible para Administradores (perfil_id = 4)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import require_admin
from app.models.tipo_inmueble import TipoInmueble
from app.models.usuario import Usuario
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==========================================
# 📋 SCHEMAS
# ==========================================

class TipoInmuebleResponse(BaseModel):
    tipo_inmueble_id: int
    nombre: str
    descripcion: Optional[str]
    icono: Optional[str]
    orden: int
    activo: bool

    class Config:
        from_attributes = True


class TipoInmuebleCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    orden: int = 0


class TipoInmuebleUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


class TipoInmueblePaginado(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[TipoInmuebleResponse]


# ==========================================
# 🛠️ ENDPOINTS CRUD
# ==========================================

@router.get("", response_model=List[TipoInmuebleResponse])
async def listar_tipos_inmueble(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """📋 Listar todos los tipos de inmueble (ordenados)"""
    try:
        tipos = db.query(TipoInmueble).order_by(TipoInmueble.orden).all()
        logger.info(f"✅ Admin {current_user.usuario_id} listó {len(tipos)} tipos de inmueble")
        return tipos
    except Exception as e:
        logger.error(f"❌ Error listando tipos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/paginado", response_model=TipoInmueblePaginado)
async def listar_tipos_paginado(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """📋 Listar tipos con paginación y búsqueda"""
    try:
        query = db.query(TipoInmueble)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(TipoInmueble.nombre.ilike(search_filter))

        total = query.count()
        total_pages = (total + page_size - 1) // page_size

        offset = (page - 1) * page_size
        tipos = query.order_by(TipoInmueble.orden).offset(offset).limit(page_size).all()

        logger.info(f"✅ Admin {current_user.usuario_id} consultó tipos paginados (página {page})")

        return TipoInmueblePaginado(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=tipos
        )
    except Exception as e:
        logger.error(f"❌ Error en paginación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{tipo_id}", response_model=TipoInmuebleResponse)
async def obtener_tipo_inmueble(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🔍 Obtener un tipo de inmueble por ID"""
    tipo = db.query(TipoInmueble).filter(
        TipoInmueble.tipo_inmueble_id == tipo_id
    ).first()

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de inmueble no encontrado"
        )

    return tipo


@router.post("", response_model=TipoInmuebleResponse)
async def crear_tipo_inmueble(
    tipo: TipoInmuebleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """➕ Crear nuevo tipo de inmueble"""
    try:
        # Validar nombre único
        existing = db.query(TipoInmueble).filter(
            TipoInmueble.nombre == tipo.nombre
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tipo con ese nombre"
            )

        nuevo_tipo = TipoInmueble(
            nombre=tipo.nombre,
            descripcion=tipo.descripcion,
            icono=tipo.icono,
            orden=tipo.orden,
            activo=True
        )

        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)

        logger.info(f"✅ Admin {current_user.usuario_id} creó tipo: {nuevo_tipo.nombre}")
        return nuevo_tipo

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando tipo: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{tipo_id}", response_model=TipoInmuebleResponse)
async def actualizar_tipo_inmueble(
    tipo_id: int,
    tipo: TipoInmuebleUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """✏️ Actualizar tipo existente"""
    try:
        tipo_db = db.query(TipoInmueble).filter(
            TipoInmueble.tipo_inmueble_id == tipo_id
        ).first()

        if not tipo_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo no encontrado"
            )

        # Actualizar campos
        if tipo.nombre is not None:
            # Validar nombre único (excepto el actual)
            existing = db.query(TipoInmueble).filter(
                TipoInmueble.nombre == tipo.nombre,
                TipoInmueble.tipo_inmueble_id != tipo_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro tipo con ese nombre"
                )
            tipo_db.nombre = tipo.nombre

        if tipo.descripcion is not None:
            tipo_db.descripcion = tipo.descripcion
        if tipo.icono is not None:
            tipo_db.icono = tipo.icono
        if tipo.orden is not None:
            tipo_db.orden = tipo.orden
        if tipo.activo is not None:
            tipo_db.activo = tipo.activo

        db.commit()
        db.refresh(tipo_db)

        logger.info(f"✅ Admin {current_user.usuario_id} actualizó tipo: {tipo_db.nombre}")
        return tipo_db

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando tipo: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{tipo_id}")
async def eliminar_tipo_inmueble(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🗑️ Eliminar tipo de inmueble"""
    try:
        tipo_db = db.query(TipoInmueble).filter(
            TipoInmueble.tipo_inmueble_id == tipo_id
        ).first()

        if not tipo_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo no encontrado"
            )

        # TODO: Validar que no tenga propiedades asociadas
        # from app.models.propiedad import Propiedad
        # propiedades_count = db.query(Propiedad).filter(
        #     Propiedad.tipo_inmueble_id == tipo_id
        # ).count()
        # if propiedades_count > 0:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"No se puede eliminar. Hay {propiedades_count} propiedades asociadas"
        #     )

        db.delete(tipo_db)
        db.commit()

        logger.info(f"✅ Admin {current_user.usuario_id} eliminó tipo: {tipo_db.nombre}")

        return {
            "success": True,
            "message": "Tipo eliminado exitosamente",
            "tipo_id": tipo_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando tipo: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
