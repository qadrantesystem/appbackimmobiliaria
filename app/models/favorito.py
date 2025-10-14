from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Favorito(Base):
    """Modelo de Favorito"""
    __tablename__ = "registro_x_inmueble_favoritos"
    
    favorito_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False)
    registro_cab_id = Column(Integer, ForeignKey("registro_x_inmueble_cab.registro_cab_id", ondelete="CASCADE"), nullable=False)
    notas = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Constraint de unicidad
    __table_args__ = (
        UniqueConstraint('usuario_id', 'registro_cab_id', name='uq_usuario_propiedad'),
    )
    
    # Relationships
    usuario = relationship("Usuario", backref="favoritos")
    propiedad = relationship("Propiedad", backref="favoritos")
    
    def __repr__(self):
        return f"<Favorito usuario={self.usuario_id} prop={self.registro_cab_id}>"
