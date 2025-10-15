# 🧪 PRUEBAS COMPLETAS - MÓDULO DE SEGURIDAD

## ✅ VALIDACIÓN DE BASE DE DATOS

### 📊 Tablas Verificadas:
- ✅ `usuarios` - 18 columnas (incluye email_verificado, foto_perfil, dni)
- ✅ `perfiles` - 4 perfiles (demandante, ofertante, corredor, admin)
- ✅ `email_verification_tokens` - 7 columnas
- ✅ `password_reset_tokens` - 7 columnas

### 👥 Usuarios de Prueba Existentes:
| ID | Email | Perfil | Estado | Verificado |
|----|-------|--------|--------|------------|
| 1 | admin@inmobiliaria.com | admin | activo | ✅ true |
| 2 | demandante@email.com | demandante | activo | ✅ true |
| 3 | ofertante@email.com | ofertante | activo | ✅ true |
| 4 | corredor@inmobiliaria.com | corredor | activo | ✅ true |
| 5 | ana.martinez@email.com | demandante | activo | ✅ true |

**Password para todos:** `123456`

---

## 🧪 FLUJO 1: REGISTRO DE NUEVO USUARIO

### Paso 1: Registrar Usuario
```powershell
$nuevoUsuario = @{
    email = "test@email.com"
    password = "123456"
    nombre = "Test"
    apellido = "Usuario"
    telefono = "999888777"
    dni = "87654321"
} | ConvertTo-Json

$registro = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register" -Method Post -ContentType "application/json" -Body $nuevoUsuario
$registro
```

**✅ Respuesta Esperada:**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente. Revisa tu email para verificar tu cuenta.",
  "data": {
    "usuario_id": 6,
    "email": "test@email.com",
    "nombre": "Test",
    "apellido": "Usuario",
    "perfil_id": 1,
    "perfil_nombre": "demandante",
    "estado": "pendiente",
    "email_verificado": false,
    "mensaje_verificacion": "Se ha enviado un código de verificación a tu email. Válido por 15 minutos."
  }
}
```

**📧 Email Enviado:**
- Asunto: `🔐 Código de Verificación: 123456 - Sistema Inmobiliario`
- Contenido: Código de 6 dígitos
- Válido: 15 minutos

---

### Paso 2: Intentar Login SIN Verificar (Debe Fallar)
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"test@email.com","password":"123456"}'
```

**❌ Error Esperado:**
```json
{
  "success": false,
  "message": "Debes verificar tu email antes de iniciar sesión. Revisa tu correo."
}
```

---

### Paso 3: Verificar Email con Código
```powershell
# Reemplaza 123456 con el código recibido por email
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/verify-email?email=test@email.com&codigo=123456" -Method Post
```

**✅ Respuesta Esperada:**
```json
{
  "success": true,
  "message": "Email verificado exitosamente. Ya puedes iniciar sesión.",
  "data": {
    "usuario_id": 6,
    "email": "test@email.com",
    "email_verificado": true,
    "estado": "activo"
  }
}
```

**📧 Email de Bienvenida Enviado:**
- Asunto: `🎉 ¡Bienvenido Test! - Sistema Inmobiliario`
- Contenido: Confirmación de cuenta activa

---

### Paso 4: Login Exitoso
```powershell
$response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"test@email.com","password":"123456"}'
$TOKEN = $response.data.access_token
$response
```

**✅ Respuesta Esperada:**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "usuario": {
      "usuario_id": 6,
      "email": "test@email.com",
      "nombre": "Test",
      "apellido": "Usuario",
      "perfil_id": 1,
      "perfil_nombre": "demandante",
      "permisos": {
        "buscar": true,
        "contactar": true,
        "ver_historial": true,
        "guardar_favoritos": true
      }
    }
  }
}
```

---

## 🧪 FLUJO 2: REENVÍO DE CÓDIGO

### Caso: Código Expiró (después de 15 minutos)
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/resend-verification?email=test@email.com" -Method Post
```

**✅ Respuesta Esperada:**
```json
{
  "success": true,
  "message": "Código de verificación reenviado. Revisa tu email.",
  "data": {
    "email": "test@email.com",
    "mensaje": "Código válido por 15 minutos"
  }
}
```

---

## 🧪 FLUJO 3: LOGIN CON USUARIOS EXISTENTES

### Login como Admin
```powershell
$responseAdmin = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"admin@inmobiliaria.com","password":"123456"}'
$TOKEN_ADMIN = $responseAdmin.data.access_token
$responseAdmin.data.usuario
```

**✅ Permisos Admin:**
```json
{
  "all": true,
  "ver_reportes": true,
  "gestionar_planes": true,
  "moderar_contenido": true,
  "gestionar_usuarios": true,
  "aprobar_suscripciones": true,
  "mantenimiento_maestras": true
}
```

---

