# 🏠 API PARA REGISTRAR INMUEBLES CON FOTOS

Base URL: `https://appbackimmobiliaria-production.up.railway.app`

---

## 🔐 AUTENTICACIÓN

Todas estas APIs requieren token JWT en el header:
```
Authorization: Bearer {tu_token_jwt}
```

Para obtener el token:
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login
```

---

## 📋 ENDPOINTS PRINCIPALES

### 1️⃣ **CREAR PROPIEDAD CON IMÁGENES** ⭐ (Recomendado)

**Endpoint:** `POST /api/v1/propiedades/con-imagenes`

**URL Completa:** 
```
https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/con-imagenes
```

**Descripción:** Crea una propiedad y sube automáticamente las imágenes a ImageKit en una sola petición.

**Content-Type:** `multipart/form-data`

**Parámetros:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `propiedad_json` | string (JSON) | ✅ | Datos de la propiedad en formato JSON |
| `imagen_principal` | File | ✅ | Foto principal (1 foto obligatoria, max 10MB) |
| `imagenes_galeria` | File[] | ❌ | Galería de fotos (hasta 5 fotos, max 10MB c/u) |

**JSON de `propiedad_json`:**
```json
{
  "propietario_real_nombre": "Juan Pérez García",
  "propietario_real_dni": "12345678",
  "propietario_real_telefono": "+51999888777",
  "propietario_real_email": "juan.perez@email.com",
  
  "tipo_inmueble_id": 1,
  "distrito_id": 1,
  "nombre_inmueble": "Oficina Premium San Isidro",
  "direccion": "Av. Javier Prado 123, Piso 8",
  "latitud": -12.0975,
  "longitud": -77.0305,
  
  "area": 120.50,
  "habitaciones": 0,
  "banos": 2,
  "parqueos": 3,
  "antiguedad": 5,
  
  "transaccion": "alquiler",
  "precio_alquiler": 3500.00,
  "precio_venta": null,
  "moneda": "PEN",
  
  "titulo": "Oficina moderna en San Isidro con vista panorámica",
  "descripcion": "Amplia oficina en edificio corporativo clase A...",
  
  "caracteristicas": [
    {"caracteristica_id": 1, "valor": "Sí"},
    {"caracteristica_id": 2, "valor": "24/7"},
    {"caracteristica_id": 15, "valor": "Fibra óptica"}
  ]
}
```

**Respuesta Exitosa (201):**
```json
{
  "success": true,
  "message": "Propiedad creada exitosamente con imágenes",
  "data": {
    "registro_cab_id": 25,
    "titulo": "Oficina moderna en San Isidro",
    "estado": "borrador",
    "imagen_principal": "https://ik.imagekit.io/jhgqqfbjr/propiedades/propiedad_20_principal_xyz.jpg",
    "total_imagenes_galeria": 3,
    "imagenes_galeria": [
      "https://ik.imagekit.io/jhgqqfbjr/propiedades/propiedad_20_galeria_1.jpg",
      "https://ik.imagekit.io/jhgqqfbjr/propiedades/propiedad_20_galeria_2.jpg",
      "https://ik.imagekit.io/jhgqqfbjr/propiedades/propiedad_20_galeria_3.jpg"
    ],
    "total_caracteristicas": 3
  }
}
```

**Límites:**
- ✅ 1 imagen principal (obligatoria)
- ✅ Hasta 5 imágenes en galería
- ✅ Máximo 10MB por imagen
- ✅ Formatos: JPG, PNG, WEBP

---

### 2️⃣ **ACTUALIZAR PROPIEDAD COMPLETA** ⭐ (Recomendado para edición)

**Endpoint:** `PUT /api/v1/propiedades/actualizar-completa/{propiedad_id}`

**URL Completa:** 
```
https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-completa/25
```

**Descripción:** Actualiza TODO de golpe: cabecera, características e imágenes. Solo envías lo que quieres cambiar.

**Content-Type:** `multipart/form-data`

**Parámetros:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `propiedad_json` | string (JSON) | ❌ | Datos a actualizar (solo incluir campos que se quieren cambiar) |
| `imagen_principal` | File | ❌ | Nueva foto principal (solo si se quiere cambiar) |
| `imagenes_galeria` | File[] | ❌ | Nueva galería (hasta 5 fotos, solo si se quiere cambiar) |

**JSON de `propiedad_json` (TODOS LOS CAMPOS SON OPCIONALES):**
```json
{
  "titulo": "Oficina Premium San Isidro - ACTUALIZADO",
  "precio_alquiler": 3800.00,
  "descripcion": "Nueva descripción actualizada...",
  "latitud": -12.0980,
  "longitud": -77.0310,
  
  "caracteristicas": [
    {"caracteristica_id": 1, "valor": "Sí"},
    {"caracteristica_id": 5, "valor": "Actualizado"}
  ]
}
```

**Ventajas:**
- ✅ Solo envías lo que quieres cambiar
- ✅ Si no envías imágenes, mantiene las actuales
- ✅ Si no envías características, mantiene las actuales
- ✅ Actualiza cabecera + detalle + imágenes en UNA transacción
- ✅ Admin puede editar cualquier propiedad

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "message": "Propiedad actualizada exitosamente",
  "data": {
    "registro_cab_id": 25,
    "titulo": "Oficina Premium San Isidro - ACTUALIZADO",
    "estado": "publicado",
    "imagen_principal_nueva": "https://ik.imagekit.io/.../principal_updated.jpg",
    "imagenes_galeria_nuevas": [
      "https://ik.imagekit.io/.../galeria_1_updated.jpg"
    ],
    "total_imagenes_galeria": 1
  }
}
```

