"""
📊 API de Dashboard - Estadísticas Dinámicas COMPLETAS
Sistema Inmobiliario - Endpoint único adaptable a todos los perfiles
Incluye: Búsquedas, Favoritos, Propiedades, Estado CRM
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from typing import Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user
from app.models.busqueda import Busqueda
from app.models.propiedad import Propiedad
from app.models.favorito import Favorito
from app.models.usuario import Usuario
from app.models.tipo_inmueble import TipoInmueble
from app.models.distrito import Distrito
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/estadisticas")
async def obtener_estadisticas_dashboard(
    anio: Optional[int] = Query(None, description="Filtrar por año"),
    mes: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mes (1-12)"),
    usuario_id: Optional[int] = Query(None, description="[ADMIN ONLY] Ver stats de usuario específico"),
    perfil_id: Optional[int] = Query(None, ge=1, le=4, description="[ADMIN ONLY] Filtrar por tipo de perfil"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    📊 Obtener estadísticas COMPLETAS para el dashboard

    **Dinámico según perfil del usuario:**
    - **Admin (perfil_id=4)**: Puede ver TODAS las stats o filtrar por usuario/perfil
    - **Demandante (perfil_id=1)**: Sus búsquedas y favoritos
    - **Ofertante (perfil_id=2)**: Sus propiedades publicadas + estado CRM
    - **Corredor (perfil_id=3)**: Sus propiedades y pipeline CRM

    **Datos incluidos:**
    - Búsquedas: por tipo, distrito, mes
    - Favoritos: por tipo, distrito, mes
    - Propiedades: por tipo, distrito, estado, estado_crm, mes
    - Métricas: vistas, contactos, compartidos
    """
    try:
        # Determinar si es Admin
        es_admin = current_user.perfil_id == 4

        # Si no es admin e intenta ver datos de otro usuario → ERROR
        if not es_admin and usuario_id and usuario_id != current_user.usuario_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para ver estadísticas de otros usuarios"
            )

        # Determinar el usuario objetivo
        target_user_id = usuario_id if es_admin and usuario_id else current_user.usuario_id

        # Si es admin sin usuario_id específico → stats globales
        mostrar_global = es_admin and not usuario_id

        # Fecha actual para defaults
        now = datetime.now()
        filtro_anio = anio if anio else now.year

        # Usuario IDs para filtrado de perfil (admin)
        user_ids = []
        if mostrar_global and perfil_id:
            usuarios_perfil = db.query(Usuario.usuario_id).filter(Usuario.perfil_id == perfil_id).all()
            user_ids = [u[0] for u in usuarios_perfil]

        logger.info(f"📊 Dashboard - User: {current_user.usuario_id}, Perfil: {current_user.perfil_id}, Target: {target_user_id}, Global: {mostrar_global}")

        resultado = {
            "perfil_id": current_user.perfil_id,
            "perfil_nombre": {1: "Demandante", 2: "Ofertante", 3: "Corredor", 4: "Administrador"}[current_user.perfil_id],
            "usuario_id": target_user_id,
            "es_global": mostrar_global,
            "filtros": {
                "anio": filtro_anio,
                "mes": mes,
                "perfil_id": perfil_id
            },
            "busquedas": {},
            "favoritos": {},
            "propiedades": {},
            "resumen": {}
        }

        # ============================================
        # 🔍 BÚSQUEDAS (Demandante + Admin)
        # ============================================
        if current_user.perfil_id in [1, 4]:
            query_busquedas = db.query(Busqueda).filter(
                extract('year', Busqueda.fecha_busqueda) == filtro_anio
            )

            if mes:
                query_busquedas = query_busquedas.filter(
                    extract('month', Busqueda.fecha_busqueda) == mes
                )

            # Aplicar filtros de usuario
            if not mostrar_global:
                query_busquedas = query_busquedas.filter(Busqueda.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                query_busquedas = query_busquedas.filter(Busqueda.usuario_id.in_(user_ids))

            total_busquedas = query_busquedas.count()
            busquedas_all = query_busquedas.all()

            # Por tipo de inmueble
            busquedas_por_tipo = {}
            for busqueda in busquedas_all:
                criterios = busqueda.criterios_json or {}
                tipo_id = criterios.get('tipo_inmueble_id')
                if tipo_id:
                    tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == tipo_id).first()
                    tipo_nombre = tipo.nombre if tipo else "Otro"
                else:
                    tipo_nombre = "Todos los tipos"
                busquedas_por_tipo[tipo_nombre] = busquedas_por_tipo.get(tipo_nombre, 0) + 1

            # Por distrito
            busquedas_por_distrito = {}
            for busqueda in busquedas_all:
                criterios = busqueda.criterios_json or {}
                distrito_id = criterios.get('distrito_id')
                if distrito_id:
                    distrito = db.query(Distrito).filter(Distrito.distrito_id == distrito_id).first()
                    distrito_nombre = distrito.nombre if distrito else "Otro"
                else:
                    distrito_nombre = "Todos los distritos"
                busquedas_por_distrito[distrito_nombre] = busquedas_por_distrito.get(distrito_nombre, 0) + 1

            # Por mes
            busquedas_mes_query = db.query(
                extract('month', Busqueda.fecha_busqueda).label('mes'),
                func.count(Busqueda.busqueda_id).label('cantidad')
            ).filter(extract('year', Busqueda.fecha_busqueda) == filtro_anio)

            if not mostrar_global:
                busquedas_mes_query = busquedas_mes_query.filter(Busqueda.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                busquedas_mes_query = busquedas_mes_query.filter(Busqueda.usuario_id.in_(user_ids))

            busquedas_por_mes = {int(r.mes): r.cantidad for r in busquedas_mes_query.group_by('mes').all()}

            resultado["busquedas"] = {
                "total": total_busquedas,
                "por_tipo_inmueble": busquedas_por_tipo,
                "por_distrito": busquedas_por_distrito,
                "por_mes": busquedas_por_mes
            }

        # ============================================
        # ❤️ FAVORITOS (Demandante + Admin)
        # ============================================
        if current_user.perfil_id in [1, 4]:
            query_fav = db.query(Favorito).filter(
                extract('year', Favorito.fecha_agregado) == filtro_anio
            )

            if mes:
                query_fav = query_fav.filter(extract('month', Favorito.fecha_agregado) == mes)

            if not mostrar_global:
                query_fav = query_fav.filter(Favorito.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                query_fav = query_fav.filter(Favorito.usuario_id.in_(user_ids))

            total_favoritos = query_fav.count()

            # Por tipo
            fav_tipo = db.query(
                TipoInmueble.nombre,
                func.count(Favorito.favorito_id).label('cantidad')
            ).join(Propiedad, Propiedad.registro_cab_id == Favorito.registro_cab_id
            ).join(TipoInmueble
            ).filter(extract('year', Favorito.fecha_agregado) == filtro_anio)

            if mes:
                fav_tipo = fav_tipo.filter(extract('month', Favorito.fecha_agregado) == mes)
            if not mostrar_global:
                fav_tipo = fav_tipo.filter(Favorito.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                fav_tipo = fav_tipo.filter(Favorito.usuario_id.in_(user_ids))

            favoritos_por_tipo = {r.nombre: r.cantidad for r in fav_tipo.group_by(TipoInmueble.nombre).all()}

            # Por distrito
            fav_dist = db.query(
                Distrito.nombre,
                func.count(Favorito.favorito_id).label('cantidad')
            ).join(Propiedad, Propiedad.registro_cab_id == Favorito.registro_cab_id
            ).join(Distrito
            ).filter(extract('year', Favorito.fecha_agregado) == filtro_anio)

            if mes:
                fav_dist = fav_dist.filter(extract('month', Favorito.fecha_agregado) == mes)
            if not mostrar_global:
                fav_dist = fav_dist.filter(Favorito.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                fav_dist = fav_dist.filter(Favorito.usuario_id.in_(user_ids))

            favoritos_por_distrito = {r.nombre: r.cantidad for r in fav_dist.group_by(Distrito.nombre).all()}

            # Por mes
            fav_mes = db.query(
                extract('month', Favorito.fecha_agregado).label('mes'),
                func.count(Favorito.favorito_id).label('cantidad')
            ).filter(extract('year', Favorito.fecha_agregado) == filtro_anio)

            if not mostrar_global:
                fav_mes = fav_mes.filter(Favorito.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                fav_mes = fav_mes.filter(Favorito.usuario_id.in_(user_ids))

            favoritos_por_mes = {int(r.mes): r.cantidad for r in fav_mes.group_by('mes').all()}

            resultado["favoritos"] = {
                "total": total_favoritos,
                "por_tipo_inmueble": favoritos_por_tipo,
                "por_distrito": favoritos_por_distrito,
                "por_mes": favoritos_por_mes
            }

        # ============================================
        # 🏢 PROPIEDADES (Ofertante + Corredor + Admin)
        # ============================================
        if current_user.perfil_id in [2, 3, 4]:
            query_prop = db.query(Propiedad).filter(
                extract('year', Propiedad.created_at) == filtro_anio
            )

            if mes:
                query_prop = query_prop.filter(extract('month', Propiedad.created_at) == mes)

            if not mostrar_global:
                query_prop = query_prop.filter(Propiedad.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                query_prop = query_prop.filter(Propiedad.usuario_id.in_(user_ids))

            total_propiedades = query_prop.count()

            # Por estado
            prop_estado = db.query(
                Propiedad.estado,
                func.count(Propiedad.registro_cab_id).label('cantidad')
            ).filter(extract('year', Propiedad.created_at) == filtro_anio)

            if mes:
                prop_estado = prop_estado.filter(extract('month', Propiedad.created_at) == mes)
            if not mostrar_global:
                prop_estado = prop_estado.filter(Propiedad.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                prop_estado = prop_estado.filter(Propiedad.usuario_id.in_(user_ids))

            propiedades_por_estado = {r.estado: r.cantidad for r in prop_estado.group_by(Propiedad.estado).all()}

            # 🔥 Por estado CRM (BRUTAL para pipeline de ventas)
            prop_crm = db.query(
                Propiedad.estado_crm,
                func.count(Propiedad.registro_cab_id).label('cantidad')
            ).filter(extract('year', Propiedad.created_at) == filtro_anio)

            if mes:
                prop_crm = prop_crm.filter(extract('month', Propiedad.created_at) == mes)
            if not mostrar_global:
                prop_crm = prop_crm.filter(Propiedad.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                prop_crm = prop_crm.filter(Propiedad.usuario_id.in_(user_ids))

            propiedades_por_estado_crm = {r.estado_crm: r.cantidad for r in prop_crm.group_by(Propiedad.estado_crm).all()}

            # Por tipo
            prop_tipo = db.query(
                TipoInmueble.nombre,
                func.count(Propiedad.registro_cab_id).label('cantidad')
            ).join(TipoInmueble
            ).filter(extract('year', Propiedad.created_at) == filtro_anio)

            if mes:
                prop_tipo = prop_tipo.filter(extract('month', Propiedad.created_at) == mes)
            if not mostrar_global:
                prop_tipo = prop_tipo.filter(Propiedad.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                prop_tipo = prop_tipo.filter(Propiedad.usuario_id.in_(user_ids))

            propiedades_por_tipo = {r.nombre: r.cantidad for r in prop_tipo.group_by(TipoInmueble.nombre).all()}

            # Por distrito
            prop_dist = db.query(
                Distrito.nombre,
                func.count(Propiedad.registro_cab_id).label('cantidad')
            ).join(Distrito
            ).filter(extract('year', Propiedad.created_at) == filtro_anio)

            if mes:
                prop_dist = prop_dist.filter(extract('month', Propiedad.created_at) == mes)
            if not mostrar_global:
                prop_dist = prop_dist.filter(Propiedad.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                prop_dist = prop_dist.filter(Propiedad.usuario_id.in_(user_ids))

            propiedades_por_distrito = {r.nombre: r.cantidad for r in prop_dist.group_by(Distrito.nombre).all()}

            # Métricas
            total_vistas = query_prop.with_entities(func.sum(Propiedad.vistas)).scalar() or 0
            total_contactos = query_prop.with_entities(func.sum(Propiedad.contactos)).scalar() or 0
            total_compartidos = query_prop.with_entities(func.sum(Propiedad.compartidos)).scalar() or 0

            # Por mes
            prop_mes = db.query(
                extract('month', Propiedad.created_at).label('mes'),
                func.count(Propiedad.registro_cab_id).label('cantidad')
            ).filter(extract('year', Propiedad.created_at) == filtro_anio)

            if not mostrar_global:
                prop_mes = prop_mes.filter(Propiedad.usuario_id == target_user_id)
            elif perfil_id and user_ids:
                prop_mes = prop_mes.filter(Propiedad.usuario_id.in_(user_ids))

            propiedades_por_mes = {int(r.mes): r.cantidad for r in prop_mes.group_by('mes').all()}

            resultado["propiedades"] = {
                "total": total_propiedades,
                "por_estado": propiedades_por_estado,
                "por_estado_crm": propiedades_por_estado_crm,
                "por_tipo_inmueble": propiedades_por_tipo,
                "por_distrito": propiedades_por_distrito,
                "por_mes": propiedades_por_mes,
                "total_vistas": int(total_vistas),
                "total_contactos": int(total_contactos),
                "total_compartidos": int(total_compartidos)
            }

        # ============================================
        # 📊 RESUMEN EJECUTIVO
        # ============================================
        resultado["resumen"] = {
            "total_busquedas": resultado.get("busquedas", {}).get("total", 0),
            "total_favoritos": resultado.get("favoritos", {}).get("total", 0),
            "total_propiedades": resultado.get("propiedades", {}).get("total", 0),
            "propiedades_publicadas": resultado.get("propiedades", {}).get("por_estado", {}).get("publicado", 0),
            "total_vistas": resultado.get("propiedades", {}).get("total_vistas", 0),
            "total_contactos": resultado.get("propiedades", {}).get("total_contactos", 0),
            "total_compartidos": resultado.get("propiedades", {}).get("total_compartidos", 0),
            # CRM Pipeline
            "propiedades_lead": resultado.get("propiedades", {}).get("por_estado_crm", {}).get("lead", 0),
            "propiedades_contacto": resultado.get("propiedades", {}).get("por_estado_crm", {}).get("contacto", 0),
            "propiedades_cerrado_ganado": resultado.get("propiedades", {}).get("por_estado_crm", {}).get("cerrado_ganado", 0)
        }

        logger.info(f"✅ Stats OK - Búsquedas: {resultado['resumen']['total_busquedas']}, Favoritos: {resultado['resumen']['total_favoritos']}, Props: {resultado['resumen']['total_propiedades']}")

        return {
            "success": True,
            "data": resultado
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
