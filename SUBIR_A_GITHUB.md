# 📤 SUBIR PROYECTO A GITHUB

## ✅ Ya está listo el commit local

El proyecto ya tiene un commit local con todos los archivos. Solo falta hacer push.

## 🔑 OPCIÓN 1: Usar GitHub Desktop (MÁS FÁCIL)

1. Abre **GitHub Desktop**
2. File → Add Local Repository
3. Selecciona: `C:\Users\acairamp\Documents\proyecto\appimmobilarioback\backend`
4. Click en **Publish repository**
5. Nombre: `appbackimmobiliaria`
6. Owner: `qadrantesystem`
7. ✅ Listo!

## 🔑 OPCIÓN 2: Línea de comandos

```bash
cd C:\Users\acairamp\Documents\proyecto\appimmobilarioback\backend

# Verificar que el token tenga permisos de "repo"
# Si no funciona, genera un nuevo token en: https://github.com/settings/tokens

# Hacer push
git push -u origin main
```

## 🚀 DESPUÉS DE SUBIR A GITHUB

### Conectar con Railway:

1. Ve a: https://railway.app
2. Click en **New Project**
3. Selecciona **Deploy from GitHub repo**
4. Busca: `qadrantesystem/appbackimmobiliaria`
5. Railway detectará automáticamente que es FastAPI

### Configurar Variables de Entorno en Railway:

```
DATABASE_URL=postgresql://postgres:esbHQXHuToTttMYUpnRCkYAdHMpXapuM@maglev.proxy.rlwy.net:44913/railway

SECRET_KEY=inmobiliaria-super-secret-key-2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

IMAGEKIT_PRIVATE_KEY=private_juJdHhsZIjOMwacjNq6/94YqfYo=
IMAGEKIT_PUBLIC_KEY=public_m7rawfzMCD/O2+1pNfMA8aHqCkk=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/3y7rfi7jj

SENDGRID_API_KEY=tu-sendgrid-api-key-aqui
SENDGRID_FROM_EMAIL=noreply@inmobiliaria.com
SENDGRID_FROM_NAME=Sistema Inmobiliario

ENVIRONMENT=production
ALLOWED_HOSTS=*
```

### Railway desplegará automáticamente y te dará una URL:
```
https://tu-app.up.railway.app
```

## 📚 Endpoints disponibles:

- **Docs**: https://tu-app.up.railway.app/docs
- **Health**: https://tu-app.up.railway.app/health
- **Auth**: https://tu-app.up.railway.app/api/v1/auth/login

## 🧪 Probar API:

### 1. Registrar usuario:
```bash
POST https://tu-app.up.railway.app/api/v1/auth/register
{
  "email": "test@email.com",
  "password": "123456",
  "nombre": "Test",
  "apellido": "User"
}
```

### 2. Login:
```bash
POST https://tu-app.up.railway.app/api/v1/auth/login
{
  "email": "test@email.com",
  "password": "123456"
}
```

### 3. Ver propiedades:
```bash
GET https://tu-app.up.railway.app/api/v1/propiedades
```

---

## ⚠️ IMPORTANTE:

Antes de probar, asegúrate de ejecutar los scripts SQL en la base de datos de Railway:

```bash
# Conectarse a Railway PostgreSQL
psql postgresql://postgres:esbHQXHuToTttMYUpnRCkYAdHMpXapuM@maglev.proxy.rlwy.net:44913/railway

# Ejecutar scripts
\i scripts/00_ejecutar_todo.sql
```

O ejecutarlos uno por uno desde Railway Dashboard → PostgreSQL → Query

---

¡Listo cumpa! 🚀
