from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Ocupante(Base):
    """Modelo de Ocupante de Inmueble normalizado.
    Registra a las personas o empresas que ocupan un inmueble
    (inquilinos, arrendatarios, usuarios en comodato, etc.).
    """
    __tablename__ = "ocupantes_inmueble"

    ocupante_id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    telefono = Column(String(50))
    email = Column(String(255))
    tipo_persona = Column(String(20), default="natural")
    empresa = Column(String(255))
    notas = Column(Text)
    activo = Column(Boolean, default=True, index=True)

    # Auditoría
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)

    # Relación inversa a transacciones
    transacciones = relationship("InmuebleTransaccion", back_populates="ocupante")

    def __repr__(self):
        return f"<Ocupante {self.nombre} - {self.dni}>"
