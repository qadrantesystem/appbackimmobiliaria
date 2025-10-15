"""
🏠 API de Propiedades con Subida de Imágenes
Sistema Inmobiliario - Crear propiedad con imágenes en un solo request
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, model_validator, Field
from decimal import Decimal
import json
import logging

from app.database import get_db
from app.dependencies import require_ofertante
from app.models.propiedad import Propiedad
from app.models.propiedad_detalle import PropiedadDetalle
from app.models.usuario import Usuario
from app.services.imagekit_service import imagekit_service

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# 📋 SCHEMAS
# ============================================

class CaracteristicaInput(BaseModel):
    caracteristica_id: int
    valor: str

class PropiedadCreateWithImages(BaseModel):
    # Propietario real
    propietario_real_nombre: str
    propietario_real_dni: str
    propietario_real_telefono: str
    propietario_real_email: Optional[str] = None
    
    # Corredor (opcional)
    corredor_asignado_id: Optional[int] = None
    comision_corredor: Optional[Decimal] = None
    
    # Datos del inmueble
    tipo_inmueble_id: int
    distrito_id: int
    nombre_inmueble: str
    direccion: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    
    # Características básicas
    area: Decimal
    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    parqueos: Optional[int] = None
    antiguedad: Optional[int] = None
    
    # Transacción y precios
    transaccion: str = Field(..., pattern="^(venta|alquiler|ambos)$")
    precio_venta: Optional[Decimal] = None
    precio_alquiler: Optional[Decimal] = None
    moneda: str = "PEN"
    
    # Descripción
    titulo: str
    descripcion: Optional[str] = None
    
    # Características detalladas
    caracteristicas: Optional[List[CaracteristicaInput]] = []
    
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        """Convierte string JSON a dict si es necesario"""
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.post("/con-imagenes", status_code=201)
async def crear_propiedad_con_imagenes(
    # JSON con datos de la propiedad
    propiedad_json: str = Form(..., description="JSON con todos los datos de la propiedad"),
    
    # Imagen principal (obligatoria)
    imagen_principal: UploadFile = File(..., description="Foto principal de la propiedad"),
    
    # Galería de imágenes (hasta 5, opcional)
    imagenes_galeria: Optional[List[UploadFile]] = File(None, description="Hasta 5 fotos adicionales"),
    
    # Autenticación
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    🏠 Crear propiedad con subida automática de imágenes a ImageKit
    
    **Pasos:**
    1. Valida los datos de la propiedad
    2. Sube imagen principal a ImageKit
    3. Sube galería (hasta 5 fotos) a ImageKit
    4. Guarda en registro_x_inmueble_cab
    5. Guarda características en registro_x_inmueble_det
    
    **Límites:**
    - Imagen principal: 1 foto (obligatoria)
    - Galería: hasta 5 fotos (opcional)
    - Tamaño máximo por imagen: 10MB
    """
    try:
        # 1. Parsear y validar JSON
        logger.info(f"📝 Parseando datos de propiedad...")
        propiedad_data = PropiedadCreateWithImages.model_validate_json(propiedad_json)
        
        # 2. Validar límite de imágenes de galería
        if imagenes_galeria and len(imagenes_galeria) > 5:
            raise HTTPException(
                status_code=400,
                detail="Máximo 5 imágenes en la galería"
            )
        
        # 3. Subir imagen principal a ImageKit
        logger.info(f"📸 Subiendo imagen principal a ImageKit...")
        
        # Leer contenido de la imagen
        imagen_principal_content = await imagen_principal.read()
        
        # Generar nombre único
        filename_principal = f"propiedad_{current_user.usuario_id}_{propiedad_data.nombre_inmueble.replace(' ', '_')}_principal"
        
        # Subir a ImageKit
        resultado_principal = imagekit_service.upload_image(
            file=imagen_principal_content,
            file_name=filename_principal,
            folder="/propiedades"
        )
        
        if not resultado_principal.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo imagen principal: {resultado_principal.get('error')}"
            )
        
        url_imagen_principal = resultado_principal['url']
        logger.info(f"✅ Imagen principal subida: {url_imagen_principal}")
        
        # 4. Subir galería a ImageKit (si existe)
        urls_galeria = []
        
        if imagenes_galeria:
            logger.info(f"📸 Subiendo {len(imagenes_galeria)} imágenes a la galería...")
            
            for idx, imagen in enumerate(imagenes_galeria, 1):
                # Leer contenido
                imagen_content = await imagen.read()
                
                # Generar nombre único
                filename_galeria = f"propiedad_{current_user.usuario_id}_{propiedad_data.nombre_inmueble.replace(' ', '_')}_galeria_{idx}"
                
                # Subir a ImageKit
                resultado_galeria = imagekit_service.upload_image(
                    file=imagen_content,
                    file_name=filename_galeria,
                    folder="/propiedades"
                )
                
                if resultado_galeria.get('success'):
                    urls_galeria.append(resultado_galeria['url'])
                    logger.info(f"✅ Imagen {idx} subida: {resultado_galeria['url']}")
                else:
                    logger.warning(f"⚠️ Error subiendo imagen {idx}: {resultado_galeria.get('error')}")
        
        # 5. Crear registro en registro_x_inmueble_cab
        logger.info(f"💾 Guardando propiedad en base de datos...")
        
        nueva_propiedad = Propiedad(
            usuario_id=current_user.usuario_id,
            propietario_real_nombre=propiedad_data.propietario_real_nombre,
            propietario_real_dni=propiedad_data.propietario_real_dni,
            propietario_real_telefono=propiedad_data.propietario_real_telefono,
            propietario_real_email=propiedad_data.propietario_real_email,
            corredor_asignado_id=propiedad_data.corredor_asignado_id,
            comision_corredor=propiedad_data.comision_corredor,
            tipo_inmueble_id=propiedad_data.tipo_inmueble_id,
            distrito_id=propiedad_data.distrito_id,
            nombre_inmueble=propiedad_data.nombre_inmueble,
            direccion=propiedad_data.direccion,
            latitud=propiedad_data.latitud,
            longitud=propiedad_data.longitud,
            area=propiedad_data.area,
            habitaciones=propiedad_data.habitaciones,
            banos=propiedad_data.banos,
            parqueos=propiedad_data.parqueos,
            antiguedad=propiedad_data.antiguedad,
            transaccion=propiedad_data.transaccion,
            precio_venta=propiedad_data.precio_venta,
            precio_alquiler=propiedad_data.precio_alquiler,
            moneda=propiedad_data.moneda,
            titulo=propiedad_data.titulo,
            descripcion=propiedad_data.descripcion,
            imagen_principal=url_imagen_principal,
            imagenes=urls_galeria if urls_galeria else None,
            estado="borrador",
            created_by=current_user.usuario_id
        )
        
        db.add(nueva_propiedad)
        db.commit()
        db.refresh(nueva_propiedad)
        
        logger.info(f"✅ Propiedad creada con ID: {nueva_propiedad.registro_cab_id}")
        
        # 6. Guardar características en registro_x_inmueble_det
        if propiedad_data.caracteristicas:
            logger.info(f"💾 Guardando {len(propiedad_data.caracteristicas)} características...")
            
            for caract in propiedad_data.caracteristicas:
                detalle = PropiedadDetalle(
                    registro_cab_id=nueva_propiedad.registro_cab_id,
                    caracteristica_id=caract.caracteristica_id,
                    valor=caract.valor
                )
                db.add(detalle)
            
            db.commit()
            logger.info(f"✅ Características guardadas")
        
        # 7. Retornar respuesta exitosa
        return {
            "success": True,
            "message": "Propiedad creada exitosamente con imágenes",
            "data": {
                "registro_cab_id": nueva_propiedad.registro_cab_id,
                "titulo": nueva_propiedad.titulo,
                "estado": nueva_propiedad.estado,
                "imagen_principal": url_imagen_principal,
                "total_imagenes_galeria": len(urls_galeria),
                "imagenes_galeria": urls_galeria,
                "total_caracteristicas": len(propiedad_data.caracteristicas) if propiedad_data.caracteristicas else 0
            }
        }
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"JSON inválido: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando propiedad: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear propiedad: {str(e)}"
        )

