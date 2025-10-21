"""
🔍 API de Búsquedas
Sistema Inmobiliario - Historial y búsquedas guardadas con alertas
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.dependencies import get_current_user, get_optional_user, require_admin
from app.models.busqueda import Busqueda
from app.models.usuario import Usuario
from app.models.tipo_inmueble import TipoInmueble
from app.models.distrito import Distrito
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class BusquedaCreate(BaseModel):
    criterios_json: dict = Field(..., description="JSON completo con todos los criterios de búsqueda")
    cantidad_resultados: Optional[int] = 0
    sesion_id: Optional[str] = None

class BusquedaGuardadaCreate(BaseModel):
    criterios_json: dict = Field(..., description="JSON completo con todos los criterios de búsqueda")
    nombre_busqueda: str = Field(..., min_length=3, max_length=100)
    frecuencia_alerta: str = Field(..., pattern="^(inmediata|diaria|semanal)$")
    alerta_activa: bool = True

class BusquedaGuardadaUpdate(BaseModel):
    nombre_busqueda: Optional[str] = Field(None, min_length=3, max_length=100)
    frecuencia_alerta: Optional[str] = Field(None, pattern="^(inmediata|diaria|semanal)$")
    alerta_activa: Optional[bool] = None

class BusquedaResponse(BaseModel):
    busqueda_id: int
    usuario_id: Optional[int]
    criterios_json: dict
    cantidad_resultados: Optional[int]
    fecha_busqueda: datetime
    es_guardada: bool
    nombre_busqueda: Optional[str]
    frecuencia_alerta: Optional[str]
    alerta_activa: Optional[bool]
    
    # Campos calculados
    codigo_busqueda: Optional[str] = None
    descripcion_legible: Optional[str] = None
    usuario_nombre: Optional[str] = None
    
    # Datos completos del usuario (JOIN)
    usuario: Optional[dict] = None
    
    class Config:
        from_attributes = True

# ============================================
# 📌 ENDPOINTS - HISTORIAL
# ============================================

@router.post("/registrar", response_model=BusquedaResponse, status_code=201)
async def registrar_busqueda(
    busqueda_data: BusquedaCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_optional_user)
):
    """
    📝 Registrar una búsqueda en el historial
    - Usuario logueado: se guarda con su ID
    - Usuario anónimo: se guarda con sesion_id
    """
    try:
        nueva_busqueda = Busqueda(
            usuario_id=current_user.usuario_id if current_user else None,
            ip_address=request.client.host,
            es_guardada=False,
            **busqueda_data.model_dump()
        )
        
        db.add(nueva_busqueda)
        db.commit()
        db.refresh(nueva_busqueda)
        
        # Generar datos adicionales
        response_data = nueva_busqueda.__dict__.copy()
        response_data['codigo_busqueda'] = nueva_busqueda.generar_codigo()
        response_data['descripcion_legible'] = nueva_busqueda.generar_descripcion_legible(db)
        
        if current_user:
            response_data['usuario_nombre'] = f"{current_user.nombre} {current_user.apellido}"
        
        logger.info(f"✅ Búsqueda registrada: {nueva_busqueda.busqueda_id} - {response_data['descripcion_legible']}")
        
        return response_data
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error registrando búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error al registrar búsqueda: {str(e)}")

@router.get("/historial", response_model=List[BusquedaResponse])
@router.get("/mis-busquedas", response_model=List[BusquedaResponse])
async def obtener_historial(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Obtener historial de búsquedas del usuario"""
    try:
        busquedas = db.query(Busqueda).filter(
            Busqueda.usuario_id == current_user.usuario_id,
            Busqueda.es_guardada == False
        ).order_by(Busqueda.fecha_busqueda.desc()).limit(limit).all()

        # Enriquecer con datos adicionales
        resultados = []
        for busqueda in busquedas:
            data = busqueda.__dict__.copy()
            data['codigo_busqueda'] = busqueda.generar_codigo()
            data['descripcion_legible'] = busqueda.generar_descripcion_legible(db)
            data['usuario_nombre'] = f"{current_user.nombre} {current_user.apellido}"
            # Agregar datos completos del usuario
            data['usuario'] = {
                "usuario_id": current_user.usuario_id,
                "email": current_user.email,
                "nombre": current_user.nombre,
                "apellido": current_user.apellido,
                "telefono": current_user.telefono,
                "dni": current_user.dni,
                "perfil_id": current_user.perfil_id,
                "estado": current_user.estado,
                "fecha_registro": current_user.fecha_registro
            }

            resultados.append(data)

        return resultados

    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener historial")

