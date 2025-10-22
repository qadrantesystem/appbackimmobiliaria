# ================================================================
# 🔍 BÚSQUEDA AVANZADA - Endpoint POST con Body Estructurado
# ================================================================
# Agregar este código al final de propiedades.py después de la línea 486

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
            "area": 100,              // Aplicará ±15% → 85-115 m²
            "precio": 500000,         // Aplicará ±15% → 425000-575000
            "habitaciones": [2, 3],
            "banos": [2],
            "parqueos": 1
        },
        "filtros_avanzados": [      // Características dinámicas (registro_x_inmueble_det)
            {
                "caracteristica_id": 5,
                "valor": "Si"
            },
            {
                "caracteristica_id": 12,
                "valor": "Ascensor"
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
        else:  # venta o ambos
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

    # ============================================
    # 3️⃣ FILTROS AVANZADOS (registro_x_inmueble_det)
    # ============================================
    if busqueda.filtros_avanzados and len(busqueda.filtros_avanzados) > 0:
        for filtro_avanzado in busqueda.filtros_avanzados:
            # Subconsulta para filtrar por características dinámicas
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

    # Ordenar por fecha (más recientes primero)
    query = query.order_by(Propiedad.created_at.desc())

    # Paginación
    offset = (busqueda.page - 1) * busqueda.limit
    propiedades = query.offset(offset).limit(busqueda.limit).all()

    # Obtener IDs de favoritos del usuario autenticado
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
            imagenes=prop.imagenes or [],  # 🔥 Para carrusel
            estado=prop.estado,
            estado_crm=prop.estado_crm,
            vistas=prop.vistas,
            contactos=prop.contactos,
            created_at=prop.created_at,
            es_favorito=prop.registro_cab_id in favoritos_ids  # ⭐ FAVORITO
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
