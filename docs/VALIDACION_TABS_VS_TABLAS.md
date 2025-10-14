# ✅ VALIDACIÓN: TABS vs TABLAS DE BASE DE DATOS

## 🎯 Objetivo
Validar que las tablas de la base de datos cubren TODOS los tabs definidos en el frontend.

---

## 🔍 PERFIL: DEMANDANTE

### Tab 1: Dashboard 📊

**KPIs requeridos:**
- ✅ Búsquedas realizadas → `busqueda_x_inmueble_mov WHERE usuario_id=X AND es_guardada=false`
- ✅ Búsquedas restantes → `suscripciones.limite_busquedas - COUNT(busquedas)`
- ✅ Favoritos totales → `COUNT(*) FROM registro_x_inmueble_favoritos WHERE usuario_id=X`
- ✅ Búsquedas guardadas → `COUNT(*) FROM busqueda_x_inmueble_mov WHERE usuario_id=X AND es_guardada=true`

**Gráficos:**
- ✅ Búsquedas por tipo → `busqueda_x_inmueble_mov GROUP BY tipo_inmueble_id`
- ✅ Actividad mensual → `busqueda_x_inmueble_mov GROUP BY MONTH(fecha_busqueda)`

**Timeline:**
- ✅ Actividad reciente → `busqueda_x_inmueble_mov ORDER BY fecha_busqueda DESC LIMIT 10`

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 2: Favoritos ❤️

**Datos requeridos:**
```sql
SELECT 
  f.favorito_id,
  f.notas,
  f.created_at,
  c.imagen_principal,
  c.titulo,
  c.nombre_inmueble,
  t.nombre as tipo,
  d.nombre as distrito,
  c.precio_alquiler,
  c.precio_venta
FROM registro_x_inmueble_favoritos f
JOIN registro_x_inmueble_cab c ON f.registro_cab_id = c.registro_cab_id
JOIN tipo_inmueble_mae t ON c.tipo_inmueble_id = t.tipo_inmueble_id
JOIN distritos_mae d ON c.distrito_id = d.distrito_id
WHERE f.usuario_id = X
ORDER BY f.created_at DESC;
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 3: Historial de Búsquedas 🕐

**Datos requeridos:**
```sql
SELECT 
  b.busqueda_id,
  b.fecha_busqueda,
  t.nombre as tipo_inmueble,
  b.distritos_ids,
  b.precio_min,
  b.precio_max,
  b.cantidad_resultados,
  b.es_guardada,
  b.nombre_busqueda
FROM busqueda_x_inmueble_mov b
LEFT JOIN tipo_inmueble_mae t ON b.tipo_inmueble_id = t.tipo_inmueble_id
WHERE b.usuario_id = X
ORDER BY b.fecha_busqueda DESC;
```

**Filtros:**
- ✅ Por fecha → `WHERE fecha_busqueda BETWEEN X AND Y`
- ✅ Por año/mes → `WHERE YEAR(fecha_busqueda) = X`

**Acciones:**
- ✅ Repetir búsqueda → Usar criterios de `busqueda_x_inmueble_mov`
- ✅ Ver resultados → Query a `registro_x_inmueble_cab` con criterios
- ✅ Guardar → `UPDATE busqueda_x_inmueble_mov SET es_guardada=true, nombre_busqueda=X`

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 4: Mi Perfil 👤

**Datos requeridos:**
```sql
SELECT 
  u.*,
  s.plan_id,
  p.nombre as plan_nombre,
  p.limite_busquedas,
  p.limite_registros,
  s.fecha_inicio,
  s.fecha_fin,
  s.estado
FROM usuarios u
LEFT JOIN suscripciones s ON u.usuario_id = s.usuario_id
LEFT JOIN planes_mae p ON s.plan_id = p.plan_id
WHERE u.usuario_id = X;
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

## 🏠 PERFIL: OFERTANTE (Propietario)

### Tab 1: Dashboard 📊

**KPIs requeridos:**
- ✅ Propiedades publicadas → `COUNT(*) FROM registro_x_inmueble_cab WHERE usuario_id=X`
- ✅ Registros restantes → `suscripciones.limite_registros - COUNT(propiedades)`
- ✅ Total vistas → `SUM(vistas) FROM registro_x_inmueble_cab WHERE usuario_id=X`
- ✅ Total contactos → `SUM(contactos) FROM registro_x_inmueble_cab WHERE usuario_id=X`