@router.get("/buscar/{codigo}", response_model=BusquedaResponse)
async def buscar_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Solo admin
):
    """
    🔍 Buscar por código (ej: BUS-20250115-000001)
    Solo para administradores
    """
    try:
        # Extraer el ID del código
        partes = codigo.split('-')
        if len(partes) != 3 or not partes[2].isdigit():
            raise HTTPException(status_code=400, detail="Código de búsqueda inválido")
        
        busqueda_id = int(partes[2])
        
        busqueda = db.query(Busqueda).filter(Busqueda.busqueda_id == busqueda_id).first()
        
        if not busqueda:
            raise HTTPException(status_code=404, detail="Búsqueda no encontrada")
        
        # Enriquecer datos
        data = busqueda.__dict__.copy()
        data['codigo_busqueda'] = busqueda.generar_codigo()
        data['descripcion_legible'] = busqueda.generar_descripcion_legible(db)
        
        # Obtener nombre del usuario
        if busqueda.usuario_id:
            usuario = db.query(Usuario).filter(Usuario.usuario_id == busqueda.usuario_id).first()
            if usuario:
                data['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error buscando por código {codigo}: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar")

@router.get("/admin/todas", response_model=List[BusquedaResponse])
async def listar_todas_busquedas_admin(
    usuario_id: Optional[int] = Query(None),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    📊 Listar todas las búsquedas (solo admin)
    Permite filtrar por usuario y rango de fechas
    """
    try:
        query = db.query(Busqueda)
        
        if usuario_id:
            query = query.filter(Busqueda.usuario_id == usuario_id)
        
        if fecha_desde:
            query = query.filter(Busqueda.fecha_busqueda >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Busqueda.fecha_busqueda <= fecha_hasta)
        
        busquedas = query.order_by(Busqueda.fecha_busqueda.desc()).limit(limit).all()
        
        # Enriquecer datos
        resultados = []
        for busqueda in busquedas:
            data = busqueda.__dict__.copy()
            data['codigo_busqueda'] = busqueda.generar_codigo()
            data['descripcion_legible'] = busqueda.generar_descripcion_legible(db)
            
            if busqueda.usuario_id:
                usuario = db.query(Usuario).filter(Usuario.usuario_id == busqueda.usuario_id).first()
                if usuario:
                    data['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
                    # Agregar datos completos del usuario
                    data['usuario'] = {
                        "usuario_id": usuario.usuario_id,
                        "email": usuario.email,
                        "nombre": usuario.nombre,
                        "apellido": usuario.apellido,
                        "telefono": usuario.telefono,
                        "dni": usuario.dni,
                        "perfil_id": usuario.perfil_id,
                        "estado": usuario.estado,
                        "fecha_registro": usuario.fecha_registro
                    }
            
            resultados.append(data)
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Error listando búsquedas (admin): {e}")
        raise HTTPException(status_code=500, detail="Error al listar búsquedas")

@router.delete("/historial")
async def limpiar_historial(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🗑️ Limpiar historial de búsquedas"""
    try:
        eliminadas = db.query(Busqueda).filter(
            Busqueda.usuario_id == current_user.usuario_id,
            Busqueda.es_guardada == False
        ).delete()
        
        db.commit()
        
        logger.info(f"✅ Historial limpiado: usuario={current_user.usuario_id}, eliminadas={eliminadas}")
        
        return {
            "success": True,
            "message": f"{eliminadas} búsquedas eliminadas del historial"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error limpiando historial: {e}")
        raise HTTPException(status_code=500, detail="Error al limpiar historial")

# ============================================
# 📌 ENDPOINTS - BÚSQUEDAS GUARDADAS (ALERTAS)
# ============================================

@router.get("/guardadas", response_model=List[BusquedaResponse])
async def listar_busquedas_guardadas(
    activa: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """📋 Listar búsquedas guardadas del usuario"""
    try:
        query = db.query(Busqueda).filter(
            Busqueda.usuario_id == current_user.usuario_id,
            Busqueda.es_guardada == True
        )
        
        if activa is not None:
            query = query.filter(Busqueda.alerta_activa == activa)
        
        busquedas = query.order_by(Busqueda.fecha_busqueda.desc()).all()
        
        # Enriquecer datos
        resultados = []
        for busqueda in busquedas:
            data = busqueda.__dict__.copy()
            data['codigo_busqueda'] = busqueda.generar_codigo()
            data['descripcion_legible'] = busqueda.generar_descripcion_legible(db)
            data['usuario_nombre'] = f"{current_user.nombre} {current_user.apellido}"
            # Agregar datos completos del usuario
            data['usuario'] = {
                "usuario_id": current_user.usuario_id,
                "email": current_user.email,
                "nombre": current_user.nombre,
                "apellido": current_user.apellido,
                "telefono": current_user.telefono,
                "dni": current_user.dni,
                "perfil_id": current_user.perfil_id,
                "estado": current_user.estado,
                "fecha_registro": current_user.fecha_registro
            }
            
            resultados.append(data)
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Error listando búsquedas guardadas: {e}")
        raise HTTPException(status_code=500, detail="Error al listar búsquedas guardadas")

@router.post("/guardadas", response_model=BusquedaResponse, status_code=201)
async def guardar_busqueda(
    busqueda_data: BusquedaGuardadaCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """⭐ Guardar búsqueda para recibir alertas"""
    try:
        nueva_busqueda = Busqueda(
            usuario_id=current_user.usuario_id,
            ip_address=request.client.host,
            es_guardada=True,
            **busqueda_data.model_dump()
        )
        
        db.add(nueva_busqueda)
        db.commit()
        db.refresh(nueva_busqueda)
        
        # Enriquecer datos
        data = nueva_busqueda.__dict__.copy()
        data['codigo_busqueda'] = nueva_busqueda.generar_codigo()
        data['descripcion_legible'] = nueva_busqueda.generar_descripcion_legible(db)
        data['usuario_nombre'] = f"{current_user.nombre} {current_user.apellido}"
        
        logger.info(f"✅ Búsqueda guardada: {nueva_busqueda.busqueda_id} - {data['descripcion_legible']}")
        
        return data
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error guardando búsqueda: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar búsqueda: {str(e)}")

@router.put("/guardadas/{busqueda_id}", response_model=BusquedaResponse)
async def actualizar_busqueda_guardada(
    busqueda_id: int,
    busqueda_data: BusquedaGuardadaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """✏️ Actualizar búsqueda guardada"""
    try:
        busqueda = db.query(Busqueda).filter(
            Busqueda.busqueda_id == busqueda_id,
            Busqueda.usuario_id == current_user.usuario_id,
            Busqueda.es_guardada == True
        ).first()
        
        if not busqueda:
            raise HTTPException(status_code=404, detail="Búsqueda guardada no encontrada")
        
        update_data = busqueda_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(busqueda, field, value)
        
        db.commit()
        db.refresh(busqueda)
        
        # Enriquecer datos
        data = busqueda.__dict__.copy()
        data['codigo_busqueda'] = busqueda.generar_codigo()
        data['descripcion_legible'] = busqueda.generar_descripcion_legible(db)
        data['usuario_nombre'] = f"{current_user.nombre} {current_user.apellido}"
        
        logger.info(f"✅ Búsqueda guardada actualizada: {busqueda_id}")
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando búsqueda guardada {busqueda_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")

@router.delete("/guardadas/{busqueda_id}")
async def eliminar_busqueda_guardada(
    busqueda_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """🗑️ Eliminar búsqueda guardada"""
    try:
        busqueda = db.query(Busqueda).filter(
            Busqueda.busqueda_id == busqueda_id,
            Busqueda.usuario_id == current_user.usuario_id,
            Busqueda.es_guardada == True
        ).first()
        
        if not busqueda:
            raise HTTPException(status_code=404, detail="Búsqueda guardada no encontrada")
        
        db.delete(busqueda)
        db.commit()
        
        logger.info(f"✅ Búsqueda guardada eliminada: {busqueda_id}")
        
        return {
            "success": True,
            "message": "Búsqueda guardada eliminada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error eliminando búsqueda guardada {busqueda_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