---

### 3️⃣ **ACTUALIZAR SOLO IMÁGENES** (Método alternativo)

**Endpoint:** `POST /api/v1/propiedades/actualizar-imagenes/{propiedad_id}`

**URL Completa:** 
```
https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-imagenes/25
```

**Descripción:** Actualiza la imagen principal y/o galería de una propiedad existente.

**Content-Type:** `multipart/form-data`

**Parámetros:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `imagen_principal` | File | ❌ | Nueva imagen principal |
| `imagenes_galeria` | File[] | ❌ | Nueva galería (hasta 5 fotos) |

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "message": "Imágenes actualizadas exitosamente",
  "data": {
    "registro_cab_id": 25,
    "imagen_principal": "https://ik.imagekit.io/jhgqqfbjr/propiedades/updated.jpg",
    "imagenes_galeria": [
      "https://ik.imagekit.io/jhgqqfbjr/propiedades/galeria_1_updated.jpg"
    ]
  }
}
```

---

### 3️⃣ **CREAR PROPIEDAD SIN FOTOS** (Método alternativo)

**Endpoint:** `POST /api/v1/propiedades`

**URL Completa:** 
```
https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades
```

**Descripción:** Crea una propiedad sin subir fotos. Las URLs de imágenes deben proporcionarse previamente.

**Content-Type:** `application/json`

**Body:**
```json
{
  "propietario_real_nombre": "María López",
  "propietario_real_dni": "87654321",
  "propietario_real_telefono": "+51988777666",
  "propietario_real_email": "maria@email.com",
  
  "tipo_inmueble_id": 2,
  "distrito_id": 2,
  "nombre_inmueble": "Casa en Surco",
  "direccion": "Calle Los Pinos 456",
  "latitud": -12.1234,
  "longitud": -77.0123,
  
  "area": 180.00,
  "habitaciones": 3,
  "banos": 3,
  "parqueos": 2,
  
  "transaccion": "venta",
  "precio_venta": 450000.00,
  "moneda": "PEN",
  
  "titulo": "Casa espaciosa en Surco",
  "descripcion": "Amplia casa con jardín...",
  
  "imagen_principal": "https://url-de-imagen-ya-subida.jpg",
  "imagenes": [
    "https://url-1.jpg",
    "https://url-2.jpg"
  ],
  
  "caracteristicas": [
    {"caracteristica_id": 5, "valor": "200"},
    {"caracteristica_id": 7, "valor": "Sí"}
  ]
}
```

---

### 4️⃣ **PUBLICAR PROPIEDAD** (Cambiar estado)

**Endpoint:** `PATCH /api/v1/propiedades/{propiedad_id}/estado`

**URL Completa:** 
```
https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/25/estado
```

**Descripción:** Cambia el estado de la propiedad (borrador → publicado).

**Content-Type:** `application/json`

**Body:**
```json
{
  "estado": "publicado"
}
```

**Estados válidos:**
- `borrador` - No visible públicamente
- `publicado` - Visible en búsquedas públicas
- `pausado` - Temporalmente oculta
- `cerrado` - Inmueble ya vendido/alquilado

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Estado actualizado correctamente",
  "data": {
    "registro_cab_id": 25,
    "estado": "publicado"
  }
}
```

---

## 📊 APIS DE CONSULTA (NECESARIAS ANTES DE REGISTRAR)

### 5️⃣ **OBTENER TIPOS DE INMUEBLE**

```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/tipos-inmueble
```

**Respuesta:**
```json
[
  {"tipo_inmueble_id": 1, "nombre": "Oficina en Edificio", "icono": "🏢"},
  {"tipo_inmueble_id": 2, "nombre": "Casa", "icono": "🏠"},
  {"tipo_inmueble_id": 3, "nombre": "Departamento", "icono": "🏘️"}
]
```

---

### 6️⃣ **OBTENER DISTRITOS**

```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/distritos
```

**Respuesta:**
```json
[
  {"distrito_id": 1, "nombre": "San Isidro", "ciudad": "Lima", "provincia": "Lima"},
  {"distrito_id": 2, "nombre": "Surco", "ciudad": "Lima", "provincia": "Lima"}
]
```

---

