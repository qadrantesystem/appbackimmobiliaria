# 🚀 URLs RÁPIDAS - REGISTRO DE INMUEBLES

Base: `https://appbackimmobiliaria-production.up.railway.app`

---

## 🔐 AUTENTICACIÓN

```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login
```

---

## 📋 REGISTRO DE PROPIEDADES

### ⭐ Crear propiedad con fotos (TODO EN UNO)
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/con-imagenes
```
**Headers:** `Authorization: Bearer {token}`  
**Content-Type:** `multipart/form-data`  
**Límite:** 1 imagen principal + hasta 5 en galería

---

### ⭐ Actualizar propiedad completa (TODO DE GOLPE)
```
PUT https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-completa/{id}
```
**Content-Type:** `multipart/form-data`  
**Actualiza:** Cabecera + Detalle + Imágenes (solo lo que envíes)

---

### Actualizar solo imágenes
```
POST https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-imagenes/{id}
```

---

### Publicar propiedad
```
PATCH https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/{id}/estado
```
Body: `{"estado": "publicado"}`

---

## 📊 DATOS NECESARIOS (Consulta previa)

### Tipos de inmueble
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/tipos-inmueble
```

### Distritos
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/distritos
```

### Características por tipo
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/{tipo_id}/agrupadas
```

---

## 📄 Ver mis propiedades
```
GET https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/mis-propiedades?limit=50
```

---

## 📚 DOCUMENTACIÓN
```
https://appbackimmobiliaria-production.up.railway.app/docs
```
