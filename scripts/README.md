# 📁 Scripts SQL - Base de Datos Inmobiliaria

Scripts SQL organizados por carpetas con **FILAS DE DATOS REALES** (no solo estructura).

## 📂 Estructura de Carpetas

```
scripts/
├── 00_ejecutar_todo.sql          # 🚀 Script maestro (ejecuta todo)
├── 01_seguridad/                 # 👥 Usuarios y perfiles
│   ├── 01_perfiles.sql           # 3 perfiles
│   └── 02_usuarios.sql           # 10 usuarios
├── 02_maestras/                  # 📚 Catálogos
│   ├── 01_planes_mae.sql         # 4 planes
│   ├── 02_distritos_mae.sql      # 10 distritos
│   ├── 03_tipo_inmueble_mae.sql  # 12 tipos
│   ├── 04_caracteristicas_mae.sql # 51 características
│   └── 05_caracteristicas_x_inmueble_mae.sql # 51 relaciones
└── 03_transaccionales/           # 📊 Datos de operación
    ├── 01_propiedades.sql        # 10 propiedades
    ├── 02_propiedad_caracteristicas.sql # 33 valores
    ├── 03_suscripciones.sql      # 8 suscripciones
    ├── 04_busqueda_x_inmueble_mov.sql # 15 búsquedas
    ├── 05_registro_x_inmueble_mov.sql # 20 interacciones
    └── 06_favoritos.sql          # 12 favoritos
```

## 🎯 Filosofía: FILAS, NO COLUMNAS

Cada script contiene:
- ✅ Creación de tabla
- ✅ **DATOS REALES** insertados (filas completas)
- ✅ Índices necesarios
- ✅ Resumen de resultados

**NO** son scripts vacíos, son datos listos para usar.

## 🚀 Ejecución Rápida

### Opción 1: Script Maestro (Recomendado)

```bash
# Conectar a PostgreSQL
psql "postgresql://usuario:password@host:puerto/database"

# Ejecutar todo
\i 00_ejecutar_todo.sql
```

### Opción 2: Ejecutar por Carpetas

```bash
# 1. Seguridad
\i 01_seguridad/01_perfiles.sql
\i 01_seguridad/02_usuarios.sql

# 2. Maestras
\i 02_maestras/01_planes_mae.sql
\i 02_maestras/02_distritos_mae.sql
\i 02_maestras/03_tipo_inmueble_mae.sql
\i 02_maestras/04_caracteristicas_mae.sql
\i 02_maestras/05_caracteristicas_x_inmueble_mae.sql

# 3. Transaccionales
\i 03_transaccionales/01_propiedades.sql
\i 03_transaccionales/02_propiedad_caracteristicas.sql
\i 03_transaccionales/03_suscripciones.sql
\i 03_transaccionales/04_busqueda_x_inmueble_mov.sql
\i 03_transaccionales/05_registro_x_inmueble_mov.sql
```

### Opción 3: Desde Railway CLI

```bash
# Conectar a Railway PostgreSQL
railway connect

# Ejecutar script
\i scripts/00_ejecutar_todo.sql
```

## 📊 Resumen de Datos

| Categoría | Tabla | Registros | Descripción |
|-----------|-------|-----------|-------------|
| **Seguridad** | perfiles | 3 | Tipos de usuario |
| | usuarios | 10 | Usuarios de prueba |
| **Maestras** | planes_mae | 4 | Planes de suscripción |
| | distritos_mae | 10 | Distritos de Lima |
| | tipo_inmueble_mae | 12 | Tipos de inmuebles |
| | caracteristicas_mae | 51 | Características |
| | caracteristicas_x_inmueble_mae | 51 | Relaciones |
| **Transaccionales** | propiedades | 10 | Inmuebles publicados |
| | propiedad_caracteristicas | 33 | Valores de características |
| | suscripciones | 8 | Suscripciones activas |
| | busqueda_x_inmueble_mov | 15 | Búsquedas realizadas |
| | registro_x_inmueble_mov | 20 | Interacciones |
| | favoritos | 12 | Propiedades favoritas |
| **TOTAL** | | **239** | **Registros insertados** |

## 🔐 Credenciales de Prueba

### Usuario Arrendatario
```
Email: juan.perez@email.com
Password: demo123
Perfil: arrendatario
Plan: Gratuito
```

### Usuario Propietario
```
Email: maria.garcia@inmobiliaria.com
Password: demo123
Perfil: propietario
Plan: Profesional
```

### Usuario Admin
```
Email: admin@inmobiliaria.com
Password: demo123
Perfil: admin
Plan: Empresarial
```

## 📝 Detalles por Carpeta

### 01_seguridad/

**Perfiles (3 filas)**
- arrendatario: Busca propiedades
- propietario: Publica propiedades
- admin: Administra el sistema

**Usuarios (10 filas)**
- 10 usuarios de ejemplo con datos completos
- Passwords hasheados con bcrypt
- Diferentes perfiles y planes

### 02_maestras/

**Planes (4 filas)**
- Gratuito: 3 propiedades, 5 imágenes
- Básico: 10 propiedades, 15 imágenes
- Profesional: 50 propiedades, 30 imágenes
- Empresarial: Ilimitado, 100 imágenes

**Distritos (10 filas)**
- San Isidro, Miraflores, San Borja, Surco, etc.
- Con coordenadas GPS reales

**Tipos de Inmuebles (12 filas)**
- Oficina, Casa, Departamento, Local, Terreno, etc.
- Con iconos Font Awesome

