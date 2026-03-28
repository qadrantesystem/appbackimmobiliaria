"""
Modelo de Contactos/Leads CRM
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Contacto(Base):
    __tablename__ = "contactos_inmueble"

    contacto_id = Column(Integer, primary_key=True, index=True)
    registro_cab_id = Column(Integer, ForeignKey("registro_x_inmueble_cab.registro_cab_id", ondelete="CASCADE"), nullable=False)

    # Datos del interesado
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    nombre = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    telefono = Column(String(20))
    mensaje = Column(Text)

    # Tracking
    tipo_contacto = Column(String(20), default="registrado")  # invitado | registrado
    estado = Column(String(20), default="nuevo")  # nuevo | atendido | en_negociacion | cerrado
    corredor_id = Column(Integer, ForeignKey("usuarios.usuario_id"))
    notas_corredor = Column(Text)

    # Metadata
    busqueda_id = Column(Integer, ForeignKey("busqueda_x_inmueble_mov.busqueda_id"))
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    atendido_at = Column(TIMESTAMP)

    # Relationships
    propiedad = relationship("Propiedad", backref="contactos_leads")
    usuario = relationship("Usuario", foreign_keys=[usuario_id], backref="contactos_realizados")
    corredor = relationship("Usuario", foreign_keys=[corredor_id], backref="contactos_asignados")
