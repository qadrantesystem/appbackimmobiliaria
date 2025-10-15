-- ============================================
-- 🔧 ARREGLAR CONSTRAINT DE ESTADO
-- ============================================

-- Eliminar constraint viejo que no incluye 'pendiente'
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS usuarios_estado_check;

-- Verificar que solo quede el constraint correcto
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'usuarios'::regclass 
AND conname LIKE '%estado%';

-- ✅ Ahora debe quedar solo: check_usuario_estado con (pendiente, activo, inactivo, suspendido)
