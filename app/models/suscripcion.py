from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Suscripcion(Base):
    """Modelo de Suscripción"""
    __tablename__ = "suscripciones"
    
    suscripcion_id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes_mae.plan_id"), nullable=False)
    fecha_inicio = Column(TIMESTAMP, nullable=False)
    fecha_fin = Column(TIMESTAMP, nullable=False)
    monto_pagado = Column(DECIMAL(10, 2), nullable=False)
    metodo_pago = Column(String(50))
    transaccion_id = Column(String(255))
    estado = Column(String(20), default="activa", nullable=False)
    auto_renovar = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    cancelada_at = Column(TIMESTAMP)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("estado IN ('activa', 'cancelada', 'expirada', 'suspendida')", name="check_suscripcion_estado"),
    )
    
    # Relationships
    usuario = relationship("Usuario", backref="suscripciones")
    plan = relationship("Plan", backref="suscripciones")
    
    def __repr__(self):
        return f"<Suscripcion usuario={self.usuario_id} plan={self.plan_id}>"
