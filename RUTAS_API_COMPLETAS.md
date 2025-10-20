# 🌐 RUTAS COMPLETAS DEL API - BACKEND INMOBILIARIO

**Base URL:** `https://appbackimmobiliaria-production.up.railway.app`

---

## 📍 **ENDPOINTS PÚBLICOS (No requieren autenticación)**

### 1. **Tipos de Inmueble**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/tipos-inmueble
```
**Respuesta:** Lista de tipos de inmueble (Oficina, Casa, Departamento, etc.)

---

### 2. **Distritos**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/distritos
```
**Respuesta:** Lista de distritos disponibles (San Isidro, Miraflores, etc.)

---

### 3. **Características** 
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas
```
**Respuesta:** Lista de todas las características (51 total)

**Filtros opcionales:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas?activo=true
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas?categoria=AREAS_COMUNES_EDIFICIO
```

---

### 4. **Características por Tipo de Inmueble (Lista simple)**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/{tipo_inmueble_id}
```
**Ejemplo:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/1
```
**Respuesta:** Lista plana de características para ese tipo

---

### 5. **Características AGRUPADAS por Tipo de Inmueble** ⭐ (NUEVO - ARREGLADO)
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/{tipo_inmueble_id}/agrupadas
```
**Ejemplo:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/1/agrupadas
```
**Respuesta:** Características agrupadas por categoría (ideal para filtros en frontend)

```json
{
  "tipo_inmueble_id": 1,
  "tipo_inmueble_nombre": "Oficina en Edificio",
  "categorias": [
    {
      "nombre": "Áreas Comunes del Edificio",
      "orden": 1,
      "caracteristicas": [
        {
          "caracteristica_id": 1,
          "nombre": "Parqueos Simples",
          "descripcion": "Espacios de estacionamiento estándar",
          "tipo_input": "number",
          "unidad": "unid",
          "requerido": false,
          "orden": 1
        }
      ]
    }
  ]
}
```

---

### 6. **Propiedades (búsqueda pública)** 🗺️
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades
```

**Incluye:** latitud, longitud, imágenes (principal + galería)

**Con filtros:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?tipo_inmueble_id=1&distrito_id=1&limit=10&page=1
```

**Parámetros de filtro disponibles:**
- `tipo_inmueble_id` - Filtrar por tipo
- `distrito_id` - Filtrar por distrito (puede ser "1,2,3")
- `transaccion` - "venta" o "alquiler"
- `precio_min` - Precio mínimo
- `precio_max` - Precio máximo
- `area_min` - Área mínima (m²)
- `area_max` - Área máxima (m²)
- `habitaciones` - Número de habitaciones (puede ser "2,3")
- `banos` - Número de baños
- `parqueos` - Número mínimo de parqueos
- `page` - Página (default: 1)
- `limit` - Resultados por página (default: 12, max: 100)

**Respuesta incluye:**
```json
{
  "data": [{
    "registro_cab_id": 1,
    "titulo": "Oficina moderna",
    "latitud": -12.0975,
    "longitud": -77.0305,
    "imagen_principal": "https://...",
    "imagenes": ["url1", "url2", "url3"],
    // ... más campos
  }],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 50,
    "total_pages": 5
  }
}
```

---

### 7. **Detalle de Propiedad**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{propiedad_id}
```
**Ejemplo:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1
```
**Incluye:** Características completas, propietario, corredor, imágenes, latitud/longitud

---

### 8. **Incrementar vistas de propiedad**
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{propiedad_id}/vista
```
Incrementa contador de vistas cada vez que un usuario ve el detalle.

---

### 9. **Contactar propiedad**
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{propiedad_id}/contacto
```
**Body:**
```json
{
  "nombre": "Juan Pérez",
  "telefono": "+51999888777",
  "email": "juan@email.com",
  "mensaje": "Me interesa esta propiedad"
}
```
Incrementa contador de contactos y envía notificación al propietario.

---

## 🔐 **ENDPOINTS CON AUTENTICACIÓN**

### 10. **Login**
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@email.com",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "usuario": {...}
  }
}
```

---

### 11. **Registro**
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/register
Content-Type: application/json

{
  "email": "nuevo@email.com",
  "password": "password123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "999888777",
  "dni": "12345678"
}
```

---

