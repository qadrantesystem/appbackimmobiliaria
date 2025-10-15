from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Usuario(Base):
    """Modelo de Usuario"""
    __tablename__ = "usuarios"
    
    usuario_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    dni = Column(String(20))
    foto_perfil = Column(String(500))  # URL de ImageKit
    perfil_id = Column(Integer, ForeignKey("perfiles.perfil_id"), nullable=False)
    estado = Column(String(20), default="activo", nullable=False)
    plan_id = Column(Integer, ForeignKey("planes_mae.plan_id"))
    fecha_inicio_suscripcion = Column(TIMESTAMP)
    fecha_fin_suscripcion = Column(TIMESTAMP)
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    fecha_ultima_sesion = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo', 'suspendido')", name="check_usuario_estado"),
    )
    
    # Relationships
    perfil = relationship("Perfil", backref="usuarios")
    plan = relationship("Plan", backref="usuarios")
    
    def __repr__(self):
        return f"<Usuario {self.email}>"
