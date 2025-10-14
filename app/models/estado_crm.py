from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class EstadoCRM(Base):
    """Modelo de Estado CRM"""
    __tablename__ = "estados_crm_mae"
    
    estado_crm_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255))
    color = Column(String(20))
    icono = Column(String(50))
    orden = Column(Integer)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EstadoCRM {self.nombre}>"