## 🏠 **GESTIÓN DE PROPIEDADES (Ofertante/Corredor)**

### 12. **Mis Propiedades** 🗺️
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/mis-propiedades
Authorization: Bearer {token}
```
**Parámetros opcionales:**
- `page` - Número de página (default: 1)
- `limit` - Resultados por página (default: 10, max: 100)
- `estado` - Filtrar por estado ("borrador", "publicado", "pausado", "cerrado")

**Respuesta incluye:**
- Lista de propiedades del usuario (Admin ve TODAS)
- Estadísticas: total_propiedades, publicadas, borradores, total_vistas, total_contactos
- **IMPORTANTE:** Incluye latitud y longitud para mapas 🗺️

---

### 13. **Crear Propiedad CON IMÁGENES** ⭐ (TODO EN UNO)
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/con-imagenes
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**FormData:**
- `propiedad_json` (string): JSON con todos los datos
- `imagen_principal` (File): 1 foto obligatoria (max 10MB)
- `imagenes_galeria` (File[]): Hasta 5 fotos opcionales (max 10MB c/u)

**Ejemplo de propiedad_json:**
```json
{
  "propietario_real_nombre": "Juan Pérez",
  "propietario_real_dni": "12345678",
  "propietario_real_telefono": "+51999888777",
  "tipo_inmueble_id": 1,
  "distrito_id": 1,
  "nombre_inmueble": "Oficina Premium",
  "direccion": "Av. Javier Prado 123",
  "latitud": -12.0975,
  "longitud": -77.0305,
  "area": 120.50,
  "habitaciones": 0,
  "banos": 2,
  "parqueos": 3,
  "transaccion": "alquiler",
  "precio_alquiler": 3500.00,
  "moneda": "PEN",
  "titulo": "Oficina moderna con vista",
  "descripcion": "Amplia oficina...",
  "caracteristicas": [
    {"caracteristica_id": 1, "valor": "Sí"},
    {"caracteristica_id": 2, "valor": "24/7"}
  ]
}
```

**Hace:**
1. Sube imágenes a ImageKit automáticamente
2. Crea registro_x_inmueble_cab
3. Crea registro_x_inmueble_det (características)
4. Todo en UNA transacción

---

### 14. **Actualizar Propiedad COMPLETA** ⭐ (TODO DE GOLPE)
```
PUT https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-completa/{propiedad_id}
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**FormData (TODOS OPCIONALES):**
- `propiedad_json` (string): Solo incluir campos que quieres cambiar
- `imagen_principal` (File): Nueva imagen principal (opcional)
- `imagenes_galeria` (File[]): Nueva galería (opcional, hasta 5)

**Ejemplo - Solo actualizar precio y título:**
```json
{
  "titulo": "Oficina Premium ACTUALIZADO",
  "precio_alquiler": 3800.00
}
```

**Ventajas:**
- Solo envías lo que quieres cambiar
- Si no envías imágenes, mantiene las actuales
- Si no envías características, mantiene las actuales
- Actualiza cabecera + detalle + imágenes en UNA transacción
- Admin puede editar cualquier propiedad

---

### 15. **Actualizar solo imágenes**
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-imagenes/{propiedad_id}
Authorization: Bearer {token}
Content-Type: multipart/form-data
```
**FormData:**
- `imagen_principal` (File, opcional)
- `imagenes_galeria` (File[], opcional, hasta 5)

---

### 16. **Cambiar estado de propiedad**
```
PATCH https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{propiedad_id}/estado
Authorization: Bearer {token}
```
**Body:**
```json
{
  "estado": "publicado"
}
```
**Estados válidos:** "borrador", "publicado", "pausado", "cerrado"

---

### 17. **Favoritos** (requiere token)
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/favoritos
Authorization: Bearer {token}
```

```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/favoritos
Authorization: Bearer {token}
Content-Type: application/json

{
  "propiedad_id": 1
}
```

---

### 18. **Búsquedas guardadas** (requiere token)
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/busquedas
Authorization: Bearer {token}
```

```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/busquedas
Authorization: Bearer {token}
Content-Type: application/json

