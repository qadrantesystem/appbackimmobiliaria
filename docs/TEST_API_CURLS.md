# 🧪 TEST API - CURLS COMPLETOS

Base URL: `https://appbackimmobiliaria-production.up.railway.app`

---

## 1️⃣ HEALTH CHECK

```bash
curl https://appbackimmobiliaria-production.up.railway.app/health
```

**Respuesta esperada:**
```json
{
  "success": true,
  "status": "healthy",
  "environment": "production"
}
```

---

## 2️⃣ AUTENTICACIÓN

### 📝 Registrar Usuario

```bash
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@email.com",
    "password": "123456",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "999888777",
    "dni": "12345678"
  }'
```

### 🔐 Login

```bash
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@email.com",
    "password": "123456"
  }'
```

**Guarda el `access_token` de la respuesta para los siguientes requests**

### 🔐 Login con usuario de prueba (Admin)

```bash
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@inmobiliaria.com",
    "password": "123456"
  }'
```

### 🔐 Login con usuario de prueba (Ofertante)

```bash
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ofertante@email.com",
    "password": "123456"
  }'
```

---

## 3️⃣ USUARIOS (Requiere Token)

### 👤 Ver Mi Perfil

```bash
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

### ✏️ Actualizar Mi Perfil

```bash
curl -X PUT https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Carlos",
    "apellido": "Pérez García",
    "telefono": "999888777"
  }'
```

### 🔑 Cambiar Contraseña

```bash
curl -X PUT https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me/password \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "123456",
    "password_nueva": "654321",
    "password_confirmacion": "654321"
  }'
```

### 👥 Listar Usuarios (Solo Admin)

```bash
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios?page=1&limit=10" \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_ADMIN"
```

---

## 4️⃣ PROPIEDADES

### 🏠 Listar Propiedades (Público - Sin Token)

```bash
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?page=1&limit=12"
```

### 🏠 Listar con Filtros

```bash
# Filtrar por tipo de inmueble
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?tipo_inmueble_id=1"

# Filtrar por distrito
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?distrito_id=1,2,3"

# Filtrar por transacción
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?transaccion=alquiler"

# Filtrar por precio
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?transaccion=alquiler&precio_min=500&precio_max=2000"

# Filtrar por habitaciones
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?habitaciones=2,3"

# Filtro completo
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?tipo_inmueble_id=1&distrito_id=1&transaccion=alquiler&precio_min=500&precio_max=2000&habitaciones=2,3&banos=2&area_min=50&area_max=150"
```

### 🔍 Ver Detalle de Propiedad

```bash
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1
```

### 👁️ Incrementar Vista

```bash
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1/vista
```

### 📧 Contactar Propietario

```bash
curl -X POST "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1/contacto?nombre=Juan&email=juan@email.com&telefono=999888777&mensaje=Me%20interesa%20la%20propiedad"
```

### 🏠 Mis Propiedades (Requiere Token Ofertante)

```bash
curl "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/me/propiedades?page=1&limit=10" \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_OFERTANTE"
```

### ➕ Crear Propiedad (Requiere Token Ofertante)

```bash
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_OFERTANTE" \
  -H "Content-Type: application/json" \
  -d '{
    "propietario_real_nombre": "Carlos Mendoza",
    "propietario_real_dni": "87654321",
    "propietario_real_telefono": "999777666",
    "propietario_real_email": "carlos@email.com",
    "tipo_inmueble_id": 1,
    "distrito_id": 1,
    "nombre_inmueble": "Departamento Moderno",
    "direccion": "Av. Principal 123, San Isidro",
    "area": 85.5,
    "habitaciones": 3,
    "banos": 2,
    "parqueos": 1,
    "transaccion": "alquiler",
    "precio_alquiler": 1500,
    "moneda": "PEN",
    "titulo": "Hermoso departamento en San Isidro",
    "descripcion": "Departamento moderno con vista panorámica"
  }'
```

### 🔄 Cambiar Estado de Propiedad

```bash
curl -X PATCH https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1/estado \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_OFERTANTE" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "publicado"
  }'
```

---

## 5️⃣ DOCUMENTACIÓN INTERACTIVA

### 📚 Swagger UI
```
https://appbackimmobiliaria-production.up.railway.app/docs
```

### 📖 ReDoc
```
https://appbackimmobiliaria-production.up.railway.app/redoc
```

---

## 🔑 VARIABLES PARA USAR

Después de hacer login, guarda el token:

```bash
# Guardar token en variable (Linux/Mac)
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Usar en requests
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me \
  -H "Authorization: Bearer $TOKEN"
```

```powershell
# Guardar token en variable (Windows PowerShell)
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Usar en requests
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me `
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 USUARIOS DE PRUEBA

Si ejecutaste los scripts SQL, puedes usar estos usuarios:

| Email | Password | Perfil |
|-------|----------|--------|
| admin@inmobiliaria.com | 123456 | Admin |
| demandante@email.com | 123456 | Demandante |
| ofertante@email.com | 123456 | Ofertante |
| corredor@inmobiliaria.com | 123456 | Corredor |

---

## 🧪 SECUENCIA DE PRUEBA COMPLETA

```bash
# 1. Health Check
curl https://appbackimmobiliaria-production.up.railway.app/health

# 2. Registrar usuario
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@email.com","password":"123456","nombre":"Test","apellido":"User"}'

# 3. Login
curl -X POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@email.com","password":"123456"}'

# 4. Ver propiedades (público)
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades

# 5. Ver detalle de propiedad
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1

# 6. Ver mi perfil (con token)
curl https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## ✅ RESPUESTAS ESPERADAS

### ✅ Success Response
```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": {...}
}
```

### ❌ Error Response
```json
{
  "success": false,
  "message": "Descripción del error",
  "detail": "Detalles adicionales"
}
```

---

¡Listo cumpa! 🚀
