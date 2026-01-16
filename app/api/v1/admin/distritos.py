"""
📍 CRUD Mantenimiento - Distritos
Solo accesible para Administradores (perfil_id = 4)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import require_admin
from app.models.distrito import Distrito
from app.models.usuario import Usuario
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==========================================
# 📋 SCHEMAS
# ==========================================

class DistritoResponse(BaseModel):
    distrito_id: int
    nombre: str
    provincia: Optional[str]
    departamento: Optional[str]
    activo: bool

    class Config:
        from_attributes = True


class DistritoCreate(BaseModel):
    nombre: str
    provincia: Optional[str] = None
    departamento: Optional[str] = None


class DistritoUpdate(BaseModel):
    nombre: Optional[str] = None
    provincia: Optional[str] = None
    departamento: Optional[str] = None
    activo: Optional[bool] = None


class DistritoPaginado(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[DistritoResponse]


# ==========================================
# 🛠️ ENDPOINTS CRUD
# ==========================================

@router.get("", response_model=List[DistritoResponse])
async def listar_distritos(
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """📋 Listar todos los distritos"""
    try:
        query = db.query(Distrito)

        if activo is not None:
            query = query.filter(Distrito.activo == activo)

        distritos = query.order_by(Distrito.nombre).all()
        logger.info(f"✅ Admin {current_user.usuario_id} listó {len(distritos)} distritos")
        return distritos
    except Exception as e:
        logger.error(f"❌ Error listando distritos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/paginado", response_model=DistritoPaginado)
async def listar_distritos_paginado(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """📋 Listar distritos con paginación y búsqueda"""
    try:
        query = db.query(Distrito)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(Distrito.nombre.ilike(search_filter))

        total = query.count()
        total_pages = (total + page_size - 1) // page_size

        offset = (page - 1) * page_size
        distritos = query.order_by(Distrito.nombre).offset(offset).limit(page_size).all()

        logger.info(f"✅ Admin {current_user.usuario_id} consultó distritos paginados (página {page})")

        return DistritoPaginado(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=distritos
        )
    except Exception as e:
        logger.error(f"❌ Error en paginación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{distrito_id}", response_model=DistritoResponse)
async def obtener_distrito(
    distrito_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🔍 Obtener un distrito por ID"""
    distrito = db.query(Distrito).filter(
        Distrito.distrito_id == distrito_id
    ).first()

    if not distrito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Distrito no encontrado"
        )

    return distrito


@router.post("", response_model=DistritoResponse)
async def crear_distrito(
    distrito: DistritoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """➕ Crear nuevo distrito"""
    try:
        # Validar nombre único
        existing = db.query(Distrito).filter(
            Distrito.nombre == distrito.nombre
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un distrito con ese nombre"
            )

        nuevo_distrito = Distrito(
            nombre=distrito.nombre,
            provincia=distrito.provincia,
            departamento=distrito.departamento,
            activo=True
        )

        db.add(nuevo_distrito)
        db.commit()
        db.refresh(nuevo_distrito)

        logger.info(f"✅ Admin {current_user.usuario_id} creó distrito: {nuevo_distrito.nombre}")
        return nuevo_distrito

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando distrito: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{distrito_id}", response_model=DistritoResponse)
async def actualizar_distrito(
    distrito_id: int,
    distrito: DistritoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """✏️ Actualizar distrito existente"""
    try:
        distrito_db = db.query(Distrito).filter(
            Distrito.distrito_id == distrito_id
        ).first()

        if not distrito_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distrito no encontrado"
            )

        # Actualizar campos
        if distrito.nombre is not None:
            # Validar nombre único (excepto el actual)
            existing = db.query(Distrito).filter(
                Distrito.nombre == distrito.nombre,
                Distrito.distrito_id != distrito_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro distrito con ese nombre"
                )
            distrito_db.nombre = distrito.nombre

        if distrito.provincia is not None:
            distrito_db.provincia = distrito.provincia
        if distrito.departamento is not None:
            distrito_db.departamento = distrito.departamento
        if distrito.activo is not None:
            distrito_db.activo = distrito.activo

        db.commit()
        db.refresh(distrito_db)

        logger.info(f"✅ Admin {current_user.usuario_id} actualizó distrito: {distrito_db.nombre}")
        return distrito_db

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando distrito: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{distrito_id}")
async def eliminar_distrito(
    distrito_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🗑️ Eliminar distrito"""
    try:
        distrito_db = db.query(Distrito).filter(
            Distrito.distrito_id == distrito_id
        ).first()

        if not distrito_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distrito no encontrado"
            )

        # TODO: Validar que no tenga propiedades asociadas

        db.delete(distrito_db)
        db.commit()

        logger.info(f"✅ Admin {current_user.usuario_id} eliminó distrito: {distrito_db.nombre}")

        return {
            "success": True,
            "message": "Distrito eliminado exitosamente",
            "distrito_id": distrito_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando distrito: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
