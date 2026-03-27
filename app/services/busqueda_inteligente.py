"""
🔍 Servicio de Búsqueda Inteligente con Combinaciones
Sistema Inmobiliario CUADRANTE
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from app.models.propiedad import Propiedad
from app.models.propiedad_detalle import PropiedadDetalle
from itertools import combinations as itertools_combinations
import logging

logger = logging.getLogger(__name__)


class BusquedaInteligenteService:
    """Servicio para búsquedas con combinaciones inteligentes"""

    def __init__(self, db: Session):
        self.db = db

    def buscar_con_combinaciones(
        self,
        area_min: Optional[float] = None,
        area_max: Optional[float] = None,
        tipo_inmueble_id: Optional[int] = None,
        distrito_ids: Optional[List[int]] = None,
        transaccion: Optional[str] = None,
        precio_max: Optional[float] = None,
        limit: int = 12,
        usuario_id: Optional[int] = None  # Para favoritos
    ) -> Dict[str, Any]:
        """
        Busca propiedades individuales Y combinaciones que cumplan criterios

        Args:
            area_min: Área mínima buscada
            area_max: Área máxima buscada
            tipo_inmueble_id: Filtro por tipo
            distrito_ids: Lista de IDs de distritos
            transaccion: 'venta', 'alquiler' o 'ambos'
            precio_max: Precio máximo
            limit: Límite de resultados
            usuario_id: ID del usuario (para favoritos, opcional)

        Returns:
            {
                "individuales": [...],
                "combinaciones": [...],
                "total": int
            }
        """
        logger.info(f"🔍 Búsqueda inteligente: area_min={area_min}, tipo={tipo_inmueble_id}")

        # 1. Buscar propiedades individuales que cumplan
        individuales = self._buscar_individuales(
            area_min=area_min,
            area_max=area_max,
            tipo_inmueble_id=tipo_inmueble_id,
            distrito_ids=distrito_ids,
            transaccion=transaccion,
            precio_max=precio_max,
            usuario_id=usuario_id
        )

        # 2. Buscar combinaciones (solo si hay área mínima)
        combinaciones = []
        if area_min and tipo_inmueble_id == 1:  # Solo para oficinas
            combinaciones = self._buscar_combinaciones(
                area_min=area_min,
                area_max=area_max,
                distrito_ids=distrito_ids,
                transaccion=transaccion,
                precio_max=precio_max
            )

        logger.info(f"✅ Encontradas: {len(individuales)} individuales, {len(combinaciones)} combinaciones")

        return {
            "individuales": individuales,
            "combinaciones": combinaciones,
            "total": len(individuales) + len(combinaciones)
        }

    def _buscar_individuales(
        self,
        area_min: Optional[float],
        area_max: Optional[float],
        tipo_inmueble_id: Optional[int],
        distrito_ids: Optional[List[int]],
        transaccion: Optional[str],
        precio_max: Optional[float],
        usuario_id: Optional[int]
    ) -> List[Dict]:
        """Búsqueda tradicional de propiedades individuales"""

        query = self.db.query(Propiedad).filter(
            Propiedad.estado == "publicado"
        )

        # Filtros
        if tipo_inmueble_id:
            query = query.filter(Propiedad.tipo_inmueble_id == tipo_inmueble_id)

        if distrito_ids:
            query = query.filter(Propiedad.distrito_id.in_(distrito_ids))

        if transaccion:
            query = query.filter(
                or_(
                    Propiedad.transaccion == transaccion,
                    Propiedad.transaccion == "ambos"
                )
            )

        if area_min:
            query = query.filter(Propiedad.area >= area_min)

        if area_max:
            query = query.filter(Propiedad.area <= area_max)

        if precio_max:
            if transaccion == "alquiler":
                query = query.filter(Propiedad.precio_alquiler <= precio_max)
            elif transaccion == "venta":
                query = query.filter(Propiedad.precio_venta <= precio_max)

        propiedades = query.order_by(Propiedad.created_at.desc()).all()

        # Serializar
        return [self._serializar_propiedad_individual(prop, usuario_id) for prop in propiedades]

    def _buscar_combinaciones(
        self,
        area_min: float,
        area_max: Optional[float],
        distrito_ids: Optional[List[int]],
        transaccion: Optional[str],
        precio_max: Optional[float]
    ) -> List[Dict]:
        """
        Busca combinaciones de oficinas del mismo edificio/piso
        que sumen el área mínima
        """

        # 1. Obtener oficinas candidatas (área < area_min individualmente)
        query = self.db.query(Propiedad).filter(
            Propiedad.estado == "publicado",
            Propiedad.padre_registro_cab_id.isnot(None),  # Solo oficinas (no edificios)
            Propiedad.tipo_inmueble_id == 1,  # Oficinas
            Propiedad.area < area_min  # No cumplen solas
        )

        if distrito_ids:
            query = query.filter(Propiedad.distrito_id.in_(distrito_ids))

        if transaccion:
            query = query.filter(
                or_(
                    Propiedad.transaccion == transaccion,
                    Propiedad.transaccion == "ambos"
                )
            )

        oficinas_candidatas = query.all()

        if not oficinas_candidatas:
            return []

        logger.info(f"📊 Candidatas para combinación: {len(oficinas_candidatas)} oficinas")

        # 2. Agrupar por (edificio, piso, propietario, transacción)
        grupos = {}
        for oficina in oficinas_candidatas:
            # ✅ CORREGIDO: Usar columna piso directamente, no buscar en detalles
            piso = oficina.piso if oficina.piso is not None else self._obtener_piso(oficina.registro_cab_id)
            if piso is None:
                logger.warning(f"⚠️ Oficina {oficina.registro_cab_id} sin piso, omitiendo")
                continue

            key = (
                oficina.padre_registro_cab_id,
                piso,
                oficina.propietario_id,
                oficina.transaccion
            )

            if key not in grupos:
                grupos[key] = []
            grupos[key].append(oficina)

        # 3. Encontrar combinaciones válidas
        combinaciones = []
        for key, oficinas in grupos.items():
            if len(oficinas) >= 2:  # Necesitamos al menos 2 oficinas
                combos = self._generar_combinaciones(
                    oficinas,
                    area_min,
                    area_max,
                    precio_max,
                    transaccion
                )
                combinaciones.extend(combos)

        # 4. Ordenar por área total (más cercanas al target primero)
        combinaciones.sort(key=lambda x: x["area_total"])

        return combinaciones

    def _obtener_piso(self, registro_cab_id: int) -> Optional[int]:
        """Obtiene el número de piso de una oficina"""
        detalle = self.db.query(PropiedadDetalle).filter(
            PropiedadDetalle.registro_cab_id == registro_cab_id,
            PropiedadDetalle.caracteristica_id == 112  # 112 = Piso (número de piso de la oficina)
        ).first()

        if detalle and detalle.valor:
            try:
                return int(detalle.valor)
            except:
                return None
        return None

    def _generar_combinaciones(
        self,
        oficinas: List[Propiedad],
        area_min: float,
        area_max: Optional[float],
        precio_max: Optional[float],
        transaccion: Optional[str]
    ) -> List[Dict]:
        """
        Genera todas las combinaciones posibles que cumplan criterios
        Limitado a máximo 4 oficinas por combinación para evitar explosión combinatoria
        """
        resultados = []

        # Probar combinaciones de 2, 3, 4 oficinas
        for n in range(2, min(5, len(oficinas) + 1)):
            for combo in itertools_combinations(oficinas, n):
                area_total = sum(ofi.area for ofi in combo)

                # Validar área
                if area_total < area_min:
                    continue
                if area_max and area_total > area_max:
                    continue

                # Calcular precios totales
                precio_total_venta = sum(
                    float(ofi.precio_venta) for ofi in combo
                    if ofi.precio_venta
                ) or None

                precio_total_alquiler = sum(
                    float(ofi.precio_alquiler) for ofi in combo
                    if ofi.precio_alquiler
                ) or None

                # Validar precio máximo
                if precio_max:
                    if transaccion == "alquiler" and precio_total_alquiler:
                        if precio_total_alquiler > precio_max:
                            continue
                    elif transaccion == "venta" and precio_total_venta:
                        if precio_total_venta > precio_max:
                            continue

                # Generar combinación
                # ✅ CORREGIDO: Usar columna piso directamente
                piso = combo[0].piso if combo[0].piso is not None else self._obtener_piso(combo[0].registro_cab_id)

                # Obtener coordenadas del edificio padre
                edificio = self.db.query(Propiedad).filter(
                    Propiedad.registro_cab_id == combo[0].padre_registro_cab_id
                ).first()

                resultados.append({
                    "tipo": "combinacion",
                    "cantidad_oficinas": n,
                    "area_total": float(area_total),
                    "precio_venta_total": float(precio_total_venta) if precio_total_venta else None,
                    "precio_alquiler_total": float(precio_total_alquiler) if precio_total_alquiler else None,
                    "transaccion": combo[0].transaccion,
                    "moneda": combo[0].moneda,
                    "glosa": self._generar_glosa(combo),
                    "edificio_id": combo[0].padre_registro_cab_id,
                    "edificio_nombre": edificio.titulo if edificio else None,
                    "piso": piso,
                    "distrito": combo[0].distrito.nombre if combo[0].distrito else None,
                    "distrito_id": combo[0].distrito_id,
                    "latitud": self._obtener_coordenada(edificio, combo, "latitud"),
                    "longitud": self._obtener_coordenada(edificio, combo, "longitud"),
                    "oficinas": [self._serializar_oficina_simple(ofi) for ofi in combo]
                })

        return resultados

    def _obtener_coordenada(self, edificio, combo, campo: str) -> Optional[str]:
        """Obtener coordenada: del edificio, de las oficinas, o de cualquier hermana del edificio"""
        # 1. Del edificio padre
        if edificio and getattr(edificio, campo):
            return str(getattr(edificio, campo))
        # 2. De las oficinas de la combinación
        for ofi in combo:
            val = getattr(ofi, campo, None)
            if val:
                return str(val)
        # 3. De cualquier oficina hermana del mismo edificio
        if combo[0].padre_registro_cab_id:
            hermana = self.db.query(Propiedad).filter(
                Propiedad.padre_registro_cab_id == combo[0].padre_registro_cab_id,
                getattr(Propiedad, campo).isnot(None)
            ).first()
            if hermana:
                return str(getattr(hermana, campo))
        return None

    def _generar_glosa(self, oficinas: List[Propiedad]) -> str:
        """Genera texto descriptivo de la combinación"""
        nombres = [ofi.nombre_inmueble for ofi in oficinas]
        return f"Combinación de {len(oficinas)} oficinas: {' + '.join(nombres)}"

    def _serializar_oficina_simple(self, oficina: Propiedad) -> Dict:
        """Convierte oficina a dict simplificado"""
        return {
            "registro_cab_id": oficina.registro_cab_id,
            "nombre": oficina.nombre_inmueble,
            "area": float(oficina.area),
            "precio_venta": float(oficina.precio_venta) if oficina.precio_venta else None,
            "precio_alquiler": float(oficina.precio_alquiler) if oficina.precio_alquiler else None,
            "imagen_principal": oficina.imagen_principal
        }

    def _serializar_propiedad_individual(self, prop: Propiedad, usuario_id: Optional[int]) -> Dict:
        """Convierte propiedad a dict completo"""
        # TODO: Agregar lógica de favoritos si usuario_id está presente

        # Obtener edificio padre si existe (para nombre y coordenadas)
        edificio_nombre = None
        edificio_latitud = None
        edificio_longitud = None
        edificio_direccion = None

        if prop.padre_registro_cab_id:
            edificio = self.db.query(Propiedad).filter(
                Propiedad.registro_cab_id == prop.padre_registro_cab_id
            ).first()
            if edificio:
                edificio_nombre = edificio.nombre_inmueble or edificio.titulo
                edificio_latitud = str(edificio.latitud) if edificio.latitud else None
                edificio_longitud = str(edificio.longitud) if edificio.longitud else None
                edificio_direccion = edificio.direccion

        # Usar coordenadas propias o heredar del edificio padre
        latitud = str(prop.latitud) if prop.latitud else edificio_latitud
        longitud = str(prop.longitud) if prop.longitud else edificio_longitud
        direccion = prop.direccion or edificio_direccion

        return {
            "tipo": "individual",
            "registro_cab_id": prop.registro_cab_id,
            "titulo": prop.titulo,
            "nombre_inmueble": prop.nombre_inmueble,
            "tipo_inmueble_id": prop.tipo_inmueble_id,
            "distrito": prop.distrito.nombre if prop.distrito else None,
            "distrito_id": prop.distrito_id,
            "direccion": direccion,
            "area": float(prop.area),
            "precio_venta": float(prop.precio_venta) if prop.precio_venta else None,
            "precio_alquiler": float(prop.precio_alquiler) if prop.precio_alquiler else None,
            "transaccion": prop.transaccion,
            "moneda": prop.moneda,
            "imagen_principal": prop.imagen_principal,
            "imagenes": prop.imagenes,
            "vistas": prop.vistas,
            "estado": prop.estado,
            "padre_registro_cab_id": prop.padre_registro_cab_id,
            "edificio_nombre": edificio_nombre,
            "latitud": latitud,
            "longitud": longitud
        }