@router.post("/actualizar-imagenes/{propiedad_id}")
async def actualizar_imagenes_propiedad(
    propiedad_id: int,
    imagen_principal: Optional[UploadFile] = File(None),
    imagenes_galeria: Optional[List[UploadFile]] = File(None),
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    📸 Actualizar imágenes de una propiedad existente
    """
    try:
        # Buscar propiedad
        propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
        
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        
        # Verificar permisos
        if propiedad.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta propiedad")
        
        urls_actualizadas = {}
        
        # Actualizar imagen principal si se proporciona
        if imagen_principal:
            logger.info(f"📸 Actualizando imagen principal...")
            
            imagen_content = await imagen_principal.read()
            filename = f"propiedad_{propiedad_id}_principal_updated"
            
            resultado = imagekit_service.upload_image(
                file=imagen_content,
                file_name=filename,
                folder="/propiedades"
            )
            
            if resultado.get('success'):
                propiedad.imagen_principal = resultado['url']
                urls_actualizadas['imagen_principal'] = resultado['url']
                logger.info(f"✅ Imagen principal actualizada")
        
        # Actualizar galería si se proporciona
        if imagenes_galeria:
            if len(imagenes_galeria) > 5:
                raise HTTPException(status_code=400, detail="Máximo 5 imágenes en la galería")
            
            logger.info(f"📸 Actualizando galería ({len(imagenes_galeria)} imágenes)...")
            
            urls_galeria = []
            for idx, imagen in enumerate(imagenes_galeria, 1):
                imagen_content = await imagen.read()
                filename = f"propiedad_{propiedad_id}_galeria_{idx}_updated"
                
                resultado = imagekit_service.upload_image(
                    file=imagen_content,
                    file_name=filename,
                    folder="/propiedades"
                )
                
                if resultado.get('success'):
                    urls_galeria.append(resultado['url'])
            
            propiedad.imagenes = urls_galeria
            urls_actualizadas['imagenes_galeria'] = urls_galeria
            logger.info(f"✅ Galería actualizada con {len(urls_galeria)} imágenes")
        
        db.commit()
        
        return {
            "success": True,
            "message": "Imágenes actualizadas exitosamente",
            "data": {
                "registro_cab_id": propiedad_id,
                **urls_actualizadas
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando imágenes: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar imágenes: {str(e)}")
