# 🎬 CONFIGURAR IMAGEKIT EN RAILWAY

## 📋 VARIABLES DE ENTORNO PARA RAILWAY

Ve a Railway → Tu Proyecto → Variables y agrega estas:

```bash
# 🎬 ImageKit Configuration
IMAGEKIT_PRIVATE_KEY=private_1xysV6NsG2Lm3I+iU63EhJHfJ2g=
IMAGEKIT_PUBLIC_KEY=public_y/LX/tLO5qSkPjgOTlEx8JnFq9Q=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/tu-id-aqui
```

---

## ⚠️ IMPORTANTE:

1. **IMAGEKIT_URL_ENDPOINT**: Reemplaza `tu-id-aqui` con tu ID real de ImageKit
   - Lo encuentras en: ImageKit Dashboard → URL Endpoint
   - Ejemplo: `https://ik.imagekit.io/abc123xyz`

2. **Después de agregar las variables:**
   - Railway redesplegará automáticamente
   - Espera 1-2 minutos

---

## 🧪 PROBAR SUBIDA DE FOTO

### 1️⃣ Login y obtener token:
```powershell
$response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" -Method Post -ContentType "application/json" -Body '{"email":"admin@inmobiliaria.com","password":"123456"}'
$TOKEN = $response.data.access_token
Write-Host "Token guardado"
```

### 2️⃣ Ver perfil actual:
```powershell
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/perfiles/me" -Headers @{Authorization="Bearer $TOKEN"}
```

### 3️⃣ Subir foto de perfil:
```powershell
# Preparar archivo
$file = Get-Item "C:\ruta\a\tu\foto.jpg"

# Crear form data
$form = @{
    file = $file
}

# Subir
Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/perfiles/avatar" -Method Post -Headers @{Authorization="Bearer $TOKEN"} -Form $form
```

### 4️⃣ Verificar que se subió:
```powershell
$perfil = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/perfiles/me" -Headers @{Authorization="Bearer $TOKEN"}
$perfil.data.foto_perfil
```

---

## 📸 ESTRUCTURA DE CARPETAS EN IMAGEKIT

Las fotos se guardarán en:
```
inmobiliaria/
  └── avatars/
      └── avatar_user_1_foto.jpg
      └── avatar_user_2_foto.png
      └── ...
```

---

## ✅ ENDPOINTS DISPONIBLES:

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/perfiles/me` | Ver mi perfil | 🔐 Token |
| PUT | `/api/v1/perfiles/me` | Actualizar perfil | 🔐 Token |
| POST | `/api/v1/perfiles/avatar` | Subir foto | 🔐 Token |
| DELETE | `/api/v1/perfiles/avatar` | Eliminar foto | 🔐 Token |

---

## 🔑 TUS CREDENCIALES IMAGEKIT:

```
Private Key: private_1xysV6NsG2Lm3I+iU63EhJHfJ2g=
Public Key:  public_y/LX/tLO5qSkPjgOTlEx8JnFq9Q=
```

**⚠️ NUNCA compartas estas claves públicamente**

---

¡Listo cumpa! 🚀
