-- ============================================
-- 🔧 FIX: Actualizar passwords de usuarios
-- Password: "123456"
-- Hash válido de bcrypt (60 caracteres)
-- ============================================

-- Hash válido para password "123456"
-- Generado con: bcrypt.hashpw(b"123456", bcrypt.gensalt())
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' WHERE email = 'admin@inmobiliaria.com';
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' WHERE email = 'demandante@email.com';
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' WHERE email = 'ofertante@email.com';
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' WHERE email = 'corredor@inmobiliaria.com';
UPDATE usuarios SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu' WHERE email = 'ana.martinez@email.com';

-- Verificar
SELECT email, LENGTH(password_hash) as hash_length FROM usuarios;
