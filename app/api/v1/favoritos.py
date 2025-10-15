"""
⭐ API de Favoritos
Sistema Inmobiliario - Gestión de propiedades favoritas
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.favorito import Favorito
from app.models.propiedad import Propiedad
from app.models.usuario import Usuario
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class FavoritoCreate(BaseModel):
    registro_cab_id: int
    notas: Optional[str] = None

class FavoritoUpdate(BaseModel):
    notas: Optional[str] = None

class FavoritoResponse(BaseModel):
    favorito_id: int
    usuario_id: int
    registro_cab_id: int
    notas: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoritoDetalle(FavoritoResponse):
    propiedad_titulo: str
    propiedad_direccion: Optional[str]
    propiedad_precio: Optional[float]
    propiedad_tipo: Optional[str]

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/", response_model=List[FavoritoDetalle])
async def listar_mis_favoritos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Listar mis propiedades favoritas"""
    try:
        resultados = db.query(Favorito, Propiedad).join(
            Propiedad, Favorito.registro_cab_id == Propiedad.registro_cab_id
        ).filter(
            Favorito.usuario_id == current_user.usuario_id
        ).order_by(Favorito.created_at.desc()).all()
        
        favoritos = []
        for fav, prop in resultados:
            favoritos.append({
                **fav.__dict__,
                "propiedad_titulo": prop.titulo or "Sin título",
                "propiedad_direccion": prop.direccion,
                "propiedad_precio": float(prop.precio) if prop.precio else None,
                "propiedad_tipo": prop.tipo_operacion
            })
        
        return favoritos
        
    except Exception as e:
        logger.error(f"❌ Error listando favoritos: {e}")
        raise HTTPException(status_code=500, detail="Error al listar favoritos")

@router.post("/", response_model=FavoritoResponse, status_code=201)
async def agregar_favorito(
    favorito_data: FavoritoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """➕ Agregar propiedad a favoritos"""
    try:
        # Verificar que la propiedad existe
        propiedad = db.query(Propiedad).filter(
            Propiedad.registro_cab_id == favorito_data.registro_cab_id
        ).first()
        
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        
        # Verificar si ya existe en favoritos
        existe = db.query(Favorito).filter(
            Favorito.usuario_id == current_user.usuario_id,
            Favorito.registro_cab_id == favorito_data.registro_cab_id
        ).first()
        
        if existe:
            raise HTTPException(status_code=400, detail="Esta propiedad ya está en tus favoritos")
        
        nuevo_favorito = Favorito(
            usuario_id=current_user.usuario_id,
            **favorito_data.model_dump()
        )
        
        db.add(nuevo_favorito)
        db.commit()
        db.refresh(nuevo_favorito)
        
        logger.info(f"✅ Favorito agregado: usuario={current_user.usuario_id}, propiedad={favorito_data.registro_cab_id}")
        
        return nuevo_favorito
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error agregando favorito: {e}")
        raise HTTPException(status_code=500, detail=f"Error al agregar favorito: {str(e)}")

@router.get("/{favorito_id}", response_model=FavoritoDetalle)
async def obtener_favorito(
    favorito_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🔍 Obtener un favorito por ID"""
    try:
        resultado = db.query(Favorito, Propiedad).join(
            Propiedad, Favorito.registro_cab_id == Propiedad.registro_cab_id
        ).filter(
            Favorito.favorito_id == favorito_id,
            Favorito.usuario_id == current_user.usuario_id
        ).first()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Favorito no encontrado")
        
        fav, prop = resultado
        
        return {
            **fav.__dict__,
            "propiedad_titulo": prop.titulo or "Sin título",
            "propiedad_direccion": prop.direccion,
            "propiedad_precio": float(prop.precio) if prop.precio else None,
            "propiedad_tipo": prop.tipo_operacion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo favorito {favorito_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener favorito")

@router.put("/{favorito_id}", response_model=FavoritoResponse)
async def actualizar_favorito(
    favorito_id: int,
    favorito_data: FavoritoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """✏️ Actualizar notas de un favorito"""
    try:
        favorito = db.query(Favorito).filter(
            Favorito.favorito_id == favorito_id,
            Favorito.usuario_id == current_user.usuario_id
        ).first()
        
        if not favorito:
            raise HTTPException(status_code=404, detail="Favorito no encontrado")
        
        if favorito_data.notas is not None:
            favorito.notas = favorito_data.notas
        
        db.commit()
        db.refresh(favorito)
        
        logger.info(f"✅ Favorito actualizado: {favorito_id}")
        
        return favorito
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando favorito {favorito_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar favorito: {str(e)}")

@router.delete("/{favorito_id}")
async def eliminar_favorito(
    favorito_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🗑️ Eliminar un favorito"""
    try:
        favorito = db.query(Favorito).filter(
            Favorito.favorito_id == favorito_id,
            Favorito.usuario_id == current_user.usuario_id
        ).first()
        
        if not favorito:
            raise HTTPException(status_code=404, detail="Favorito no encontrado")
        
        db.delete(favorito)
        db.commit()
        
        logger.info(f"✅ Favorito eliminado: {favorito_id}")
        
        return {
            "success": True,
            "message": "Favorito eliminado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando favorito {favorito_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar favorito: {str(e)}")

@router.delete("/propiedad/{registro_cab_id}")
async def eliminar_favorito_por_propiedad(
    registro_cab_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🗑️ Eliminar favorito por ID de propiedad"""
    try:
        favorito = db.query(Favorito).filter(
            Favorito.registro_cab_id == registro_cab_id,
            Favorito.usuario_id == current_user.usuario_id
        ).first()
        
        if not favorito:
            raise HTTPException(status_code=404, detail="Favorito no encontrado")
        
        db.delete(favorito)
        db.commit()
        
        logger.info(f"✅ Favorito eliminado por propiedad: {registro_cab_id}")
        
        return {
            "success": True,
            "message": "Favorito eliminado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando favorito de propiedad {registro_cab_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar favorito: {str(e)}")
