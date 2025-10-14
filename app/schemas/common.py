from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """Schema genérico de respuesta"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

class PaginationParams(BaseModel):
    """Schema para parámetros de paginación"""
    page: int = 1
    limit: int = 10
    
    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico de respuesta paginada"""
    success: bool = True
    data: List[T]
    pagination: dict
    
    class Config:
        from_attributes = True
