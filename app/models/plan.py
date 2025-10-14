from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Plan(Base):
    """Modelo de Plan de Suscripción"""
    __tablename__ = "planes_mae"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255))
    precio = Column(DECIMAL(10, 2), default=0)
    duracion_dias = Column(Integer, default=30)
    limite_busquedas = Column(Integer, default=10)
    limite_registros = Column(Integer, default=1)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Plan {self.nombre}>"
