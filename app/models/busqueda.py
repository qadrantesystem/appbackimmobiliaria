from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey, CheckConstraint, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Busqueda(Base):
    """Modelo de Búsqueda"""
    __tablename__ = "busqueda_x_inmueble_mov"
    
    busqueda_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    sesion_id = Column(String(100))
    
    # Criterios de búsqueda
    tipo_inmueble_id = Column(Integer, ForeignKey("tipo_inmueble_mae.tipo_inmueble_id"))
    distritos_ids = Column(ARRAY(Integer))
    transaccion = Column(String(20))
    precio_min = Column(DECIMAL(12, 2))
    precio_max = Column(DECIMAL(12, 2))
    area_min = Column(DECIMAL(10, 2))
    area_max = Column(DECIMAL(10, 2))
    habitaciones = Column(ARRAY(Integer))
    banos = Column(ARRAY(Integer))
    parqueos_min = Column(Integer)
    antiguedad_max = Column(Integer)
    implementacion = Column(String(50))
    filtros_avanzados = Column(JSON)
    
    # Resultados
    cantidad_resultados = Column(Integer)
    
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
    
    # Constraints
    __table_args__ = (
        CheckConstraint("frecuencia_alerta IN ('inmediata', 'diaria', 'semanal')", name="check_frecuencia_alerta"),
    )
    
    # Relationships
    usuario = relationship("Usuario", backref="busquedas")
    tipo_inmueble = relationship("TipoInmueble", backref="busquedas")
    
    def __repr__(self):
        return f"<Busqueda {self.busqueda_id}>"