**Gráficos:**
- ✅ Registros por tipo → `registro_x_inmueble_cab GROUP BY tipo_inmueble_id`
- ✅ Estado propiedades → `registro_x_inmueble_cab GROUP BY estado`

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 2: Mis Propiedades 🏢

**Datos requeridos:**
```sql
SELECT 
  c.registro_cab_id,
  c.imagen_principal,
  c.titulo,
  c.nombre_inmueble,
  c.estado,
  c.estado_crm,
  c.vistas,
  c.contactos,
  c.corredor_asignado_id,
  u.nombre_completo as corredor_nombre,
  COUNT(f.favorito_id) as total_favoritos
FROM registro_x_inmueble_cab c
LEFT JOIN usuarios u ON c.corredor_asignado_id = u.usuario_id
LEFT JOIN registro_x_inmueble_favoritos f ON c.registro_cab_id = f.registro_cab_id
WHERE c.usuario_id = X
GROUP BY c.registro_cab_id
ORDER BY c.created_at DESC;
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 3: Favoritos ❤️

**ESTADO:** ✅ IGUAL QUE DEMANDANTE

---

### Tab 4: Mi Perfil 👤

**ESTADO:** ✅ IGUAL QUE DEMANDANTE

---

## 🔄 PERFIL: AMBOS (Demandante + Ofertante)

### Tab 1: Dashboard 📊

**KPIs combinados:**
- ✅ Búsquedas realizadas → `busqueda_x_inmueble_mov`
- ✅ Propiedades publicadas → `registro_x_inmueble_cab`
- ✅ Favoritos totales → `registro_x_inmueble_favoritos`
- ✅ Contactos en mis propiedades → `SUM(contactos) FROM registro_x_inmueble_cab`

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tabs 2-5

**ESTADO:** ✅ COMBINACIÓN DE DEMANDANTE + OFERTANTE

---

## 🤝 PERFIL: CORREDOR

### Tab 1: Pipeline CRM 🎯

**Datos requeridos:**
```sql
-- Contar por estado
SELECT 
  estado_crm,
  COUNT(*) as total
FROM registro_x_inmueble_cab
WHERE corredor_asignado_id = X
GROUP BY estado_crm;

-- Cards por estado
SELECT 
  c.registro_cab_id,
  c.nombre_inmueble,
  c.propietario_real_nombre,
  c.estado_crm,
  c.precio_alquiler,
  c.precio_venta,
  t.nombre as tipo,
  d.nombre as distrito,
  c.created_at,
  (SELECT MAX(created_at) FROM registro_x_inmueble_tracking WHERE registro_cab_id = c.registro_cab_id) as ultima_actualizacion
FROM registro_x_inmueble_cab c
JOIN tipo_inmueble_mae t ON c.tipo_inmueble_id = t.tipo_inmueble_id
JOIN distritos_mae d ON c.distrito_id = d.distrito_id
WHERE c.corredor_asignado_id = X
ORDER BY c.estado_crm, c.created_at DESC;
```

**Arrastrar entre columnas:**
```sql
-- Cambiar estado
UPDATE registro_x_inmueble_cab 
SET estado_crm = 'nuevo_estado' 
WHERE registro_cab_id = X;

-- Registrar en tracking
INSERT INTO registro_x_inmueble_tracking (
  registro_cab_id, estado_anterior, estado_nuevo, corredor_id, motivo
) VALUES (X, 'lead', 'contacto', Y, 'Cliente respondió llamada');
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 2: Mis Leads 📋

**Datos requeridos:**
```sql
SELECT 
  c.registro_cab_id as id_lead,
  'Registro' as tipo,
  c.propietario_real_nombre as cliente,
  t.nombre as tipo_inmueble,
  d.nombre as distrito,
  c.estado_crm,
  (SELECT MAX(created_at) FROM registro_x_inmueble_tracking WHERE registro_cab_id = c.registro_cab_id) as ultima_actualizacion
FROM registro_x_inmueble_cab c
JOIN tipo_inmueble_mae t ON c.tipo_inmueble_id = t.tipo_inmueble_id
JOIN distritos_mae d ON c.distrito_id = d.distrito_id
WHERE c.corredor_asignado_id = X
ORDER BY ultima_actualizacion DESC;
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 3: Cola de Atención 📥

**Propiedades SIN asignar:**
```sql
SELECT 
  c.registro_cab_id,
  c.nombre_inmueble,
  c.propietario_real_nombre,
  t.nombre as tipo,
  d.nombre as distrito,
  c.estado_crm,
  c.created_at,
  DATEDIFF(NOW(), c.created_at) as dias_sin_asignar
