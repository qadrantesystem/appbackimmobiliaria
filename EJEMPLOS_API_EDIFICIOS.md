# 🧪 EJEMPLOS DE USO - API EDIFICIOS COMPLETOS

Esta guía proporciona ejemplos prácticos para probar todos los endpoints implementados.

---

## 🔐 Prerequisitos

### 1. Obtener Token de Autenticación

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tu-email@dominio.com",
    "password": "tu-password"
  }'
```

**Respuesta**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Guardar el token**:
```bash
export TOKEN="eyJhbGc..."
```

---

## 📋 EJEMPLO 1: Crear Edificio Completo

### Archivo: `edificio_completo.json`

```json
{
  "edificio": {
    "propietario_id": 1,
    "tipo_inmueble_id": 12,
    "distrito_id": 15,
    "nombre_inmueble": "Torre Empresarial Sky",
    "direccion": "Av. Javier Prado Este 456, San Isidro",
    "latitud": -12.094070,
    "longitud": -77.031750,
    "area": 1350.00,
    "antiguedad": 5,
    "implementacion": 3,
    "transaccion": "alquiler",
    "precio_alquiler": 35000.00,
    "moneda": "PEN",
    "titulo": "Edificio Corporativo Premium - San Isidro",
    "descripcion": "Moderno edificio de 9 pisos con 27 oficinas equipadas",
    "caracteristicas": [
      {"caracteristica_id": 1, "valor": "9"},
      {"caracteristica_id": 2, "valor": "2"},
      {"caracteristica_id": 5, "valor": "Si"}
    ]
  },
  "oficinas": [
    {
      "piso": 9,
      "numero_oficina": 901,
      "nombre": "Oficina 901",
      "area": 50.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"},
        {"caracteristica_id": 128, "valor": "true"}
      ]
    },
    {
      "piso": 9,
      "numero_oficina": 902,
      "nombre": "Oficina 902",
      "area": 50.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"},
        {"caracteristica_id": 125, "valor": "true"}
      ]
    },
    {
      "piso": 9,
      "numero_oficina": 903,
      "nombre": "Oficina 903",
      "area": 50.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"}
      ]
    },
    {
      "piso": 8,
      "numero_oficina": 801,
      "nombre": "Oficina 801",
      "area": 50.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"}
      ]
    },
    {
      "piso": 8,
      "numero_oficina": 802,
      "nombre": "Oficina 802",
      "area": 50.00,
      "caracteristicas": []
    },
    {
      "piso": 8,
      "numero_oficina": 803,
      "nombre": "Oficina 803",
      "area": 50.00,
      "caracteristicas": []
    }
  ],
  "sotanos": [
    {"nivel": -1, "parqueos": 20},
    {"nivel": -2, "parqueos": 25}
  ]
}
```

### Request cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/edificios/edificio-completo" \
  -H "Authorization: Bearer $TOKEN" \
  -F "edificio_json=@edificio_completo.json" \
  -F "imagen_principal=@edificio_principal.jpg" \
  -F "imagenes_galeria=@galeria1.jpg" \
  -F "imagenes_galeria=@galeria2.jpg"
```

### Respuesta esperada:

```json
{
  "success": true,
  "message": "Edificio completo creado exitosamente",
  "data": {
    "edificio": {
      "id": 15,
      "nombre": "Torre Empresarial Sky",
      "imagen_principal": "https://ik.imagekit.io/.../edificio_15_principal.jpg",
      "total_imagenes_galeria": 2
    },
    "oficinas": [
      {"id": 31, "nombre": "Oficina 901", "piso": 9, "area": 50.0, "equipamientos": 2},
      {"id": 32, "nombre": "Oficina 902", "piso": 9, "area": 50.0, "equipamientos": 2},
      {"id": 33, "nombre": "Oficina 903", "piso": 9, "area": 50.0, "equipamientos": 1}
    ],
    "total_oficinas": 6,
    "total_sotanos": 2,
    "total_parqueos": 45
  }
}
```

