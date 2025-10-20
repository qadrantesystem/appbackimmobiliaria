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

### 6. **Propiedades (búsqueda pública)**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades
```

**Con filtros:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?tipo_inmueble_id=1&distrito_id=1&limit=10&offset=0
```

**Parámetros de filtro disponibles:**
- `tipo_inmueble_id` - Filtrar por tipo
- `distrito_id` - Filtrar por distrito  
- `precio_min` - Precio mínimo
- `precio_max` - Precio máximo
- `area_min` - Área mínima (m²)
- `area_max` - Área máxima (m²)
- `limit` - Cantidad de resultados (default: 10)
- `offset` - Para paginación (default: 0)

---

### 7. **Detalle de Propiedad**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{propiedad_id}
```
**Ejemplo:**
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/1
```

---

## 🔐 **ENDPOINTS CON AUTENTICACIÓN**

### 8. **Login**
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

### 9. **Registro**
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

### 10. **Favoritos** (requiere token)
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

### 11. **Búsquedas guardadas** (requiere token)
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

## 📋 **RESUMEN PARA FRONTEND**

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
// 1. Obtener tipos de inmueble para select
const tiposInmueble = await fetch('https://appbackimmobiliaria-production.up.railway.app/api/v1/tipos-inmueble')
  .then(res => res.json());

// 2. Obtener distritos para select
const distritos = await fetch('https://appbackimmobiliaria-production.up.railway.app/api/v1/distritos')
  .then(res => res.json());

// 3. Obtener características agrupadas para filtros avanzados
const caracteristicas = await fetch('https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/1/agrupadas')
  .then(res => res.json());

// 4. Buscar propiedades con filtros
const propiedades = await fetch('https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?tipo_inmueble_id=1&distrito_id=1&limit=20')
  .then(res => res.json());

// 5. Login y guardar token
const loginResponse = await fetch('https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@email.com', password: 'pass123' })
}).then(res => res.json());

const token = loginResponse.data.access_token;
localStorage.setItem('token', token);

// 6. Usar endpoints autenticados
const favoritos = await fetch('https://appbackimmobiliaria-production.up.railway.app/api/v1/favoritos', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(res => res.json());
```

---

## 📝 **NOTAS IMPORTANTES**

1. **CORS:** Ya está configurado para permitir todas las origins
2. **Autenticación:** Los endpoints protegidos requieren header `Authorization: Bearer {token}`
3. **Paginación:** Usa `limit` y `offset` para propiedades
4. **Filtros:** Combina múltiples parámetros en la URL con `&`
5. **Errores:** Todos retornan estructura consistente con `success`, `message`, `detail`

---

## 🧪 **Testing**

**Health Check:**
```
GET https://appbackimmobiliaria-production.up.railway.app/health
```

**Documentación Interactiva:**
```
https://appbackimmobiliaria-production.up.railway.app/docs
```
