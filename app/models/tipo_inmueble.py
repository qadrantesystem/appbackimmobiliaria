from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.sql import func
from app.database import Base

class TipoInmueble(Base):
    """Modelo de Tipo de Inmueble"""
    __tablename__ = "tipo_inmueble_mae"
    
    tipo_inmueble_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    icono = Column(String(50))
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TipoInmueble {self.nombre}>"
