from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, CheckConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Busqueda(Base):
    """Modelo de Búsqueda"""
    __tablename__ = "busqueda_x_inmueble_mov"
    __table_args__ = (
        CheckConstraint("frecuencia_alerta IN ('inmediata', 'diaria', 'semanal')", name="check_frecuencia_alerta"),
        {'extend_existing': True}
    )
    
    busqueda_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    sesion_id = Column(String(100))
    
    # JSON completo de criterios
    criterios_json = Column(JSON, nullable=False)
    
    # Resultados
    cantidad_resultados = Column(Integer, default=0)
    
    # Búsqueda guardada (alertas)
    es_guardada = Column(Boolean, default=False)
    nombre_busqueda = Column(String(100))
    frecuencia_alerta = Column(String(20))
    alerta_activa = Column(Boolean, default=False)
    ultima_notificacion = Column(TIMESTAMP)
    total_notificaciones = Column(Integer, default=0)
    
    # Auditoría
    fecha_busqueda = Column(TIMESTAMP, server_default=func.now())
    ip_address = Column(String(45))
    
    # Relationships
    usuario = relationship("Usuario", backref="busquedas")
    
    def generar_descripcion_legible(self, db):
        """Genera descripción legible de la búsqueda desde criterios_json"""
        from app.models.tipo_inmueble import TipoInmueble
        from app.models.distrito import Distrito
        
        partes = []
        criterios = self.criterios_json or {}
        
        # Tipo de búsqueda
        tipo_busqueda = criterios.get('tipo', 'generica')
        partes.append(f"[{tipo_busqueda.upper()}]")
        
        # Tipo de inmueble
        if criterios.get('tipo_inmueble_id'):
            tipo = db.query(TipoInmueble).filter(TipoInmueble.tipo_inmueble_id == criterios['tipo_inmueble_id']).first()
            if tipo:
                partes.append(tipo.nombre)
        
        # Distritos
        if criterios.get('distritos_ids'):
            distritos = db.query(Distrito).filter(Distrito.distrito_id.in_(criterios['distritos_ids'])).all()
            if distritos:
                nombres = [d.nombre for d in distritos[:3]]  # Máximo 3
                if len(distritos) > 3:
                    nombres.append(f"+{len(distritos)-3} más")
                partes.append(f"en {', '.join(nombres)}")
        
        # Transacción
        if criterios.get('transaccion'):
            partes.append(f"para {criterios['transaccion']}")
        
        # Área/Metraje
        if criterios.get('metraje'):
            partes.append(f"~{criterios['metraje']} m²")
        elif criterios.get('area_min') or criterios.get('area_max'):
            if criterios.get('area_min') and criterios.get('area_max'):
                partes.append(f"{criterios['area_min']}-{criterios['area_max']} m²")
            elif criterios.get('area_min'):
                partes.append(f"desde {criterios['area_min']} m²")
            elif criterios.get('area_max'):
                partes.append(f"hasta {criterios['area_max']} m²")
        
        # Presupuesto
        if criterios.get('presupuesto'):
            partes.append(f"~${criterios['presupuesto']:,.0f}")
        elif criterios.get('presupuesto_min') or criterios.get('presupuesto_max'):
            if criterios.get('presupuesto_min') and criterios.get('presupuesto_max'):
                partes.append(f"${criterios['presupuesto_min']:,.0f}-${criterios['presupuesto_max']:,.0f}")
            elif criterios.get('presupuesto_min'):
                partes.append(f"desde ${criterios['presupuesto_min']:,.0f}")
            elif criterios.get('presupuesto_max'):
                partes.append(f"hasta ${criterios['presupuesto_max']:,.0f}")
        
        # Parqueos
        if criterios.get('parqueos_min'):
            partes.append(f"mín. {criterios['parqueos_min']} parqueos")
        
        # Implementación
        if criterios.get('implementacion'):
            partes.append(f"({criterios['implementacion']})")
        
        return " ".join(partes) if partes else "Búsqueda sin filtros específicos"
    
    def generar_codigo(self):
        """Genera código único de búsqueda"""
        from datetime import datetime
        fecha = datetime.now().strftime("%Y%m%d")
        return f"BUS-{fecha}-{self.busqueda_id:06d}"
    
    def __repr__(self):
        return f"<Busqueda {self.busqueda_id}>"
