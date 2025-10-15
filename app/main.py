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

try:
    from app.api.v1 import perfiles
    app.include_router(perfiles.router, prefix="/api/v1/perfiles", tags=["👤 Perfiles"])
    print("   ✅ Perfiles")
except ImportError as e:
    print(f"   ⚠️ Error cargando perfiles: {e}")

try:
    from app.api.v1 import test_services
    app.include_router(test_services.router, prefix="/api/v1/test", tags=["🧪 Testing"])
    print("   ✅ Test Services")
except ImportError as e:
    print(f"   ⚠️ Error cargando test services: {e}")

try:
    from app.api.v1 import planes
    app.include_router(planes.router, prefix="/api/v1/planes", tags=["💳 Planes"])
    print("   ✅ Planes")
except ImportError as e:
    print(f"   ⚠️ Error cargando planes: {e}")

try:
    from app.api.v1 import distritos
    app.include_router(distritos.router, prefix="/api/v1/distritos", tags=["📍 Distritos"])
    print("   ✅ Distritos")
except ImportError as e:
    print(f"   ⚠️ Error cargando distritos: {e}")

try:
    from app.api.v1 import tipos_inmueble
    app.include_router(tipos_inmueble.router, prefix="/api/v1/tipos-inmueble", tags=["🏠 Tipos de Inmueble"])
    print("   ✅ Tipos de Inmueble")
except ImportError as e:
    print(f"   ⚠️ Error cargando tipos de inmueble: {e}")

try:
    from app.api.v1 import caracteristicas
    app.include_router(caracteristicas.router, prefix="/api/v1/caracteristicas", tags=["⭐ Características"])
    print("   ✅ Características")
except ImportError as e:
    print(f"   ⚠️ Error cargando características: {e}")

try:
    from app.api.v1 import caracteristicas_x_inmueble
    app.include_router(caracteristicas_x_inmueble.router, prefix="/api/v1/caracteristicas-x-inmueble", tags=["🔗 Características x Inmueble"])
    print("   ✅ Características x Inmueble")
except ImportError as e:
    print(f"   ⚠️ Error cargando características x inmueble: {e}")

try:
    from app.api.v1 import estados_crm
    app.include_router(estados_crm.router, prefix="/api/v1/estados-crm", tags=["📊 Estados CRM"])
    print("   ✅ Estados CRM")
except ImportError as e:
    print(f"   ⚠️ Error cargando estados CRM: {e}")

try:
    from app.api.v1 import suscripciones
    app.include_router(suscripciones.router, prefix="/api/v1/suscripciones", tags=["💳 Suscripciones"])
    print("   ✅ Suscripciones")
except ImportError as e:
    print(f"   ⚠️ Error cargando suscripciones: {e}")

try:
    from app.api.v1 import favoritos
    app.include_router(favoritos.router, prefix="/api/v1/favoritos", tags=["⭐ Favoritos"])
    print("   ✅ Favoritos")
except ImportError as e:
    print(f"   ⚠️ Error cargando favoritos: {e}")

# TODO: Más endpoints (búsquedas, tracking, etc.)

print("✅ Aplicación lista!")
