from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class Plan(Base):
    """Modelo de Plan de Suscripción"""
    __tablename__ = "planes_mae"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio_mensual = Column(DECIMAL(10, 2))
    precio_anual = Column(DECIMAL(10, 2))
    moneda = Column(String(3), default='USD')
    max_propiedades = Column(Integer)
    max_imagenes_por_propiedad = Column(Integer)
    destacar_propiedades = Column(Boolean, default=False)
    soporte_prioritario = Column(Boolean, default=False)
    caracteristicas = Column(JSONB)
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Plan {self.nombre}>"
