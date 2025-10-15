-- ============================================
-- 📧 Agregar columnas de verificación de email
-- ============================================

-- 1. Agregar columnas de verificación
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_verificado BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS codigo_verificacion VARCHAR(10);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS codigo_verificacion_expira TIMESTAMP;

-- 2. Actualizar constraint de estado para incluir 'pendiente'
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS check_usuario_estado;
ALTER TABLE usuarios ADD CONSTRAINT check_usuario_estado 
    CHECK (estado IN ('pendiente', 'activo', 'inactivo', 'suspendido'));

-- 3. Actualizar usuarios existentes (marcarlos como verificados)
UPDATE usuarios SET email_verificado = TRUE WHERE email_verificado IS NULL;
UPDATE usuarios SET estado = 'activo' WHERE estado = 'activo' AND email_verificado = TRUE;

-- 4. Verificar columnas
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
AND column_name IN ('email_verificado', 'codigo_verificacion', 'codigo_verificacion_expira', 'estado')
ORDER BY ordinal_position;

-- ✅ Listo para verificación de email
