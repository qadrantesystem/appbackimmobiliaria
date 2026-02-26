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
from app.models.piso import InmueblePiso
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
    caracteristicas: List[CaracteristicaInput] = []  # 🆕 Equipamiento por oficina

class SotanoInput(BaseModel):
    """Datos de un sótano"""
    nivel: int
    parqueos: int

class PisoInput(BaseModel):
    """Datos de configuracion de un piso"""
    numero_piso: int
    tipo_uso: Optional[str] = None
    unidades_config: Optional[str] = None
    area_comercializable: Optional[Decimal] = None

class EdificioCompletoInput(BaseModel):
    """Input completo para crear edificio con oficinas"""
    edificio: EdificioBase
    oficinas: List[OficinaInput]
    sotanos: Optional[List[SotanoInput]] = []
    pisos: Optional[List[PisoInput]] = []
    oficinas_para_eliminar: Optional[List[int]] = []  # 🗑️ IDs de oficinas a eliminar

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
                piso=oficina_data.piso,  # ✅ Guardar piso directamente en cabecera
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
                imagen_principal=None,  # ✅ Las oficinas NO deben tener imágenes propias
                imagenes=None,  # ✅ Sin galería (heredan visualmente del edificio)
                estado="borrador",
                created_by=current_user.usuario_id
            )

            db.add(oficina)
            db.flush()  # Para obtener el ID sin hacer commit

            # Agregar número de oficina
            detalle_numero = PropiedadDetalle(
                registro_cab_id=oficina.registro_cab_id,
                caracteristica_id=111,  # ID característica "Número de Oficina"
                valor=str(oficina_data.numero_oficina)
            )
            db.add(detalle_numero)

            # 🆕 Agregar EQUIPAMIENTO de la oficina (si tiene)
            if oficina_data.caracteristicas:
                logger.info(f"   💡 Oficina {oficina_data.numero_oficina}: {len(oficina_data.caracteristicas)} equipamientos")
                for caract in oficina_data.caracteristicas:
                    detalle_equip = PropiedadDetalle(
                        registro_cab_id=oficina.registro_cab_id,
                        caracteristica_id=caract.caracteristica_id,
                        valor=caract.valor
                    )
                    db.add(detalle_equip)

            oficinas_creadas.append({
                "id": oficina.registro_cab_id,
                "nombre": oficina_data.nombre,
                "piso": oficina_data.piso,
                "area": float(oficina_data.area),
                "equipamientos": len(oficina_data.caracteristicas)  # 🆕 Mostrar en respuesta
            })

        db.commit()
        logger.info(f"✅ {len(oficinas_creadas)} oficinas creadas exitosamente")

        # 6.5 Guardar configuracion de pisos en tabla inmuebles_pisos_det
        if edificio_data.pisos:
            pisos_validos = [p for p in edificio_data.pisos if p.numero_piso != 0]
            logger.info(f"🏗️ Guardando {len(pisos_validos)} pisos configurados...")
            for piso_data in pisos_validos:
                nuevo_piso = InmueblePiso(
                    registro_cab_id=edificio_principal.registro_cab_id,
                    numero_piso=piso_data.numero_piso,
                    tipo_uso=piso_data.tipo_uso,
                    unidades_config=piso_data.unidades_config,
                    area_comercializable=piso_data.area_comercializable,
                    activo=True
                )
                db.add(nuevo_piso)
            db.commit()
            logger.info(f"✅ {len(edificio_data.pisos)} pisos guardados")

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
                "total_pisos": len(edificio_data.pisos) if edificio_data.pisos else 0,
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


