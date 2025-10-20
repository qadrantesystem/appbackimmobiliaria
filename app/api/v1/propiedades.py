from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from decimal import Decimal
from app.database import get_db
from app.dependencies import get_current_active_user, require_ofertante, get_optional_user
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.models import Propiedad, PropiedadDetalle, Usuario, TipoInmueble, Distrito, Caracteristica
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
            telefono=prop.propietario_real_telefono,
            email=prop.propietario_real_email,
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
            telefono=prop.propietario_real_telefono,
            email=prop.propietario_real_email,
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
    db: Session = Depends(get_db)
):
    """Ver detalle de propiedad"""
    propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")
    
    # Solo mostrar si está publicada
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
    
    # Propietario
    propietario = {
        "nombre": propiedad.propietario_real_nombre,
        "telefono": propiedad.propietario_real_telefono,
        "email": propiedad.propietario_real_email
    }
    
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
    
    return ResponseModel(
        success=True,
        data=PropiedadDetalleResponse(
            registro_cab_id=propiedad.registro_cab_id,
            titulo=propiedad.titulo,
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
            compartidos=propiedad.compartidos
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
