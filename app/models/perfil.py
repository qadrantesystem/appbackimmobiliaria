from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, JSON
from sqlalchemy.sql import func
from app.database import Base

class Perfil(Base):
    """Modelo de Perfil de Usuario"""
    __tablename__ = "perfiles"
    
    perfil_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255))
    permisos = Column(JSON)  # JSONB en PostgreSQL
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Perfil {self.nombre}>"
