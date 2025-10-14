from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Tracking(Base):
    """Modelo de Tracking CRM"""
    __tablename__ = "registro_x_inmueble_tracking"
    
    tracking_id = Column(Integer, primary_key=True, index=True)
    registro_cab_id = Column(Integer, ForeignKey("registro_x_inmueble_cab.registro_cab_id", ondelete="CASCADE"), nullable=False)
    estado_anterior = Column(String(50))
    estado_nuevo = Column(String(50), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    corredor_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    motivo = Column(Text)
    metadata = Column(JSON)  # Para próximas acciones, calendario, etc.
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    propiedad = relationship("Propiedad", backref="tracking")
    usuario = relationship("Usuario", foreign_keys=[usuario_id], backref="tracking_usuario")
    corredor = relationship("Usuario", foreign_keys=[corredor_id], backref="tracking_corredor")
    
    def __repr__(self):
        return f"<Tracking prop={self.registro_cab_id} {self.estado_anterior}->{self.estado_nuevo}>"