{
  "tipo_inmueble_id": 1,
  "distrito_id": 1,
  "precio_min": 1000,
  "precio_max": 5000
}
```

---

## 📋 **RESUMEN DE ENDPOINTS**

### **Públicos (sin token):**
1. ✅ Tipos de inmueble
2. ✅ Distritos
3. ✅ Características (todas o por tipo, agrupadas)
4. ✅ Búsqueda de propiedades (con filtros)
5. ✅ Detalle de propiedad
6. ✅ Incrementar vistas
7. ✅ Contactar propiedad

### **Autenticación:**
8. ✅ Login
9. ✅ Registro

### **Gestión de Propiedades (token requerido):**
10. ✅ Mis propiedades (con estadísticas)
11. ⭐ **Crear propiedad con imágenes** (TODO EN UNO)
12. ⭐ **Actualizar propiedad completa** (TODO DE GOLPE - NUEVO)
13. ✅ Actualizar solo imágenes
14. ✅ Cambiar estado
15. ✅ Favoritos
16. ✅ Búsquedas guardadas

### **🗺️ IMPORTANTE - Coordenadas para mapas:**
- `/propiedades` ✅ Incluye latitud/longitud
- `/propiedades/mis-propiedades` ✅ Incluye latitud/longitud
- `/propiedades/{id}` ✅ Incluye latitud/longitud

### **IDs de Tipos de Inmueble más comunes:**
- `1` - Oficina en Edificio
- `2` - Casa
- `3` - Departamento
- `4` - Local Comercial

### **IDs de Distritos más comunes:**
- `1` - San Isidro
- `2` - Miraflores
- `3` - San Borja
- `4` - Surco
- `5` - La Molina

---

## 🔧 **Ejemplo de uso en Frontend (JavaScript/TypeScript)**

```javascript
const API_BASE = 'https://appbackimmobiliaria-production.up.railway.app/api/v1';

// 1. Obtener tipos de inmueble para select
const tiposInmueble = await fetch(`${API_BASE}/tipos-inmueble`)
  .then(res => res.json());

// 2. Obtener distritos para select
const distritos = await fetch(`${API_BASE}/distritos`)
  .then(res => res.json());

// 3. Obtener características agrupadas para filtros avanzados
const caracteristicas = await fetch(`${API_BASE}/caracteristicas-x-inmueble/tipo-inmueble/1/agrupadas`)
  .then(res => res.json());

// 4. Buscar propiedades con filtros (incluye latitud/longitud para mapa)
const response = await fetch(`${API_BASE}/propiedades?tipo_inmueble_id=1&distrito_id=1,2&transaccion=alquiler&limit=20&page=1`)
  .then(res => res.json());

// response.data contiene array con latitud/longitud para cada propiedad
const propiedadesConCoordenadas = response.data.map(prop => ({
  id: prop.registro_cab_id,
  titulo: prop.titulo,
  lat: prop.latitud,
  lng: prop.longitud,
  precio: prop.precio_alquiler,
  imagen: prop.imagen_principal
}));

