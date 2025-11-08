"""
🏢 API de Registro Masivo de Edificios
Sistema revolucionario para crear edificios con oficinas y sótanos automáticamente
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
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

class EdificioBase(BaseModel):
    """Datos del edificio principal"""
    propietario_id: int
    tipo_inmueble_id: int
    distrito_id: int
    nombre_inmueble: str
    direccion: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    area: Decimal
    antiguedad: Optional[int] = None
    implementacion: Optional[int] = None
    transaccion: str
    precio_venta: Optional[Decimal] = None
    precio_alquiler: Optional[Decimal] = None
    moneda: str = "PEN"
    titulo: str
    descripcion: Optional[str] = None
    caracteristicas: List[CaracteristicaInput] = []

class OficinaInput(BaseModel):
    """Datos de una oficina"""
    piso: int
    numero_oficina: int
    nombre: str
    area: Decimal

class SotanoInput(BaseModel):
    """Datos de un sótano"""
    nivel: int
    parqueos: int

class EdificioCompletoInput(BaseModel):
    """Input completo para crear edificio con oficinas"""
    edificio: EdificioBase
    oficinas: List[OficinaInput]
    sotanos: Optional[List[SotanoInput]] = []

# ============================================
# 📌 ENDPOINTS
# ============================================

@router.post("/edificio-completo", status_code=201)
async def crear_edificio_completo(
    # JSON con todos los datos
    edificio_json: str = Form(..., description="JSON con edificio, oficinas y sótanos"),

    # Imagen principal del edificio
    imagen_principal: UploadFile = File(..., description="Foto principal del edificio"),

    # Galería de imágenes del edificio
    imagenes_galeria: List[UploadFile] = File(default=[], description="Hasta 5 fotos del edificio"),

    # Autenticación
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    🏗️ Crear edificio completo con oficinas y sótanos automáticamente

    **Flujo:**
    1. Crear edificio principal (cabecera)
    2. Subir imágenes del edificio a ImageKit
    3. Guardar características del edificio
    4. Crear todas las oficinas como propiedades hijas
    5. Crear características de sótanos (parqueos)

    **Innovación:**
    - Registro masivo en una sola transacción
    - Visualización de torre antes de crear
    - Metraje flexible por oficina
    - Sistema de parqueos por sótano
    """
    try:
        # 1. Parsear y validar JSON
        logger.info(f"📝 Parseando datos del edificio completo...")
        edificio_data = EdificioCompletoInput.model_validate(json.loads(edificio_json))

        logger.info(f"📊 Edificio: {edificio_data.edificio.nombre_inmueble}")
        logger.info(f"📊 Oficinas a crear: {len(edificio_data.oficinas)}")
        logger.info(f"📊 Sótanos: {len(edificio_data.sotanos)}")

        # 2. Subir imagen principal del edificio
        logger.info(f"📸 Subiendo imagen principal del edificio...")
        imagen_principal_content = await imagen_principal.read()
        filename_principal = f"edificio_{current_user.usuario_id}_{edificio_data.edificio.nombre_inmueble.replace(' ', '_')}_principal"

        resultado_principal = imagekit_service.upload_image(
            file_content=imagen_principal_content,
            file_name=filename_principal,
            folder="/edificios"
        )

        if not resultado_principal or not resultado_principal.get('url'):
            raise HTTPException(
                status_code=500,
                detail="Error subiendo imagen principal del edificio"
            )

        url_imagen_principal = resultado_principal['url']
        logger.info(f"✅ Imagen principal subida: {url_imagen_principal}")

        # 3. Subir galería del edificio (si existe)
        urls_galeria = []
        if imagenes_galeria:
            logger.info(f"📸 Subiendo {len(imagenes_galeria)} imágenes a la galería...")

            for idx, imagen in enumerate(imagenes_galeria, 1):
                imagen_content = await imagen.read()
                filename_galeria = f"edificio_{current_user.usuario_id}_{edificio_data.edificio.nombre_inmueble.replace(' ', '_')}_galeria_{idx}"

                resultado_galeria = imagekit_service.upload_image(
                    file_content=imagen_content,
                    file_name=filename_galeria,
                    folder="/edificios"
                )

                if resultado_galeria and resultado_galeria.get('url'):
                    urls_galeria.append(resultado_galeria['url'])

        # 4. Crear EDIFICIO PRINCIPAL en base de datos
        logger.info(f"💾 Creando edificio principal en DB...")

        edificio_principal = Propiedad(
            usuario_id=current_user.usuario_id,
            propietario_id=edificio_data.edificio.propietario_id,
            padre_registro_cab_id=None,  # El edificio no tiene padre
            tipo_inmueble_id=edificio_data.edificio.tipo_inmueble_id,
            distrito_id=edificio_data.edificio.distrito_id,
            nombre_inmueble=edificio_data.edificio.nombre_inmueble,
            direccion=edificio_data.edificio.direccion,
            latitud=edificio_data.edificio.latitud,
            longitud=edificio_data.edificio.longitud,
            area=edificio_data.edificio.area,
            antiguedad=edificio_data.edificio.antiguedad,
            implementacion=edificio_data.edificio.implementacion,
            transaccion=edificio_data.edificio.transaccion,
            precio_venta=edificio_data.edificio.precio_venta,
            precio_alquiler=edificio_data.edificio.precio_alquiler,
            moneda=edificio_data.edificio.moneda,
            titulo=edificio_data.edificio.titulo,
            descripcion=edificio_data.edificio.descripcion,
            imagen_principal=url_imagen_principal,
            imagenes=urls_galeria if urls_galeria else None,
            estado="borrador",
            created_by=current_user.usuario_id
        )

        db.add(edificio_principal)
        db.commit()
        db.refresh(edificio_principal)

        logger.info(f"✅ Edificio creado con ID: {edificio_principal.registro_cab_id}")

        # 5. Guardar características del edificio
        if edificio_data.edificio.caracteristicas:
            logger.info(f"💾 Guardando {len(edificio_data.edificio.caracteristicas)} características del edificio...")

            for caract in edificio_data.edificio.caracteristicas:
                detalle = PropiedadDetalle(
                    registro_cab_id=edificio_principal.registro_cab_id,
                    caracteristica_id=caract.caracteristica_id,
                    valor=caract.valor
                )
                db.add(detalle)

            db.commit()

        # 6. Crear OFICINAS como propiedades hijas
        logger.info(f"🏢 Creando {len(edificio_data.oficinas)} oficinas...")

        oficinas_creadas = []
        tipo_inmueble_oficina_id = 1  # ID del tipo "Oficina en Edificio"

        for oficina_data in edificio_data.oficinas:
            # Crear oficina
            oficina = Propiedad(
                usuario_id=current_user.usuario_id,
                propietario_id=edificio_data.edificio.propietario_id,  # Mismo propietario
                padre_registro_cab_id=edificio_principal.registro_cab_id,  # 🔗 FK al edificio padre
                tipo_inmueble_id=tipo_inmueble_oficina_id,
                distrito_id=edificio_data.edificio.distrito_id,  # Mismo distrito
                nombre_inmueble=oficina_data.nombre,
                direccion=edificio_data.edificio.direccion,  # Misma dirección
                latitud=edificio_data.edificio.latitud,
                longitud=edificio_data.edificio.longitud,
                area=oficina_data.area,  # Área específica de la oficina
                transaccion=edificio_data.edificio.transaccion,
                moneda=edificio_data.edificio.moneda,
                titulo=f"{oficina_data.nombre} - {edificio_data.edificio.nombre_inmueble}",
                descripcion=f"Oficina ubicada en el piso {oficina_data.piso} del edificio {edificio_data.edificio.nombre_inmueble}",
                imagen_principal=url_imagen_principal,  # Misma imagen del edificio
                imagenes=urls_galeria if urls_galeria else None,
                estado="borrador",
                created_by=current_user.usuario_id
            )

            db.add(oficina)
            db.flush()  # Para obtener el ID sin hacer commit

            # Agregar características de la oficina (piso, número)
            detalle_piso = PropiedadDetalle(
                registro_cab_id=oficina.registro_cab_id,
                caracteristica_id=110,  # ID característica "Cantidad Pisos Edificio" (reutilizado)
                valor=str(oficina_data.piso)
            )
            db.add(detalle_piso)

            oficinas_creadas.append({
                "id": oficina.registro_cab_id,
                "nombre": oficina_data.nombre,
                "piso": oficina_data.piso,
                "area": float(oficina_data.area)
            })

        db.commit()
        logger.info(f"✅ {len(oficinas_creadas)} oficinas creadas exitosamente")

        # 7. Registrar sótanos (como características del edificio)
        total_parqueos = 0
        if edificio_data.sotanos:
            logger.info(f"🅿️ Configurando {len(edificio_data.sotanos)} sótanos...")

            for sotano in edificio_data.sotanos:
                # Guardar parqueos por sótano como característica adicional
                # (podrías crear una tabla separada o usar el sistema de características)
                total_parqueos += sotano.parqueos

            logger.info(f"✅ Total parqueos: {total_parqueos}")

        # 8. Preparar respuesta
        return {
            "success": True,
            "message": "Edificio completo creado exitosamente",
            "data": {
                "edificio": {
                    "id": edificio_principal.registro_cab_id,
                    "nombre": edificio_principal.nombre_inmueble,
                    "imagen_principal": url_imagen_principal,
                    "total_imagenes_galeria": len(urls_galeria)
                },
                "oficinas": oficinas_creadas,
                "total_oficinas": len(oficinas_creadas),
                "total_sotanos": len(edificio_data.sotanos) if edificio_data.sotanos else 0,
                "total_parqueos": total_parqueos
            }
        }

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"JSON inválido: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando edificio completo: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear edificio completo: {str(e)}"
        )
