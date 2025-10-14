-- ============================================
-- 🚀 SCRIPT MAESTRO - EJECUTAR TODO
-- Sistema Inmobiliario - Base de Datos Completa
-- ============================================
-- 
-- Este script ejecuta TODOS los scripts en el orden correcto
-- para crear la base de datos completa con datos de ejemplo
--
-- ORDEN DE EJECUCIÓN:
-- 1. Seguridad (perfiles, usuarios)
-- 2. Maestras (planes, distritos, tipos, características)
-- 3. Transaccionales (propiedades, suscripciones, búsquedas)
--
-- ============================================

\echo '🚀 Iniciando creación de base de datos...'
\echo ''

-- ============================================
-- 📁 PASO 1: SEGURIDAD
-- ============================================
\echo '👥 PASO 1/3: Creando tablas de SEGURIDAD...'

\i 01_seguridad/01_perfiles.sql
\echo '   ✅ Perfiles creados'

\i 01_seguridad/02_usuarios.sql
\echo '   ✅ Usuarios creados'

\echo ''

-- ============================================
-- 📁 PASO 2: MAESTRAS
-- ============================================
\echo '📚 PASO 2/3: Creando tablas MAESTRAS...'

\i 02_maestras/01_planes_mae.sql
\echo '   ✅ Planes creados'

\i 02_maestras/02_distritos_mae.sql
\echo '   ✅ Distritos creados'

\i 02_maestras/03_tipo_inmueble_mae.sql
\echo '   ✅ Tipos de inmuebles creados'

\i 02_maestras/04_caracteristicas_mae.sql
\echo '   ✅ Características creadas'

\i 02_maestras/05_caracteristicas_x_inmueble_mae.sql
\echo '   ✅ Relaciones características x inmueble creadas'

\i 02_maestras/06_estados_crm_mae.sql
\echo '   ✅ Estados CRM creados'

\echo ''

-- ============================================
-- 📁 PASO 3: TRANSACCIONALES
-- ============================================
\echo '📊 PASO 3: Creando tablas transaccionales...'
\echo ''

\i 03_transaccionales/01_registro_x_inmueble_cab.sql
\echo '   ✅ Cabecera de propiedades creada'

\i 03_transaccionales/02_registro_x_inmueble_det.sql
\echo '   ✅ Detalle de características creado'

\i 03_transaccionales/03_suscripciones.sql
\echo '   ✅ Suscripciones creadas'

\i 03_transaccionales/04_busqueda_x_inmueble_mov.sql
\echo '   ✅ Búsquedas realizadas y guardadas'

\i 03_transaccionales/05_registro_x_inmueble_tracking.sql
\echo '   ✅ Tracking de estados CRM creado'

\i 03_transaccionales/06_favoritos.sql
\echo '   ✅ Favoritos creados'

\echo ''

-- ============================================
-- ✅ RESUMEN FINAL
-- ============================================
\echo '✅ ¡BASE DE DATOS CREADA EXITOSAMENTE!'
\echo ''
\echo '📊 RESUMEN DE DATOS:'
\echo '   👥 Seguridad:'
\echo '      - 3 perfiles'
\echo '      - 10 usuarios'
\echo ''
\echo '   📚 Maestras:'
\echo '      - 4 planes'
\echo '      - 10 distritos'
\echo '      - 12 tipos de inmuebles'
\echo '      - 51 características'
\echo '      - 51 relaciones características x inmueble'
\echo '      - 7 estados CRM'
\echo ''
\echo '   📊 Transaccionales:'
\echo '      - 10 propiedades (cabecera)'
\echo '      - 33 características (detalle)'
\echo '      - 8 suscripciones'
\echo '      - 19 búsquedas (15 históricas + 4 guardadas)'
\echo '      - 15 cambios de estado (tracking CRM)'
\echo '      - 12 favoritos'
\echo ''
\echo '   🎯 TOTAL: 235 registros insertados'
\echo ''
\echo '🔐 Credenciales de prueba:'
\echo '   Email: juan.perez@email.com'
\echo '   Password: demo123'
\echo ''
\echo '   Email: admin@inmobiliaria.com'
\echo '   Password: demo123'
\echo ''
\echo '📚 Documentación: Ver MODELO_DATOS.md'
\echo ''
