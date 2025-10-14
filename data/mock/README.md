# 📦 Mock Data - API Simulada

Este directorio contiene archivos JSON que simulan las respuestas de tu API backend. Cada archivo representa una tabla de la base de datos con **FILAS (registros)** reales de ejemplo.

## 📁 Estructura de Archivos

### Tablas Maestras (Catálogos)
| Archivo | Tabla | Registros | Descripción |
|---------|-------|-----------|-------------|
| `perfiles.json` | perfiles | 3 | Tipos de usuario (arrendatario, propietario, admin) |
| `planes_mae.json` | planes_mae | 4 | Planes de suscripción (Gratuito, Básico, Profesional, Empresarial) |
| `tipo_inmueble_mae.json` | tipo_inmueble_mae | 12 | Tipos de inmuebles (Oficina, Casa, Departamento, etc.) |
| `distritos_mae.json` | distritos_mae | 10 | Distritos de Lima |
| `caracteristicas_mae.json` | caracteristicas_mae | 51 | Catálogo de características (GYM, parqueos, etc.) |

### Tablas de Relación
| Archivo | Tabla | Registros | Descripción |
|---------|-------|-----------|-------------|
| `caracteristicas_x_inmueble_mae.json` | caracteristicas_x_inmueble_mae | 51 | Qué características aplican a cada tipo de inmueble |

### Tablas Principales
| Archivo | Tabla | Registros | Descripción |
|---------|-------|-----------|-------------|
| `usuarios.json` | usuarios | 10 | Usuarios del sistema |
| `propiedades.json` | propiedades | 10 | Inmuebles publicados |
| `suscripciones.json` | suscripciones | 8 | Suscripciones activas de usuarios |

### Tablas de Valores
| Archivo | Tabla | Registros | Descripción |
|---------|-------|-----------|-------------|
| `propiedad_caracteristicas.json` | propiedad_caracteristicas | 33 | Valores específicos de características por propiedad |

### Tablas de Movimientos (Transaccionales)
| Archivo | Tabla | Registros | Descripción |
|---------|-------|-----------|-------------|
| `busqueda_x_inmueble_mov.json` | busqueda_x_inmueble_mov | 15 | Historial de búsquedas realizadas |
| `registro_x_inmueble_mov.json` | registro_x_inmueble_mov | 20 | Interacciones (vistas, favoritos, contactos) |

---

## 🔍 Formato de Respuesta

Todos los archivos siguen el mismo formato de respuesta API:

```json
{
  "success": true,
  "data": [
    { /* registro 1 */ },
    { /* registro 2 */ },
    { /* registro N */ }
  ],
  "total": N
}
```

---

## 💡 Ejemplos de Uso

### 1. Obtener todos los perfiles

**Endpoint simulado**: `GET /api/perfiles`

**Archivo**: `perfiles.json`

```javascript
// Frontend
fetch('/api/perfiles')
  .then(res => res.json())
  .then(data => {
    console.log('Perfiles:', data.data);
    // data.data = [{ perfil_id: 1, nombre: "arrendatario", ... }, ...]
  });
```

### 2. Obtener propiedades

**Endpoint simulado**: `GET /api/propiedades`

**Archivo**: `propiedades.json`

```javascript
// Frontend
fetch('/api/propiedades')
  .then(res => res.json())
  .then(data => {
    const propiedades = data.data;
    propiedades.forEach(prop => {
      console.log(`${prop.titulo} - $${prop.precio_alquiler}/mes`);
    });
  });
```

### 3. Buscar propiedades con filtros

**Endpoint simulado**: `POST /api/propiedades/buscar`

**Lógica**: Filtrar `propiedades.json` en el frontend

```javascript
// Frontend - Simular búsqueda
const filtros = {
  tipo_inmueble_id: 1,
  distritos_ids: [1, 3],
  transaccion: "alquiler",
  precio_max: 5000,
  area_min: 400,
  area_max: 600
};

fetch('/api/propiedades')
  .then(res => res.json())
  .then(data => {
    const resultados = data.data.filter(prop => {
      return prop.tipo_inmueble_id === filtros.tipo_inmueble_id &&
             filtros.distritos_ids.includes(prop.distrito_id) &&
             prop.precio_alquiler <= filtros.precio_max &&
             prop.area >= filtros.area_min &&
             prop.area <= filtros.area_max;
    });
    console.log('Resultados:', resultados);
  });
```

