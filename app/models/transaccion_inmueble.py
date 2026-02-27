from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class InmuebleTransaccion(Base):
    """Modelo de Transacciones por Inmueble (historial de operaciones)"""
    __tablename__ = "inmueble_transaccion_mov"

    transaccion_id = Column(Integer, primary_key=True, index=True)
    registro_cab_id = Column(Integer, ForeignKey("registro_x_inmueble_cab.registro_cab_id"), nullable=False, index=True)
    tipo_transaccion = Column(String(50), nullable=False)
    estado_ocupacion = Column(String(50), nullable=True)
    inquilino_nombre = Column(String(200), nullable=True)
    inquilino_ruc = Column(String(20), nullable=True)
    inquilino_contacto = Column(String(200), nullable=True)
    inquilino_telefono = Column(String(50), nullable=True)
    inquilino_email = Column(String(255), nullable=True)
    corredor_id = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=True)
    ocupante_id = Column(Integer, ForeignKey("ocupantes_inmueble.ocupante_id", ondelete="SET NULL"), nullable=True)
    comision_porcentaje = Column(DECIMAL(5, 2), nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    precio_oficina = Column(DECIMAL(12, 2), nullable=True)
    precio_estacionamiento = Column(DECIMAL(10, 2), nullable=True)
    moneda = Column(String(3), default="USD")
    es_vigente = Column(Boolean, default=True)
    observaciones = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_by = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    propiedad = relationship("Propiedad", back_populates="transacciones")
    corredor = relationship("Usuario", foreign_keys=[corredor_id])
    ocupante = relationship("Ocupante", back_populates="transacciones")

    def __repr__(self):
        return f"<InmuebleTransaccion {self.transaccion_id} - {self.tipo_transaccion}>"