---

## 🔍 EJEMPLO 2: Listar Oficinas de un Edificio

### Request:

```bash
curl -X GET "http://localhost:8000/api/v1/propiedades/15/oficinas" \
  -H "Authorization: Bearer $TOKEN"
```

### Respuesta:

```json
{
  "success": true,
  "data": [
    {
      "registro_cab_id": 31,
      "nombre": "Oficina 901",
      "piso": 9,
      "area": 50.0,
      "caracteristicas": [
        {"caracteristica_id": 124, "nombre": "Aire Acondicionado", "valor": "true"},
        {"caracteristica_id": 128, "nombre": "Mobiliario", "valor": "true"}
      ]
    },
    {
      "registro_cab_id": 32,
      "nombre": "Oficina 902",
      "piso": 9,
      "area": 50.0,
      "caracteristicas": [
        {"caracteristica_id": 124, "nombre": "Aire Acondicionado", "valor": "true"},
        {"caracteristica_id": 125, "nombre": "Internet Fibra", "valor": "true"}
      ]
    }
  ],
  "message": "6 oficinas encontradas"
}
```

---

## ✏️ EJEMPLO 3: Actualizar Edificio Completo

### Escenario: Agregar 3 oficinas más en el piso 7 y eliminar la oficina 803

### Archivo: `edificio_actualizado.json`

```json
{
  "edificio": {
    "propietario_id": 1,
    "tipo_inmueble_id": 12,
    "distrito_id": 15,
    "nombre_inmueble": "Torre Empresarial Sky (Actualizado)",
    "direccion": "Av. Javier Prado Este 456, San Isidro",
    "latitud": -12.094070,
    "longitud": -77.031750,
    "area": 1350.00,
    "antiguedad": 5,
    "implementacion": 3,
    "transaccion": "alquiler",
    "precio_alquiler": 38000.00,
    "moneda": "PEN",
    "titulo": "Edificio Corporativo Premium - San Isidro (Renovado)",
    "descripcion": "Moderno edificio con oficinas equipadas y renovado",
    "caracteristicas": [
      {"caracteristica_id": 1, "valor": "9"},
      {"caracteristica_id": 2, "valor": "2"}
    ]
  },
  "oficinas": [
    {
      "piso": 9,
      "numero_oficina": 901,
      "nombre": "Oficina 901",
      "area": 55.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"},
        {"caracteristica_id": 128, "valor": "true"},
        {"caracteristica_id": 130, "valor": "true"}
      ]
    },
    {
      "piso": 9,
      "numero_oficina": 902,
      "nombre": "Oficina 902",
      "area": 50.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"}
      ]
    },
    {
      "piso": 9,
      "numero_oficina": 903,
      "nombre": "Oficina 903",
      "area": 50.00,
      "caracteristicas": []
    },
    {
      "piso": 8,
      "numero_oficina": 801,
      "nombre": "Oficina 801",
      "area": 50.00,
      "caracteristicas": []
    },
    {
      "piso": 8,
      "numero_oficina": 802,
      "nombre": "Oficina 802",
      "area": 50.00,
      "caracteristicas": []
    },
    {
      "piso": 7,
      "numero_oficina": 701,
      "nombre": "Oficina 701",
      "area": 60.00,
      "caracteristicas": [
        {"caracteristica_id": 124, "valor": "true"},
        {"caracteristica_id": 128, "valor": "true"}
      ]
    },
    {
      "piso": 7,
      "numero_oficina": 702,
      "nombre": "Oficina 702",
      "area": 60.00,
      "caracteristicas": []
    },
    {
      "piso": 7,
      "numero_oficina": 703,
      "nombre": "Oficina 703",
      "area": 60.00,
      "caracteristicas": []
    }
  ]
}
```

### Request (sin imágenes nuevas):

```bash
curl -X PUT "http://localhost:8000/api/v1/edificios/edificio-completo/15" \
  -H "Authorization: Bearer $TOKEN" \
  -F "edificio_json=@edificio_actualizado.json"
```

