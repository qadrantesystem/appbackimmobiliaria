# 🚂 Guía de Configuración Railway

Guía paso a paso para desplegar el backend inmobiliario en Railway.

## 📋 Pre-requisitos

1. Cuenta en Railway: https://railway.app
2. Cuenta en ImageKit: https://imagekit.io
3. Cuenta en SendGrid: https://sendgrid.com
4. Repositorio en GitHub con el código

---

## 🗄️ PASO 1: Crear Base de Datos PostgreSQL

### 1.1 En Railway Dashboard
1. Click en **"New Project"**
2. Click en **"Provision PostgreSQL"**
3. Esperar a que se cree la base de datos

### 1.2 Obtener Credenciales
1. Click en el servicio PostgreSQL
2. Ir a **"Variables"** tab
3. Copiar la variable `DATABASE_URL`

**Formato de DATABASE_URL:**
```
postgresql://usuario:password@host:puerto/database
```

**Ejemplo:**
```
postgresql://postgres:KfktiHjbugWVTzvalfwxiVZwsvVFatrk@gondola.proxy.rlwy.net:54162/railway
```

---

## 🚀 PASO 2: Desplegar Backend

### 2.1 Conectar con GitHub
1. En Railway, click **"New"** > **"GitHub Repo"**
2. Seleccionar el repositorio del backend
3. Railway detectará automáticamente Python

### 2.2 Configurar Build
Railway usará automáticamente:
- `requirements.txt` para instalar dependencias
- `Procfile` para el comando de inicio
- `railway.toml` para configuración adicional

---

## 🔐 PASO 3: Configurar Variables de Entorno

### 3.1 En Railway Backend Service
1. Click en el servicio del backend
2. Ir a **"Variables"** tab
3. Click **"New Variable"**

### 3.2 Agregar Variables

#### Database (Auto-generada)
```
DATABASE_URL = postgresql://usuario:password@host:puerto/database
```
*(Copiar del servicio PostgreSQL)*

#### JWT Security
```
SECRET_KEY = tu-secret-key-super-segura-generada-aleatoriamente
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

**Generar SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

#### ImageKit
```
IMAGEKIT_PRIVATE_KEY = private_xxxxxxxxxxxxx
IMAGEKIT_PUBLIC_KEY = public_xxxxxxxxxxxxx
IMAGEKIT_URL_ENDPOINT = https://ik.imagekit.io/tu-id
```

**Obtener credenciales ImageKit:**
1. Login en https://imagekit.io
2. Dashboard > Developer Options
3. Copiar:
   - Private Key
   - Public Key
   - URL Endpoint

#### SendGrid
```
SENDGRID_API_KEY = SG.xxxxxxxxxxxxx
SENDGRID_FROM_EMAIL = tu-email@dominio.com
SENDGRID_FROM_NAME = Sistema Inmobiliario
```

**Obtener API Key SendGrid:**
1. Login en https://sendgrid.com
2. Settings > API Keys
3. Create API Key
4. Copiar la key (solo se muestra una vez)

**Verificar dominio:**
1. Settings > Sender Authentication
2. Verify Single Sender
3. Completar formulario y verificar email

#### Environment
```
ENVIRONMENT = production
```

### 3.3 Variables Completas (Resumen)

```env
# Database
DATABASE_URL=postgresql://usuario:password@host:puerto/database

# JWT
SECRET_KEY=tu-secret-key-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ImageKit
IMAGEKIT_PRIVATE_KEY=private_xxxxx
IMAGEKIT_PUBLIC_KEY=public_xxxxx
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/tu-id

# SendGrid
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@tudominio.com
SENDGRID_FROM_NAME=Sistema Inmobiliario

# Environment
ENVIRONMENT=production
```

---

## 🔄 PASO 4: Desplegar y Verificar

### 4.1 Deploy Automático
Railway desplegará automáticamente cuando:
- Hagas push a la rama principal
- Cambies variables de entorno

### 4.2 Ver Logs
1. Click en el servicio backend
2. Tab **"Deployments"**
3. Click en el deployment activo
4. Ver **"View Logs"**

### 4.3 Verificar Health Check
```bash
curl https://tu-app.up.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

### 4.4 Ver Documentación API
```
https://tu-app.up.railway.app/docs
```

---

## 🗃️ PASO 5: Inicializar Base de Datos

### 5.1 Conectar a PostgreSQL (Opcional)
```bash
# Desde tu terminal local
psql "postgresql://usuario:password@host:puerto/database"
```

### 5.2 Ejecutar Migraciones
Railway ejecutará automáticamente las migraciones si tienes configurado Alembic.

Si necesitas ejecutar manualmente:
```bash
# En Railway CLI o localmente con DATABASE_URL de Railway
alembic upgrade head
```

### 5.3 Poblar Datos Iniciales
Puedes crear un script `init_db.py` para insertar datos maestros:

```python
# init_db.py
from app.database import SessionLocal
from app.models import Perfil, PlanMae, TipoInmuebleMae, DistritoMae

def init_database():
    db = SessionLocal()
    
    # Insertar perfiles
    perfiles = [
        Perfil(perfil_id=1, nombre="arrendatario"),
        Perfil(perfil_id=2, nombre="propietario"),
        Perfil(perfil_id=3, nombre="admin")
    ]
    db.add_all(perfiles)
    
    # Insertar planes
    # ...
    
    db.commit()
    db.close()

if __name__ == "__main__":
    init_database()
```

---

## 🔗 PASO 6: Configurar Dominio (Opcional)

### 6.1 Dominio Personalizado
1. En Railway, ir a **"Settings"** del servicio
2. **"Domains"** > **"Custom Domain"**
3. Agregar tu dominio (ej: `api.tudominio.com`)
4. Configurar DNS:
   - Tipo: `CNAME`
   - Nombre: `api`
   - Valor: `tu-app.up.railway.app`

---

## 📊 PASO 7: Monitoreo

### 7.1 Ver Métricas
Railway muestra automáticamente:
- CPU usage
- Memory usage
- Network traffic
- Request count

### 7.2 Logs en Tiempo Real
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

---

## 🚨 Troubleshooting

### Error: "Application failed to respond"
- Verificar que el puerto sea `$PORT` (Railway lo asigna automáticamente)
- Revisar logs para errores de inicio

### Error: "Database connection failed"
- Verificar `DATABASE_URL` en variables
- Asegurar que PostgreSQL esté activo

### Error: "Module not found"
- Verificar que `requirements.txt` esté completo
- Railway debe instalar todas las dependencias automáticamente

### Imágenes no se suben
- Verificar credenciales de ImageKit
- Revisar logs para errores específicos

### Emails no se envían
- Verificar API Key de SendGrid
- Asegurar que el email de origen esté verificado

---

## ✅ Checklist de Deploy

- [ ] PostgreSQL creado en Railway
- [ ] `DATABASE_URL` configurada
- [ ] `SECRET_KEY` generada y configurada
- [ ] Credenciales ImageKit configuradas
- [ ] API Key SendGrid configurada
- [ ] Email de origen verificado en SendGrid
- [ ] Repositorio conectado con Railway
- [ ] Deploy exitoso (sin errores en logs)
- [ ] Health check responde correctamente
- [ ] Documentación API accesible en `/docs`
- [ ] Migraciones ejecutadas
- [ ] Datos maestros insertados

---

## 📚 Recursos

- **Railway Docs**: https://docs.railway.app
- **ImageKit Docs**: https://docs.imagekit.io
- **SendGrid Docs**: https://docs.sendgrid.com
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Última actualización**: 2025-01-14