**Características (51 filas)**
- Agrupadas en 6 categorías:
  - AREAS_COMUNES_EDIFICIO (18)
  - ASCENSORES (3)
  - IMPLEMENTACION_DETALLE (10)
  - SOPORTE_EDIFICIO (7)
  - CERCANIA_ESTRATEGICA (6)
  - VISTA_OFICINA (7)

**Relaciones (51 filas)**
- Todas las características para tipo_inmueble_id = 1 (Oficina)

### 03_transaccionales/

**Propiedades (10 filas)**
- 6 oficinas en diferentes distritos
- 1 departamento en Miraflores
- 1 casa en La Molina
- 1 local comercial en Miraflores
- 1 almacén en Jesús María
- Con precios, imágenes, descripciones reales

**Características de Propiedades (33 filas)**
- Valores específicos por propiedad
- Números (parqueos, depósitos)
- Booleanos (GYM, cafetería, etc.)

**Suscripciones (8 filas)**
- Suscripciones activas de usuarios
- Con métodos de pago y transacciones

**Búsquedas (15 filas)**
- Historial de búsquedas con filtros
- Usuarios logueados y anónimos

**Interacciones (20 filas)**
- Vistas, favoritos, contactos
- Con detalles en JSON

**Favoritos (12 filas)**
- Propiedades guardadas por usuarios
- Con notas opcionales
- Usuario 1 tiene 4 favoritos
- Usuario 3 tiene 3 favoritos

## 🔄 Actualizar Datos

Para actualizar solo una tabla:

```bash
# Ejemplo: Actualizar usuarios
psql "postgresql://..." -f 01_seguridad/02_usuarios.sql
```

## 🗑️ Limpiar Base de Datos

```sql
-- Eliminar todas las tablas (CUIDADO!)
DROP TABLE IF EXISTS favoritos CASCADE;
DROP TABLE IF EXISTS registro_x_inmueble_mov CASCADE;
DROP TABLE IF EXISTS busqueda_x_inmueble_mov CASCADE;
DROP TABLE IF EXISTS propiedad_caracteristicas CASCADE;
DROP TABLE IF EXISTS propiedades CASCADE;
DROP TABLE IF EXISTS suscripciones CASCADE;
DROP TABLE IF EXISTS caracteristicas_x_inmueble_mae CASCADE;
DROP TABLE IF EXISTS caracteristicas_mae CASCADE;
DROP TABLE IF EXISTS tipo_inmueble_mae CASCADE;
DROP TABLE IF EXISTS distritos_mae CASCADE;
DROP TABLE IF EXISTS planes_mae CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS perfiles CASCADE;
```

## 📚 Consultas Útiles

### Ver todas las tablas creadas
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Contar registros por tabla
```sql
SELECT 
    'perfiles' as tabla, COUNT(*) as registros FROM perfiles
UNION ALL
SELECT 'usuarios', COUNT(*) FROM usuarios
UNION ALL
SELECT 'planes_mae', COUNT(*) FROM planes_mae
UNION ALL
SELECT 'distritos_mae', COUNT(*) FROM distritos_mae
UNION ALL
SELECT 'tipo_inmueble_mae', COUNT(*) FROM tipo_inmueble_mae
UNION ALL
SELECT 'caracteristicas_mae', COUNT(*) FROM caracteristicas_mae
UNION ALL
SELECT 'caracteristicas_x_inmueble_mae', COUNT(*) FROM caracteristicas_x_inmueble_mae
UNION ALL
SELECT 'propiedades', COUNT(*) FROM propiedades
UNION ALL
SELECT 'propiedad_caracteristicas', COUNT(*) FROM propiedad_caracteristicas
UNION ALL
SELECT 'suscripciones', COUNT(*) FROM suscripciones
UNION ALL
SELECT 'busqueda_x_inmueble_mov', COUNT(*) FROM busqueda_x_inmueble_mov
UNION ALL
SELECT 'registro_x_inmueble_mov', COUNT(*) FROM registro_x_inmueble_mov
UNION ALL
SELECT 'favoritos', COUNT(*) FROM favoritos;
```

### Ver propiedades con sus características
```sql
SELECT 
    p.titulo,
    p.distrito_id,
    p.area,
    p.precio_alquiler,
    COUNT(pc.id) as total_caracteristicas
FROM propiedades p
LEFT JOIN propiedad_caracteristicas pc ON p.propiedad_id = pc.propiedad_id
GROUP BY p.propiedad_id, p.titulo, p.distrito_id, p.area, p.precio_alquiler
ORDER BY p.propiedad_id;
```

## 🎯 Próximos Pasos

1. ✅ Ejecutar scripts en Railway PostgreSQL
2. ✅ Verificar que todos los datos se insertaron
3. ✅ Crear modelos SQLAlchemy en el backend
4. ✅ Crear endpoints API
5. ✅ Conectar frontend con backend

## 📖 Documentación Relacionada

- `MODELO_DATOS.md` - Modelo completo de la base de datos
- `RAILWAY_SETUP.md` - Guía de configuración Railway
- `README.md` - Documentación del backend

### Ver favoritos de un usuario
```sql
SELECT 
    f.favorito_id,
    f.notas,
    f.created_at as fecha_guardado,
    p.titulo,
    p.precio_alquiler,
    p.area,
    d.nombre as distrito
FROM favoritos f
JOIN propiedades p ON f.propiedad_id = p.propiedad_id
JOIN distritos_mae d ON p.distrito_id = d.distrito_id
WHERE f.usuario_id = 1
ORDER BY f.created_at DESC;
```

---

**Versión**: 1.0  
**Fecha**: 2025-01-14  
**Total de registros**: 239
