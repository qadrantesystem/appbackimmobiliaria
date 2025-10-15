"""
📍 API de Distritos
Sistema Inmobiliario - Solo lectura (GET)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.distrito import Distrito
from pydantic import BaseModel
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class DistritoResponse(BaseModel):
    distrito_id: int
    nombre: str
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    activo: bool
    orden: int
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS (Solo GET)
# ============================================

@router.get("/", response_model=List[DistritoResponse])
async def listar_distritos(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad"),
    provincia: Optional[str] = Query(None, description="Filtrar por provincia"),
    db: Session = Depends(get_db)
):
    """
    📋 Listar todos los distritos
    
    - **activo**: Filtrar por distritos activos/inactivos (opcional)
    - **ciudad**: Filtrar por ciudad (opcional)
    - **provincia**: Filtrar por provincia (opcional)
    - Ordenados por campo 'orden' y nombre
    """
    try:
        query = db.query(Distrito)
        
        if activo is not None:
            query = query.filter(Distrito.activo == activo)
        
        if ciudad:
            query = query.filter(Distrito.ciudad.ilike(f"%{ciudad}%"))
        
        if provincia:
            query = query.filter(Distrito.provincia.ilike(f"%{provincia}%"))
        
        distritos = query.order_by(Distrito.orden, Distrito.nombre).all()
        
        logger.info(f"✅ Listados {len(distritos)} distritos")
        
        return distritos
        
    except Exception as e:
        logger.error(f"❌ Error listando distritos: {e}")
        raise HTTPException(status_code=500, detail="Error al listar distritos")

@router.get("/{distrito_id}", response_model=DistritoResponse)
async def obtener_distrito(
    distrito_id: int,
    db: Session = Depends(get_db)
):
    """
    🔍 Obtener un distrito por ID
    """
    try:
        distrito = db.query(Distrito).filter(Distrito.distrito_id == distrito_id).first()
        
        if not distrito:
            raise HTTPException(status_code=404, detail="Distrito no encontrado")
        
        return distrito
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo distrito {distrito_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener distrito")
