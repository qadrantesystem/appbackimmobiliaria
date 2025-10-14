from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    """Excepción para recursos no encontrados"""
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(HTTPException):
    """Excepción para acceso no autorizado"""
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(HTTPException):
    """Excepción para acceso prohibido"""
    def __init__(self, detail: str = "Acceso prohibido"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class BadRequestException(HTTPException):
    """Excepción para solicitudes incorrectas"""
    def __init__(self, detail: str = "Solicitud incorrecta"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ConflictException(HTTPException):
    """Excepción para conflictos (ej: duplicados)"""
    def __init__(self, detail: str = "Conflicto en la solicitud"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
