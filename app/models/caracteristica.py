from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Caracteristica(Base):
    """Modelo de Característica"""
    __tablename__ = "caracteristicas_mae"
    
    caracteristica_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo_dato = Column(String(20), default="checkbox")
    categoria = Column(String(50))
    icono = Column(String(50))
    requerido = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Caracteristica {self.nombre}>"
