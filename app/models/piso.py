from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class InmueblePiso(Base):
    """Modelo de Pisos por Inmueble (Detalle de pisos de un edificio)"""
    __tablename__ = "inmuebles_pisos_det"

    piso_id = Column(Integer, primary_key=True, index=True)
    registro_cab_id = Column(Integer, ForeignKey("registro_x_inmueble_cab.registro_cab_id"), nullable=False, index=True)
    numero_piso = Column(Integer, nullable=False)
    tipo_uso = Column(String(100), nullable=True)
    unidades_config = Column(Text, nullable=True)  # JSON: detalle por unidad en pisos mixtos
    area_total = Column(DECIMAL(10, 2), nullable=True)
    area_comercializable = Column(DECIMAL(10, 2), nullable=True)
    cantidad_unidades = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("registro_cab_id", "numero_piso", name="uq_piso_por_inmueble"),
    )

    # Relationships
    propiedad = relationship("Propiedad", back_populates="pisos")

    def __repr__(self):
        return f"<InmueblePiso {self.piso_id} - Piso {self.numero_piso}>"
