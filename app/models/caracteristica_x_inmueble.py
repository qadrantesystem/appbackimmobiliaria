from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CaracteristicaXInmueble(Base):
    """Modelo de Característica por Tipo de Inmueble"""
    __tablename__ = "caracteristicas_x_inmueble_mae"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_inmueble_id = Column(Integer, ForeignKey('tipo_inmueble_mae.tipo_inmueble_id'), nullable=False)
    caracteristica_id = Column(Integer, ForeignKey('caracteristicas_mae.caracteristica_id'), nullable=False)
    requerido = Column(Boolean, default=False)
    visible_en_filtro = Column(Boolean, default=True)
    orden = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    categoria_override_id = Column(Integer, ForeignKey('categorias_mae.categoria_id'), nullable=True)

    # Relaciones
    tipo_inmueble = relationship("TipoInmueble")
    caracteristica = relationship("Caracteristica")
    categoria_override = relationship("Categoria", foreign_keys=[categoria_override_id])
    
    def __repr__(self):
        return f"<CaracteristicaXInmueble tipo:{self.tipo_inmueble_id} car:{self.caracteristica_id}>"
