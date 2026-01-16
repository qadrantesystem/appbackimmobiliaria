"""
📊 CRUD Mantenimiento - Estados CRM
Solo accesible para Administradores (perfil_id = 4)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import require_admin
from app.models.estado_crm import EstadoCRM
from app.models.usuario import Usuario
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ==========================================
# 📋 SCHEMAS
# ==========================================

class EstadoCRMResponse(BaseModel):
    estado_id: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    color: Optional[str]
    icono: Optional[str]
    orden: int
    es_final: bool
    es_ganado: bool
    activo: bool

    class Config:
        from_attributes = True


class EstadoCRMCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    color: Optional[str] = "#6B7280"
    icono: Optional[str] = None
    orden: int = 0
    es_final: bool = False
    es_ganado: bool = False


class EstadoCRMUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    orden: Optional[int] = None
    es_final: Optional[bool] = None
    es_ganado: Optional[bool] = None
    activo: Optional[bool] = None


class EstadoCRMPaginado(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[EstadoCRMResponse]


# ==========================================
# 🛠️ ENDPOINTS CRUD
# ==========================================

@router.get("", response_model=List[EstadoCRMResponse])
async def listar_estados_crm(
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """📋 Listar todos los estados CRM (ordenados por orden)"""
    try:
        query = db.query(EstadoCRM)

        if activo is not None:
            query = query.filter(EstadoCRM.activo == activo)

        estados = query.order_by(EstadoCRM.orden).all()
        logger.info(f"✅ Admin {current_user.usuario_id} listó {len(estados)} estados CRM")
        return estados
    except Exception as e:
        logger.error(f"❌ Error listando estados CRM: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/paginado", response_model=EstadoCRMPaginado)
async def listar_estados_paginado(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """📋 Listar estados CRM con paginación y búsqueda"""
    try:
        query = db.query(EstadoCRM)

        if search:
            search_filter = f"%{search}%"
            query = query.filter(EstadoCRM.nombre.ilike(search_filter))

        total = query.count()
        total_pages = (total + page_size - 1) // page_size

        offset = (page - 1) * page_size
        estados = query.order_by(EstadoCRM.orden).offset(offset).limit(page_size).all()

        logger.info(f"✅ Admin {current_user.usuario_id} consultó estados CRM paginados (página {page})")

        return EstadoCRMPaginado(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=estados
        )
    except Exception as e:
        logger.error(f"❌ Error en paginación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{estado_id}", response_model=EstadoCRMResponse)
async def obtener_estado_crm(
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🔍 Obtener un estado CRM por ID"""
    estado = db.query(EstadoCRM).filter(
        EstadoCRM.estado_id == estado_id
    ).first()

    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado CRM no encontrado"
        )

    return estado


@router.post("", response_model=EstadoCRMResponse)
async def crear_estado_crm(
    estado: EstadoCRMCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """➕ Crear nuevo estado CRM"""
    try:
        # Validar código único
        existing = db.query(EstadoCRM).filter(
            EstadoCRM.codigo == estado.codigo
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un estado con ese código"
            )

        nuevo_estado = EstadoCRM(
            codigo=estado.codigo,
            nombre=estado.nombre,
            descripcion=estado.descripcion,
            color=estado.color,
            icono=estado.icono,
            orden=estado.orden,
            es_final=estado.es_final,
            es_ganado=estado.es_ganado,
            activo=True
        )

        db.add(nuevo_estado)
        db.commit()
        db.refresh(nuevo_estado)

        logger.info(f"✅ Admin {current_user.usuario_id} creó estado CRM: {nuevo_estado.nombre}")
        return nuevo_estado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creando estado CRM: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{estado_id}", response_model=EstadoCRMResponse)
async def actualizar_estado_crm(
    estado_id: int,
    estado: EstadoCRMUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """✏️ Actualizar estado CRM existente"""
    try:
        estado_db = db.query(EstadoCRM).filter(
            EstadoCRM.estado_id == estado_id
        ).first()

        if not estado_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estado CRM no encontrado"
            )

        # Actualizar campos
        if estado.codigo is not None:
            # Validar código único (excepto el actual)
            existing = db.query(EstadoCRM).filter(
                EstadoCRM.codigo == estado.codigo,
                EstadoCRM.estado_id != estado_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe otro estado con ese código"
                )
            estado_db.codigo = estado.codigo

        if estado.nombre is not None:
            estado_db.nombre = estado.nombre
        if estado.descripcion is not None:
            estado_db.descripcion = estado.descripcion
        if estado.color is not None:
            estado_db.color = estado.color
        if estado.icono is not None:
            estado_db.icono = estado.icono
        if estado.orden is not None:
            estado_db.orden = estado.orden
        if estado.es_final is not None:
            estado_db.es_final = estado.es_final
        if estado.es_ganado is not None:
            estado_db.es_ganado = estado.es_ganado
        if estado.activo is not None:
            estado_db.activo = estado.activo

        db.commit()
        db.refresh(estado_db)

        logger.info(f"✅ Admin {current_user.usuario_id} actualizó estado CRM: {estado_db.nombre}")
        return estado_db

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando estado CRM: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{estado_id}")
async def eliminar_estado_crm(
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """🗑️ Eliminar estado CRM"""
    try:
        estado_db = db.query(EstadoCRM).filter(
            EstadoCRM.estado_id == estado_id
        ).first()

        if not estado_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estado CRM no encontrado"
            )

        # TODO: Validar que no esté en uso

        db.delete(estado_db)
        db.commit()

        logger.info(f"✅ Admin {current_user.usuario_id} eliminó estado CRM: {estado_db.nombre}")

        return {
            "success": True,
            "message": "Estado CRM eliminado exitosamente",
            "estado_id": estado_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando estado CRM: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
