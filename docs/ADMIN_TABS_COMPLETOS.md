# 👑 PERFIL: ADMINISTRADOR - TABS COMPLETOS

**Control total del sistema**

### Dashboard: `pages/admin/dashboard.html`

---

## 📊 Tab 1: Super Dashboard

- KPIs globales:
  - Total usuarios registrados
  - Usuarios activos (último mes)
  - Total propiedades publicadas
  - Total búsquedas realizadas
  - Transacciones cerradas
  - Revenue total
- Gráficos:
  - Usuarios nuevos por mes (línea)
  - Búsquedas totales por tipo (barras)
  - Registros totales por tipo (barras)
  - Pipeline CRM global (funnel)
  - Distribución de planes (dona)
  - Mapa de calor (distritos más buscados)
- Filtros: Año, Mes, Fecha, Tipo inmueble

---

## 👥 Tab 2: Gestión de Usuarios

- Tabla con TODOS los usuarios
- Columnas:
  - ID
  - Nombre completo
  - Email
  - Tipo usuario (user/corredor/admin)
  - Tipo perfil (demandante/ofertante/ambos)
  - Plan actual
  - Estado (activo/inactivo)
  - Búsquedas usadas
  - Registros usados
  - Fecha registro
  - Acciones
- Acciones disponibles:
  - Activar/Desactivar
  - Cambiar plan
  - Ver detalle completo
  - Editar
  - Eliminar
- Filtros: Estado, Plan, Tipo perfil
- Búsqueda por nombre/email

---

## 📥 Tab 3: Cola de Atención

- TODAS las propiedades y búsquedas que necesitan atención
- Vista de bandeja (inbox)
- Columnas:
  - ID
  - Tipo (Búsqueda/Registro)
  - Usuario propietario
  - Tipo inmueble
  - Distrito
  - Estado CRM
  - Días en estado
  - Corredor asignado
  - Acciones
- Acciones disponibles:
  - Asignar a corredor
  - Tomar (asignármelo)
  - Ver detalle
  - Cambiar estado
- Filtros: Sin asignar, Por corredor, Por estado

---

## 💳 Tab 4: Suscripciones

**Ver flujo completo:** `backend/docs/flujos/08_suscripciones_planes.md`

### Panel de Suscripciones Pendientes

