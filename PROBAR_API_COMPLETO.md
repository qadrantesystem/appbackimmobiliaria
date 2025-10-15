# 🧪 PROBAR API COMPLETO - PASO A PASO

## 📋 PASO 1: EJECUTAR SQL EN RAILWAY

Ve a Railway → PostgreSQL → Query y ejecuta:

```sql
-- 1. Agregar columna DNI
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS dni VARCHAR(20);

-- 2. Actualizar passwords
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' 
WHERE email IN (
    'admin@inmobiliaria.com',
    'demandante@email.com',
    'ofertante@email.com',
    'corredor@inmobiliaria.com',
    'ana.martinez@email.com'
);

-- 3. Verificar
SELECT email, LENGTH(password_hash) as hash_length FROM usuarios;
```

---

## 🧪 PASO 2: PROBAR HEALTH CHECK

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/health"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "status": "healthy",
  "environment": "development"
}
```

---

## 🔐 PASO 3: PROBAR LOGIN - ADMIN

```powershell
$response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"admin@inmobiliaria.com","password":"123456"}'
$response
```

**Guardar el token:**
```powershell
$TOKEN = $response.data.access_token
Write-Host "Token guardado: $TOKEN"
```

---

## 🔐 PASO 4: PROBAR LOGIN - DEMANDANTE

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"demandante@email.com","password":"123456"}'
```

---

## 🔐 PASO 5: PROBAR LOGIN - OFERTANTE

```powershell
$responseOfertante = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"ofertante@email.com","password":"123456"}'
$TOKEN_OFERTANTE = $responseOfertante.data.access_token
$responseOfertante
```

---

## 🔐 PASO 6: PROBAR LOGIN - CORREDOR

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"corredor@inmobiliaria.com","password":"123456"}'
```

---

## 👤 PASO 7: VER MI PERFIL (Con Token)

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me" -Headers @{Authorization="Bearer $TOKEN"}
```

---

## 🏠 PASO 8: VER PROPIEDADES (Público - Sin Token)

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades"
```

---

## 🏠 PASO 9: VER DETALLE DE PROPIEDAD

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1"
```

---

## 🏠 PASO 10: MIS PROPIEDADES (Ofertante)

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/me/propiedades" -Headers @{Authorization="Bearer $TOKEN_OFERTANTE"}
```

---

## ➕ PASO 11: CREAR PROPIEDAD (Ofertante)

```powershell
$nuevaPropiedad = @{
    propietario_real_nombre = "Carlos Mendoza"
    propietario_real_dni = "87654321"
    propietario_real_telefono = "999777666"
    propietario_real_email = "carlos@email.com"
    tipo_inmueble_id = 1
    distrito_id = 1
    nombre_inmueble = "Departamento Moderno"
    direccion = "Av. Principal 123, San Isidro"
    area = 85.5
    habitaciones = 3
    banos = 2
    parqueos = 1
    transaccion = "alquiler"
    precio_alquiler = 1500
    moneda = "PEN"
    titulo = "Hermoso departamento en San Isidro"
    descripcion = "Departamento moderno con vista panorámica"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades" -Method Post -ContentType "application/json" -Headers @{Authorization="Bearer $TOKEN_OFERTANTE"} -Body $nuevaPropiedad
```

---

## 📧 PASO 12: CONTACTAR PROPIEDAD (Público)

```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1/contacto?nombre=Juan&email=juan@email.com&telefono=999888777&mensaje=Me%20interesa%20la%20propiedad" -Method Post
```

---

## 📝 PASO 13: REGISTRAR NUEVO USUARIO

```powershell
$nuevoUsuario = @{
    email = "test@email.com"
    password = "123456"
    nombre = "Test"
    apellido = "User"
    telefono = "999888777"
    dni = "12345678"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register" -Method Post -ContentType "application/json" -Body $nuevoUsuario
```

---

## ✅ RESUMEN DE USUARIOS DE PRUEBA

| Email | Password | Perfil | Descripción |
|-------|----------|--------|-------------|
| admin@inmobiliaria.com | 123456 | Admin | Administrador del sistema |
| demandante@email.com | 123456 | Demandante | Usuario buscando propiedades |
| ofertante@email.com | 123456 | Ofertante | Usuario publicando propiedades |
| corredor@inmobiliaria.com | 123456 | Corredor | Corredor inmobiliario |
| ana.martinez@email.com | 123456 | Demandante | Usuario adicional |

---

## 📚 ENDPOINTS DISPONIBLES

### 🔓 Públicos (Sin Token):
- ✅ `GET /health` - Health check
- ✅ `POST /api/v1/auth/register` - Registro
- ✅ `POST /api/v1/auth/login` - Login
- ✅ `GET /api/v1/propiedades` - Listar propiedades
- ✅ `GET /api/v1/propiedades/{id}` - Ver detalle
- ✅ `POST /api/v1/propiedades/{id}/vista` - Incrementar vista
- ✅ `POST /api/v1/propiedades/{id}/contacto` - Contactar

### 🔐 Protegidos (Requieren Token):
- 🔒 `GET /api/v1/usuarios/me` - Mi perfil
- 🔒 `PUT /api/v1/usuarios/me` - Actualizar perfil
- 🔒 `PUT /api/v1/usuarios/me/password` - Cambiar password
- 🔒 `GET /api/v1/propiedades/me/propiedades` - Mis propiedades
- 🔒 `POST /api/v1/propiedades` - Crear propiedad
- 🔒 `PATCH /api/v1/propiedades/{id}/estado` - Cambiar estado

---

## 🌐 DOCUMENTACIÓN INTERACTIVA

- **Swagger UI**: https://appbackimmobiliaria-production.up.railway.app/docs
- **ReDoc**: https://appbackimmobiliaria-production.up.railway.app/redoc

---

¡Listo cumpa! 🚀
