from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class PropiedadDetalle(Base):
    """Modelo de Detalle de Propiedad (Características)"""
    __tablename__ = "registro_x_inmueble_det"
    
    registro_det_id = Column(Integer, primary_key=True, index=True)
    registro_cab_id = Column(Integer, ForeignKey("registro_x_inmueble_cab.registro_cab_id", ondelete="CASCADE"), nullable=False)
    caracteristica_id = Column(Integer, ForeignKey("caracteristicas_mae.caracteristica_id"), nullable=False)
    valor = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    propiedad = relationship("Propiedad", backref="detalles")
    caracteristica = relationship("Caracteristica", backref="propiedad_detalles")
    
    def __repr__(self):
        return f"<PropiedadDetalle prop={self.registro_cab_id} caract={self.caracteristica_id}>"
