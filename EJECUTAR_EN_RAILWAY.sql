-- ============================================
-- 🚀 SCRIPTS PARA EJECUTAR EN RAILWAY
-- Ejecuta estos scripts en orden en Railway PostgreSQL
-- ============================================

-- ============================================
-- 1️⃣ AGREGAR COLUMNA DNI (si no existe)
-- ============================================
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS dni VARCHAR(20);

-- Verificar que se agregó
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
ORDER BY ordinal_position;

-- ============================================
-- 2️⃣ ACTUALIZAR PASSWORDS CON HASH VÁLIDO
-- Password: "123456"
-- Hash válido de bcrypt (60 caracteres)
-- ============================================

-- Actualizar todos los usuarios con el hash correcto
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' 
WHERE email IN (
    'admin@inmobiliaria.com',
    'demandante@email.com',
    'ofertante@email.com',
    'corredor@inmobiliaria.com',
    'ana.martinez@email.com'
);

-- Verificar que los passwords se actualizaron correctamente
SELECT 
    email, 
    LENGTH(password_hash) as hash_length,
    CASE 
        WHEN LENGTH(password_hash) = 60 THEN '✅ OK'
        ELSE '❌ ERROR'
    END as status
FROM usuarios
ORDER BY usuario_id;

-- ============================================
-- 3️⃣ VERIFICAR USUARIOS
-- ============================================
SELECT 
    usuario_id,
    email,
    nombre,
    apellido,
    perfil_id,
    estado,
    LENGTH(password_hash) as hash_length
FROM usuarios
ORDER BY usuario_id;

-- ============================================
-- ✅ RESULTADO ESPERADO:
-- ============================================
-- Todos los usuarios deben tener:
-- - hash_length = 60 caracteres
-- - status = ✅ OK
-- 
-- Usuarios disponibles:
-- 1. admin@inmobiliaria.com       → Admin (perfil_id = 4)
-- 2. demandante@email.com         → Demandante (perfil_id = 1)
-- 3. ofertante@email.com          → Ofertante (perfil_id = 2)
-- 4. corredor@inmobiliaria.com    → Corredor (perfil_id = 3)
-- 5. ana.martinez@email.com       → Demandante (perfil_id = 1)
--
-- Password para todos: 123456
-- ============================================
