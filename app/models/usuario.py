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

    # Campos para tipo de persona
    tipo_persona = Column(String(20), default="natural")  # natural, juridica
    tipo_documento = Column(String(10), default="DNI")  # DNI, RUC, CE, PAS

    # Campos para persona jurídica
    razon_social = Column(String(255))
    ruc = Column(String(11))
    representante_legal = Column(String(255))

    perfil_id = Column(Integer, ForeignKey("perfiles.perfil_id"), nullable=False)
    estado = Column(String(20), default="pendiente", nullable=False)  # pendiente, activo, inactivo, suspendido
    email_verificado = Column(Boolean, default=False)
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
    verification_tokens = relationship("EmailVerificationToken", back_populates="usuario", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario {self.email}>"
