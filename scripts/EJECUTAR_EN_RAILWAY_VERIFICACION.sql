-- ============================================
-- 📧 CONFIGURAR SISTEMA DE VERIFICACIÓN DE EMAIL
-- ============================================

-- 1. Agregar columnas de verificación a usuarios
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_verificado BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(500);

-- 2. Actualizar constraint de estado
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS check_usuario_estado;
ALTER TABLE usuarios ADD CONSTRAINT check_usuario_estado 
    CHECK (estado IN ('pendiente', 'activo', 'inactivo', 'suspendido'));

-- 3. Crear tabla de tokens de verificación de email
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id BIGSERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para email_verification_tokens
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_usuario_id ON email_verification_tokens(usuario_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_email ON email_verification_tokens(email);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens(token);

-- 4. Crear tabla de tokens de recuperación de contraseña
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para password_reset_tokens
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_usuario_id ON password_reset_tokens(usuario_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON password_reset_tokens(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);

-- 5. Actualizar usuarios existentes (marcarlos como verificados)
UPDATE usuarios SET email_verificado = TRUE WHERE email_verificado IS NULL OR email_verificado = FALSE;
UPDATE usuarios SET estado = 'activo' WHERE estado IN ('activo', 'pendiente') AND email_verificado = TRUE;

-- 6. Verificar todo
SELECT 'Usuarios' as tabla, COUNT(*) as total FROM usuarios;
SELECT 'Tokens Verificación' as tabla, COUNT(*) as total FROM email_verification_tokens;
SELECT 'Tokens Reset Password' as tabla, COUNT(*) as total FROM password_reset_tokens;

-- ✅ Sistema de verificación configurado
