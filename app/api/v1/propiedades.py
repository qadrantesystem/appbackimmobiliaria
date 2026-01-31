import re
from fastapi import APIRouter, Depends, Query, UploadFile, File, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_active_user, require_ofertante, get_optional_user
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.models import Propiedad, PropiedadDetalle, Usuario, TipoInmueble, Distrito, Caracteristica, Favorito, Propietario
from app.schemas.propiedad import PropiedadCreate, PropiedadUpdate, PropiedadEstadoUpdate, PropiedadResponse, PropiedadDetalleResponse
from app.schemas.common import ResponseModel, PaginatedResponse
from app.schemas.oficina_masivo import GenerarOficinasRequest, GenerarOficinasResponse, OficinaGenerada, EdificioDisponible
from app.services.imagekit_service import ImageKitService
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.busqueda_inteligente import BusquedaInteligenteService

router = APIRouter()

@router.get("")
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
    incluir_combinaciones: bool = Query(
        default=True,
        description="Incluir combinaciones inteligentes de propiedades"
    ),
    db: Session = Depends(get_db)
):
    """
    🔍 Búsqueda pública de propiedades con combinaciones inteligentes
    Endpoint público - no requiere autenticación

    Si `incluir_combinaciones=true` y se especifica `area_min`, el sistema:
    - Busca propiedades individuales que cumplan los criterios
    - Busca combinaciones de oficinas contiguas que sumen el área solicitada
    - Retorna ambos resultados unificados
    """
    print("🚀 [DEBUG] GET /propiedades endpoint llamado")
    print(f"📊 [DEBUG] Parámetros: page={page}, limit={limit}, tipo_inmueble_id={tipo_inmueble_id}, incluir_combinaciones={incluir_combinaciones}")

    # Parsear distritos
    distrito_ids = None
    if distrito_id:
        try:
            distrito_ids = [int(d) for d in distrito_id.split(",")]
        except:
            distrito_ids = None

    # Si NO se solicitan combinaciones o NO hay área mínima, usar lógica ORIGINAL
    if not incluir_combinaciones or not area_min:
        print("📌 [DEBUG] Usando búsqueda tradicional (sin combinaciones)")

        # Query base - solo propiedades publicadas + eager load propietario (LEFT JOIN)
        query = db.query(Propiedad).options(
            joinedload(Propiedad.propietario, innerjoin=False)
        ).filter(Propiedad.estado == "publicado")

        # Filtros
        if tipo_inmueble_id:
            query = query.filter(Propiedad.tipo_inmueble_id == tipo_inmueble_id)

        if distrito_ids:
            query = query.filter(Propiedad.distrito_id.in_(distrito_ids))

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

        # Total
        total = query.count()
        print(f"📈 [DEBUG] Total propiedades encontradas: {total}")

        # Ordenar por fecha (más recientes primero)
        query = query.order_by(Propiedad.created_at.desc())

        # Paginación
        offset = (page - 1) * limit
        propiedades = query.offset(offset).limit(limit).all()
        print(f"📦 [DEBUG] Propiedades obtenidas después de paginación: {len(propiedades)}")

        # Formatear respuesta
        propiedades_list = []
        for prop in propiedades:
            tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == prop.tipo_inmueble_id).first()
            distrito = db.query(Distrito).filter(Distrito.distrito_id == prop.distrito_id).first()

            propiedades_list.append(PropiedadResponse(
                registro_cab_id=prop.registro_cab_id,
                titulo=prop.titulo,
                tipo_inmueble=tipo.nombre if tipo else "N/A",
                tipo_inmueble_id=prop.tipo_inmueble_id,
                distrito=distrito.nombre if distrito else "N/A",
                direccion=prop.direccion,
                latitud=prop.latitud,
                longitud=prop.longitud,
                telefono=prop.propietario.telefono if prop.propietario else "",
                email=prop.propietario.email if prop.propietario else "",
                propietario_nombre=prop.propietario.nombre if prop.propietario else "",
                transaccion=prop.transaccion,
                precio_alquiler=prop.precio_alquiler,
                precio_venta=prop.precio_venta,
                moneda=prop.moneda,
                area=prop.area,
                implementacion=prop.implementacion,
                imagen_principal=prop.imagen_principal,
                imagenes=prop.imagenes or [],
                estado=prop.estado,
                estado_crm=prop.estado_crm,
                vistas=prop.vistas,
                contactos=prop.contactos,
                created_at=prop.created_at
            ))

        print(f"✅ [DEBUG] Propiedades formateadas: {len(propiedades_list)}")

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

    # NUEVA LÓGICA: Búsqueda inteligente con combinaciones
    print("🔥 [DEBUG] Usando búsqueda inteligente CON combinaciones")

    busqueda_service = BusquedaInteligenteService(db)

    resultado = busqueda_service.buscar_con_combinaciones(
        area_min=float(area_min) if area_min else None,
        area_max=float(area_max) if area_max else None,
        tipo_inmueble_id=tipo_inmueble_id,
        distrito_ids=distrito_ids,
        transaccion=transaccion,
        precio_max=float(precio_max) if precio_max else None,
        limit=limit * 2,  # Traer más para paginar mixto
        usuario_id=None  # Sin usuario en búsqueda pública
    )

    # Combinar individuales y combinaciones
    items_totales = resultado["individuales"] + resultado["combinaciones"]

    # Ordenar por relevancia (individuales primero, luego por área)
    items_totales.sort(key=lambda x: (
        0 if x.get("tipo") != "combinacion" else 1,  # Individuales primero
        -x.get("area_total", x.get("area", 0))  # Luego por área (mayor primero)
    ))

    # Paginar
    total = len(items_totales)
    inicio = (page - 1) * limit
    fin = inicio + limit
    items_paginados = items_totales[inicio:fin]

    print(f"✅ [DEBUG] Búsqueda inteligente completada: {len(resultado['individuales'])} individuales, {len(resultado['combinaciones'])} combinaciones")

    return {
        "success": True,
        "data": items_paginados,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        },
        "metadata": {
            "individuales": len(resultado["individuales"]),
            "combinaciones": len(resultado["combinaciones"]),
            "incluir_combinaciones": incluir_combinaciones
        }
    }

