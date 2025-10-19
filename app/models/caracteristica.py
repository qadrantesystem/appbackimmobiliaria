from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.sql import func
from app.database import Base

class Caracteristica(Base):
    """Modelo de Característica"""
    __tablename__ = "caracteristicas_mae"
    
    caracteristica_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    tipo_input = Column(String(50))  # text, number, checkbox, select
    unidad = Column(String(20))  # m2, habitaciones, baños, etc.
    categoria = Column(String(100))  # Áreas Comunes, Ascensores, etc.
    orden_categoria = Column(Integer, default=0)  # Orden de la categoría para agrupar
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Caracteristica {self.nombre}>"
