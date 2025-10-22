from fastapi import APIRouter, Depends, Query, UploadFile, File, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_active_user, require_ofertante, get_optional_user
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.models import Propiedad, PropiedadDetalle, Usuario, TipoInmueble, Distrito, Caracteristica, Favorito
from app.schemas.propiedad import PropiedadCreate, PropiedadUpdate, PropiedadEstadoUpdate, PropiedadResponse, PropiedadDetalleResponse
from app.schemas.common import ResponseModel, PaginatedResponse
from app.services.imagekit_service import ImageKitService
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[PropiedadResponse])
async def list_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    tipo_inmueble_id: Optional[int] = None,
    distrito_id: Optional[str] = None,  # Puede ser "1,2,3"
    transaccion: Optional[str] = None,
    precio_min: Optional[Decimal] = None,
    precio_max: Optional[Decimal] = None,
    area_min: Optional[Decimal] = None,
    area_max: Optional[Decimal] = None,
    habitaciones: Optional[str] = None,  # "2,3"
    banos: Optional[str] = None,
    parqueos: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Listar propiedades públicas con filtros
    Endpoint público - no requiere autenticación
    """
    # Query base - solo propiedades publicadas
    query = db.query(Propiedad).filter(Propiedad.estado == "publicado")
    
    # Filtros
    if tipo_inmueble_id:
        query = query.filter(Propiedad.tipo_inmueble_id == tipo_inmueble_id)
    
    if distrito_id:
        distritos = [int(d) for d in distrito_id.split(",")]
        query = query.filter(Propiedad.distrito_id.in_(distritos))
    
    if transaccion:
        query = query.filter(Propiedad.transaccion.in_([transaccion, "ambos"]))
    
    if precio_min or precio_max:
        if transaccion == "alquiler":
            if precio_min:
                query = query.filter(Propiedad.precio_alquiler >= precio_min)
            if precio_max:
                query = query.filter(Propiedad.precio_alquiler <= precio_max)
        elif transaccion == "venta":
            if precio_min:
                query = query.filter(Propiedad.precio_venta >= precio_min)
            if precio_max:
                query = query.filter(Propiedad.precio_venta <= precio_max)
    
    if area_min:
        query = query.filter(Propiedad.area >= area_min)
    if area_max:
        query = query.filter(Propiedad.area <= area_max)
    
    if habitaciones:
        hab_list = [int(h) for h in habitaciones.split(",")]
        query = query.filter(Propiedad.habitaciones.in_(hab_list))
    
    if banos:
        ban_list = [int(b) for b in banos.split(",")]
        query = query.filter(Propiedad.banos.in_(ban_list))
    
    if parqueos:
        query = query.filter(Propiedad.parqueos >= parqueos)
    
    # Total
    total = query.count()
    
    # Ordenar por fecha (más recientes primero)
    query = query.order_by(Propiedad.created_at.desc())
    
    # Paginación
    offset = (page - 1) * limit
    propiedades = query.offset(offset).limit(limit).all()
    
    # Formatear respuesta
    propiedades_list = []
    for prop in propiedades:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == prop.tipo_inmueble_id).first()
        distrito = db.query(Distrito).filter(Distrito.distrito_id == prop.distrito_id).first()
        
        propiedades_list.append(PropiedadResponse(
            registro_cab_id=prop.registro_cab_id,
            titulo=prop.titulo,
            tipo_inmueble=tipo.nombre if tipo else "N/A",
            distrito=distrito.nombre if distrito else "N/A",
            direccion=prop.direccion,
            latitud=prop.latitud,  # 🗺️ Para mapa
            longitud=prop.longitud,  # 🗺️ Para mapa
            telefono=prop.propietario_real_telefono or "",
            email=prop.propietario_real_email or "",
            propietario_nombre=prop.propietario_real_nombre or "",
            transaccion=prop.transaccion,
            precio_alquiler=prop.precio_alquiler,
            precio_venta=prop.precio_venta,
            moneda=prop.moneda,
            area=prop.area,
            habitaciones=prop.habitaciones,
            banos=prop.banos,
            parqueos=prop.parqueos,
            imagen_principal=prop.imagen_principal,
            imagenes=prop.imagenes or [],  # 🔥 AGREGADO para carrusel
            estado=prop.estado,
            estado_crm=prop.estado_crm,
            vistas=prop.vistas,
            contactos=prop.contactos,
            created_at=prop.created_at
        ))
    
    return PaginatedResponse(
        success=True,
        data=propiedades_list,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.get("/me/propiedades", response_model=PaginatedResponse[PropiedadResponse])
@router.get("/mis-propiedades", response_model=PaginatedResponse[PropiedadResponse])
async def my_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[str] = None,
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """Mis propiedades (Ofertante/Corredor) - Admin ve TODAS"""
    # 🔥 Admin (perfil_id == 4) puede ver TODAS las propiedades
    if current_user.perfil_id == 4:
        query = db.query(Propiedad)  # Sin filtro de usuario
    else:
        query = db.query(Propiedad).filter(Propiedad.usuario_id == current_user.usuario_id)

    if estado:
        query = query.filter(Propiedad.estado == estado)

    total = query.count()
    offset = (page - 1) * limit
    propiedades = query.order_by(Propiedad.created_at.desc()).offset(offset).limit(limit).all()

    # Obtener IDs de favoritos del usuario
    favoritos_ids = {f.registro_cab_id for f in db.query(Favorito.registro_cab_id).filter(
        Favorito.usuario_id == current_user.usuario_id
    ).all()}

    # Formatear respuesta (similar a list_properties)
    propiedades_list = []
    for prop in propiedades:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == prop.tipo_inmueble_id).first()
        distrito = db.query(Distrito).filter(Distrito.distrito_id == prop.distrito_id).first()

        propiedades_list.append(PropiedadResponse(
            registro_cab_id=prop.registro_cab_id,
            titulo=prop.titulo,
            tipo_inmueble=tipo.nombre if tipo else "N/A",
            distrito=distrito.nombre if distrito else "N/A",
            direccion=prop.direccion,
            latitud=prop.latitud,  # 🗺️ Para mapa
            longitud=prop.longitud,  # 🗺️ Para mapa
            telefono=prop.propietario_real_telefono or "",
            email=prop.propietario_real_email or "",
            propietario_nombre=prop.propietario_real_nombre or "",
            transaccion=prop.transaccion,
            precio_alquiler=prop.precio_alquiler,
            precio_venta=prop.precio_venta,
            moneda=prop.moneda,
            area=prop.area,
            habitaciones=prop.habitaciones,
            banos=prop.banos,
            parqueos=prop.parqueos,
            imagen_principal=prop.imagen_principal,
            imagenes=prop.imagenes or [],  # 🔥 AGREGADO para carrusel
            estado=prop.estado,
            estado_crm=prop.estado_crm,
            vistas=prop.vistas,
            contactos=prop.contactos,
            created_at=prop.created_at,
            es_favorito=prop.registro_cab_id in favoritos_ids  # ⭐ FAVORITO
        ))

    # Estadísticas
    stats = {
        "total_propiedades": total,
        "publicadas": db.query(Propiedad).filter(
            Propiedad.usuario_id == current_user.usuario_id,
            Propiedad.estado == "publicado"
        ).count(),
        "borradores": db.query(Propiedad).filter(
            Propiedad.usuario_id == current_user.usuario_id,
            Propiedad.estado == "borrador"
        ).count(),
        "total_vistas": db.query(func.sum(Propiedad.vistas)).filter(
            Propiedad.usuario_id == current_user.usuario_id
        ).scalar() or 0,
        "total_contactos": db.query(func.sum(Propiedad.contactos)).filter(
            Propiedad.usuario_id == current_user.usuario_id
        ).scalar() or 0
    }

    return PaginatedResponse(
        success=True,
        data=propiedades_list,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "estadisticas": stats
        }
    )

@router.get("/{propiedad_id}", response_model=ResponseModel[PropiedadDetalleResponse])
async def get_property_detail(
    propiedad_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[Usuario] = Depends(get_optional_user)
):
    """
    Ver detalle de propiedad
    - Sin token: Solo propiedades publicadas
    - Con token: Dueño puede ver sus propiedades (cualquier estado), Admin puede ver TODAS
    """
    propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")
    
    # Validar acceso según token
    if current_user:
        # Usuario autenticado: Admin puede ver todas, dueño puede ver las suyas
        if current_user.perfil_id != 4 and propiedad.usuario_id != current_user.usuario_id:
            # No es admin ni dueño, solo puede ver si está publicada
            if propiedad.estado != "publicado":
                raise NotFoundException("Propiedad no disponible")
    else:
        # Sin token: solo propiedades publicadas
        if propiedad.estado != "publicado":
            raise NotFoundException("Propiedad no disponible")
    
    # Obtener datos relacionados
    tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == propiedad.tipo_inmueble_id).first()
    distrito = db.query(Distrito).filter(Distrito.distrito_id == propiedad.distrito_id).first()
    
    # Obtener características
    detalles = db.query(PropiedadDetalle).filter(PropiedadDetalle.registro_cab_id == propiedad_id).all()
    caracteristicas = []
    for det in detalles:
        caract = db.query(Caracteristica).filter(Caracteristica.caracteristica_id == det.caracteristica_id).first()
        if caract:
            caracteristicas.append({
                "caracteristica_id": caract.caracteristica_id,
                "nombre": caract.nombre,
                "valor": det.valor,
                "categoria": caract.categoria
            })
    
    # Propietario (incluye DNI si está autenticado y es dueño/admin)
    propietario = {
        "nombre": propiedad.propietario_real_nombre or "",
        "telefono": propiedad.propietario_real_telefono or "",
        "email": propiedad.propietario_real_email or ""
    }
    
    # Agregar DNI si es dueño o admin
    if current_user and (current_user.perfil_id == 4 or propiedad.usuario_id == current_user.usuario_id):
        propietario["dni"] = propiedad.propietario_real_dni or ""
    
    # Corredor (si aplica)
    corredor = None
    if propiedad.corredor_asignado_id:
        corredor_user = db.query(Usuario).filter(Usuario.usuario_id == propiedad.corredor_asignado_id).first()
        if corredor_user:
            corredor = {
                "nombre": f"{corredor_user.nombre} {corredor_user.apellido}",
                "telefono": corredor_user.telefono,
                "email": corredor_user.email
            }
    
    # Verificar si está en favoritos (solo si hay usuario autenticado)
    es_favorito = False
    if current_user:
        es_favorito = db.query(Favorito).filter(
            Favorito.usuario_id == current_user.usuario_id,
            Favorito.registro_cab_id == propiedad_id
        ).first() is not None
    
    return ResponseModel(
        success=True,
        data=PropiedadDetalleResponse(
            registro_cab_id=propiedad.registro_cab_id,
            titulo=propiedad.titulo,
            nombre_inmueble=propiedad.nombre_inmueble,
            tipo_inmueble=tipo.nombre if tipo else "N/A",
            distrito=distrito.nombre if distrito else "N/A",
            transaccion=propiedad.transaccion,
            precio_alquiler=propiedad.precio_alquiler,
            precio_venta=propiedad.precio_venta,
            moneda=propiedad.moneda,
            area=propiedad.area,
            habitaciones=propiedad.habitaciones,
            banos=propiedad.banos,
            parqueos=propiedad.parqueos,
            imagen_principal=propiedad.imagen_principal,
            estado=propiedad.estado,
            vistas=propiedad.vistas,
            contactos=propiedad.contactos,
            created_at=propiedad.created_at,
            descripcion=propiedad.descripcion,
            direccion=propiedad.direccion,
            latitud=propiedad.latitud,
            longitud=propiedad.longitud,
            antiguedad=propiedad.antiguedad,
            imagenes=propiedad.imagenes or [],
            propietario=propietario,
            corredor=corredor,
            caracteristicas=caracteristicas,
            estado_crm=propiedad.estado_crm,
            compartidos=propiedad.compartidos,
            es_favorito=es_favorito
        )
    )

@router.post("/{propiedad_id}/vista", response_model=ResponseModel[dict])
async def increment_view(
    propiedad_id: int,
    db: Session = Depends(get_db)
):
    """Incrementar contador de vistas"""
    propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")
    
    propiedad.vistas += 1
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Vista registrada",
        data={"vistas": propiedad.vistas}
    )

@router.post("/{propiedad_id}/contacto", response_model=ResponseModel[dict])
async def contact_property(
    propiedad_id: int,
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    db: Session = Depends(get_db)
):
    """Contactar propietario de propiedad"""
    propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")
    
    # Incrementar contador de contactos
    propiedad.contactos += 1
    db.commit()
    
    # Enviar email al propietario
    EmailService.send_property_contact_notification(
        propietario_email=propiedad.propietario_real_email,
        propietario_nombre=propiedad.propietario_real_nombre,
        propiedad_titulo=propiedad.titulo,
        contacto_nombre=nombre,
        contacto_email=email,
        contacto_telefono=telefono,
        mensaje=mensaje
    )
    
    # Enviar SMS (opcional)
    if propiedad.propietario_real_telefono:
        SMSService.send_property_contact_sms(
            propietario_telefono=propiedad.propietario_real_telefono,
            propiedad_titulo=propiedad.titulo,
            contacto_nombre=nombre
        )
    
    return ResponseModel(
        success=True,
        message="Contacto registrado. El propietario se comunicará contigo pronto.",
        data={}
    )

@router.post("", response_model=ResponseModel[dict], status_code=201)
async def create_property(
    propiedad_data: PropiedadCreate,
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """Crear nueva propiedad (Ofertante/Corredor)"""
    # Crear propiedad
    nueva_propiedad = Propiedad(
        usuario_id=current_user.usuario_id,
        propietario_real_nombre=propiedad_data.propietario_real_nombre,
        propietario_real_dni=propiedad_data.propietario_real_dni,
        propietario_real_telefono=propiedad_data.propietario_real_telefono,
        propietario_real_email=propiedad_data.propietario_real_email,
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
        precio_alquiler=propiedad_data.precio_alquiler,
        precio_venta=propiedad_data.precio_venta,
        moneda=propiedad_data.moneda,
        titulo=propiedad_data.titulo,
        descripcion=propiedad_data.descripcion,
        imagen_principal=propiedad_data.imagen_principal,
        imagenes=propiedad_data.imagenes,
        estado="borrador",
        created_by=current_user.usuario_id
    )
    
    db.add(nueva_propiedad)
    db.commit()
    db.refresh(nueva_propiedad)
    
    # Agregar características
    if propiedad_data.caracteristicas:
        for caract in propiedad_data.caracteristicas:
            detalle = PropiedadDetalle(
                registro_cab_id=nueva_propiedad.registro_cab_id,
                caracteristica_id=caract.caracteristica_id,
                valor=caract.valor
            )
            db.add(detalle)
        db.commit()
    
    return ResponseModel(
        success=True,
        message="Propiedad creada exitosamente",
        data={
            "registro_cab_id": nueva_propiedad.registro_cab_id,
            "titulo": nueva_propiedad.titulo,
            "estado": nueva_propiedad.estado
        }
    )

@router.patch("/{propiedad_id}/estado", response_model=ResponseModel[dict])
async def update_property_status(
    propiedad_id: int,
    estado_data: PropiedadEstadoUpdate,
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """Cambiar estado de propiedad"""
    propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")
    
    # Verificar permisos
    if propiedad.usuario_id != current_user.usuario_id:
        raise ForbiddenException("No tienes permiso para modificar esta propiedad")
    
    propiedad.estado = estado_data.estado
    db.commit()
    
    return ResponseModel(
        success=True,
        message=f"Estado actualizado a {estado_data.estado}",
        data={"registro_cab_id": propiedad_id, "estado": estado_data.estado}
    )


# ================================================================
# 🔍 BÚSQUEDA AVANZADA - Endpoint POST con Body Estructurado
# ================================================================

# Modelos Pydantic para el Body Request
class FiltroAvanzadoItem(BaseModel):
    caracteristica_id: int
    valor: str

class BusquedaAvanzadaRequest(BaseModel):
    filtros_genericos: Optional[Dict[str, Any]] = {}
    filtros_basicos: Optional[Dict[str, Any]] = {}
    filtros_avanzados: Optional[List[FiltroAvanzadoItem]] = []
    page: int = 1
    limit: int = 12


@router.post("/buscar-avanzada", response_model=PaginatedResponse[PropiedadResponse])
async def buscar_propiedades_avanzada(
    busqueda: BusquedaAvanzadaRequest = Body(...),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Búsqueda Avanzada con Filtros Estructurados (Requiere Token)

    Body esperado:
    {
        "filtros_genericos": {
            "tipo_inmueble_id": 1,
            "distrito_ids": [1, 2, 3],
            "transaccion": "venta"
        },
        "filtros_basicos": {
            "area": 100,
            "precio": 500000,
            "habitaciones": [2, 3],
            "banos": [2],
            "parqueos": 1
        },
        "filtros_avanzados": [
            {
                "caracteristica_id": 5,
                "valor": "Si"
            }
        ],
        "page": 1,
        "limit": 12
    }
    """
    # Query base - solo propiedades publicadas
    query = db.query(Propiedad).filter(Propiedad.estado == "publicado")

    # ============================================
    # 1️⃣ FILTROS GENÉRICOS (registro_x_inmueble_cab)
    # ============================================
    filtros_gen = busqueda.filtros_genericos or {}

    # Tipo de inmueble
    if filtros_gen.get("tipo_inmueble_id"):
        query = query.filter(Propiedad.tipo_inmueble_id == filtros_gen["tipo_inmueble_id"])

    # Distritos (múltiples)
    if filtros_gen.get("distrito_ids") and len(filtros_gen["distrito_ids"]) > 0:
        query = query.filter(Propiedad.distrito_id.in_(filtros_gen["distrito_ids"]))

    # Transacción
    if filtros_gen.get("transaccion"):
        query = query.filter(Propiedad.transaccion.in_([filtros_gen["transaccion"], "ambos"]))

    # ============================================
    # 2️⃣ FILTROS BÁSICOS con ±15% (registro_x_inmueble_cab)
    # ============================================
    filtros_bas = busqueda.filtros_basicos or {}

    # Área (±15%)
    if filtros_bas.get("area"):
        area_objetivo = float(filtros_bas["area"])
        margen = area_objetivo * 0.15
        area_min = area_objetivo - margen
        area_max = area_objetivo + margen
        query = query.filter(Propiedad.area >= area_min, Propiedad.area <= area_max)

    # Precio (±15%) - según transacción
    if filtros_bas.get("precio"):
        precio_objetivo = float(filtros_bas["precio"])
        margen = precio_objetivo * 0.15
        precio_min = precio_objetivo - margen
        precio_max = precio_objetivo + margen

        transaccion = filtros_gen.get("transaccion", "venta")
        if transaccion == "alquiler":
            query = query.filter(
                Propiedad.precio_alquiler >= precio_min,
                Propiedad.precio_alquiler <= precio_max
            )
        else:
            query = query.filter(
                Propiedad.precio_venta >= precio_min,
                Propiedad.precio_venta <= precio_max
            )

    # Habitaciones (múltiples)
    if filtros_bas.get("habitaciones") and len(filtros_bas["habitaciones"]) > 0:
        query = query.filter(Propiedad.habitaciones.in_(filtros_bas["habitaciones"]))

    # Baños (múltiples)
    if filtros_bas.get("banos") and len(filtros_bas["banos"]) > 0:
        query = query.filter(Propiedad.banos.in_(filtros_bas["banos"]))

    # Parqueos (mínimo)
    if filtros_bas.get("parqueos"):
        query = query.filter(Propiedad.parqueos >= filtros_bas["parqueos"])

    # Antigüedad (años máximo)
    if filtros_bas.get("antiguedad"):
        query = query.filter(Propiedad.antiguedad <= filtros_bas["antiguedad"])

    # Implementación / Nivel de amoblamiento (múltiples opciones)
    if filtros_bas.get("implementacion") and len(filtros_bas["implementacion"]) > 0:
        query = query.filter(Propiedad.implementacion.in_(filtros_bas["implementacion"]))

    # ============================================
    # 3️⃣ FILTROS AVANZADOS (registro_x_inmueble_det)
    # ============================================
    if busqueda.filtros_avanzados and len(busqueda.filtros_avanzados) > 0:
        for filtro_avanzado in busqueda.filtros_avanzados:
            query = query.filter(
                Propiedad.registro_cab_id.in_(
                    db.query(PropiedadDetalle.registro_cab_id).filter(
                        PropiedadDetalle.caracteristica_id == filtro_avanzado.caracteristica_id,
                        PropiedadDetalle.valor == filtro_avanzado.valor
                    )
                )
            )

    # ============================================
    # PAGINACIÓN Y RESULTADO
    # ============================================
    total = query.count()
    query = query.order_by(Propiedad.created_at.desc())
    offset = (busqueda.page - 1) * busqueda.limit
    propiedades = query.offset(offset).limit(busqueda.limit).all()

    # Obtener IDs de favoritos del usuario
    favoritos_ids = {f.registro_cab_id for f in db.query(Favorito.registro_cab_id).filter(
        Favorito.usuario_id == current_user.usuario_id
    ).all()}

    # Formatear respuesta
    propiedades_list = []
    for prop in propiedades:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == prop.tipo_inmueble_id).first()
        distrito = db.query(Distrito).filter(Distrito.distrito_id == prop.distrito_id).first()

        propiedades_list.append(PropiedadResponse(
            registro_cab_id=prop.registro_cab_id,
            titulo=prop.titulo,
            tipo_inmueble=tipo.nombre if tipo else "N/A",
            distrito=distrito.nombre if distrito else "N/A",
            direccion=prop.direccion,
            latitud=prop.latitud,
            longitud=prop.longitud,
            telefono=prop.propietario_real_telefono or "",
            email=prop.propietario_real_email or "",
            propietario_nombre=prop.propietario_real_nombre or "",
            transaccion=prop.transaccion,
            precio_alquiler=prop.precio_alquiler,
            precio_venta=prop.precio_venta,
            moneda=prop.moneda,
            area=prop.area,
            habitaciones=prop.habitaciones,
            banos=prop.banos,
            parqueos=prop.parqueos,
            imagen_principal=prop.imagen_principal,
            imagenes=prop.imagenes or [],
            estado=prop.estado,
            estado_crm=prop.estado_crm,
            vistas=prop.vistas,
            contactos=prop.contactos,
            created_at=prop.created_at,
            es_favorito=prop.registro_cab_id in favoritos_ids
        ))

    return PaginatedResponse(
        success=True,
        data=propiedades_list,
        pagination={
            "page": busqueda.page,
            "limit": busqueda.limit,
            "total": total,
            "total_pages": (total + busqueda.limit - 1) // busqueda.limit
        }
    )