### 4. Obtener características de un tipo de inmueble

**Endpoint simulado**: `GET /api/caracteristicas/tipo/{tipo_inmueble_id}`

**Lógica**: Combinar `caracteristicas_x_inmueble_mae.json` + `caracteristicas_mae.json`

```javascript
// Frontend
const tipoInmuebleId = 1; // Oficina en Edificio

Promise.all([
  fetch('/api/caracteristicas_x_inmueble_mae').then(r => r.json()),
  fetch('/api/caracteristicas_mae').then(r => r.json())
]).then(([relaciones, caracteristicas]) => {
  // Filtrar relaciones para este tipo
  const relacionesTipo = relaciones.data.filter(
    r => r.tipo_inmueble_id === tipoInmuebleId
  );
  
  // Obtener IDs de características
  const caracIds = relacionesTipo.map(r => r.caracteristica_id);
  
  // Obtener características completas
  const caracteristicasTipo = caracteristicas.data.filter(
    c => caracIds.includes(c.caracteristica_id)
  );
  
  console.log('Características para Oficina:', caracteristicasTipo);
});
```

### 5. Obtener historial de búsquedas de un usuario

**Endpoint simulado**: `GET /api/busquedas/usuario/{usuario_id}`

**Archivo**: `busqueda_x_inmueble_mov.json`

```javascript
// Frontend
const usuarioId = 1;

fetch('/api/busqueda_x_inmueble_mov')
  .then(res => res.json())
  .then(data => {
    const busquedasUsuario = data.data.filter(
      b => b.usuario_id === usuarioId
    );
    console.log('Búsquedas del usuario:', busquedasUsuario);
  });
```

### 6. Obtener favoritos de un usuario

**Endpoint simulado**: `GET /api/favoritos/usuario/{usuario_id}`

**Lógica**: Filtrar `registro_x_inmueble_mov.json` + `propiedades.json`

```javascript
// Frontend
const usuarioId = 1;

Promise.all([
  fetch('/api/registro_x_inmueble_mov').then(r => r.json()),
  fetch('/api/propiedades').then(r => r.json())
]).then(([registros, propiedades]) => {
  // Filtrar favoritos del usuario
  const favoritos = registros.data.filter(
    r => r.usuario_id === usuarioId && r.tipo_interaccion === 'favorito'
  );
  
  // Obtener IDs de propiedades favoritas
  const propIds = favoritos.map(f => f.propiedad_id);
  
  // Obtener propiedades completas
  const propiedadesFavoritas = propiedades.data.filter(
    p => propIds.includes(p.propiedad_id)
  );
  
  console.log('Favoritos:', propiedadesFavoritas);
});
```

---

## 🔗 Relaciones entre Tablas

### Diagrama de Relaciones Principales

```
usuarios
├── perfil_id → perfiles
├── plan_id → planes_mae
└── suscripciones (1:N)

propiedades
├── propietario_id → usuarios
├── tipo_inmueble_id → tipo_inmueble_mae
├── distrito_id → distritos_mae
└── propiedad_caracteristicas (1:N)
    └── caracteristica_id → caracteristicas_mae

busqueda_x_inmueble_mov
├── usuario_id → usuarios
└── tipo_inmueble_id → tipo_inmueble_mae

registro_x_inmueble_mov
├── usuario_id → usuarios
└── propiedad_id → propiedades
```

---

## 🎯 Casos de Uso Completos

### Caso 1: Búsqueda de Oficinas en San Isidro

```javascript
// 1. Usuario realiza búsqueda
const busqueda = {
  usuario_id: 1,
  tipo_inmueble_id: 1,
  distritos_ids: [1], // San Isidro
  transaccion: "alquiler",
  precio_max: 5000
};

// 2. Guardar búsqueda en busqueda_x_inmueble_mov.json
// (En producción, esto sería un POST)

// 3. Filtrar propiedades
const resultados = propiedades.filter(p => 
  p.tipo_inmueble_id === 1 &&
  p.distrito_id === 1 &&
  p.precio_alquiler <= 5000 &&
  p.estado === 'disponible'
);

// 4. Registrar vistas
resultados.forEach(prop => {
  // Guardar en registro_x_inmueble_mov.json
  // tipo_interaccion: "vista"
});
```