### Request (con imágenes nuevas):

```bash
curl -X PUT "http://localhost:8000/api/v1/edificios/edificio-completo/15" \
  -H "Authorization: Bearer $TOKEN" \
  -F "edificio_json=@edificio_actualizado.json" \
  -F "imagen_principal=@nueva_principal.jpg" \
  -F "imagenes_galeria=@nueva_galeria1.jpg"
```

### Respuesta:

```json
{
  "success": true,
  "message": "Edificio completo actualizado exitosamente",
  "data": {
    "edificio": {
      "id": 15,
      "nombre": "Torre Empresarial Sky (Actualizado)",
      "imagen_principal": "https://ik.imagekit.io/.../nueva_principal.jpg",
      "total_imagenes_galeria": 1
    },
    "total_oficinas": 8,
    "oficinas_creadas": 3,
    "oficinas_actualizadas": 5,
    "oficinas_eliminadas": 1
  }
}
```

**Cambios realizados**:
- ✅ Oficina 901: Actualizada (área 50→55, +1 equipamiento)
- ✅ Oficina 902: Actualizada (características reducidas)
- ✅ Oficinas 701-703: Creadas
- 🗑️ Oficina 803: Eliminada

---

## 📊 EJEMPLO 4: Ver Detalle de Edificio (con contador de oficinas)

### Request:

```bash
curl -X GET "http://localhost:8000/api/v1/propiedades/15" \
  -H "Authorization: Bearer $TOKEN"
```

### Respuesta (incluye `total_oficinas`):

```json
{
  "success": true,
  "data": {
    "registro_cab_id": 15,
    "titulo": "Edificio Corporativo Premium - San Isidro",
    "nombre_inmueble": "Torre Empresarial Sky",
    "tipo_inmueble": "Edificio Completo",
    "distrito": "San Isidro",
    "area": 1350.0,
    "precio_alquiler": 38000.0,
    "imagen_principal": "https://...",
    "imagenes": ["https://...", "https://..."],
    "caracteristicas": [...],
    "total_oficinas": 8,
    "vistas": 45,
    "contactos": 12
  }
}
```

---

## 🗑️ EJEMPLO 5: Eliminar Oficina Individual

### Request:

```bash
curl -X DELETE "http://localhost:8000/api/v1/propiedades/33/oficina" \
  -H "Authorization: Bearer $TOKEN"
```

### Respuesta:

```json
{
  "success": true,
  "message": "Oficina 'Oficina 903' eliminada exitosamente",
  "data": {
    "oficina_eliminada": 33,
    "edificio_padre": 15,
    "oficinas_restantes": 7
  }
}
```

### Caso de error (última oficina):

```bash
# Si solo queda 1 oficina
curl -X DELETE "http://localhost:8000/api/v1/propiedades/31/oficina" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta 400**:
```json
{
  "detail": "No puedes eliminar la última oficina del edificio. Elimina el edificio completo en su lugar."
}
```

---

## 🧪 TESTS DE VALIDACIÓN

### Test 1: Verificar que oficinas NO tienen imágenes

```bash
# Obtener detalle de una oficina
curl -X GET "http://localhost:8000/api/v1/propiedades/31" \
  -H "Authorization: Bearer $TOKEN"
```

**Validar**:
- ✅ `imagen_principal` debe ser `null`
- ✅ `imagenes` debe ser `null` o `[]`

### Test 2: Intentar eliminar oficina sin permisos

```bash
# Login con otro usuario
export TOKEN2="token_de_otro_usuario"

curl -X DELETE "http://localhost:8000/api/v1/propiedades/31/oficina" \
  -H "Authorization: Bearer $TOKEN2"
