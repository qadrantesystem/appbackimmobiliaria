from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.sql import func
from app.database import Base

class EstadoCRM(Base):
    """Modelo de Estado CRM"""
    __tablename__ = "estados_crm_mae"
    
    estado_id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    color = Column(String(20))  # hex color
    icono = Column(String(50))
    orden = Column(Integer, default=0)
    es_final = Column(Boolean, default=False)  # Si es un estado final del pipeline
    es_ganado = Column(Boolean, default=False)  # Si representa una venta ganada
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EstadoCRM {self.nombre}>"
