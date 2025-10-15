"""
📊 API de Tracking CRM
Sistema Inmobiliario - Historial de cambios de estado de propiedades
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.tracking import Tracking
from app.models.propiedad import Propiedad
from app.models.usuario import Usuario
from app.models.estado_crm import EstadoCRM
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class TrackingResponse(BaseModel):
    tracking_id: int
    registro_cab_id: int
    estado_anterior: Optional[str]
    estado_nuevo: str
    usuario_id: Optional[int]
    corredor_id: Optional[int]
    motivo: Optional[str]
    metadata_json: Optional[dict]
    created_at: datetime
    
    # Datos enriquecidos
    propiedad_titulo: Optional[str] = None
    usuario_nombre: Optional[str] = None
    corredor_nombre: Optional[str] = None
    estado_anterior_nombre: Optional[str] = None
    estado_nuevo_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.get("/propiedad/{registro_cab_id}", response_model=List[TrackingResponse])
async def obtener_tracking_propiedad(
    registro_cab_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    📋 Obtener historial de cambios de estado de una propiedad
    - Usuario normal: solo ve tracking de sus propiedades
    - Admin/Corredor: ve tracking de todas las propiedades
    """
    try:
        # Verificar que la propiedad existe
        propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == registro_cab_id).first()
        
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        
        # Verificar permisos
        es_admin = current_user.perfil_id == 4
        es_corredor = current_user.perfil_id == 3
        es_propietario = propiedad.usuario_id == current_user.usuario_id
        
        if not (es_admin or es_corredor or es_propietario):
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este tracking")
        
        # Obtener tracking
        trackings = db.query(Tracking).filter(
            Tracking.registro_cab_id == registro_cab_id
        ).order_by(Tracking.created_at.desc()).all()
        
        # Enriquecer datos
        resultados = []
        for track in trackings:
            data = track.__dict__.copy()
            data['propiedad_titulo'] = propiedad.titulo
            
            # Usuario que hizo el cambio
            if track.usuario_id:
                usuario = db.query(Usuario).filter(Usuario.usuario_id == track.usuario_id).first()
                if usuario:
                    data['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
            
            # Corredor asignado
            if track.corredor_id:
                corredor = db.query(Usuario).filter(Usuario.usuario_id == track.corredor_id).first()
                if corredor:
                    data['corredor_nombre'] = f"{corredor.nombre} {corredor.apellido}"
            
            # Nombres de estados
            if track.estado_anterior:
                estado_ant = db.query(EstadoCRM).filter(EstadoCRM.codigo == track.estado_anterior).first()
                if estado_ant:
                    data['estado_anterior_nombre'] = estado_ant.nombre
            
            if track.estado_nuevo:
                estado_nvo = db.query(EstadoCRM).filter(EstadoCRM.codigo == track.estado_nuevo).first()
                if estado_nvo:
                    data['estado_nuevo_nombre'] = estado_nvo.nombre
            
            resultados.append(data)
        
        return resultados
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo tracking de propiedad {registro_cab_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tracking")

@router.get("/usuario/mis-propiedades", response_model=List[TrackingResponse])
async def obtener_tracking_mis_propiedades(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Obtener tracking de todas mis propiedades"""
    try:
        # Obtener IDs de propiedades del usuario
        propiedades = db.query(Propiedad.registro_cab_id).filter(
            Propiedad.usuario_id == current_user.usuario_id
        ).all()
        
        prop_ids = [p.registro_cab_id for p in propiedades]
        
        if not prop_ids:
            return []
        
        # Obtener tracking
        trackings = db.query(Tracking).filter(
            Tracking.registro_cab_id.in_(prop_ids)
        ).order_by(Tracking.created_at.desc()).limit(limit).all()
        
        # Enriquecer datos
        resultados = []
        for track in trackings:
            data = track.__dict__.copy()
            
            # Propiedad
            propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == track.registro_cab_id).first()
            if propiedad:
                data['propiedad_titulo'] = propiedad.titulo
            
            # Usuario
            if track.usuario_id:
                usuario = db.query(Usuario).filter(Usuario.usuario_id == track.usuario_id).first()
                if usuario:
                    data['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
            
            # Corredor
            if track.corredor_id:
                corredor = db.query(Usuario).filter(Usuario.usuario_id == track.corredor_id).first()
                if corredor:
                    data['corredor_nombre'] = f"{corredor.nombre} {corredor.apellido}"
            
            # Estados
            if track.estado_anterior:
                estado_ant = db.query(EstadoCRM).filter(EstadoCRM.codigo == track.estado_anterior).first()
                if estado_ant:
                    data['estado_anterior_nombre'] = estado_ant.nombre
            
            if track.estado_nuevo:
                estado_nvo = db.query(EstadoCRM).filter(EstadoCRM.codigo == track.estado_nuevo).first()
                if estado_nvo:
                    data['estado_nuevo_nombre'] = estado_nvo.nombre
            
            resultados.append(data)
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo tracking de mis propiedades: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tracking")

@router.get("/admin/todos", response_model=List[TrackingResponse])
async def obtener_todo_tracking_admin(
    usuario_id: Optional[int] = Query(None),
    corredor_id: Optional[int] = Query(None),
    estado_nuevo: Optional[str] = Query(None),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    📊 Obtener todo el tracking (solo admin)
    Permite filtrar por usuario, corredor, estado y fechas
    """
    try:
        query = db.query(Tracking)
        
        if usuario_id:
            query = query.filter(Tracking.usuario_id == usuario_id)
        
        if corredor_id:
            query = query.filter(Tracking.corredor_id == corredor_id)
        
        if estado_nuevo:
            query = query.filter(Tracking.estado_nuevo == estado_nuevo)
        
        if fecha_desde:
            query = query.filter(Tracking.created_at >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Tracking.created_at <= fecha_hasta)
        
        trackings = query.order_by(Tracking.created_at.desc()).limit(limit).all()
        
        # Enriquecer datos
        resultados = []
        for track in trackings:
            data = track.__dict__.copy()
            
            # Propiedad
            propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == track.registro_cab_id).first()
            if propiedad:
                data['propiedad_titulo'] = propiedad.titulo
            
            # Usuario
            if track.usuario_id:
                usuario = db.query(Usuario).filter(Usuario.usuario_id == track.usuario_id).first()
                if usuario:
                    data['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
            
            # Corredor
            if track.corredor_id:
                corredor = db.query(Usuario).filter(Usuario.usuario_id == track.corredor_id).first()
                if corredor:
                    data['corredor_nombre'] = f"{corredor.nombre} {corredor.apellido}"
            
            # Estados
            if track.estado_anterior:
                estado_ant = db.query(EstadoCRM).filter(EstadoCRM.codigo == track.estado_anterior).first()
                if estado_ant:
                    data['estado_anterior_nombre'] = estado_ant.nombre
            
            if track.estado_nuevo:
                estado_nvo = db.query(EstadoCRM).filter(EstadoCRM.codigo == track.estado_nuevo).first()
                if estado_nvo:
                    data['estado_nuevo_nombre'] = estado_nvo.nombre
            
            resultados.append(data)
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo todo el tracking (admin): {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tracking")

@router.get("/estadisticas/conversiones", response_model=dict)
async def obtener_estadisticas_conversiones(
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    📈 Obtener estadísticas de conversión de estados CRM
    Solo para administradores
    """
    try:
        query = db.query(Tracking)
        
        if fecha_desde:
            query = query.filter(Tracking.created_at >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Tracking.created_at <= fecha_hasta)
        
        trackings = query.all()
        
        # Calcular estadísticas
        total_cambios = len(trackings)
        
        # Contar por estado nuevo
        estados_count = {}
        for track in trackings:
            estado = track.estado_nuevo
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        # Contar cerrados ganados vs perdidos
        cerrados_ganados = sum(1 for t in trackings if t.estado_nuevo == 'cerrado_ganado')
        cerrados_perdidos = sum(1 for t in trackings if t.estado_nuevo == 'cerrado_perdido')
        total_cerrados = cerrados_ganados + cerrados_perdidos
        
        tasa_conversion = (cerrados_ganados / total_cerrados * 100) if total_cerrados > 0 else 0
        
        return {
            "total_cambios": total_cambios,
            "estados_count": estados_count,
            "cerrados_ganados": cerrados_ganados,
            "cerrados_perdidos": cerrados_perdidos,
            "total_cerrados": total_cerrados,
            "tasa_conversion": round(tasa_conversion, 2),
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de conversión: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas")
