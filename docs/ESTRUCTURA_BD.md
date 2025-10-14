# 📊 ESTRUCTURA DE BASE DE DATOS - RESUMEN

## 🎯 Arquitectura: Cabecera-Detalle + Movimientos

---

## 📁 TABLAS PRINCIPALES

### 1️⃣ **`registro_x_inmueble_cab`** (CABECERA)

**Propósito:** Datos generales de cada propiedad registrada

**Campos clave:**
```sql
- registro_cab_id (PK)
- usuario_id (FK) -- Usuario que registra
- propietario_real_nombre -- Nombre del propietario real
- propietario_real_dni -- DNI del propietario real
- propietario_real_telefono
- propietario_real_email
- corredor_asignado_id (FK) -- Si hay corredor
- comision_corredor
- tipo_inmueble_id, distrito_id
- nombre_inmueble, direccion, area
- habitaciones, banos, parqueos
- precio_venta, precio_alquiler
- estado_crm ('lead', 'contacto', 'propuesta', 'negociacion', 'pre_cierre', 'cerrado_ganado', 'cerrado_perdido')
- estado ('borrador', 'publicado', 'pausado', 'cerrado', 'rechazado')
- vistas, contactos, compartidos -- Métricas
```

**Relaciones:**
- 1 registro = 1 propiedad
- N características en `registro_x_inmueble_det`
- N cambios de estado en `registro_x_inmueble_tracking`
- N favoritos en `registro_x_inmueble_favoritos`

**Filtrado:**
- Usuario normal: `WHERE usuario_id = {mi_id}`
- Corredor: `WHERE corredor_asignado_id = {mi_id}`
- Admin: `SELECT *` (ve todo)

---

### 2️⃣ **`registro_x_inmueble_det`** (DETALLE)

**Propósito:** Características dinámicas del formulario multipaso

**Campos:**
```sql
- registro_det_id (PK)
- registro_cab_id (FK)
- caracteristica_id (FK)
- valor (TEXT) -- 'true', 'false', 'valor personalizado'
```

**Patrón:** EAV (Entity-Attribute-Value)

**Ejemplo:**
```sql
registro_cab_id: 1, caracteristica: "Amoblado", valor: "true"
registro_cab_id: 1, caracteristica: "Piscina", valor: "true"
registro_cab_id: 1, caracteristica: "Gimnasio", valor: "true"
```

**Ventajas:**
- Flexibilidad para agregar características sin modificar estructura
- Cada tipo de inmueble puede tener características diferentes
- Búsquedas eficientes por características específicas

---

### 3️⃣ **`busqueda_x_inmueble_mov`** (BÚSQUEDAS)

**Propósito:** Historial de búsquedas + Búsquedas guardadas con alertas

**Campos:**
```sql
- busqueda_id (PK)
- usuario_id (FK)
- tipo_inmueble_id, distritos_ids[]
- precio_min, precio_max
- area_min, area_max
- habitaciones[], banos[], parqueos_min
- filtros_avanzados (JSONB)
- cantidad_resultados

-- NUEVO: Campos para búsquedas guardadas
- es_guardada (BOOLEAN) -- true = guardada, false = histórica
- nombre_busqueda -- "Deptos San Isidro 2-3 hab"
- frecuencia_alerta -- 'inmediata', 'diaria', 'semanal'
- alerta_activa (BOOLEAN)
- ultima_notificacion
- total_notificaciones
```

**Dos usos en una tabla:**

| Tipo | es_guardada | nombre_busqueda | Alertas | Uso |
|------|-------------|-----------------|---------|-----|
| Histórica | false | NULL | No | Estadísticas, "Búsquedas recientes" |
| Guardada | true | "Deptos San Isidro" | Sí | Notificaciones automáticas |

