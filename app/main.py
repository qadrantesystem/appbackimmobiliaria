from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database import engine, Base

# Importar todos los modelos para crear las tablas
from app.models import *

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema Inmobiliario API",
    description="API REST para sistema de gestión inmobiliaria",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas en la base de datos
@app.on_event("startup")
async def startup_event():
    """Evento de inicio - Crear tablas si no existen"""
    print("🚀 Iniciando aplicación...")
    print("📊 Creando tablas en base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "Error interno"
        }
    )

# Ruta raíz
@app.get("/")
async def root():
    """Ruta raíz de la API"""
    return {
        "success": True,
        "message": "API Sistema Inmobiliario",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

# Health check
@app.get("/health")
async def health_check():
    """Verificar estado de la API"""
    return {
        "success": True,
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

# Importar y registrar routers
print("📦 Cargando módulos de API...")

try:
    from app.api.v1 import auth
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["🔐 Autenticación"])
    print("   ✅ Autenticación")
except ImportError as e:
    print(f"   ⚠️ Error cargando auth: {e}")

try:
    from app.api.v1 import usuarios
    app.include_router(usuarios.router, prefix="/api/v1/usuarios", tags=["👥 Usuarios"])
    print("   ✅ Usuarios")
except ImportError as e:
    print(f"   ⚠️ Error cargando usuarios: {e}")

try:
    from app.api.v1 import propiedades
    app.include_router(propiedades.router, prefix="/api/v1/propiedades", tags=["🏠 Propiedades"])
    print("   ✅ Propiedades")
except ImportError as e:
    print(f"   ⚠️ Error cargando propiedades: {e}")

# TODO: Más endpoints (planes, suscripciones, búsquedas, favoritos, etc.)

print("✅ Aplicación lista!")
