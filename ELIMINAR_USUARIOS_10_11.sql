-- ============================================
-- 🗑️ ELIMINAR USUARIOS 10 Y 11
-- ============================================

-- Ver usuarios antes de eliminar
SELECT usuario_id, email, nombre, apellido FROM usuarios WHERE usuario_id IN (10, 11);

-- Eliminar usuarios (cascade eliminará tokens automáticamente)
DELETE FROM usuarios WHERE usuario_id IN (10, 11);

-- Verificar eliminación
SELECT usuario_id, email, nombre, apellido FROM usuarios ORDER BY usuario_id;

-- ✅ Listo para crear nuevo usuario
