from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
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

    # ⚠️ DEPRECATED: Mantener por compatibilidad (se eliminará en futuras versiones)
    categoria = Column(String(100))  # Áreas Comunes, Ascensores, etc.
    orden_categoria = Column(Integer, default=0)  # Orden de la categoría para agrupar

    # ✅ NUEVO: Relación con tabla categorias_mae
    categoria_id = Column(Integer, ForeignKey('categorias_mae.categoria_id'), index=True)

    icono = Column(String(100), nullable=True)  # Archivo WebP del icono (ej: parking.webp)
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relación con Categoria
    categoria_obj = relationship("Categoria", back_populates="caracteristicas")

    def __repr__(self):
        return f"<Caracteristica {self.nombre}>"
