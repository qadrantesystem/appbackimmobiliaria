# 🔄 NUEVA API: ACTUALIZACIÓN COMPLETA DE PROPIEDADES

## ✅ **CREADA CON ÉXITO**

---

## 📍 **URL DEL ENDPOINT:**

```
PUT https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/actualizar-completa/{id}
```

---

## 🎯 **¿QUÉ HACE?**

Actualiza **TODO DE GOLPE** en una sola petición:

1. ✅ **Cabecera** (registro_x_inmueble_cab)
   - Título, dirección, área, precios, etc.
   
2. ✅ **Detalle** (registro_x_inmueble_det)
   - Características completas (reemplaza todas)
   
3. ✅ **Imágenes** (ImageKit)
   - Imagen principal
   - Galería (hasta 5 fotos)

---

## 💡 **VENTAJAS:**

- ✅ **Actualización parcial:** Solo envías lo que quieres cambiar
- ✅ **Flexible:** Todos los campos son opcionales
- ✅ **Transaccional:** Si algo falla, hace ROLLBACK completo
- ✅ **Seguro:** Valida permisos (dueño o admin)
- ✅ **Optimizado:** Mantiene datos actuales si no envías cambios
- ✅ **Logging:** Registra cada paso para debugging

---

## 📋 **EJEMPLO DE USO:**

### **Caso 1: Solo actualizar precio y título**

```json
// FormData
{
  "propiedad_json": {
    "titulo": "Oficina Premium ACTUALIZADO",
    "precio_alquiler": 3800.00
  }
}
// No enviar imágenes ni características
```

### **Caso 2: Actualizar todo**

```json
// FormData
{
  "propiedad_json": {
    "titulo": "Nuevo título",
    "precio_alquiler": 4000.00,
    "latitud": -12.1000,
    "longitud": -77.0400,
    "caracteristicas": [
      {"caracteristica_id": 1, "valor": "Sí"},
      {"caracteristica_id": 2, "valor": "24/7"}
    ]
  },
  "imagen_principal": [archivo_nuevo.jpg],
  "imagenes_galeria": [foto1.jpg, foto2.jpg]
}
```

### **Caso 3: Solo cambiar imágenes**

```json
// FormData
{
  "imagen_principal": [nueva_principal.jpg],
  "imagenes_galeria": [galeria1.jpg, galeria2.jpg]
}
// No enviar propiedad_json
```

---

## 🔒 **PERMISOS:**

- ✅ Dueño de la propiedad puede actualizar
- ✅ Admin (perfil_id = 4) puede actualizar CUALQUIER propiedad
- ❌ Otros usuarios reciben 403 Forbidden

---

## 📤 **RESPUESTA:**

```json
{
  "success": true,
  "message": "Propiedad actualizada exitosamente",
  "data": {
    "registro_cab_id": 25,
    "titulo": "Oficina Premium ACTUALIZADO",
    "estado": "publicado",
    "imagen_principal_nueva": "https://...",
    "imagenes_galeria_nuevas": ["https://...", "https://..."],
    "total_imagenes_galeria": 2
  }
}
```

---

## 🆚 **COMPARACIÓN CON OTROS MÉTODOS:**

| Método | Actualiza Cabecera | Actualiza Detalle | Actualiza Imágenes | Peticiones |
|--------|-------------------|-------------------|-------------------|------------|
| **actualizar-completa** ⭐ | ✅ | ✅ | ✅ | **1** |
| actualizar-imagenes | ❌ | ❌ | ✅ | 1 |
| PATCH /estado | ❌ (solo estado) | ❌ | ❌ | 1 |
| **Método anterior** | ❌ No existía | ❌ No existía | ✅ | **3+** |

---

## 🚀 **MEJORES PRÁCTICAS IMPLEMENTADAS:**

### 1. **Actualización Parcial**
Solo actualizas lo que envías. Validación: `if campo is not None`

### 2. **Transaccional**
```python
try:
    # Actualizar cabecera
    # Actualizar características
    # Subir imágenes
    db.commit()  # Todo o nada
except:
    db.rollback()  # Revierte todo
```

### 3. **Validación de Permisos**
```python
if current_user.perfil_id != 4 and propiedad.usuario_id != current_user.usuario_id:
    raise 403
```

### 4. **Logging Detallado**
```python
logger.info("🔍 Buscando propiedad...")
logger.info("✅ Permisos validados")
logger.info("📝 Actualizando cabecera...")
```

### 5. **Manejo de Errores**
```python
except HTTPException:
    raise  # Re-lanzar errores HTTP
except json.JSONDecodeError:
    raise HTTPException(400, "JSON inválido")
except Exception as e:
    db.rollback()
    raise HTTPException(500, str(e))
```

---

## 📝 **CAMPOS ACTUALIZABLES:**

### **Propietario:**
- propietario_real_nombre
- propietario_real_dni
- propietario_real_telefono
- propietario_real_email

### **Ubicación:**
- tipo_inmueble_id
- distrito_id
- nombre_inmueble
- direccion
- **latitud** 🗺️
- **longitud** 🗺️

### **Características:**
- area
- habitaciones
- banos
- parqueos
- antiguedad

### **Comercial:**
- transaccion
- precio_venta
- precio_alquiler
- moneda

### **Contenido:**
- titulo
- descripcion

### **Detalle:**
- caracteristicas[] (array completo)

### **Imágenes:**
- imagen_principal (File)
- imagenes_galeria (File[])

---

## ✅ **ESTADO:**

- ✅ Código implementado en `propiedades_upload.py`
- ✅ Schema `PropiedadUpdateComplete` creado
- ✅ Validaciones completas
- ✅ Logging implementado
- ✅ Manejo de errores robusto
- ✅ Documentación completa
- ⏳ Pendiente deploy a Railway

---

## 🧪 **PRUEBAS:**

Después del deploy, probar con:
```powershell
# Test actualización solo título
PUT /actualizar-completa/25
FormData: {
  propiedad_json: '{"titulo": "Test Actualizado"}'
}

# Test actualización completa
PUT /actualizar-completa/25
FormData: {
  propiedad_json: '{...}',
  imagen_principal: [archivo],
  imagenes_galeria: [archivo1, archivo2]
}
```

---

**Fecha:** 2025-01-20  
**Archivo:** `app/api/v1/propiedades_upload.py` (líneas 347-621)  
**Endpoint:** `PUT /api/v1/propiedades/actualizar-completa/{id}`  
**Status:** ✅ Implementado, pendiente deploy