**Ejemplo:**
```sql
-- Búsqueda histórica
INSERT INTO busqueda_x_inmueble_mov (usuario_id, tipo_inmueble_id, es_guardada)
VALUES (5, 1, false);

-- Búsqueda guardada con alertas
INSERT INTO busqueda_x_inmueble_mov (
  usuario_id, tipo_inmueble_id, es_guardada, nombre_busqueda, frecuencia_alerta, alerta_activa
) VALUES (
  5, 1, true, 'Deptos San Isidro 2-3 hab', 'diaria', true
);
```

---

### 4️⃣ **`registro_x_inmueble_tracking`** (TRACKING CRM)

**Propósito:** Seguimiento de cambios de estado en el pipeline CRM

**Campos:**
```sql
- tracking_id (PK)
- registro_cab_id (FK)
- estado_anterior
- estado_nuevo
- usuario_id (FK) -- Usuario que hizo el cambio
- corredor_id (FK) -- Corredor asignado
- motivo (TEXT)
- metadata (JSONB)
- created_at
```

**Estados CRM:**
```
lead → contacto → propuesta → negociacion → pre_cierre → cerrado_ganado/cerrado_perdido
```

**Ejemplo:**
```sql
-- Cambio de estado
INSERT INTO registro_x_inmueble_tracking (
  registro_cab_id, estado_anterior, estado_nuevo, corredor_id, motivo
) VALUES (
  1, 'lead', 'contacto', 4, 'Cliente solicitó información'
);
```

**Filtrado:**
- Corredor: `WHERE corredor_id = {mi_id}`
- Admin: `SELECT *`

---

### 5️⃣ **`registro_x_inmueble_favoritos`** (FAVORITOS)

**Propósito:** Propiedades marcadas como favoritas por usuarios

**Campos:**
```sql
- favorito_id (PK)
- usuario_id (FK)
- registro_cab_id (FK)
- notas (TEXT)
- created_at
- UNIQUE(usuario_id, registro_cab_id)
```

**Filtrado:**
- Usuario: `WHERE usuario_id = {mi_id}`

---

### 6️⃣ **`suscripciones`**

**Propósito:** Planes de usuarios

**Campos:**
```sql
- suscripcion_id (PK)
- usuario_id (FK)
- plan_id (FK)
- fecha_inicio, fecha_fin
- estado ('activa', 'cancelada', 'expirada')
```

---

## 🔄 FLUJO COMPLETO: Registro de Propiedad

### Propietario Directo:

```sql
-- 1. Crear cabecera
INSERT INTO registro_x_inmueble_cab (
  usuario_id, propietario_real_nombre, propietario_real_dni, 
  tipo_inmueble_id, nombre_inmueble, area, precio_alquiler, estado
) VALUES (
  3, 'Juan Pérez', '12345678', 1, 'Depto San Isidro', 85, 1800, 'borrador'
) RETURNING registro_cab_id; -- 11

-- 2. Agregar características
INSERT INTO registro_x_inmueble_det (registro_cab_id, caracteristica_id, valor) VALUES
(11, 1, 'true'),  -- Amoblado
(11, 5, 'true'),  -- Seguridad 24h
(11, 8, 'true');  -- Gimnasio

-- 3. Publicar
UPDATE registro_x_inmueble_cab SET estado = 'publicado' WHERE registro_cab_id = 11;

-- 4. Registrar en tracking
INSERT INTO registro_x_inmueble_tracking (registro_cab_id, estado_nuevo, usuario_id)
VALUES (11, 'lead', 3);
```

### Corredor (para cliente):

```sql
-- 1. Crear cabecera CON datos del propietario real
INSERT INTO registro_x_inmueble_cab (
  usuario_id, -- ID del corredor
  propietario_real_nombre, propietario_real_dni, propietario_real_telefono,
  corredor_asignado_id, comision_corredor,
  tipo_inmueble_id, nombre_inmueble, area, precio_alquiler, estado
) VALUES (
  4, -- Corredor
  'María López', '87654321', '+51 988777666',
  4, 5.0, -- Corredor asignado + comisión 5%
  2, 'Casa Miraflores', 180, 3500, 'borrador'
) RETURNING registro_cab_id; -- 12

-- 2-4. Mismo flujo que propietario directo
```

