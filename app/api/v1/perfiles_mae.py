from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import func
from app.database import get_db
from app.dependencies import get_current_active_user, require_admin
from app.models import Usuario, Perfil
from app.schemas.common import ResponseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ==========================================
# 📋 SCHEMAS PARA MANTENIMIENTO DE PERFILES
# ==========================================

class PerfilResponse(BaseModel):
    """Schema de respuesta para perfil"""
    perfil_id: int
    nombre: str
    descripcion: Optional[str] = None
    permisos: Optional[dict] = None

    class Config:
        from_attributes = True

class PerfilCreate(BaseModel):
    """Schema para crear perfil"""
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    permisos: Optional[dict] = None

class PerfilUpdate(BaseModel):
    """Schema para actualizar perfil"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    permisos: Optional[dict] = None

class PerfilPaginado(BaseModel):
    """Respuesta paginada de perfiles"""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[PerfilResponse]

# ==========================================
# 🛠️ ENDPOINTS DE MANTENIMIENTO (CRUD)
# ==========================================

@router.get("", response_model=ResponseModel[List[PerfilResponse]])
async def listar_perfiles_mantenimiento(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📋 Listar todos los perfiles (catálogo de roles)
    Endpoint para mantenimiento del sistema
    """
    try:
        perfiles = db.query(Perfil).all()
        return ResponseModel(
            success=True,
            message="Perfiles obtenidos exitosamente",
            data=perfiles
        )
    except Exception as e:
        logger.error(f"❌ Error listando perfiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar perfiles: {str(e)}"
        )

@router.get("/paginado", response_model=PerfilPaginado)
async def listar_perfiles_paginado(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(5, ge=1, le=100, description="Tamaño de página"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📋 Listar perfiles con paginación y búsqueda
    Endpoint para mantenimiento del sistema
    """
    try:
        # Query base
        query = db.query(Perfil)

        # Aplicar filtro de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Perfil.nombre.ilike(search_filter)) |
                (Perfil.descripcion.ilike(search_filter))
            )

        # Calcular total y páginas
        total = query.count()
        total_pages = (total + page_size - 1) // page_size

        # Aplicar paginación
        offset = (page - 1) * page_size
        perfiles = query.order_by(Perfil.perfil_id).offset(offset).limit(page_size).all()

        return PerfilPaginado(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=perfiles
        )
    except Exception as e:
        logger.error(f"❌ Error en paginación de perfiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al paginar perfiles: {str(e)}"
        )

@router.post("", response_model=ResponseModel[PerfilResponse])
async def crear_perfil_mantenimiento(
    perfil: PerfilCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    ➕ Crear nuevo perfil (rol)
    Endpoint para mantenimiento del sistema
    """
    try:
        # Validar que no exista un perfil con el mismo nombre
        existing = db.query(Perfil).filter(func.lower(Perfil.nombre) == func.lower(perfil.nombre)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un perfil con ese nombre"
            )

        # Crear nuevo perfil
        nuevo_perfil = Perfil(
            nombre=perfil.nombre,
            descripcion=perfil.descripcion,
            permisos=perfil.permisos
        )

        db.add(nuevo_perfil)
        db.commit()
        db.refresh(nuevo_perfil)

        logger.info(f"✅ Perfil creado: {nuevo_perfil.nombre}")

        return ResponseModel(
            success=True,
            message="Perfil creado exitosamente",
            data=nuevo_perfil
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando perfil: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear perfil: {str(e)}"
        )

@router.put("/{perfil_id}", response_model=ResponseModel[PerfilResponse])
async def actualizar_perfil_mantenimiento(
    perfil_id: int,
    perfil: PerfilUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    ✏️ Actualizar perfil existente
    Endpoint para mantenimiento del sistema
    """
    try:
        # Buscar perfil
        perfil_db = db.query(Perfil).filter(Perfil.perfil_id == perfil_id).first()
        if not perfil_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )

        # Validar nombre único si se está cambiando
        if perfil.nombre and perfil.nombre != perfil_db.nombre:
            existing = db.query(Perfil).filter(func.lower(Perfil.nombre) == func.lower(perfil.nombre)).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un perfil con ese nombre"
                )

        # Actualizar campos
        if perfil.nombre:
            perfil_db.nombre = perfil.nombre
        if perfil.descripcion is not None:
            perfil_db.descripcion = perfil.descripcion
        if perfil.permisos is not None:
            perfil_db.permisos = perfil.permisos

        db.commit()
        db.refresh(perfil_db)

        logger.info(f"✅ Perfil actualizado: {perfil_db.nombre}")

        return ResponseModel(
            success=True,
            message="Perfil actualizado exitosamente",
            data=perfil_db
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando perfil: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )

@router.delete("/{perfil_id}", response_model=ResponseModel[dict])
async def eliminar_perfil_mantenimiento(
    perfil_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    🗑️ Eliminar perfil
    Endpoint para mantenimiento del sistema
    """
    try:
        # Buscar perfil
        perfil_db = db.query(Perfil).filter(Perfil.perfil_id == perfil_id).first()
        if not perfil_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )

        # Validar que no haya usuarios con este perfil
        usuarios_count = db.query(Usuario).filter(Usuario.perfil_id == perfil_id).count()
        if usuarios_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el perfil porque tiene {usuarios_count} usuario(s) asignado(s)"
            )

        # Hard delete intencional: Perfil es tabla maestra del sistema.
        # Validación previa garantiza que no hay usuarios asignados.
        db.delete(perfil_db)
        db.commit()

        logger.info(f"✅ Perfil eliminado: {perfil_db.nombre}")

        return ResponseModel(
            success=True,
            message="Perfil eliminado exitosamente",
            data={"perfil_id": perfil_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando perfil: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar perfil: {str(e)}"
        )