// 5. Login y guardar token
const loginResponse = await fetch(`${API_BASE}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
}).then(res => res.json());

const token = loginResponse.data.access_token;
localStorage.setItem('token', token);

// 6. Obtener mis propiedades (con estadísticas y coordenadas)
const misPropiedades = await fetch(`${API_BASE}/propiedades/mis-propiedades?limit=50`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(res => res.json());

console.log('Estadísticas:', misPropiedades.pagination.estadisticas);
// { total_propiedades: 21, publicadas: 16, borradores: 0, total_vistas: 350, total_contactos: 58 }

// 7. Crear propiedad con imágenes (FormData)
const formData = new FormData();

const propiedadData = {
  propietario_real_nombre: "Juan Pérez",
  propietario_real_dni: "12345678",
  propietario_real_telefono: "+51999888777",
  tipo_inmueble_id: 1,
  distrito_id: 1,
  nombre_inmueble: "Oficina Premium",
  direccion: "Av. Javier Prado 123",
  latitud: -12.0975,
  longitud: -77.0305,
  area: 120.50,
  banos: 2,
  transaccion: "alquiler",
  precio_alquiler: 3500.00,
  moneda: "PEN",
  titulo: "Oficina moderna",
  caracteristicas: [
    { caracteristica_id: 1, valor: "Sí" }
  ]
};

formData.append('propiedad_json', JSON.stringify(propiedadData));
formData.append('imagen_principal', imagenPrincipalFile);
formData.append('imagenes_galeria', galeriaFile1);
formData.append('imagenes_galeria', galeriaFile2);

const nuevaPropiedad = await fetch(`${API_BASE}/propiedades/con-imagenes`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
}).then(res => res.json());

console.log('Propiedad creada:', nuevaPropiedad.data.registro_cab_id);

// 8. Actualizar propiedad (solo lo que cambió)
const formDataUpdate = new FormData();

formDataUpdate.append('propiedad_json', JSON.stringify({
  titulo: "Oficina Premium ACTUALIZADO",
  precio_alquiler: 3800.00
}));

const actualizada = await fetch(`${API_BASE}/propiedades/actualizar-completa/25`, {
  method: 'PUT',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formDataUpdate
}).then(res => res.json());

// 9. Publicar propiedad
await fetch(`${API_BASE}/propiedades/25/estado`, {
  method: 'PATCH',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ estado: 'publicado' })
});

// 10. Contactar propiedad (público)
await fetch(`${API_BASE}/propiedades/1/contacto`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nombre: "Interesado",
    telefono: "+51999888777",
    email: "interesado@email.com",
    mensaje: "Me interesa esta propiedad"
  })
});
```

---

## 📝 **NOTAS IMPORTANTES**

### **Generales:**
1. **CORS:** Ya está configurado para permitir todas las origins
2. **Autenticación:** Los endpoints protegidos requieren header `Authorization: Bearer {token}`
3. **Paginación:** Usa `page` y `limit` para propiedades
4. **Filtros:** Combina múltiples parámetros en la URL con `&`
5. **Errores:** Todos retornan estructura consistente con `success`, `message`, `detail`

### **🗺️ Coordenadas para mapas:**
- **TODOS los endpoints de propiedades** incluyen `latitud` y `longitud`
- `/propiedades` (búsqueda pública)
- `/propiedades/mis-propiedades` (autenticado)
- `/propiedades/{id}` (detalle)

### **📸 Imágenes:**
- **Subida automática a ImageKit** en endpoints `/con-imagenes` y `/actualizar-completa`
- Límite: 1 imagen principal + hasta 5 en galería
- Máximo: 10MB por imagen
- Formatos: JPG, PNG, WEBP
- Las URLs se retornan en la respuesta

### **⭐ Endpoints destacados:**
1. **POST /propiedades/con-imagenes** - Crear propiedad completa (cabecera + detalle + imágenes) en 1 petición
2. **PUT /propiedades/actualizar-completa/{id}** - Actualizar TODO de golpe (solo envías lo que cambió)
3. **GET /caracteristicas-x-inmueble/tipo-inmueble/{id}/agrupadas** - Características agrupadas por categoría
4. **GET /propiedades/mis-propiedades** - Con estadísticas y coordenadas

### **🔐 Permisos:**
- **Ofertante/Corredor:** Puede crear y editar sus propiedades
- **Admin (perfil_id = 4):** Puede ver y editar TODAS las propiedades
- **Usuario regular:** Solo puede ver propiedades públicas

### **📊 Estados de propiedades:**
- `borrador` - No visible públicamente
- `publicado` - Visible en búsquedas públicas
- `pausado` - Temporalmente oculta
- `cerrado` - Inmueble ya vendido/alquilado

---

## 🧪 **Testing & Documentación**

**Health Check:**
```
GET https://appbackimmobiliaria-production.up.railway.app/health
```

**Documentación Interactiva (Swagger):**
```
https://appbackimmobiliaria-production.up.railway.app/docs
```

**ReDoc:**
```
https://appbackimmobiliaria-production.up.railway.app/redoc
```

---

## 🚀 **ÚLTIMAS ACTUALIZACIONES**

### **✅ Enero 2025:**
1. ✅ Agregado `latitud` y `longitud` a todas las respuestas de propiedades
2. ✅ Creado endpoint `/actualizar-completa/{id}` para actualización completa
3. ✅ Mejoras en paginación con estadísticas
4. ✅ Soporte para múltiples distritos en filtros ("1,2,3")
5. ✅ Galería de imágenes incluida en respuestas
6. ✅ Características agrupadas por categoría

---

**Versión:** 1.0  
**Última actualización:** 2025-01-20  
**Backend URL:** https://appbackimmobiliaria-production.up.railway.app  
**Estado:** ✅ Todos los endpoints funcionando en producción
