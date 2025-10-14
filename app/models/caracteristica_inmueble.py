from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class CaracteristicaInmueble(Base):
    """Modelo de Relación Característica x Tipo de Inmueble"""
    __tablename__ = "caracteristicas_x_inmueble_mae"
    
    relacion_id = Column(Integer, primary_key=True, index=True)
    tipo_inmueble_id = Column(Integer, ForeignKey("tipo_inmueble_mae.tipo_inmueble_id"), nullable=False)
    caracteristica_id = Column(Integer, ForeignKey("caracteristicas_mae.caracteristica_id"), nullable=False)
    
    # Constraint de unicidad
    __table_args__ = (
        UniqueConstraint('tipo_inmueble_id', 'caracteristica_id', name='uq_tipo_caracteristica'),
    )
    
    def __repr__(self):
        return f"<CaracteristicaInmueble tipo={self.tipo_inmueble_id} caract={self.caracteristica_id}>"
