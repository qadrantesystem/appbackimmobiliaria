from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FavoritoCreate(BaseModel):
    """Schema para crear favorito"""
    registro_cab_id: int
    notas: Optional[str] = Field(None, max_length=500)

class FavoritoUpdate(BaseModel):
    """Schema para actualizar favorito"""
    notas: Optional[str] = Field(None, max_length=500)

class FavoritoResponse(BaseModel):
    """Schema de respuesta de Favorito"""
    favorito_id: int
    propiedad: dict  # PropiedadResponse simplificado
    notas: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