@router.get("/me/propiedades", response_model=PaginatedResponse[PropiedadResponse])
@router.get("/mis-propiedades", response_model=PaginatedResponse[PropiedadResponse])
async def my_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),  # Límite por defecto 50, máximo 500
    estado: Optional[str] = None,  # ✅ Opcional: NO filtra por defecto (incluye borradores)
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    Mis propiedades con paginación
    - Admin (perfil_id == 4): Ve TODAS las propiedades de todos los usuarios
    - Ofertantes/Corredores (perfil_id 2,3): Solo ven SUS propiedades
    - Por defecto incluye TODOS los estados (publicado, borrador, pausado)
    """
    # 🔥 Admin (perfil_id == 4) puede ver TODAS las propiedades
    if current_user.perfil_id == 4:
        query = db.query(Propiedad).options(joinedload(Propiedad.propietario, innerjoin=False))  # Admin: TODAS
    else:
        # Ofertantes/Corredores: Solo sus propiedades
        query = db.query(Propiedad).options(joinedload(Propiedad.propietario, innerjoin=False)).filter(Propiedad.usuario_id == current_user.usuario_id)

    # Filtro opcional por estado (si no se especifica, trae TODOS)
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
            tipo_inmueble_id=prop.tipo_inmueble_id,  # ✅ ID para filtros en frontend
            distrito=distrito.nombre if distrito else "N/A",
            direccion=prop.direccion,
            latitud=prop.latitud,  # 🗺️ Para mapa
            longitud=prop.longitud,  # 🗺️ Para mapa
            telefono=prop.propietario.telefono if prop.propietario else "",
            email=prop.propietario.email if prop.propietario else "",
            propietario_nombre=prop.propietario.nombre if prop.propietario else "",
            transaccion=prop.transaccion,
            precio_alquiler=prop.precio_alquiler,
            precio_venta=prop.precio_venta,
            moneda=prop.moneda,
            area=prop.area,
            implementacion=prop.implementacion,  # 🏗️ Nivel de implementación
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

@router.get("/{edificio_id}/oficinas", response_model=ResponseModel[List[dict]])
async def get_oficinas_edificio(
    edificio_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    🏬 Retorna todas las oficinas hijas de un edificio con sus características
    
    Returns:
    {
        "data": [
            {
                "registro_cab_id": 31,
                "numero_oficina": 901,
                "piso": 9,
                "nombre": "Oficina 901",
                "area": 50.0,
                "caracteristicas": [
                    {"caracteristica_id": 124, "nombre": "AAC", "valor": "true"},
                    {"caracteristica_id": 128, "nombre": "Mobiliario", "valor": "true"}
                ]
            },
            ...
        ]
    }
    """
    # Validar que el edificio existe
    edificio = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == edificio_id
    ).first()
    
    if not edificio:
        raise NotFoundException("Edificio no encontrado")
    
    # Obtener oficinas hijas
    oficinas = db.query(Propiedad).filter(
        Propiedad.padre_registro_cab_id == edificio_id
    ).order_by(Propiedad.registro_cab_id).all()
    
    oficinas_list = []
    for oficina in oficinas:
        # ✅ Obtener piso desde columna cabecera (preferido) o fallback a característica 110
        piso = oficina.piso  # Campo de cabecera (nuevo)
        if piso is None:
            # Fallback: buscar en características (para oficinas antiguas)
            piso_det = db.query(PropiedadDetalle).filter(
                PropiedadDetalle.registro_cab_id == oficina.registro_cab_id,
                PropiedadDetalle.caracteristica_id == 110
            ).first()
            piso = int(piso_det.valor) if piso_det else None

        # Extraer numero_oficina del nombre si existe (ej: "Oficina 901" -> 901)
        numero_oficina = None
        if oficina.nombre_inmueble:
            match = re.search(r'(\d+)', oficina.nombre_inmueble)
            if match:
                numero_oficina = int(match.group(1))

        # Obtener TODAS las características de la oficina
        caracteristicas = []
        equip_dets = db.query(
            PropiedadDetalle.caracteristica_id,
            PropiedadDetalle.valor,
            Caracteristica.nombre
        ).join(
            Caracteristica,
            PropiedadDetalle.caracteristica_id == Caracteristica.caracteristica_id
        ).filter(
            PropiedadDetalle.registro_cab_id == oficina.registro_cab_id
        ).all()

        for det in equip_dets:
            caracteristicas.append({
                "caracteristica_id": det.caracteristica_id,
                "nombre": det.nombre,
                "valor": det.valor
            })

        oficinas_list.append({
            "registro_cab_id": oficina.registro_cab_id,
            "nombre": oficina.nombre_inmueble,
            "numero_oficina": numero_oficina,
            "piso": piso,
            "area": float(oficina.area) if oficina.area else None,
            "estado": oficina.estado,
            "precio_venta": float(oficina.precio_venta) if oficina.precio_venta else None,
            "precio_alquiler": float(oficina.precio_alquiler) if oficina.precio_alquiler else None,
            "caracteristicas": caracteristicas
        })
    
    return ResponseModel(
        success=True,
        data=oficinas_list,
        message=f"{len(oficinas_list)} oficinas encontradas"
    )