### 7️⃣ **OBTENER CARACTERÍSTICAS POR TIPO DE INMUEBLE** ⭐

```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/1/agrupadas
```

**Respuesta:**
```json
{
  "tipo_inmueble_id": 1,
  "tipo_inmueble_nombre": "Oficina en Edificio",
  "categorias": [
    {
      "nombre": "Seguridad",
      "caracteristicas": [
        {"caracteristica_id": 1, "nombre": "Vigilancia 24/7", "tipo": "boolean"},
        {"caracteristica_id": 2, "nombre": "Cámaras de seguridad", "tipo": "boolean"}
      ]
    },
    {
      "nombre": "Servicios",
      "caracteristicas": [
        {"caracteristica_id": 15, "nombre": "Internet", "tipo": "text"}
      ]
    }
  ]
}
```

---

## 🔄 FLUJO COMPLETO PARA REGISTRAR INMUEBLE

### **Paso 1: Login**
```bash
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login
Body: {"email": "user@example.com", "password": "password123"}
# Guardar token de respuesta
```

### **Paso 2: Obtener tipos de inmueble**
```bash
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/tipos-inmueble
# Seleccionar tipo_inmueble_id
```

### **Paso 3: Obtener distritos**
```bash
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/distritos
# Seleccionar distrito_id
```

### **Paso 4: Obtener características del tipo**
```bash
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/{tipo_id}/agrupadas
# Seleccionar características aplicables
```

### **Paso 5: Crear propiedad con imágenes**
```bash
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/con-imagenes
Headers: Authorization: Bearer {token}
Content-Type: multipart/form-data

FormData:
- propiedad_json: {...}  # JSON con todos los datos
- imagen_principal: [archivo]
- imagenes_galeria: [archivo1, archivo2, ...]
```

### **Paso 6: Publicar propiedad**
```bash
PATCH https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{id}/estado
Headers: Authorization: Bearer {token}
Body: {"estado": "publicado"}
```

---

## 📝 EJEMPLO COMPLETO EN POWERSHELL

```powershell
# 1. Login
$loginBody = @{
    email = "alancairampoma@gmail.com"
    password = "Matias123"
} | ConvertTo-Json

$login = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login" `
    -Method POST -Body $loginBody -ContentType "application/json"

$token = $login.data.access_token

# 2. Crear propiedad con imágenes
$headers = @{
    "Authorization" = "Bearer $token"
}

$propiedadJson = @{
    propietario_real_nombre = "Test Usuario"
    propietario_real_dni = "12345678"
    propietario_real_telefono = "+51999888777"
    tipo_inmueble_id = 1
    distrito_id = 1
    nombre_inmueble = "Oficina Test"
    direccion = "Av. Test 123"
    latitud = -12.0975
    longitud = -77.0305
    area = 100.00
    transaccion = "alquiler"
    precio_alquiler = 2500.00
    moneda = "PEN"
    titulo = "Oficina de prueba"
} | ConvertTo-Json

$form = @{
    propiedad_json = $propiedadJson
    imagen_principal = Get-Item "C:\ruta\foto_principal.jpg"
    imagenes_galeria = @(
        Get-Item "C:\ruta\foto1.jpg",
        Get-Item "C:\ruta\foto2.jpg"
    )
}

$response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/con-imagenes" `
    -Method POST -Headers $headers -Form $form

Write-Host "Propiedad creada con ID: $($response.data.registro_cab_id)"
```

---

## ❌ ERRORES COMUNES

| Código | Error | Solución |
|--------|-------|----------|
| 401 | Unauthorized | Token inválido o expirado. Hacer login nuevamente |
| 400 | JSON inválido | Verificar formato del JSON en `propiedad_json` |
| 400 | Máximo 5 imágenes | Reducir cantidad de fotos en galería |
| 413 | Payload too large | Imagen supera 10MB. Comprimir imagen |
| 403 | Forbidden | Usuario no tiene perfil Ofertante/Corredor |
| 500 | Error ImageKit | Verificar configuración de ImageKit |

---

## 🔗 DOCUMENTACIÓN COMPLETA

**Swagger UI:** https://appbackimmobiliaria-production.up.railway.app/docs

**ReDoc:** https://appbackimmobiliaria-production.up.railway.app/redoc

---

## ✅ CHECKLIST ANTES DE REGISTRAR

- [ ] Tengo token JWT válido
- [ ] Tengo `tipo_inmueble_id` válido
- [ ] Tengo `distrito_id` válido
- [ ] Tengo al menos 1 imagen principal (max 10MB)
- [ ] Las imágenes están en formato JPG/PNG/WEBP
- [ ] Los datos del propietario están completos
- [ ] El precio corresponde al tipo de transacción
- [ ] La latitud y longitud son opcionales pero recomendadas

---

**Última actualización:** 2025-01-20  
**Backend:** https://appbackimmobiliaria-production.up.railway.app  
**Versión API:** v1
