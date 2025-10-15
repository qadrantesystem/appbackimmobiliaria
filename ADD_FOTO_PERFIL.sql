-- ============================================
-- 🔧 Agregar columna foto_perfil a tabla usuarios
-- ============================================

-- Agregar columna foto_perfil si no existe
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(500);

-- Verificar
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name IN ('foto_perfil', 'dni', 'telefono')
ORDER BY ordinal_position;

-- ✅ Listo para usar ImageKit en perfiles