@router.get("/edificios-disponibles", response_model=ResponseModel[List[EdificioDisponible]])
async def listar_edificios_disponibles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📋 Listar edificios disponibles para selector de padre

    Retorna edificios que pueden tener oficinas hijas.
    """
    # Buscar tipo_inmueble_id = 12 (Edificio Completo)
    # NO usar LIKE porque captura "Oficina en Edificio" (tipo 1)
    tipo_edificio = db.query(TipoInmueble).filter(
        TipoInmueble.tipo_inmueble_id == 12  # Edificio Completo
    ).first()

    if not tipo_edificio:
        return ResponseModel(
            success=True,
            data=[],
            message="No se encontró el tipo 'Edificio Completo' (ID 12) en el sistema"
        )

    # Query edificios sin padre (padre_registro_cab_id IS NULL)
    edificios = db.query(Propiedad).filter(
        Propiedad.tipo_inmueble_id == 12,  # Directamente tipo 12
        Propiedad.padre_registro_cab_id.is_(None)
    ).all()

    # Formatear respuesta con características de cantidad de pisos
    edificios_list = []
    for edificio in edificios:
        # Buscar característica "Cantidad de Pisos"
        cantidad_pisos = None
        pisos_det = db.query(PropiedadDetalle).join(Caracteristica).filter(
            PropiedadDetalle.registro_cab_id == edificio.registro_cab_id,
            Caracteristica.nombre.ilike("%piso%")
        ).first()

        if pisos_det:
            cantidad_pisos = pisos_det.valor

        edificios_list.append(EdificioDisponible(
            registro_cab_id=edificio.registro_cab_id,
            nombre_inmueble=edificio.nombre_inmueble,
            direccion=edificio.direccion,
            tipo_inmueble_id=edificio.tipo_inmueble_id,  # ✅ Para filtros en frontend
            distrito_id=edificio.distrito_id,  # ✅ Para herencia
            latitud=str(edificio.latitud) if edificio.latitud else None,  # ✅ Para herencia
            longitud=str(edificio.longitud) if edificio.longitud else None,  # ✅ Para herencia
            cantidad_pisos=cantidad_pisos
        ))

    return ResponseModel(
        success=True,
        data=edificios_list,
        message=f"{len(edificios_list)} edificios disponibles"
    )
@router.get("/{edificio_id}/caracteristicas", response_model=ResponseModel[Dict[str, List[dict]]])
async def obtener_caracteristicas_edificio(
    edificio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    📋 Obtener características de un edificio agrupadas por categoría

    Usado para mostrar detalles del edificio padre al registrar oficina.
    """
    # Validar que el edificio existe
    edificio = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == edificio_id
    ).first()

    if not edificio:
        raise NotFoundException("Edificio no encontrado")

    # Obtener características con JOIN optimizado (evita N+1 queries)
    caracteristicas_query = db.query(
        PropiedadDetalle.caracteristica_id,
        PropiedadDetalle.valor,
        Caracteristica.nombre,
        Caracteristica.tipo_input,
        Caracteristica.categoria_id,
        Caracteristica.categoria  # DEPRECATED: para agrupar temporalmente
    ).join(
        Caracteristica,
        PropiedadDetalle.caracteristica_id == Caracteristica.caracteristica_id
    ).filter(
        PropiedadDetalle.registro_cab_id == edificio_id
    ).all()

    # Agrupar por categoría
    caracteristicas_agrupadas = {}
    
    for c in caracteristicas_query:
        # Usar categoria_id como clave (más adelante se puede mapear a nombre)
        categoria = c.categoria or "General"

        if categoria not in caracteristicas_agrupadas:
            caracteristicas_agrupadas[categoria] = []

        caracteristicas_agrupadas[categoria].append({
            "caracteristica_id": c.caracteristica_id,
            "nombre": c.nombre,
            "valor": c.valor,
            "tipo_input": c.tipo_input,
            "categoria_id": c.categoria_id  # ✅ Incluir categoria_id
        })

    return ResponseModel(
        success=True,
        data=caracteristicas_agrupadas,
        message=f"Características del edificio {edificio.nombre_inmueble}"
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
    
    # Obtener características con JOIN optimizado (evita N+1 queries)
    caracteristicas_query = db.query(
        PropiedadDetalle.caracteristica_id,
        PropiedadDetalle.valor,
        Caracteristica.nombre,
        Caracteristica.categoria_id,  # ✅ Usar categoria_id (INTEGER)
        Caracteristica.categoria      # ⚠️ DEPRECATED: mantener por compatibilidad
    ).join(
        Caracteristica,
        PropiedadDetalle.caracteristica_id == Caracteristica.caracteristica_id
    ).filter(
        PropiedadDetalle.registro_cab_id == propiedad_id
    ).all()
    
    caracteristicas = [
        {
            "caracteristica_id": c.caracteristica_id,
            "nombre": c.nombre,
            "valor": c.valor,
            "categoria_id": c.categoria_id,  # ✅ Incluir categoria_id
            "categoria": c.categoria         # ⚠️ DEPRECATED
        }
        for c in caracteristicas_query
    ]
    
    # Propietario (incluye DNI si está autenticado y es dueño/admin)
    propietario = {
        "nombre": propiedad.propietario.nombre if propiedad.propietario else "",
        "telefono": propiedad.propietario.telefono if propiedad.propietario else "",
        "email": propiedad.propietario.email if propiedad.propietario else ""
    }

    # Agregar DNI si es dueño o admin
    if current_user and (current_user.perfil_id == 4 or propiedad.usuario_id == current_user.usuario_id):
        propietario["dni"] = propiedad.propietario.dni if propiedad.propietario else ""
    
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
    
    # 🏢 Si es Edificio Completo (tipo_inmueble_id == 12), agregar oficinas hijas
    total_oficinas = None
    oficinas_list = []
    
    # Usar tipo_inmueble_id == 12 (más robusto que buscar en nombre)
    print(f"🔍 DEBUG: tipo_inmueble_id = {propiedad.tipo_inmueble_id}, padre_registro_cab_id = {propiedad.padre_registro_cab_id}")
    if propiedad.tipo_inmueble_id == 12 and propiedad.padre_registro_cab_id is None:
        print(f"✅ Condición cumplida, buscando oficinas para edificio {propiedad_id}")
        # Obtener oficinas hijas
        oficinas = db.query(Propiedad).filter(
            Propiedad.padre_registro_cab_id == propiedad_id
        ).order_by(Propiedad.registro_cab_id).all()
        
        total_oficinas = len(oficinas)
        
        # Para cada oficina, obtener sus características
        for oficina in oficinas:
            # Buscar características específicas: Piso y Número de Oficina
            caract_oficina = db.query(
                PropiedadDetalle.caracteristica_id,
                PropiedadDetalle.valor,
                Caracteristica.nombre
            ).join(
                Caracteristica,
                PropiedadDetalle.caracteristica_id == Caracteristica.caracteristica_id
            ).filter(
                PropiedadDetalle.registro_cab_id == oficina.registro_cab_id
            ).all()
            
            # ✅ Obtener piso directamente de la columna de la oficina
            piso = oficina.piso
            numero_oficina = None
            caracteristicas_oficina = []

            for c in caract_oficina:
                caracteristicas_oficina.append({
                    "caracteristica_id": c.caracteristica_id,
                    "nombre": c.nombre,
                    "valor": c.valor
                })

                # Número de oficina aún viene de características
                if "oficina" in c.nombre.lower() and "número" in c.nombre.lower():
                    try:
                        numero_oficina = int(c.valor)
                    except:
                        numero_oficina = c.valor

            oficinas_list.append({
                "registro_cab_id": oficina.registro_cab_id,
                "nombre_inmueble": oficina.nombre_inmueble,
                "piso": piso,
                "numero_oficina": numero_oficina,
                "area": float(oficina.area) if oficina.area else None,
                "estado": oficina.estado,
                "precio_venta": float(oficina.precio_venta) if oficina.precio_venta else None,
                "precio_alquiler": float(oficina.precio_alquiler) if oficina.precio_alquiler else None,
                "caracteristicas": caracteristicas_oficina
            })
    
    response_data = PropiedadDetalleResponse(
        registro_cab_id=propiedad.registro_cab_id,
        titulo=propiedad.titulo,
        nombre_inmueble=propiedad.nombre_inmueble,
        tipo_inmueble=tipo.nombre if tipo else "N/A",
        tipo_inmueble_id=propiedad.tipo_inmueble_id,  # ✅ ID para filtros
        distrito=distrito.nombre if distrito else "N/A",
        transaccion=propiedad.transaccion,
        precio_alquiler=propiedad.precio_alquiler,
        precio_venta=propiedad.precio_venta,
        moneda=propiedad.moneda,
        area=propiedad.area,
        implementacion=propiedad.implementacion,  # 🏗️ Nivel de implementación
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
        es_favorito=es_favorito,
        padre_registro_cab_id=propiedad.padre_registro_cab_id,
        piso=propiedad.piso
    )
    
    # Agregar oficinas como campo extra si aplica
    result = ResponseModel(success=True, data=response_data)
    print(f"🔍 DEBUG: total_oficinas = {total_oficinas}, len(oficinas_list) = {len(oficinas_list)}")
    if total_oficinas is not None:
        # Añadir info extra al response
        result.data.__dict__['total_oficinas'] = total_oficinas
        result.data.__dict__['oficinas'] = oficinas_list  # ✅ Array de oficinas con características
        print(f"✅ DEBUG: Oficinas agregadas al response: {len(oficinas_list)} oficinas")
    else:
        print(f"❌ DEBUG: total_oficinas es None, no se agregaron oficinas")
    
    return result

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
    if propiedad.propietario and propiedad.propietario.email:
        EmailService.send_property_contact_notification(
            propietario_email=propiedad.propietario.email,
            propietario_nombre=propiedad.propietario.nombre,
            propiedad_titulo=propiedad.titulo,
            contacto_nombre=nombre,
            contacto_email=email,
            contacto_telefono=telefono,
            mensaje=mensaje
        )

    # Enviar SMS (opcional)
    if propiedad.propietario and propiedad.propietario.telefono:
        SMSService.send_property_contact_sms(
            propietario_telefono=propiedad.propietario.telefono,
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
        propietario_id=propiedad_data.propietario_id,
        padre_registro_cab_id=propiedad_data.padre_registro_cab_id,
        piso=propiedad_data.piso,
        tipo_inmueble_id=propiedad_data.tipo_inmueble_id,
        distrito_id=propiedad_data.distrito_id,
        nombre_inmueble=propiedad_data.nombre_inmueble,
        direccion=propiedad_data.direccion,
        latitud=propiedad_data.latitud,
        longitud=propiedad_data.longitud,
        area=propiedad_data.area,
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

@router.put("/{propiedad_id}/publicar", response_model=ResponseModel[dict])
async def publicar_propiedad(
    propiedad_id: int,
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    🚀 Publicar propiedad (cambiar de borrador a publicado)
    
    Permisos:
    - Admin (perfil 4): Puede publicar cualquier propiedad
    - Ofertante/Corredor: Solo puede publicar sus propiedades
    """
    propiedad = db.query(Propiedad).filter(Propiedad.registro_cab_id == propiedad_id).first()
    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")
    
    # Verificar permisos: Admin puede publicar cualquier propiedad
    if current_user.perfil_id != 4 and propiedad.usuario_id != current_user.usuario_id:
        raise ForbiddenException("No tienes permiso para publicar esta propiedad")
    
    # Verificar que está en borrador
    if propiedad.estado != "borrador":
        raise BadRequestException(f"La propiedad ya está en estado '{propiedad.estado}'")
    
    # Cambiar estado a publicado
    propiedad.estado = "publicado"
    db.commit()
    db.refresh(propiedad)
    
    return ResponseModel(
        success=True,
        message="Propiedad publicada exitosamente",
        data={
            "registro_cab_id": propiedad.registro_cab_id,
            "titulo": propiedad.titulo,
            "estado": propiedad.estado,
            "updated_at": propiedad.updated_at
        }
    )

@router.delete("/{oficina_id}/oficina", response_model=ResponseModel[dict])
async def eliminar_oficina(
    oficina_id: int,
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar una oficina individual (solo si pertenece a un edificio)
    
    Validaciones:
    - La oficina debe tener padre_registro_cab_id
    - El propietario debe ser dueño del edificio padre
    - No puede eliminar si es la última oficina del edificio
    """
    # Validar que la oficina existe
    oficina = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == oficina_id
    ).first()
    
    if not oficina:
        raise NotFoundException("Oficina no encontrada")
    
    # Validar que es una oficina de edificio (tiene padre)
    if not oficina.padre_registro_cab_id:
        raise BadRequestException("Esta no es una oficina de edificio, no se puede eliminar mediante este endpoint")
    
    # Obtener edificio padre
    edificio = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == oficina.padre_registro_cab_id
    ).first()
    
    if not edificio:
        raise NotFoundException("Edificio padre no encontrado")
    
    # Verificar permisos: debe ser dueño del edificio o admin
    if edificio.usuario_id != current_user.usuario_id and current_user.perfil_id != 4:
        raise ForbiddenException("No tienes permiso para eliminar esta oficina")
    
    # Contar oficinas restantes del edificio
    oficinas_count = db.query(func.count()).select_from(Propiedad).filter(
        Propiedad.padre_registro_cab_id == edificio.registro_cab_id
    ).scalar()
    
    if oficinas_count <= 1:
        raise BadRequestException("No puedes eliminar la última oficina del edificio. Elimina el edificio completo en su lugar.")
    
    # Eliminar características de la oficina
    db.query(PropiedadDetalle).filter(
        PropiedadDetalle.registro_cab_id == oficina_id
    ).delete()
    
    # Eliminar oficina
    oficina_nombre = oficina.nombre_inmueble
    db.delete(oficina)
    db.commit()
    
    return ResponseModel(
        success=True,
        message=f"Oficina '{oficina_nombre}' eliminada exitosamente",
        data={
            "oficina_eliminada": oficina_id,
            "edificio_padre": edificio.registro_cab_id,
            "oficinas_restantes": oficinas_count - 1
        }
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
    incluir_combinaciones: bool = True  # NUEVO: Búsqueda inteligente con combinaciones


@router.post("/buscar-avanzada")
async def buscar_propiedades_avanzada(
    busqueda: BusquedaAvanzadaRequest = Body(...),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Búsqueda Avanzada con Filtros Estructurados y Combinaciones Inteligentes (Requiere Token)

    Body esperado:
    {
        "filtros_genericos": {
            "tipo_inmueble_id": 1,
            "distrito_ids": [1, 2, 3],
            "transaccion": "venta"
        },
        "filtros_basicos": {
            "area": 100,              // Aplicará ±15% → 85-115 m²
            "precio": 500000,         // Aplicará ±15% → 425000-575000
            "antiguedad": 10
        },
        "filtros_avanzados": [
            {
                "caracteristica_id": 5,
                "valor": "Si"
            }
        ],
        "page": 1,
        "limit": 12,
        "incluir_combinaciones": true  // NUEVO: Habilitar combinaciones inteligentes
    }
    """
    filtros_gen = busqueda.filtros_genericos or {}
    filtros_bas = busqueda.filtros_basicos or {}

    # Calcular área con ±15% si se especifica
    area_min = None
    area_max = None
    if filtros_bas.get("area"):
        area_objetivo = float(filtros_bas["area"])
        margen = area_objetivo * 0.15
        area_min = area_objetivo - margen
        area_max = area_objetivo + margen

    # Calcular precio con ±15% si se especifica
    precio_max = None
    if filtros_bas.get("precio"):
        precio_objetivo = float(filtros_bas["precio"])
        margen = precio_objetivo * 0.15
        precio_max = precio_objetivo + margen  # Solo usaremos el máximo para combinaciones

    # Verificar si se debe usar búsqueda inteligente con combinaciones
    usar_inteligente = (
        busqueda.incluir_combinaciones
        and area_min is not None
        and filtros_gen.get("tipo_inmueble_id") == 1  # Solo oficinas
        and not busqueda.filtros_avanzados  # No soportar filtros avanzados en combinaciones (por ahora)
    )

    if usar_inteligente:
        print("🔥 [DEBUG] Búsqueda autenticada CON combinaciones inteligentes")

        # Usar servicio de búsqueda inteligente
        busqueda_service = BusquedaInteligenteService(db)

        resultado = busqueda_service.buscar_con_combinaciones(
            area_min=area_min,
            area_max=area_max,
            tipo_inmueble_id=filtros_gen.get("tipo_inmueble_id"),
            distrito_ids=filtros_gen.get("distrito_ids"),
            transaccion=filtros_gen.get("transaccion"),
            precio_max=precio_max,
            limit=busqueda.limit * 2,
            usuario_id=current_user.usuario_id
        )

        # Combinar individuales y combinaciones
        items_totales = resultado["individuales"] + resultado["combinaciones"]

        # Ordenar por relevancia
        items_totales.sort(key=lambda x: (
            0 if x.get("tipo") != "combinacion" else 1,
            -x.get("area_total", x.get("area", 0))
        ))

        # Paginar
        total = len(items_totales)
        inicio = (busqueda.page - 1) * busqueda.limit
        fin = inicio + busqueda.limit
        items_paginados = items_totales[inicio:fin]

        print(f"✅ [DEBUG] Búsqueda inteligente autenticada: {len(resultado['individuales'])} individuales, {len(resultado['combinaciones'])} combinaciones")

        return {
            "success": True,
            "data": items_paginados,
            "pagination": {
                "page": busqueda.page,
                "limit": busqueda.limit,
                "total": total,
                "total_pages": (total + busqueda.limit - 1) // busqueda.limit
            },
            "metadata": {
                "individuales": len(resultado["individuales"]),
                "combinaciones": len(resultado["combinaciones"]),
                "incluir_combinaciones": True
            }
        }

    # LÓGICA TRADICIONAL (sin combinaciones)
    print("📌 [DEBUG] Búsqueda autenticada tradicional (sin combinaciones)")

    # Query base - solo propiedades publicadas + eager load propietario (LEFT JOIN)
    query = db.query(Propiedad).options(
        joinedload(Propiedad.propietario, innerjoin=False)
    ).filter(Propiedad.estado == "publicado")

    # ============================================
    # 1️⃣ FILTROS GENÉRICOS (registro_x_inmueble_cab)
    # ============================================

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

    # Área (±15%)
    if area_min is not None and area_max is not None:
        query = query.filter(Propiedad.area >= area_min, Propiedad.area <= area_max)

    # Precio (±15%) - según transacción
    if filtros_bas.get("precio"):
        precio_objetivo = float(filtros_bas["precio"])
        margen = precio_objetivo * 0.15
        precio_min = precio_objetivo - margen
        precio_max_query = precio_objetivo + margen

        transaccion = filtros_gen.get("transaccion", "venta")
        if transaccion == "alquiler":
            query = query.filter(
                Propiedad.precio_alquiler >= precio_min,
                Propiedad.precio_alquiler <= precio_max_query
            )
        else:
            query = query.filter(
                Propiedad.precio_venta >= precio_min,
                Propiedad.precio_venta <= precio_max_query
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
            tipo_inmueble_id=prop.tipo_inmueble_id,
            distrito=distrito.nombre if distrito else "N/A",
            direccion=prop.direccion,
            latitud=prop.latitud,
            longitud=prop.longitud,
            telefono=prop.propietario.telefono if prop.propietario else "",
            email=prop.propietario.email if prop.propietario else "",
            propietario_nombre=prop.propietario.nombre if prop.propietario else "",
            transaccion=prop.transaccion,
            precio_alquiler=prop.precio_alquiler,
            precio_venta=prop.precio_venta,
            moneda=prop.moneda,
            area=prop.area,
            implementacion=prop.implementacion,
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


# ============================================
# 🔓 BÚSQUEDA AVANZADA PÚBLICA (Sin Autenticación)
# ============================================

@router.post("/buscar-avanzada-publica")
async def buscar_propiedades_avanzada_publica(
    busqueda: BusquedaAvanzadaRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    🔍 Búsqueda Avanzada Pública con Combinaciones Inteligentes (NO requiere Token)

    Endpoint para usuarios invitados (no autenticados).
    Misma funcionalidad que /buscar-avanzada pero sin favoritos.
    """
    filtros_gen = busqueda.filtros_genericos or {}
    filtros_bas = busqueda.filtros_basicos or {}

    # Calcular área con ±15% si se especifica
    area_min = None
    area_max = None
    if filtros_bas.get("area"):
        area_objetivo = float(filtros_bas["area"])
        margen = area_objetivo * 0.15
        area_min = area_objetivo - margen
        area_max = area_objetivo + margen

    # Calcular precio con ±15% si se especifica
    precio_max = None
    if filtros_bas.get("precio"):
        precio_objetivo = float(filtros_bas["precio"])
        margen = precio_objetivo * 0.15
        precio_max = precio_objetivo + margen

    # Verificar si se debe usar búsqueda inteligente con combinaciones
    usar_inteligente = (
        busqueda.incluir_combinaciones
        and area_min is not None
        and filtros_gen.get("tipo_inmueble_id") == 1  # Solo oficinas
        and not busqueda.filtros_avanzados
    )

    if usar_inteligente:
        print("🔥 [DEBUG] Búsqueda PÚBLICA CON combinaciones inteligentes")

        busqueda_service = BusquedaInteligenteService(db)

        resultado = busqueda_service.buscar_con_combinaciones(
            area_min=area_min,
            area_max=area_max,
            tipo_inmueble_id=filtros_gen.get("tipo_inmueble_id"),
            distrito_ids=filtros_gen.get("distrito_ids"),
            transaccion=filtros_gen.get("transaccion"),
            precio_max=precio_max,
            limit=busqueda.limit * 2,
            usuario_id=None  # Sin usuario (público)
        )

        # Combinar individuales y combinaciones
        items_totales = resultado["individuales"] + resultado["combinaciones"]

        # Ordenar por relevancia
        items_totales.sort(key=lambda x: (
            0 if x.get("tipo") != "combinacion" else 1,
            -x.get("area_total", x.get("area", 0))
        ))

        # Paginar
        total = len(items_totales)
        inicio = (busqueda.page - 1) * busqueda.limit
        fin = inicio + busqueda.limit
        items_paginados = items_totales[inicio:fin]

        print(f"✅ [DEBUG] Búsqueda pública: {len(resultado['individuales'])} individuales, {len(resultado['combinaciones'])} combinaciones")

        return {
            "success": True,
            "data": items_paginados,
            "pagination": {
                "page": busqueda.page,
                "limit": busqueda.limit,
                "total": total,
                "total_pages": (total + busqueda.limit - 1) // busqueda.limit
            },
            "metadata": {
                "individuales": len(resultado["individuales"]),
                "combinaciones": len(resultado["combinaciones"]),
                "incluir_combinaciones": True
            }
        }

    # LÓGICA TRADICIONAL (sin combinaciones)
    print("📌 [DEBUG] Búsqueda pública tradicional (sin combinaciones)")

    query = db.query(Propiedad).options(
        joinedload(Propiedad.propietario, innerjoin=False)
    ).filter(Propiedad.estado == "publicado")

    # Filtros genéricos
    if filtros_gen.get("tipo_inmueble_id"):
        query = query.filter(Propiedad.tipo_inmueble_id == filtros_gen["tipo_inmueble_id"])

    if filtros_gen.get("distrito_ids") and len(filtros_gen["distrito_ids"]) > 0:
        query = query.filter(Propiedad.distrito_id.in_(filtros_gen["distrito_ids"]))

    if filtros_gen.get("transaccion"):
        query = query.filter(Propiedad.transaccion.in_([filtros_gen["transaccion"], "ambos"]))

    # Filtros básicos
    if area_min is not None and area_max is not None:
        query = query.filter(Propiedad.area >= area_min, Propiedad.area <= area_max)

    if filtros_bas.get("precio"):
        precio_objetivo = float(filtros_bas["precio"])
        margen = precio_objetivo * 0.15
        precio_min = precio_objetivo - margen
        precio_max_query = precio_objetivo + margen

        transaccion = filtros_gen.get("transaccion", "venta")
        if transaccion == "alquiler":
            query = query.filter(
                Propiedad.precio_alquiler >= precio_min,
                Propiedad.precio_alquiler <= precio_max_query
            )
        else:
            query = query.filter(
                Propiedad.precio_venta >= precio_min,
                Propiedad.precio_venta <= precio_max_query
            )

    # Filtros avanzados
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

    # Paginación
    total = query.count()
    query = query.order_by(Propiedad.created_at.desc())
    offset = (busqueda.page - 1) * busqueda.limit
    propiedades = query.offset(offset).limit(busqueda.limit).all()

    # Formatear respuesta (sin favoritos)
    propiedades_list = []
    for prop in propiedades:
        tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == prop.tipo_inmueble_id).first()
        distrito = db.query(Distrito).filter(Distrito.distrito_id == prop.distrito_id).first()

        propiedades_list.append(PropiedadResponse(
            registro_cab_id=prop.registro_cab_id,
            titulo=prop.titulo,
            tipo_inmueble=tipo.nombre if tipo else "N/A",
            tipo_inmueble_id=prop.tipo_inmueble_id,
            distrito=distrito.nombre if distrito else "N/A",
            direccion=prop.direccion,
            latitud=prop.latitud,
            longitud=prop.longitud,
            telefono=prop.propietario.telefono if prop.propietario else "",
            email=prop.propietario.email if prop.propietario else "",
            propietario_nombre=prop.propietario.nombre if prop.propietario else "",
            transaccion=prop.transaccion,
            precio_alquiler=prop.precio_alquiler,
            precio_venta=prop.precio_venta,
            moneda=prop.moneda,
            area=prop.area,
            implementacion=prop.implementacion,
            imagen_principal=prop.imagen_principal,
            imagenes=prop.imagenes or [],
            estado=prop.estado,
            estado_crm=prop.estado_crm,
            vistas=prop.vistas,
            contactos=prop.contactos,
            created_at=prop.created_at,
            es_favorito=False  # Siempre False para usuarios no autenticados
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


# ============================================
# 🏢 GENERACIÓN MASIVA DE OFICINAS
# ============================================



@router.post("/generar-oficinas-masivo", response_model=ResponseModel[GenerarOficinasResponse])
async def generar_oficinas_masivo(
    request: GenerarOficinasRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_ofertante)
):
    """
    🏢 Generar oficinas masivamente para un edificio

    Crea múltiples oficinas en un solo paso basado en una plantilla:
    - Piso desde/hasta: Rango de pisos
    - Plantilla: Configuración de oficinas por piso (sufijo, área, características)

    Todas las oficinas se crean en estado "borrador" para edición posterior.
    """
    # Validar que el edificio padre existe
    edificio = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == request.edificio_id
    ).first()

    if not edificio:
        raise NotFoundException("Edificio padre no encontrado")

    # Validar que el propietario existe
    propietario = db.query(Propietario).filter(
        Propietario.propietario_id == request.propietario_id
    ).first()

    if not propietario:
        raise NotFoundException("Propietario no encontrado")

    # Validar rango de pisos
    if request.piso_desde > request.piso_hasta:
        raise BadRequestException("El piso inicial no puede ser mayor al piso final")

    # Buscar característica "Piso" y "Número de Oficina"
    caract_piso = db.query(Caracteristica).filter(
        Caracteristica.nombre == "Piso"
    ).first()

    caract_numero = db.query(Caracteristica).filter(
        Caracteristica.nombre == "Número de Oficina"
    ).first()

    try:
        oficinas_creadas = []
        total_oficinas = 0

        # Iterar por cada piso
        for piso_num in range(request.piso_desde, request.piso_hasta + 1):
            # Iterar por cada plantilla de oficina
            for plantilla in request.plantilla_oficinas:
                # Generar nombre: "Oficina {PISO}{SUFIJO}"
                nombre_oficina = f"Oficina {piso_num}{plantilla.sufijo}"

                # Crear registro en CAB
                nueva_oficina = Propiedad(
                    usuario_id=current_user.usuario_id,
                    propietario_id=request.propietario_id,
                    padre_registro_cab_id=request.edificio_id,  # 🔥 Recursividad
                    tipo_inmueble_id=edificio.tipo_inmueble_id,  # Mismo tipo que edificio
                    distrito_id=request.distrito_id,
                    nombre_inmueble=nombre_oficina,
                    direccion=edificio.direccion,  # Heredar dirección del edificio
                    latitud=edificio.latitud,
                    longitud=edificio.longitud,
                    area=plantilla.area,
                    antiguedad=edificio.antiguedad,  # Heredar antigüedad
                    transaccion=request.transaccion,
                    precio_alquiler=request.precio_alquiler_base,
                    precio_venta=request.precio_venta_base,
                    moneda=request.moneda,
                    titulo=f"{nombre_oficina} - {edificio.nombre_inmueble}",
                    descripcion=f"Oficina en {edificio.nombre_inmueble}, Piso {piso_num}",
                    estado="borrador",  # 🔥 Siempre borrador para edición posterior
                    created_by=current_user.usuario_id
                )

                db.add(nueva_oficina)
                db.flush()  # Para obtener el ID generado

                # Agregar característica "Piso" a DET
                if caract_piso:
                    det_piso = PropiedadDetalle(
                        registro_cab_id=nueva_oficina.registro_cab_id,
                        caracteristica_id=caract_piso.caracteristica_id,
                        valor=str(piso_num)
                    )
                    db.add(det_piso)

                # Agregar característica "Número de Oficina" a DET
                if caract_numero:
                    det_numero = PropiedadDetalle(
                        registro_cab_id=nueva_oficina.registro_cab_id,
                        caracteristica_id=caract_numero.caracteristica_id,
                        valor=plantilla.sufijo
                    )
                    db.add(det_numero)

                # Agregar características personalizadas de la plantilla
                for caract_plantilla in plantilla.caracteristicas:
                    det_custom = PropiedadDetalle(
                        registro_cab_id=nueva_oficina.registro_cab_id,
                        caracteristica_id=caract_plantilla.caracteristica_id,
                        valor=caract_plantilla.valor
                    )
                    db.add(det_custom)

                # Agregar a la lista de respuesta
                oficinas_creadas.append(OficinaGenerada(
                    registro_cab_id=nueva_oficina.registro_cab_id,
                    nombre_inmueble=nombre_oficina,
                    piso=piso_num,
                    area=plantilla.area
                ))

                total_oficinas += 1

        # Commit final
        db.commit()

        return ResponseModel(
            success=True,
            message=f"Se generaron {total_oficinas} oficinas exitosamente",
            data=GenerarOficinasResponse(
                oficinas_creadas=total_oficinas,
                edificio_padre=edificio.nombre_inmueble,
                detalles=oficinas_creadas
            )
        )

    except Exception as e:
        db.rollback()
        raise BadRequestException(f"Error al generar oficinas: {str(e)}")




# ============================================
# 👤 ASIGNACIÓN DE CORREDOR
# ============================================

class AsignarCorredorRequest(BaseModel):
    corredor_id: int
    estado_crm: Optional[str] = None
    comision: Optional[float] = None


@router.patch("/{propiedad_id}/asignar-corredor", response_model=ResponseModel[dict])
async def asignar_corredor(
    propiedad_id: int,
    data: AsignarCorredorRequest,
    current_user: Usuario = Depends(require_ofertante),
    db: Session = Depends(get_db)
):
    """
    👤 Asignar corredor a una propiedad

    Solo usuarios con perfil de ofertante o admin pueden asignar corredores.

    Body:
    {
        "corredor_id": 123,
        "estado_crm": "contactado",  // opcional
        "comision": 5.5  // opcional, porcentaje
    }
    """
    # Validar que la propiedad existe
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()

    if not propiedad:
        raise NotFoundException("Propiedad no encontrada")

    # Verificar permisos: Admin puede asignar a cualquier propiedad
    # Ofertante solo puede asignar corredor a sus propias propiedades
    if current_user.perfil_id != 4 and propiedad.usuario_id != current_user.usuario_id:
        raise ForbiddenException("No tienes permiso para asignar corredor a esta propiedad")

    # Validar que el corredor existe y tiene perfil de corredor (perfil_id = 3)
    corredor = db.query(Usuario).filter(
        Usuario.usuario_id == data.corredor_id,
        Usuario.perfil_id == 3  # Perfil de corredor
    ).first()

    if not corredor:
        raise NotFoundException("Corredor no encontrado o no tiene perfil de corredor")

    # Asignar corredor
    propiedad.corredor_asignado_id = data.corredor_id

    # Actualizar estado CRM si se proporciona
    if data.estado_crm:
        # Validar que el estado es válido
        estados_validos = ['lead', 'contactado', 'visita_programada', 'negociacion',
                          'cerrado_ganado', 'cerrado_perdido', 'nuevo_lead',
                          'en_negociacion', 'calificado', 'propuesta_enviada']
        if data.estado_crm not in estados_validos:
            raise BadRequestException(f"Estado CRM inválido. Estados válidos: {', '.join(estados_validos)}")
        propiedad.estado_crm = data.estado_crm

    # Actualizar comisión si se proporciona
    if data.comision is not None:
        if data.comision < 0 or data.comision > 100:
            raise BadRequestException("La comisión debe estar entre 0 y 100%")
        propiedad.comision_corredor = data.comision

    db.commit()
    db.refresh(propiedad)

    return ResponseModel(
        success=True,
        message=f"Corredor {corredor.nombre} {corredor.apellido} asignado exitosamente",
        data={
            "registro_cab_id": propiedad.registro_cab_id,
            "corredor_asignado_id": propiedad.corredor_asignado_id,
            "corredor_nombre": f"{corredor.nombre} {corredor.apellido}",
            "estado_crm": propiedad.estado_crm,
            "comision_corredor": float(propiedad.comision_corredor) if propiedad.comision_corredor else None
        }
    )

# ============================================
# 🔄 ACTUALIZAR CORREDOR Y COMISIÓN
# ============================================

class ActualizarCorredorRequest(BaseModel):
    corredor_asignado_id: Optional[int] = None
    comision_corredor: Optional[Decimal] = None

@router.put("/{propiedad_id}/corredor", response_model=ResponseModel[dict])
async def actualizar_corredor_comision(
    propiedad_id: int,
    data: ActualizarCorredorRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    🔄 Actualizar corredor asignado y/o comisión de una propiedad
    
    **Permite:**
    - Actualizar solo el corredor
    - Actualizar solo la comisión
    - Actualizar ambos
    - Remover corredor (enviando null)
    
    **Permisos:**
    - Admin puede actualizar cualquier propiedad
    - Ofertante solo puede actualizar sus propias propiedades
    """
    # 1. Buscar propiedad
    propiedad = db.query(Propiedad).filter(
        Propiedad.registro_cab_id == propiedad_id
    ).first()
    
    if not propiedad:
        raise NotFoundException(f"Propiedad {propiedad_id} no encontrada")
    
    # 2. Verificar permisos
    if current_user.perfil_id != 4 and propiedad.usuario_id != current_user.usuario_id:
        raise ForbiddenException("No tienes permiso para modificar esta propiedad")
    
    # 3. Validar corredor si se proporciona
    corredor = None
    if data.corredor_asignado_id is not None:
        corredor = db.query(Usuario).filter(
            Usuario.usuario_id == data.corredor_asignado_id,
            Usuario.perfil_id == 2  # Perfil corredor
        ).first()
        
        if not corredor:
            raise BadRequestException(f"Corredor {data.corredor_asignado_id} no encontrado o no tiene perfil de corredor")
    
    # 4. Actualizar campos
    cambios = []
    
    if data.corredor_asignado_id is not None:
        propiedad.corredor_asignado_id = data.corredor_asignado_id
        if corredor:
            cambios.append(f"Corredor asignado: {corredor.nombre} {corredor.apellido}")
        else:
            cambios.append("Corredor removido")
    
    if data.comision_corredor is not None:
        propiedad.comision_corredor = data.comision_corredor
        cambios.append(f"Comisión actualizada: {float(data.comision_corredor)}%")
    
    if not cambios:
        raise BadRequestException("Debe proporcionar al menos un campo para actualizar")
    
    propiedad.updated_by = current_user.usuario_id
    db.commit()
    db.refresh(propiedad)
    
    # 5. Preparar respuesta
    corredor_nombre = None
    if propiedad.corredor_asignado_id:
        corredor_actual = db.query(Usuario).filter(
            Usuario.usuario_id == propiedad.corredor_asignado_id
        ).first()
        if corredor_actual:
            corredor_nombre = f"{corredor_actual.nombre} {corredor_actual.apellido}"
    
    return ResponseModel(
        success=True,
        message=f"Propiedad actualizada: {', '.join(cambios)}",
        data={
            "registro_cab_id": propiedad.registro_cab_id,
            "corredor_asignado_id": propiedad.corredor_asignado_id,
            "corredor_nombre": corredor_nombre,
            "comision_corredor": float(propiedad.comision_corredor) if propiedad.comision_corredor else None,
            "cambios": cambios
        }
    )
