# 🏠 Sistema Inmobiliario - Backend API

API REST desarrollada con FastAPI para sistema de gestión inmobiliaria.

## 🚀 Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **Pydantic** - Validación de datos

## 📋 Requisitos

- Python 3.10+
- PostgreSQL 14+
- pip

## 🔧 Instalación

### 1. Clonar repositorio
```bash
cd backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Copiar `.env.example` a `.env` y configurar:
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales de Railway:
```
DATABASE_URL=postgresql://postgres:tu-password@host:puerto/railway
SECRET_KEY=tu-clave-secreta
```

### 6. Ejecutar scripts SQL
Ejecutar los scripts en orden desde `scripts/`:
```bash
psql -h host -U postgres -d railway -f scripts/00_ejecutar_todo.sql
```

## ▶️ Ejecutar Aplicación

### Modo desarrollo
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Documentación API

Una vez iniciada la aplicación, acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Autenticación
│   │       ├── usuarios.py      # Gestión de usuarios
│   │       ├── propiedades.py   # Propiedades
│   │       └── ...
│   ├── core/
│   │   ├── config.py           # Configuración
│   │   ├── security.py         # JWT y passwords
│   │   └── exceptions.py       # Excepciones custom
│   ├── models/                 # Modelos SQLAlchemy
│   ├── schemas/                # Schemas Pydantic
│   ├── services/               # Lógica de negocio
│   ├── database.py             # Conexión BD
│   ├── dependencies.py         # Dependencias FastAPI
│   └── main.py                 # Aplicación principal
├── scripts/                    # Scripts SQL
├── docs/                       # Documentación
├── .env                        # Variables de entorno
├── requirements.txt            # Dependencias Python
└── README.md
```

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens) para autenticación.

### Registro
```bash
POST /api/v1/auth/register
{
  "email": "usuario@email.com",
  "password": "123456",
  "nombre": "Juan",
  "apellido": "Pérez"
}
```

### Login
```bash
POST /api/v1/auth/login
{
  "email": "usuario@email.com",
  "password": "123456"
}
```

Retorna:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {...}
}
```

### Usar token
Incluir en headers de requests protegidos:
```
Authorization: Bearer {access_token}
```

## 👥 Perfiles de Usuario

1. **Demandante** - Busca propiedades
2. **Ofertante** - Publica propiedades
3. **Corredor** - Gestiona leads y propiedades
4. **Admin** - Acceso completo

## 📊 Base de Datos

### Tablas Principales

**Seguridad:**
- `perfiles` - Perfiles de usuario
- `usuarios` - Usuarios del sistema

**Maestras:**
- `planes_mae` - Planes de suscripción
- `distritos_mae` - Distritos
- `tipo_inmueble_mae` - Tipos de inmueble
- `caracteristicas_mae` - Características
- `estados_crm_mae` - Estados CRM

**Transaccionales:**
- `suscripciones` - Suscripciones de usuarios
- `registro_x_inmueble_cab` - Propiedades (cabecera)
- `registro_x_inmueble_det` - Características de propiedades
- `busqueda_x_inmueble_mov` - Búsquedas
- `registro_x_inmueble_favoritos` - Favoritos
- `registro_x_inmueble_tracking` - Tracking CRM

## 🧪 Testing

```bash
pytest
```

## 📝 Usuarios de Prueba

Después de ejecutar los scripts SQL:

| Email | Password | Perfil |
|-------|----------|--------|
| admin@inmobiliaria.com | 123456 | Admin |
| demandante@email.com | 123456 | Demandante |
| ofertante@email.com | 123456 | Ofertante |
| corredor@inmobiliaria.com | 123456 | Corredor |

## 🚀 Deploy en Railway

1. Conectar repositorio a Railway
2. Configurar variables de entorno
3. Railway detectará automáticamente FastAPI
4. La app se desplegará en: `https://tu-app.up.railway.app`

## 📞 Soporte

Para dudas o problemas, contactar al equipo de desarrollo.

---

**Versión:** 1.0.0  
**Última actualización:** 2025-01-25