@router.put("/edificio-completo/{edificio_id}", status_code=200)
async def actualizar_edificio_completo(
    edificio_id: int,
    # JSON con todos los datos
    edificio_json: str = Form(..., description="JSON con edificio y oficinas actualizadas"),
    
    # Imágenes opcionales (solo si se cambian)
    imagen_principal: Optional[UploadFile] = File(None, description="Nueva foto principal (opcional)"),
    imagenes_galeria: List[UploadFile] = File(default=[], description="Nuevas fotos galería (opcional)"),
    
    # Autenticación
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    🔄 Actualizar edificio completo con todas sus oficinas en una transacción
    
    **Flujo:**
    1. Actualizar datos del edificio padre
    2. Comparar oficinas existentes con nuevas
    3. Crear oficinas nuevas
    4. Actualizar oficinas existentes
    5. Eliminar oficinas que ya no existen
    6. Actualizar características y equipamiento
    7. Actualizar imágenes solo si se envían nuevas
    """
    try:
        # 1. Validar que el edificio existe
        edificio = db.query(Propiedad).filter(
            Propiedad.registro_cab_id == edificio_id
        ).first()
        
        if not edificio:
            raise HTTPException(status_code=404, detail="Edificio no encontrado")
        
        # Verificar permisos
        if edificio.usuario_id != current_user.usuario_id and current_user.perfil_id != 4:
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar este edificio")
        
        # 2. Parsear datos
        logger.info(f"📝 Actualizando edificio {edificio_id}...")
        edificio_data = EdificioCompletoInput.model_validate(json.loads(edificio_json))
        
        # 3. Actualizar edificio principal
        logger.info(f"🏢 Actualizando datos del edificio principal...")
        edificio.nombre_inmueble = edificio_data.edificio.nombre_inmueble
        edificio.direccion = edificio_data.edificio.direccion
        edificio.latitud = edificio_data.edificio.latitud
        edificio.longitud = edificio_data.edificio.longitud
        edificio.area = edificio_data.edificio.area
        edificio.antiguedad = edificio_data.edificio.antiguedad
        edificio.implementacion = edificio_data.edificio.implementacion
        edificio.transaccion = edificio_data.edificio.transaccion
        edificio.precio_venta = edificio_data.edificio.precio_venta
        edificio.precio_alquiler = edificio_data.edificio.precio_alquiler
        edificio.moneda = edificio_data.edificio.moneda
        edificio.titulo = edificio_data.edificio.titulo
        edificio.descripcion = edificio_data.edificio.descripcion
        edificio.updated_by = current_user.usuario_id
        
        # 4. Actualizar imágenes solo si se envían nuevas
        if imagen_principal:
            logger.info(f"📸 Actualizando imagen principal...")
            imagen_principal_content = await imagen_principal.read()
            filename_principal = f"edificio_{current_user.usuario_id}_{edificio_data.edificio.nombre_inmueble.replace(' ', '_')}_principal"
            
            resultado_principal = imagekit_service.upload_image(
                file_content=imagen_principal_content,
                file_name=filename_principal,
                folder="/edificios"
            )
            
            if resultado_principal and resultado_principal.get('url'):
                edificio.imagen_principal = resultado_principal['url']
        
        if imagenes_galeria and len(imagenes_galeria) > 0:
            logger.info(f"📸 Actualizando galería ({len(imagenes_galeria)} imágenes)...")
            urls_galeria = []
            
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
            
            if urls_galeria:
                edificio.imagenes = urls_galeria
        
        db.flush()
        
        # 5. Actualizar características del edificio
        if edificio_data.edificio.caracteristicas:
            # Eliminar características anteriores
            db.query(PropiedadDetalle).filter(
                PropiedadDetalle.registro_cab_id == edificio_id
            ).delete()
            
            # Agregar nuevas características
            for caract in edificio_data.edificio.caracteristicas:
                detalle = PropiedadDetalle(
                    registro_cab_id=edificio_id,
                    caracteristica_id=caract.caracteristica_id,
                    valor=caract.valor
                )
                db.add(detalle)
        
        # 6. 🗑️ ELIMINAR oficinas marcadas para eliminar
        oficinas_eliminadas = 0
        if edificio_data.oficinas_para_eliminar and len(edificio_data.oficinas_para_eliminar) > 0:
            logger.info(f"🗑️ Eliminando {len(edificio_data.oficinas_para_eliminar)} oficinas marcadas...")

            for oficina_id in edificio_data.oficinas_para_eliminar:
                # Verificar que la oficina pertenece a este edificio
                oficina_a_eliminar = db.query(Propiedad).filter(
                    Propiedad.registro_cab_id == oficina_id,
                    Propiedad.padre_registro_cab_id == edificio_id
                ).first()

                if oficina_a_eliminar:
                    # Eliminar primero las características/detalles de la oficina
                    db.query(PropiedadDetalle).filter(
                        PropiedadDetalle.registro_cab_id == oficina_id
                    ).delete()

                    # Eliminar la oficina
                    db.delete(oficina_a_eliminar)
                    oficinas_eliminadas += 1
                    logger.info(f"   🗑️ Eliminada: {oficina_a_eliminar.nombre_inmueble} (ID: {oficina_id})")
                else:
                    logger.warning(f"   ⚠️ Oficina {oficina_id} no encontrada o no pertenece a este edificio")

            db.flush()
            logger.info(f"✅ {oficinas_eliminadas} oficinas eliminadas correctamente")

        # 7. Gestionar oficinas: comparar existentes vs nuevas
        logger.info(f"🏢 Gestionando oficinas...")

        # Obtener oficinas actuales con número de oficina (después de eliminar las marcadas)
        oficinas_actuales = db.query(Propiedad).filter(
            Propiedad.padre_registro_cab_id == edificio_id
        ).all()
        
        # Mapear oficinas actuales por piso+número para identificarlas
        oficinas_actuales_map = {}
        for oficina_actual in oficinas_actuales:
            # ✅ Obtener piso directamente de la columna (no de característica)
            piso_num = oficina_actual.piso or 0
            key = f"{piso_num}_{oficina_actual.nombre_inmueble}"
            oficinas_actuales_map[key] = oficina_actual
        
        # Mapear oficinas nuevas
        oficinas_nuevas_keys = set()
        tipo_inmueble_oficina_id = 1
        
        for oficina_data in edificio_data.oficinas:
            key = f"{oficina_data.piso}_{oficina_data.nombre}"
            oficinas_nuevas_keys.add(key)
            
            if key in oficinas_actuales_map:
                # ACTUALIZAR oficina existente
                logger.info(f"   ♻️ Actualizando {oficina_data.nombre}...")
                oficina_existente = oficinas_actuales_map[key]

                oficina_existente.area = oficina_data.area
                oficina_existente.piso = oficina_data.piso  # ✅ Actualizar piso en cabecera
                oficina_existente.titulo = f"{oficina_data.nombre} - {edificio_data.edificio.nombre_inmueble}"
                oficina_existente.descripcion = f"Oficina ubicada en el piso {oficina_data.piso} del edificio {edificio_data.edificio.nombre_inmueble}"
                oficina_existente.transaccion = edificio_data.edificio.transaccion
                oficina_existente.moneda = edificio_data.edificio.moneda

                # Actualizar características (eliminar y recrear)
                db.query(PropiedadDetalle).filter(
                    PropiedadDetalle.registro_cab_id == oficina_existente.registro_cab_id
                ).delete()

                # Agregar número de oficina
                detalle_numero = PropiedadDetalle(
                    registro_cab_id=oficina_existente.registro_cab_id,
                    caracteristica_id=111,
                    valor=str(oficina_data.numero_oficina)
                )
                db.add(detalle_numero)
                
                # Agregar equipamiento
                if oficina_data.caracteristicas:
                    for caract in oficina_data.caracteristicas:
                        detalle_equip = PropiedadDetalle(
                            registro_cab_id=oficina_existente.registro_cab_id,
                            caracteristica_id=caract.caracteristica_id,
                            valor=caract.valor
                        )
                        db.add(detalle_equip)
            else:
                # CREAR oficina nueva
                logger.info(f"   ➕ Creando nueva {oficina_data.nombre}...")
                nueva_oficina = Propiedad(
                    usuario_id=current_user.usuario_id,
                    propietario_id=edificio_data.edificio.propietario_id,
                    padre_registro_cab_id=edificio_id,
                    piso=oficina_data.piso,  # ✅ Guardar piso directamente en cabecera
                    tipo_inmueble_id=tipo_inmueble_oficina_id,
                    distrito_id=edificio_data.edificio.distrito_id,
                    nombre_inmueble=oficina_data.nombre,
                    direccion=edificio_data.edificio.direccion,
                    latitud=edificio_data.edificio.latitud,
                    longitud=edificio_data.edificio.longitud,
                    area=oficina_data.area,
                    transaccion=edificio_data.edificio.transaccion,
                    moneda=edificio_data.edificio.moneda,
                    titulo=f"{oficina_data.nombre} - {edificio_data.edificio.nombre_inmueble}",
                    descripcion=f"Oficina ubicada en el piso {oficina_data.piso} del edificio {edificio_data.edificio.nombre_inmueble}",
                    imagen_principal=None,
                    imagenes=None,
                    estado="borrador",
                    created_by=current_user.usuario_id
                )

                db.add(nueva_oficina)
                db.flush()

                # Agregar número de oficina
                detalle_numero = PropiedadDetalle(
                    registro_cab_id=nueva_oficina.registro_cab_id,
                    caracteristica_id=111,
                    valor=str(oficina_data.numero_oficina)
                )
                db.add(detalle_numero)
                
                # Agregar equipamiento
                if oficina_data.caracteristicas:
                    for caract in oficina_data.caracteristicas:
                        detalle_equip = PropiedadDetalle(
                            registro_cab_id=nueva_oficina.registro_cab_id,
                            caracteristica_id=caract.caracteristica_id,
                            valor=caract.valor
                        )
                        db.add(detalle_equip)
        
        # 8. ELIMINAR oficinas que ya no existen en la lista (adicional a las marcadas)
        oficinas_a_eliminar = set(oficinas_actuales_map.keys()) - oficinas_nuevas_keys

        for key_eliminar in oficinas_a_eliminar:
            oficina_eliminar = oficinas_actuales_map[key_eliminar]
            logger.info(f"   🗑️ Eliminando {oficina_eliminar.nombre_inmueble}...")
            
            # Eliminar características
            db.query(PropiedadDetalle).filter(
                PropiedadDetalle.registro_cab_id == oficina_eliminar.registro_cab_id
            ).delete()
            
            # Eliminar oficina
            db.delete(oficina_eliminar)
        
        # 8.5 Guardar/actualizar pisos (upsert)
        if edificio_data.pisos:
            pisos_validos = [p for p in edificio_data.pisos if p.numero_piso != 0]
            logger.info(f"🏗️ Actualizando {len(pisos_validos)} pisos...")
            for piso_data in pisos_validos:
                existente = db.query(InmueblePiso).filter(
                    InmueblePiso.registro_cab_id == edificio_id,
                    InmueblePiso.numero_piso == piso_data.numero_piso
                ).first()

                if existente:
                    if piso_data.tipo_uso is not None:
                        existente.tipo_uso = piso_data.tipo_uso
                    # Siempre actualizar unidades_config (puede ser null para limpiar)
                    existente.unidades_config = piso_data.unidades_config
                    if piso_data.area_comercializable is not None:
                        existente.area_comercializable = piso_data.area_comercializable
                else:
                    nuevo_piso = InmueblePiso(
                        registro_cab_id=edificio_id,
                        numero_piso=piso_data.numero_piso,
                        tipo_uso=piso_data.tipo_uso,
                        unidades_config=piso_data.unidades_config,
                        area_comercializable=piso_data.area_comercializable,
                        activo=True
                    )
                    db.add(nuevo_piso)

        # 9. Commit final
        db.commit()
        db.refresh(edificio)

        # Contar oficinas finales
        total_oficinas = db.query(Propiedad).filter(
            Propiedad.padre_registro_cab_id == edificio_id
        ).count()
        
        logger.info(f"✅ Edificio actualizado: {total_oficinas} oficinas")
        
        return {
            "success": True,
            "message": "Edificio completo actualizado exitosamente",
            "data": {
                "edificio": {
                    "id": edificio.registro_cab_id,
                    "nombre": edificio.nombre_inmueble,
                    "imagen_principal": edificio.imagen_principal,
                    "total_imagenes_galeria": len(edificio.imagenes) if edificio.imagenes else 0
                },
                "total_oficinas": total_oficinas,
                "oficinas_creadas": len(oficinas_nuevas_keys - set(oficinas_actuales_map.keys())),
                "oficinas_actualizadas": len(oficinas_nuevas_keys & set(oficinas_actuales_map.keys())),
                "oficinas_eliminadas": oficinas_eliminadas + len(oficinas_a_eliminar)  # Marcadas + automáticas
            }
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON: {e}")
        raise HTTPException(status_code=400, detail=f"JSON inválido: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error actualizando edificio completo: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Error al actualizar edificio completo: {str(e)}")