```
┌─────────────────────────────────────────────────────────┐
│ 💳 GESTIÓN DE SUSCRIPCIONES                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Filtros: [Pendientes ▼] [Todos los planes ▼] [Buscar] │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ID │ Usuario │ Plan │ Monto │ Estado │ Fecha │ Acc. ││
│ ├────┼─────────┼──────┼───────┼────────┼───────┼──────┤│
│ │ 15 │ Juan P. │Premium│S/ 49 │Pendiente│14/01 │[Ver] ││
│ │ 14 │ María L.│Profes.│S/ 99 │Activa  │12/01 │[Ver] ││
│ │ 13 │ Carlos R│Premium│S/ 49 │Rechazada│10/01│[Ver] ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ KPIs:                                                   │
│ • Pendientes de aprobación: 3                          │
│ • Activas este mes: 12                                 │
│ • Rechazadas este mes: 2                               │
│ • Revenue mensual: S/ 1,245                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Acciones:
- ✅ Aprobar suscripción
- ❌ Rechazar suscripción
- 👁️ Ver comprobante de pago
- 📝 Agregar notas

### Datos requeridos:
- Usuario solicitante
- Plan seleccionado
- Comprobante de pago (imagen)
- Número de operación
- Monto pagado
- Fecha de solicitud

---

## ⚙️ Tab 5: Mantenimiento

**Layout:** Menú Lateral + Formulario Central + Lista

### Estructura:

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO DEL SISTEMA                                    │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  [FORMULARIO CENTRAL]                           │
│              │                                                  │
│ • Planes     │  Agregar/Editar registro                        │
│ • Distritos  │                                                  │
│ • Tipos      │  [Campos del formulario]                        │
│ • Caract.    │                                                  │
│ • Caract. x  │                                                  │
│   Inmueble   │  [Guardar] [Cancelar]                           │
│ • Estados    │                                                  │
│              │                                                  │
│              │  ─────────────────────────────────────────────  │
│              │                                                  │
│              │  [LISTA DE REGISTROS]                           │
│              │                                                  │
│              │  Tabla con todos los registros                  │
│              │  [Editar] [Eliminar]                            │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

### Sección 1: Planes de Suscripción

**Formulario:**
- Nombre del plan
- Descripción
- Precio (S/)
- Duración (días)
- Límite de búsquedas (-1 = ilimitado)
- Límite de registros (-1 = ilimitado)
- Características incluidas (checkboxes):
  - [ ] Alertas de búsqueda
  - [ ] Soporte prioritario
  - [ ] Estadísticas avanzadas
  - [ ] Asignación de corredor
  - [ ] Promoción destacada
- Activo: [✓]

**Lista:**
| ID | Nombre | Precio | Búsquedas | Registros | Estado | Acciones |
|----|--------|--------|-----------|-----------|--------|----------|
| 1  | Básico | Gratis | 10        | 1         | Activo | [Editar] |
| 2  | Premium| S/ 49  | ∞         | 5         | Activo | [Editar] |
| 3  | Profesional | S/ 99 | ∞    | ∞         | Activo | [Editar] |

**Tabla:** `planes_mae`

---

### Sección 2: Distritos

**Formulario:**
- Nombre del distrito
- Zona (Lima Centro, Lima Moderna, Lima Este, etc.)
- Activo: [✓]

**Lista:**
| ID | Nombre | Zona | Estado | Acciones |
|----|--------|------|--------|----------|
| 1  | San Isidro | Lima Centro | Activo | [Editar] |
| 2  | Miraflores | Lima Centro | Activo | [Editar] |
| 3  | Surco | Lima Moderna | Activo | [Editar] |
| 4  | La Molina | Lima Este | Activo | [Editar] |

**Tabla:** `distritos_mae`

---

### Sección 3: Tipos de Inmueble

**Formulario:**
- Nombre del tipo
- Descripción
- Icono (emoji o clase CSS)
- Activo: [✓]

**Lista:**
| ID | Nombre | Icono | Estado | Acciones |
|----|--------|-------|--------|----------|
| 1  | Departamento | 🏢 | Activo | [Editar] |
| 2  | Casa | 🏠 | Activo | [Editar] |
| 3  | Oficina | 🏢 | Activo | [Editar] |
| 4  | Local Comercial | 🏪 | Activo | [Editar] |
| 5  | Terreno | 🌳 | Activo | [Editar] |

**Tabla:** `tipo_inmueble_mae`

---

### Sección 4: Características

**Formulario:**
- Nombre de la característica
- Tipo de dato (checkbox, text, number, select)
- Categoría (General, Amenidades, Seguridad, etc.)
- Icono
- Requerido: [ ]
- Activo: [✓]

**Lista:**
| ID | Nombre | Tipo | Categoría | Estado | Acciones |
|----|--------|------|-----------|--------|----------|
| 1  | Amoblado | Checkbox | General | Activo | [Editar] [Asignar] |
| 2  | Piscina | Checkbox | Amenidades | Activo | [Editar] [Asignar] |
| 3  | Gimnasio | Checkbox | Amenidades | Activo | [Editar] [Asignar] |
| 4  | Seguridad 24h | Checkbox | Seguridad | Activo | [Editar] [Asignar] |

**Tabla:** `caracteristicas_mae`

**Nota:** Las características se crean primero de forma independiente, luego se asignan a tipos de inmueble en la siguiente sección.

---

### Sección 5: Relaciones Características x Inmueble

**Propósito:** Asignar características a tipos de inmueble específicos.

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO > CARACTERÍSTICAS X TIPO DE INMUEBLE          │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  ASIGNAR CARACTERÍSTICAS                        │
│              │                                                  │
│ • Planes     │  Tipo de Inmueble: [Departamento ▼]            │
│ • Distritos  │                                                  │
│ • Tipos      │  Características disponibles:                   │
│ • Caract.    │  ┌────────────────────────────────────────────┐ │
│ • Caract.x   │  │ [✓] Amoblado                               │ │
│   Inmueble ◄ │  │ [✓] Gimnasio                               │ │
│ • Estados    │  │ [✓] Seguridad 24h                          │ │
│              │  │ [ ] Piscina                                │ │
│              │  │ [✓] Ascensor                               │ │
│              │  │ [✓] Balcón                                 │ │
│              │  │ [ ] Jardín                                 │ │
│              │  │ [ ] Garaje                                 │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
│              │  [Guardar Asignaciones]                         │
│              │                                                  │
│              │  ─────────────────────────────────────────────  │
│              │                                                  │
│              │  RESUMEN POR TIPO DE INMUEBLE                   │
│              │  ┌────────────────────────────────────────────┐ │
│              │  │ Tipo         │ Características │ Acciones  │ │
│              │  ├──────────────┼─────────────────┼───────────┤ │
│              │  │ Departamento │ 15 asignadas    │ [Gestionar]│ │
│              │  │ Casa         │ 18 asignadas    │ [Gestionar]│ │
│              │  │ Oficina      │ 8 asignadas     │ [Gestionar]│ │
│              │  │ Local Com.   │ 6 asignadas     │ [Gestionar]│ │
│              │  │ Terreno      │ 4 asignadas     │ [Gestionar]│ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

**Funcionalidad:**
1. Seleccionar tipo de inmueble del dropdown
2. Ver lista de TODAS las características disponibles
3. Marcar/desmarcar las que aplican a ese tipo
4. Guardar asignaciones

**Ejemplo de asignaciones:**

**Departamento:**
- ✅ Amoblado
- ✅ Gimnasio
- ✅ Seguridad 24h
- ✅ Ascensor
- ✅ Balcón
- ❌ Piscina (no aplica)
- ❌ Jardín (no aplica)

**Casa:**
- ✅ Amoblado
- ✅ Piscina
- ✅ Jardín
- ✅ Garaje
- ✅ Seguridad 24h
- ❌ Ascensor (no aplica)

**Oficina:**
- ✅ Amoblado
- ✅ Seguridad 24h
- ✅ Ascensor
- ✅ Estacionamiento
- ❌ Piscina (no aplica)
- ❌ Jardín (no aplica)

**Tabla:** `caracteristicas_x_inmueble_mae`

**Estructura:**
```sql
CREATE TABLE caracteristicas_x_inmueble_mae (
  relacion_id SERIAL PRIMARY KEY,
  tipo_inmueble_id INTEGER REFERENCES tipo_inmueble_mae(tipo_inmueble_id),
  caracteristica_id INTEGER REFERENCES caracteristicas_mae(caracteristica_id),
  UNIQUE(tipo_inmueble_id, caracteristica_id)
);
```

**Queries:**

```sql
-- Ver características de un tipo de inmueble
SELECT 
  c.caracteristica_id,
  c.nombre,
  c.tipo_dato,
  c.categoria,
  CASE WHEN cx.relacion_id IS NOT NULL THEN true ELSE false END as asignada