FROM registro_x_inmueble_cab c
JOIN tipo_inmueble_mae t ON c.tipo_inmueble_id = t.tipo_inmueble_id
JOIN distritos_mae d ON c.distrito_id = d.distrito_id
WHERE c.corredor_asignado_id IS NULL
  AND c.estado = 'publicado'
ORDER BY c.created_at ASC;
```

**Tomar lead:**
```sql
UPDATE registro_x_inmueble_cab 
SET corredor_asignado_id = X, comision_corredor = 5.0
WHERE registro_cab_id = Y;

INSERT INTO registro_x_inmueble_tracking (
  registro_cab_id, estado_anterior, estado_nuevo, corredor_id, motivo
) VALUES (Y, NULL, 'lead', X, 'Lead asignado a corredor');
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 4: Métricas 📈

**KPIs requeridos:**
```sql
-- Leads totales
SELECT COUNT(*) FROM registro_x_inmueble_cab WHERE corredor_asignado_id = X;

-- Por estado
SELECT estado_crm, COUNT(*) 
FROM registro_x_inmueble_cab 
WHERE corredor_asignado_id = X 
GROUP BY estado_crm;

-- Cerrados ganados
SELECT COUNT(*) FROM registro_x_inmueble_cab 
WHERE corredor_asignado_id = X AND estado_crm = 'cerrado_ganado';

-- Comisiones del mes
SELECT SUM(comision_corredor * COALESCE(precio_venta, precio_alquiler * 12) / 100) as comisiones
FROM registro_x_inmueble_cab
WHERE corredor_asignado_id = X 
  AND estado_crm = 'cerrado_ganado'
  AND MONTH(updated_at) = MONTH(NOW());
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 5: Calendario 📅

**✅ CUBIERTO POR:** `registro_x_inmueble_tracking`

**Query para calendario:**
```sql
SELECT 
  t.tracking_id,
  t.registro_cab_id,
  c.nombre_inmueble,
  c.propietario_real_nombre,
  t.estado_nuevo as evento,
  t.motivo as descripcion,
  t.created_at as fecha_evento,
  t.metadata->>'proxima_accion' as proxima_accion,
  t.metadata->>'fecha_programada' as fecha_programada
FROM registro_x_inmueble_tracking t
JOIN registro_x_inmueble_cab c ON t.registro_cab_id = c.registro_cab_id
WHERE t.corredor_id = X
  AND (t.created_at >= CURDATE() OR t.metadata->>'fecha_programada' >= CURDATE())
ORDER BY COALESCE(t.metadata->>'fecha_programada', t.created_at) ASC;
```

**Uso del campo `metadata` para próximas acciones:**
```sql
-- Registrar seguimiento con próxima acción
INSERT INTO registro_x_inmueble_tracking (
  registro_cab_id, estado_anterior, estado_nuevo, corredor_id, motivo, metadata
) VALUES (
  1, 'contacto', 'propuesta', 4, 
  'Cliente interesado, enviar propuesta formal',
  '{"proxima_accion": "Enviar propuesta por email", "fecha_programada": "2025-01-30 10:00:00"}'
);
```

**ESTADO:** ✅ TABLA EXISTENTE - NO SE NECESITA NUEVA TABLA

---

## 👑 PERFIL: ADMINISTRADOR

### Tab 1: Super Dashboard 📊

**KPIs globales:**
- ✅ Total usuarios → `COUNT(*) FROM usuarios`
- ✅ Usuarios activos → `COUNT(*) FROM usuarios WHERE last_login > DATE_SUB(NOW(), INTERVAL 30 DAY)`
- ✅ Total propiedades → `COUNT(*) FROM registro_x_inmueble_cab`
- ✅ Total búsquedas → `COUNT(*) FROM busqueda_x_inmueble_mov`
- ✅ Transacciones cerradas → `COUNT(*) FROM registro_x_inmueble_cab WHERE estado_crm = 'cerrado_ganado'`

**Gráficos:**
- ✅ Usuarios nuevos por mes → `usuarios GROUP BY MONTH(created_at)`
- ✅ Búsquedas por tipo → `busqueda_x_inmueble_mov GROUP BY tipo_inmueble_id`
- ✅ Registros por tipo → `registro_x_inmueble_cab GROUP BY tipo_inmueble_id`
- ✅ Pipeline CRM global → `registro_x_inmueble_cab GROUP BY estado_crm`
- ✅ Distribución de planes → `suscripciones GROUP BY plan_id`

**Mapa de calor:**
- ✅ Distritos más buscados → `busqueda_x_inmueble_mov, unnest(distritos_ids) GROUP BY distrito_id`

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 2: Gestión de Usuarios 👥

**Datos requeridos:**
```sql
SELECT 
  u.usuario_id,
  u.nombre_completo,
  u.email,
  u.perfil_id,
  p.nombre as perfil_nombre,
  s.plan_id,
  pl.nombre as plan_nombre,
  u.estado,
  (SELECT COUNT(*) FROM busqueda_x_inmueble_mov WHERE usuario_id = u.usuario_id) as busquedas_usadas,
  (SELECT COUNT(*) FROM registro_x_inmueble_cab WHERE usuario_id = u.usuario_id) as registros_usados,
  u.created_at