### Login como Demandante
```powershell
$responseDemandante = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"demandante@email.com","password":"123456"}'
$TOKEN_DEMANDANTE = $responseDemandante.data.access_token
$responseDemandante.data.usuario
```

**✅ Permisos Demandante:**
```json
{
  "buscar": true,
  "publicar": false,
  "contactar": true,
  "ver_historial": true,
  "guardar_favoritos": true
}
```

---

### Login como Ofertante
```powershell
$responseOfertante = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"ofertante@email.com","password":"123456"}'
$TOKEN_OFERTANTE = $responseOfertante.data.access_token
$responseOfertante.data.usuario
```

**✅ Permisos Ofertante:**
```json
{
  "buscar": true,
  "publicar": true,
  "contactar": true,
  "ver_estadisticas": true,
  "guardar_favoritos": true,
  "gestionar_propiedades": true
}
```

---

### Login como Corredor
```powershell
$responseCorredor = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"corredor@inmobiliaria.com","password":"123456"}'
$TOKEN_CORREDOR = $responseCorredor.data.access_token
$responseCorredor.data.usuario
```

**✅ Permisos Corredor:**
```json
{
  "buscar": true,
  "publicar": true,
  "comisiones": true,
  "pipeline_crm": true,
  "asignar_leads": true,
  "ver_estadisticas": true,
  "gestionar_propiedades": true
}
```

---

## 🧪 FLUJO 4: ENDPOINTS PROTEGIDOS

### Ver Mi Perfil (Requiere Token)
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/usuarios/me" -Headers @{Authorization="Bearer $TOKEN"}
```

### Ver Mi Perfil Completo (Con Foto)
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/perfiles/me" -Headers @{Authorization="Bearer $TOKEN"}
```

### Subir Foto de Perfil
```powershell
$file = Get-Item "C:\ruta\a\tu\foto.jpg"
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/perfiles/avatar" -Method Post -Headers @{Authorization="Bearer $TOKEN"} -Form @{file=$file}
```

### Actualizar Perfil
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/perfiles/me?nombre=Juan&apellido=Perez&telefono=999888777" -Method Put -Headers @{Authorization="Bearer $TOKEN"}
```

---

## 🧪 FLUJO 5: VALIDACIONES DE SEGURIDAD

### ❌ Email Duplicado
```powershell
# Intentar registrar email existente
$usuarioDuplicado = @{
    email = "admin@inmobiliaria.com"
    password = "123456"
    nombre = "Test"
    apellido = "Duplicado"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register" -Method Post -ContentType "application/json" -Body $usuarioDuplicado
```

**❌ Error Esperado:**
```json
{
  "success": false,
  "message": "El email ya está registrado"
}
```

---

### ❌ Código Incorrecto
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/verify-email?email=test@email.com&codigo=999999" -Method Post
```

**❌ Error Esperado:**
```json
{
  "success": false,
  "message": "Código de verificación incorrecto"
}
```

---

### ❌ Código Expirado (después de 15 minutos)
```powershell
# Usar código antiguo
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/verify-email?email=test@email.com&codigo=123456" -Method Post
```

**❌ Error Esperado:**
```json
{
  "success": false,
  "message": "El código de verificación ha expirado. Solicita uno nuevo."
}
```

---

### ❌ Credenciales Incorrectas
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"test@email.com","password":"wrongpassword"}'
```

**❌ Error Esperado:**
```json
{
  "success": false,
  "message": "Credenciales incorrectas"
}
```

---

## 📊 RESUMEN DE ENDPOINTS

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | 🔓 | Registrar usuario |
| `/api/v1/auth/verify-email` | POST | 🔓 | Verificar email |
| `/api/v1/auth/resend-verification` | POST | 🔓 | Reenviar código |
| `/api/v1/auth/login` | POST | 🔓 | Iniciar sesión |
| `/api/v1/auth/logout` | POST | 🔐 | Cerrar sesión |
| `/api/v1/usuarios/me` | GET | 🔐 | Ver mi perfil |
| `/api/v1/perfiles/me` | GET | 🔐 | Ver perfil completo |
| `/api/v1/perfiles/avatar` | POST | 🔐 | Subir foto |
| `/api/v1/perfiles/me` | PUT | 🔐 | Actualizar perfil |

---

## ✅ CHECKLIST DE VALIDACIÓN

- [x] Tabla `usuarios` con 18 columnas
- [x] Tabla `email_verification_tokens` creada
- [x] Tabla `password_reset_tokens` creada
- [x] 5 usuarios de prueba con email verificado
- [x] 4 perfiles con permisos configurados
- [x] Passwords con hash bcrypt de 60 caracteres
- [x] Registro genera token y envía email
- [x] Login requiere email verificado
- [x] Verificación activa cuenta
- [x] Email de bienvenida se envía
- [x] Reenvío de código funciona
- [x] Tokens expiran en 15 minutos
- [x] Permisos por perfil funcionan

---

¡Todo listo cumpa! 🚀
