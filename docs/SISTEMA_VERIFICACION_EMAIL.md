# 📧 SISTEMA DE VERIFICACIÓN DE EMAIL - PROFESIONAL

## 🎯 CARACTERÍSTICAS

✅ **Registro con verificación de email obligatoria**
✅ **Código de 6 dígitos enviado por email**
✅ **Tokens almacenados en tabla separada**
✅ **Expiración de 15 minutos**
✅ **Email de bienvenida después de verificar**
✅ **Reenvío de código si expira**
✅ **Sistema de recuperación de contraseña**

---

## 📋 PASO 1: EJECUTAR SQL EN RAILWAY

Ve a Railway → PostgreSQL → Query y ejecuta:

```sql
-- Ver archivo: EJECUTAR_EN_RAILWAY_VERIFICACION.sql
```

Esto creará:
- ✅ Columnas `email_verificado` y `foto_perfil` en `usuarios`
- ✅ Tabla `email_verification_tokens`
- ✅ Tabla `password_reset_tokens`
- ✅ Índices para búsquedas rápidas

---

## 📧 PASO 2: CONFIGURAR SENDGRID EN RAILWAY

Ve a Railway → Variables y agrega:

```bash
SENDGRID_API_KEY=TU_API_KEY_AQUI
SENDGRID_FROM_EMAIL=noreply@tudominio.com
SENDGRID_FROM_NAME=Sistema Inmobiliario
```

---

## 🧪 PASO 3: PROBAR EL FLUJO COMPLETO

### 1️⃣ Registrar nuevo usuario:
```powershell
$nuevoUsuario = @{
    email = "test@email.com"
    password = "123456"
    nombre = "Juan"
    apellido = "Pérez"
    telefono = "999888777"
    dni = "12345678"
} | ConvertTo-Json

$registro = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register" -Method Post -ContentType "application/json" -Body $nuevoUsuario
$registro
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente. Revisa tu email para verificar tu cuenta.",
  "data": {
    "usuario_id": 6,
    "email": "test@email.com",
    "estado": "pendiente",
    "email_verificado": false,
    "mensaje_verificacion": "Se ha enviado un código de verificación a tu email. Válido por 15 minutos."
  }
}
```

📧 **El usuario recibirá un email con código de 6 dígitos**

---

### 2️⃣ Intentar login SIN verificar (debe fallar):
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"test@email.com","password":"123456"}'
```

**Error esperado:**
```json
{
  "detail": "Debes verificar tu email antes de iniciar sesión. Revisa tu correo."
}
```

---

### 3️⃣ Verificar email con código:
```powershell
# Reemplaza 123456 con el código recibido por email
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/verify-email?email=test@email.com&codigo=123456" -Method Post
```

**Respuesta esperada:**
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

📧 **El usuario recibirá un email de bienvenida**

---

### 4️⃣ Ahora SÍ puede hacer login:
```powershell
$response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"test@email.com","password":"123456"}'
$TOKEN = $response.data.access_token
$response
```

**Respuesta esperada:**
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
      "nombre": "Juan",
      "apellido": "Pérez"
    }
  }
}
```

---

### 5️⃣ Reenviar código si expiró:
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/resend-verification?email=test@email.com" -Method Post
```

---

## 📊 ESTRUCTURA DE TABLAS

### `email_verification_tokens`
```sql
id              | BIGSERIAL (PK)
usuario_id      | INTEGER (FK → usuarios)
email           | VARCHAR(255)
token           | VARCHAR(6)
expires_at      | TIMESTAMP
used            | BOOLEAN
created_at      | TIMESTAMP
```

### `password_reset_tokens`
```sql
id              | BIGSERIAL (PK)
usuario_id      | INTEGER (FK → usuarios)
email           | VARCHAR(255)
token           | VARCHAR(6)
expires_at      | TIMESTAMP
used            | BOOLEAN
created_at      | TIMESTAMP
```

---

## 🔐 ENDPOINTS DISPONIBLES

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Registrar usuario | 🔓 Público |
| POST | `/api/v1/auth/verify-email` | Verificar email con código | 🔓 Público |
| POST | `/api/v1/auth/resend-verification` | Reenviar código | 🔓 Público |
| POST | `/api/v1/auth/login` | Login (requiere email verificado) | 🔓 Público |
| POST | `/api/v1/auth/logout` | Logout | 🔐 Token |

---

## 📧 EMAILS QUE SE ENVÍAN

### 1. Email de Verificación
- **Asunto:** 🔐 Código de Verificación: 123456 - Sistema Inmobiliario
- **Contenido:** Código de 6 dígitos, válido por 15 minutos
- **Diseño:** HTML profesional con gradientes

### 2. Email de Bienvenida
- **Asunto:** 🎉 ¡Bienvenido Juan! - Sistema Inmobiliario
- **Contenido:** Confirmación de cuenta verificada
- **Diseño:** HTML profesional con features del sistema

---

## ✅ VENTAJAS DE ESTE SISTEMA

1. **Profesional**: Igual que Gmail, Facebook, etc.
2. **Seguro**: Tokens en tabla separada, no en usuario
3. **Escalable**: Fácil agregar más tipos de tokens
4. **Auditable**: Historial de todos los tokens generados
5. **Limpio**: Código organizado y mantenible

---

¡Listo cumpa! 🚀