FROM usuarios u
LEFT JOIN perfiles p ON u.perfil_id = p.perfil_id
LEFT JOIN suscripciones s ON u.usuario_id = s.usuario_id
LEFT JOIN planes_mae pl ON s.plan_id = pl.plan_id
ORDER BY u.created_at DESC;
```

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 3: Cola de Atención 📥

**ESTADO:** ✅ IGUAL QUE CORREDOR (pero ve TODAS, no solo las asignadas)

---

### Tab 4: Configuración ⚙️

**Tipos de Inmueble:**
- ✅ `tipo_inmueble_mae` - CRUD completo

**Características:**
- ✅ `caracteristicas_mae` - CRUD completo
- ✅ `caracteristicas_x_inmueble_mae` - Relaciones

**Estados CRM:**
- ✅ `estados_crm_mae` - CRUD completo

**Planes:**
- ✅ `planes_mae` - CRUD completo

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

### Tab 5: Reportes 📄

**Reportes disponibles:**
- ✅ Usuarios por plan → `usuarios JOIN suscripciones JOIN planes_mae`
- ✅ Propiedades por distrito → `registro_x_inmueble_cab JOIN distritos_mae`
- ✅ Transacciones del mes → `registro_x_inmueble_cab WHERE estado_crm = 'cerrado_ganado'`
- ✅ Performance corredores → `registro_x_inmueble_cab GROUP BY corredor_asignado_id`

**ESTADO:** ✅ TODAS LAS TABLAS EXISTEN

---

## 📊 RESUMEN FINAL

### ✅ TABLAS QUE CUBREN TODO (6):

1. ✅ `registro_x_inmueble_cab` - Propiedades (cabecera)
2. ✅ `registro_x_inmueble_det` - Características (detalle)
3. ✅ `busqueda_x_inmueble_mov` - Búsquedas históricas + guardadas
4. ✅ `registro_x_inmueble_favoritos` - Favoritos
5. ✅ `registro_x_inmueble_tracking` - Tracking CRM
6. ✅ `suscripciones` - Planes y límites

### ✅ TABLAS MAESTRAS (6):

1. ✅ `usuarios` - Usuarios
2. ✅ `perfiles` - Roles
3. ✅ `planes_mae` - Planes
4. ✅ `tipo_inmueble_mae` - Tipos
5. ✅ `distritos_mae` - Distritos
6. ✅ `caracteristicas_mae` - Características
7. ✅ `caracteristicas_x_inmueble_mae` - Relaciones
8. ✅ `estados_crm_mae` - Estados CRM

---

## 🎉 CONCLUSIÓN

### ✅ COBERTURA: 100%

**TODOS los tabs están cubiertos por las tablas existentes:**

**Las tablas actuales permiten:**
- ✅ Dashboard de Demandante (100%)
- ✅ Dashboard de Ofertante (100%)
- ✅ Dashboard Ambos (100%)
- ✅ Dashboard Corredor (100%) - Calendario cubierto por `registro_x_inmueble_tracking`
- ✅ Dashboard Admin (100%)

---

## 🚀 RECOMENDACIÓN

**PROCEDER CON LA CREACIÓN DE LOS HTMLs** ✅

Las tablas están perfectas para soportar TODOS los tabs definidos.

**Calendario de corredor:** Cubierto por `registro_x_inmueble_tracking` usando el campo `metadata` para próximas acciones programadas.

**Fecha de validación:** 2025-01-25  
**Estado:** APROBADO PARA DESARROLLO FRONTEND ✅  
**Cobertura:** 100% - NO SE NECESITAN TABLAS ADICIONALES