### Caso 2: Usuario agrega propiedad a favoritos

```javascript
// 1. Usuario hace clic en "favorito"
const registro = {
  usuario_id: 1,
  propiedad_id: 1,
  tipo_interaccion: "favorito",
  detalles: { accion: "agregar" },
  fecha_interaccion: new Date().toISOString()
};

// 2. Guardar en registro_x_inmueble_mov.json
// (En producción, esto sería un POST)
```

### Caso 3: Mostrar filtros avanzados dinámicos

```javascript
// 1. Usuario selecciona "Oficina en Edificio"
const tipoInmuebleId = 1;

// 2. Obtener características aplicables
const relaciones = caracteristicas_x_inmueble_mae.data.filter(
  r => r.tipo_inmueble_id === tipoInmuebleId
);

// 3. Obtener detalles de características
const caracIds = relaciones.map(r => r.caracteristica_id);
const caracteristicas = caracteristicas_mae.data.filter(
  c => caracIds.includes(c.caracteristica_id)
);

// 4. Agrupar por categoría
const porCategoria = {};
caracteristicas.forEach(c => {
  if (!porCategoria[c.categoria]) {
    porCategoria[c.categoria] = [];
  }
  porCategoria[c.categoria].push(c);
});

// 5. Renderizar acordeón de filtros
Object.keys(porCategoria).forEach(categoria => {
  console.log(`Categoría: ${categoria}`);
  porCategoria[categoria].forEach(c => {
    console.log(`  - ${c.nombre} (${c.tipo_input})`);
  });
});
```

---

## 🚀 Migración a API Real

Cuando implementes el backend real, estos archivos te servirán como:

1. **Datos de prueba** para poblar la base de datos
2. **Estructura de respuesta** que debe devolver tu API
3. **Casos de prueba** para validar endpoints

### Ejemplo de endpoint real (Node.js + Express)

```javascript
// GET /api/propiedades
app.get('/api/propiedades', async (req, res) => {
  try {
    const propiedades = await db.query(`
      SELECT p.*, t.nombre as tipo_inmueble, d.nombre as distrito
      FROM propiedades p
      JOIN tipo_inmueble_mae t ON p.tipo_inmueble_id = t.tipo_inmueble_id
      JOIN distritos_mae d ON p.distrito_id = d.distrito_id
      WHERE p.estado = 'disponible'
      ORDER BY p.destacado DESC, p.created_at DESC
    `);
    
    res.json({
      success: true,
      data: propiedades.rows,
      total: propiedades.rows.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});
```

---

## 📊 Estadísticas de los Mocks

| Tabla | Registros | Uso |
|-------|-----------|-----|
| **Maestras** | 80 | Catálogos estáticos |
| **Usuarios** | 10 | Datos de prueba |
| **Propiedades** | 10 | Inmuebles de ejemplo |
| **Relaciones** | 51 | Configuración de filtros |
| **Valores** | 33 | Características de propiedades |
| **Movimientos** | 35 | Búsquedas e interacciones |
| **TOTAL** | **219 registros** | Datos completos para testing |

---

## 🔐 Notas de Seguridad

1. **Passwords**: Los `password_hash` en `usuarios.json` son ficticios. En producción usar bcrypt real.
2. **IPs**: Las direcciones IP son de ejemplo (192.168.x.x).
3. **Tokens**: No incluir tokens reales en estos mocks.
4. **Datos sensibles**: Estos mocks son solo para desarrollo local.

---

## ✅ Checklist de Implementación

- [x] Crear estructura de carpetas `backend/data/mock/`
- [x] Generar 12 archivos JSON con datos reales
- [x] Documentar formato de respuesta API
- [x] Incluir ejemplos de uso
- [x] Documentar relaciones entre tablas
- [ ] Crear servidor mock con Express (opcional)
- [ ] Implementar endpoints reales en backend
- [ ] Migrar datos a PostgreSQL
- [ ] Actualizar frontend para consumir API real

---

**Fecha de creación**: 2025-01-14  
**Versión**: 1.0  
**Total de registros**: 219
