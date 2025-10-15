-- ============================================
-- 🔧 FIX: Agregar columna DNI a tabla usuarios
-- ============================================

-- Agregar columna DNI si no existe
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS dni VARCHAR(20);

-- Verificar
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
ORDER BY ordinal_position;
