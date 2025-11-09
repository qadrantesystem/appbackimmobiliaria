-- ============================================
-- 🚀 OPTIMIZACIÓN: ÍNDICES PARA EDIFICIOS COMPLETOS
-- ============================================
-- Fecha: 2025-11-09
-- Propósito: Mejorar performance de consultas de oficinas y características
-- Ejecutar en: PostgreSQL
-- ============================================

BEGIN;

-- ============================================
-- 1️⃣ ÍNDICE: Buscar oficinas por edificio padre
-- ============================================
-- Beneficia: GET /propiedades/{edificio_id}/oficinas
-- Mejora: Query de O(n) a O(log n)

CREATE INDEX IF NOT EXISTS idx_inmueble_padre 
ON registro_x_inmueble_cab(padre_registro_cab_id) 
WHERE padre_registro_cab_id IS NOT NULL;

COMMENT ON INDEX idx_inmueble_padre IS 
'Índice parcial para buscar oficinas de un edificio. Solo indexa registros con padre.';

-- ============================================
-- 2️⃣ ÍNDICE: Características de equipamiento
-- ============================================
-- Beneficia: Queries de características IDs 122-130
-- Mejora: Filtrado rápido de equipamiento de oficinas

CREATE INDEX IF NOT EXISTS idx_caracteristicas_equipamiento 
ON registro_x_inmueble_det(caracteristica_id)
WHERE caracteristica_id BETWEEN 122 AND 130;

COMMENT ON INDEX idx_caracteristicas_equipamiento IS 
'Índice parcial para características de equipamiento de oficinas (IDs 122-130).';

-- ============================================
-- 3️⃣ ÍNDICE COMPUESTO: Detalle por cabecera y característica
-- ============================================
-- Beneficia: Joins entre cab y det
-- Mejora: Lookup directo en vez de scan

CREATE INDEX IF NOT EXISTS idx_det_cab_caract 
ON registro_x_inmueble_det(registro_cab_id, caracteristica_id);

COMMENT ON INDEX idx_det_cab_caract IS 
'Índice compuesto para optimizar joins entre cabecera y detalle.';

-- ============================================
-- 4️⃣ ÍNDICE: Búsqueda de piso de oficina
-- ============================================
-- Beneficia: Ordenamiento y filtrado por piso
-- Mejora: Queries del endpoint PUT actualizar edificio

CREATE INDEX IF NOT EXISTS idx_det_piso 
ON registro_x_inmueble_det(registro_cab_id, caracteristica_id)
WHERE caracteristica_id = 110;

COMMENT ON INDEX idx_det_piso IS 
'Índice para buscar el piso de una oficina (caracteristica_id = 110).';

-- ============================================
-- 5️⃣ ÍNDICE: Tipo de inmueble para filtros
-- ============================================
-- Beneficia: Queries que filtran por tipo (edificios, oficinas, etc.)
-- Mejora: Detección de edificios en GET /propiedades/{id}

CREATE INDEX IF NOT EXISTS idx_cab_tipo_inmueble 
ON registro_x_inmueble_cab(tipo_inmueble_id, padre_registro_cab_id);

COMMENT ON INDEX idx_cab_tipo_inmueble IS 
'Índice compuesto para filtrar por tipo de inmueble y relación padre-hijo.';

-- ============================================
-- 6️⃣ ÍNDICE: Usuario propietario de inmuebles
-- ============================================
-- Beneficia: Validación de permisos en DELETE y PUT
-- Mejora: Verificación rápida de ownership

CREATE INDEX IF NOT EXISTS idx_cab_usuario 
ON registro_x_inmueble_cab(usuario_id, registro_cab_id);

COMMENT ON INDEX idx_cab_usuario IS 
'Índice para buscar inmuebles por usuario (validación de permisos).';

COMMIT;

-- ============================================
-- 📊 ANÁLISIS DE IMPACTO ESPERADO
-- ============================================

-- Consulta 1: Listar oficinas de edificio
-- ANTES: Seq Scan en registro_x_inmueble_cab
-- DESPUÉS: Index Scan usando idx_inmueble_padre
-- MEJORA ESTIMADA: 80-90% más rápido para edificios con 20+ oficinas

-- Consulta 2: Características de equipamiento
-- ANTES: Seq Scan en registro_x_inmueble_det
-- DESPUÉS: Bitmap Index Scan usando idx_caracteristicas_equipamiento
-- MEJORA ESTIMADA: 70-80% más rápido

-- Consulta 3: Join cab-det
-- ANTES: Hash Join con Seq Scan
-- DESPUÉS: Nested Loop con Index Scan
-- MEJORA ESTIMADA: 50-60% más rápido

-- ============================================
-- 🧪 VERIFICAR ÍNDICES CREADOS
-- ============================================

SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('registro_x_inmueble_cab', 'registro_x_inmueble_det')
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- ============================================
-- 📈 ANALIZAR PERFORMANCE (OPCIONAL)
-- ============================================

-- Actualizar estadísticas de las tablas
ANALYZE registro_x_inmueble_cab;
ANALYZE registro_x_inmueble_det;

-- Ver tamaño de índices
SELECT 
    indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
    AND indexrelname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================
-- ✅ VALIDACIÓN POST-IMPLEMENTACIÓN
-- ============================================

-- Test 1: Verificar índice de padre
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM registro_x_inmueble_cab 
WHERE padre_registro_cab_id = 1;
-- Debe usar: Index Scan using idx_inmueble_padre

-- Test 2: Verificar índice de equipamiento
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM registro_x_inmueble_det
WHERE caracteristica_id BETWEEN 122 AND 130;
-- Debe usar: Bitmap Index Scan on idx_caracteristicas_equipamiento

-- Test 3: Verificar join optimizado
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.*, d.valor 
FROM registro_x_inmueble_cab c
JOIN registro_x_inmueble_det d ON c.registro_cab_id = d.registro_cab_id
WHERE c.padre_registro_cab_id = 1 
    AND d.caracteristica_id = 110;
-- Debe usar índices compuestos

-- ============================================
-- 🔄 ROLLBACK (Si es necesario)
-- ============================================

-- Para revertir todos los índices:
/*
DROP INDEX IF EXISTS idx_inmueble_padre;
DROP INDEX IF EXISTS idx_caracteristicas_equipamiento;
DROP INDEX IF EXISTS idx_det_cab_caract;
DROP INDEX IF EXISTS idx_det_piso;
DROP INDEX IF EXISTS idx_cab_tipo_inmueble;
DROP INDEX IF EXISTS idx_cab_usuario;
*/

-- ============================================
-- 📝 NOTAS FINALES
-- ============================================

-- 1. Estos índices son seguros de aplicar en producción
-- 2. No afectan datos existentes, solo mejoran performance
-- 3. Ocupan espacio adicional (~5-10% del tamaño de la tabla)
-- 4. Se mantienen automáticamente por PostgreSQL
-- 5. Usar EXPLAIN ANALYZE para verificar uso en queries reales

-- ============================================
-- ✅ FIN DEL SCRIPT
-- ============================================