```

**Respuesta esperada 403**:
```json
{
  "detail": "No tienes permiso para eliminar esta oficina"
}
```

### Test 3: Actualizar con transacción interrumpida

```bash
# JSON con oficina duplicada (mismo piso+nombre)
# Debería hacer rollback completo
```

---

## 📈 PERFORMANCE TESTS

### Test Query Oficinas (con índices)

```sql
-- En PostgreSQL
EXPLAIN ANALYZE 
SELECT * FROM registro_x_inmueble_cab 
WHERE padre_registro_cab_id = 15;
```

**Resultado esperado**:
```
Index Scan using idx_inmueble_padre on registro_x_inmueble_cab
  (cost=0.15..8.17 rows=8 width=...)
  Planning Time: 0.123 ms
  Execution Time: 0.256 ms
```

---

## 🔄 FLUJO COMPLETO: Crear → Editar → Eliminar

### 1. Crear edificio con 3 oficinas

```bash
curl -X POST "http://localhost:8000/api/v1/edificios/edificio-completo" \
  -H "Authorization: Bearer $TOKEN" \
  -F "edificio_json=@edificio_inicial.json" \
  -F "imagen_principal=@foto.jpg"
# Respuesta: edificio_id = 20
```

### 2. Listar oficinas creadas

```bash
curl -X GET "http://localhost:8000/api/v1/propiedades/20/oficinas" \
  -H "Authorization: Bearer $TOKEN"
# Validar: 3 oficinas
```

### 3. Actualizar: Agregar 2 oficinas, modificar 1, eliminar 1

```bash
curl -X PUT "http://localhost:8000/api/v1/edificios/edificio-completo/20" \
  -H "Authorization: Bearer $TOKEN" \
  -F "edificio_json=@edificio_actualizado.json"
# Validar respuesta: creadas=2, actualizadas=2, eliminadas=1
```

### 4. Verificar contador en detalle

```bash
curl -X GET "http://localhost:8000/api/v1/propiedades/20" \
  -H "Authorization: Bearer $TOKEN"
# Validar: total_oficinas = 4
```

### 5. Eliminar una oficina específica

```bash
curl -X DELETE "http://localhost:8000/api/v1/propiedades/51/oficina" \
  -H "Authorization: Bearer $TOKEN"
# Validar: oficinas_restantes = 3
```

---

## 🐛 DEBUGGING

### Logs del Backend

```bash
# Ver logs en tiempo real
tail -f logs/backend.log | grep "edificio"
```

**Buscar**:
- `✅ Edificio creado con ID:`
- `♻️ Actualizando Oficina`
- `➕ Creando nueva Oficina`
- `🗑️ Eliminando Oficina`

### Verificar BD directamente

```sql
-- Contar oficinas de un edificio
SELECT COUNT(*) 
FROM registro_x_inmueble_cab 
WHERE padre_registro_cab_id = 15;

-- Ver oficinas con equipamiento
SELECT 
    c.nombre_inmueble,
    COUNT(d.caracteristica_id) as total_equipamiento
FROM registro_x_inmueble_cab c
LEFT JOIN registro_x_inmueble_det d ON c.registro_cab_id = d.registro_cab_id
WHERE c.padre_registro_cab_id = 15
    AND d.caracteristica_id BETWEEN 122 AND 130
GROUP BY c.nombre_inmueble;

-- Verificar que oficinas no tienen imágenes
SELECT nombre_inmueble, imagen_principal, imagenes
FROM registro_x_inmueble_cab
WHERE padre_registro_cab_id IS NOT NULL;
-- Debe retornar todo NULL
```

---

## ✅ CHECKLIST DE VALIDACIÓN

Antes de considerar completa la implementación, validar:

- [ ] POST edificio crea oficinas sin imágenes
- [ ] GET oficinas retorna características correctas
- [ ] PUT actualiza/crea/elimina oficinas correctamente
- [ ] GET detalle incluye `total_oficinas` para edificios
- [ ] DELETE oficina valida permisos y última oficina
- [ ] Transacciones hacen rollback en error
- [ ] Logs son claros y descriptivos
- [ ] Índices mejoran performance (EXPLAIN ANALYZE)

---

**¡Testing completo para edificios completos!** 🚀