---

## 📊 QUERIES ÚTILES

### Ver propiedad con características:
```sql
SELECT 
  c.nombre_inmueble,
  c.precio_alquiler,
  c.area,
  c.propietario_real_nombre,
  u.nombre_completo as registrado_por,
  json_agg(
    json_build_object('caracteristica', car.nombre, 'valor', d.valor)
  ) as caracteristicas
FROM registro_x_inmueble_cab c
LEFT JOIN registro_x_inmueble_det d ON c.registro_cab_id = d.registro_cab_id
LEFT JOIN caracteristicas_mae car ON d.caracteristica_id = car.caracteristica_id
LEFT JOIN usuarios u ON c.usuario_id = u.usuario_id
WHERE c.registro_cab_id = 1
GROUP BY c.registro_cab_id, u.usuario_id;
```

### Ver propiedades de un corredor:
```sql
SELECT 
  c.registro_cab_id,
  c.nombre_inmueble,
  c.propietario_real_nombre,
  c.estado_crm,
  c.vistas,
  c.contactos
FROM registro_x_inmueble_cab c
WHERE c.corredor_asignado_id = 4
ORDER BY c.created_at DESC;
```

### Ver historial de cambios de una propiedad:
```sql
SELECT 
  t.tracking_id,
  t.estado_anterior,
  t.estado_nuevo,
  t.motivo,
  t.created_at,
  u.nombre_completo as realizado_por
FROM registro_x_inmueble_tracking t
LEFT JOIN usuarios u ON t.usuario_id = u.usuario_id
WHERE t.registro_cab_id = 1
ORDER BY t.created_at ASC;
```

### Ver búsquedas guardadas activas:
```sql
SELECT 
  b.nombre_busqueda,
  b.frecuencia_alerta,
  b.cantidad_resultados,
  b.ultima_notificacion,
  d.nombre as distrito
FROM busqueda_x_inmueble_mov b
LEFT JOIN distritos_mae d ON d.distrito_id = ANY(b.distritos_ids)
WHERE b.usuario_id = 5 
  AND b.es_guardada = true 
  AND b.alerta_activa = true
ORDER BY b.fecha_busqueda DESC;
```

### Ver favoritos de un usuario:
```sql
SELECT 
  f.favorito_id,
  f.notas,
  c.nombre_inmueble,
  c.precio_alquiler,
  c.area,
  d.nombre as distrito
FROM registro_x_inmueble_favoritos f
JOIN registro_x_inmueble_cab c ON f.registro_cab_id = c.registro_cab_id
JOIN distritos_mae d ON c.distrito_id = d.distrito_id
WHERE f.usuario_id = 1
ORDER BY f.created_at DESC;
```

---

## 🎯 RESUMEN DE DATOS

```
📁 01_seguridad/          13 registros
📁 02_maestras/          135 registros
📁 03_transaccionales/    97 registros

🎯 TOTAL: 245 registros
```

### Transaccionales (detalle):
- 10 propiedades (cabecera)
- 33 características (detalle)
- 8 suscripciones
- 19 búsquedas (15 históricas + 4 guardadas)
- 15 cambios de estado (tracking)
- 12 favoritos

---

## ✅ VENTAJAS DE ESTA ARQUITECTURA

1. **Transparencia total:** Propietario real siempre registrado
2. **Flexibilidad:** Características dinámicas sin modificar estructura
3. **Trazabilidad:** Tracking completo de cambios de estado
4. **Escalabilidad:** Fácil agregar nuevas características
5. **Filtrado eficiente:** Cada usuario ve solo su data
6. **CRM integrado:** Pipeline de ventas incorporado
7. **Alertas automáticas:** Búsquedas guardadas con notificaciones
