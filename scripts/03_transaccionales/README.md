# 📁 TABLAS TRANSACCIONALES

## ✅ ARCHIVOS VÁLIDOS (USAR ESTOS)

### 1. `01_registro_x_inmueble_cab.sql` ✅
- **Tabla:** `registro_x_inmueble_cab`
- **Propósito:** Cabecera de propiedades registradas
- **Registros:** 10 propiedades
- **Campos clave:** usuario_id, propietario_real_*, corredor_asignado_id, estado_crm

### 2. `02_registro_x_inmueble_det.sql` ✅
- **Tabla:** `registro_x_inmueble_det`
- **Propósito:** Detalle de características dinámicas (formulario multipaso)
- **Registros:** 33 características
- **Patrón:** EAV (Entity-Attribute-Value)

### 3. `03_suscripciones.sql` ✅
- **Tabla:** `suscripciones`
- **Propósito:** Planes de usuarios
- **Registros:** 8 suscripciones

### 4. `04_busqueda_x_inmueble_mov.sql` ✅
- **Tabla:** `busqueda_x_inmueble_mov`
- **Propósito:** Búsquedas históricas + Búsquedas guardadas con alertas
- **Registros:** 19 (15 históricas + 4 guardadas)
- **Campo clave:** `es_guardada` (true = guardada, false = histórica)

### 5. `05_registro_x_inmueble_tracking.sql` ✅
- **Tabla:** `registro_x_inmueble_tracking`
- **Propósito:** Tracking de cambios de estado CRM
- **Registros:** 15 cambios de estado
- **Estados:** lead → contacto → propuesta → negociacion → pre_cierre → cerrado

### 6. `06_favoritos.sql` ✅
- **Tabla:** `registro_x_inmueble_favoritos`
- **Propósito:** Favoritos de usuarios
- **Registros:** 12 favoritos

---

## 🗑️ ARCHIVOS OBSOLETOS (ELIMINAR)

### ❌ `01_propiedades.sql`
- **Razón:** Reemplazado por `01_registro_x_inmueble_cab.sql`
- **Acción:** ELIMINAR

### ❌ `02_propiedad_caracteristicas.sql`
- **Razón:** Reemplazado por `02_registro_x_inmueble_det.sql`
- **Acción:** ELIMINAR

### ❌ `05_registro_x_inmueble_mov.sql`
- **Razón:** Tabla de interacciones duplicada, no se usa
- **Acción:** ELIMINAR

### ❌ `07_tracking_estados.sql`
- **Razón:** Reemplazado por `05_registro_x_inmueble_tracking.sql`
- **Acción:** ELIMINAR

### ❌ `08_busquedas_guardadas.sql`
- **Razón:** Ya integrado en `04_busqueda_x_inmueble_mov.sql`
- **Acción:** ELIMINAR

---

## 📊 ORDEN DE EJECUCIÓN

El script maestro `00_ejecutar_todo.sql` ejecuta en este orden:

```sql
1. 01_registro_x_inmueble_cab.sql
2. 02_registro_x_inmueble_det.sql
3. 03_suscripciones.sql
4. 04_busqueda_x_inmueble_mov.sql
5. 05_registro_x_inmueble_tracking.sql
6. 06_favoritos.sql
```

---

## 🎯 TOTAL DE REGISTROS

```
Cabecera:        10 propiedades
Detalle:         33 características
Suscripciones:    8 planes
Búsquedas:       19 (15 + 4 guardadas)
Tracking:        15 cambios de estado
Favoritos:       12 favoritos
─────────────────────────────────
TOTAL:           97 registros
```

---

## 📚 DOCUMENTACIÓN

Ver `backend/docs/ESTRUCTURA_BD.md` para detalles completos de la arquitectura.
