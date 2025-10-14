from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Distrito(Base):
    """Modelo de Distrito"""
    __tablename__ = "distritos_mae"
    
    distrito_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ciudad = Column(String(100))
    provincia = Column(String(100))
    latitud = Column(DECIMAL(10, 8))
    longitud = Column(DECIMAL(11, 8))
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def __repr__(self):
        return f"<Distrito {self.nombre}>"