FROM caracteristicas_mae c
LEFT JOIN caracteristicas_x_inmueble_mae cx 
  ON c.caracteristica_id = cx.caracteristica_id 
  AND cx.tipo_inmueble_id = 1  -- Departamento
ORDER BY c.categoria, c.nombre;

-- Asignar característica a tipo
INSERT INTO caracteristicas_x_inmueble_mae (tipo_inmueble_id, caracteristica_id)
VALUES (1, 5)  -- Departamento + Gimnasio
ON CONFLICT DO NOTHING;

-- Desasignar característica
DELETE FROM caracteristicas_x_inmueble_mae 
WHERE tipo_inmueble_id = 1 AND caracteristica_id = 5;
```

---

### Sección 6: Estados CRM

**Formulario:**
- Nombre del estado
- Descripción
- Color (hex)
- Icono
- Orden (número)
- Activo: [✓]

**Lista:**
| Orden | Nombre | Color | Icono | Estado | Acciones |
|-------|--------|-------|-------|--------|----------|
| 1 | Lead | 🔵 | 📋 | Activo | [Editar] |
| 2 | Contacto | 🟢 | 📞 | Activo | [Editar] |
| 3 | Propuesta | 🟡 | 📄 | Activo | [Editar] |
| 4 | Negociación | 🟠 | 💬 | Activo | [Editar] |
| 5 | Pre-cierre | 🟣 | 🤝 | Activo | [Editar] |
| 6 | Cerrado Ganado | 🟢 | ✅ | Activo | [Editar] |
| 7 | Cerrado Perdido | 🔴 | ❌ | Activo | [Editar] |

**Tabla:** `estados_crm_mae`

---

## 📄 Tab 6: Reportes

### Reportes Predefinidos:

1. **Usuarios por Plan**
   - Gráfico de dona
   - Tabla con detalle
   - Exportar a CSV/Excel

2. **Propiedades por Distrito**
   - Gráfico de barras
   - Mapa de calor
   - Exportar a CSV/Excel

3. **Transacciones del Mes**
   - Lista de propiedades cerradas
   - Total de comisiones
   - Performance por corredor
   - Exportar a CSV/Excel

4. **Performance de Corredores**
   - Ranking de corredores
   - Tasa de conversión
   - Comisiones generadas
   - Tiempo promedio de cierre
   - Exportar a CSV/Excel

5. **Actividad de Usuarios**
   - Usuarios activos vs inactivos
   - Búsquedas por día/semana/mes
   - Registros por día/semana/mes
   - Exportar a CSV/Excel

### Filtros Globales:
- Rango de fechas
- Tipo de inmueble
- Distrito
- Plan de suscripción
- Estado CRM

---

## 📊 Resumen de Tabs del Admin

| Tab | Nombre | Función Principal | Tabla Principal |
|-----|--------|-------------------|-----------------|
| 1 | Super Dashboard | KPIs y gráficos globales | Todas |
| 2 | Usuarios | Gestión de usuarios | `usuarios`, `suscripciones` |
| 3 | Cola | Propiedades sin asignar | `registro_x_inmueble_cab` |
| 4 | Suscripciones | Aprobar/Rechazar planes | `suscripciones` |
| 5 | Mantenimiento | CRUD de maestras | Todas las `_mae` |
| 6 | Reportes | Exportar datos | Todas |

---

## ✅ Validación con Base de Datos

**Tab 4: Suscripciones**
- ✅ `suscripciones` - Aprobar/Rechazar
- ✅ `planes_mae` - Planes disponibles
- ✅ `usuarios` - Usuarios
- ✅ Campos: `comprobante_pago`, `numero_operacion`, `estado`, `aprobado_por`, `notas_admin`

**Tab 5: Mantenimiento (6 secciones)**
- ✅ Sección 1: `planes_mae` - CRUD completo
- ✅ Sección 2: `distritos_mae` - CRUD completo
- ✅ Sección 3: `tipo_inmueble_mae` - CRUD completo
- ✅ Sección 4: `caracteristicas_mae` - CRUD completo
- ✅ Sección 5: `caracteristicas_x_inmueble_mae` - Asignar características a tipos
- ✅ Sección 6: `estados_crm_mae` - CRUD completo

**Tab 6: Reportes**
- ✅ Queries complejas de todas las tablas
- ✅ Exportación a CSV/Excel

---

## 🎯 CONCLUSIÓN

**ADMIN tiene 6 tabs completos:**
1. ✅ Super Dashboard
2. ✅ Gestión de Usuarios
3. ✅ Cola de Atención
4. ✅ Suscripciones (NUEVO)
5. ✅ Mantenimiento (NUEVO - Menú lateral + Formulario + Lista)
6. ✅ Reportes

**TODAS LAS TABLAS EXISTEN** ✅

**APROBADO PARA DESARROLLO FRONTEND** 🚀
