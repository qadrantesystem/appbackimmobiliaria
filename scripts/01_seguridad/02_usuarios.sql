-- ============================================
-- 👤 TABLA: usuarios
-- Usuarios del sistema
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    dni VARCHAR(20),
    foto_perfil VARCHAR(500),
    perfil_id INTEGER NOT NULL REFERENCES perfiles(perfil_id),
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    plan_id INTEGER REFERENCES planes_mae(plan_id),
    fecha_inicio_suscripcion TIMESTAMP,
    fecha_fin_suscripcion TIMESTAMP,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_sesion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_perfil ON usuarios(perfil_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usuarios(estado);

-- ============================================
-- 📊 INSERTAR FILAS (Datos de ejemplo)
-- Password: "123456" hasheado con bcrypt
-- Hash válido: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu
-- ============================================

INSERT INTO usuarios (usuario_id, email, password_hash, nombre, apellido, telefono, dni, perfil_id, estado, plan_id, fecha_registro) VALUES
-- Admin (perfil_id = 4)
(1, 'admin@inmobiliaria.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu', 
 'Admin', 'Sistema', '+51 900000000', '00000000', 4, 'activo', NULL, '2024-01-01 00:00:00'),

-- Demandante (perfil_id = 1)
(2, 'demandante@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu', 
 'Juan', 'Pérez', '+51 987654321', '12345678', 1, 'activo', 1, '2024-01-15 10:00:00'),

-- Ofertante (perfil_id = 2)
(3, 'ofertante@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu', 
 'María', 'García', '+51 912345678', '87654321', 2, 'activo', 2, '2024-02-01 10:00:00'),

-- Corredor (perfil_id = 3)
(4, 'corredor@inmobiliaria.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu', 
 'Carlos', 'Rodríguez', '+51 998877665', '11223344', 3, 'activo', NULL, '2024-01-10 10:00:00'),

-- Usuario adicional Demandante
(5, 'ana.martinez@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXNm7Hxu', 
 'Ana', 'Martínez', '+51 955443322', '55667788', 1, 'activo', 1, '2024-04-20 10:00:00')

ON CONFLICT (usuario_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('usuarios_usuario_id_seq', (SELECT MAX(usuario_id) FROM usuarios));

-- ============================================
-- 📈 RESULTADO: 5 usuarios creados
-- Password de prueba: 123456
-- ============================================
-- USUARIOS CREADOS:
-- 1. admin@inmobiliaria.com       → Admin (sin plan)
-- 2. demandante@email.com         → Demandante (Plan Básico)
-- 3. ofertante@email.com          → Ofertante (Plan Premium)
-- 4. corredor@inmobiliaria.com    → Corredor (sin plan)
-- 5. ana.martinez@email.com       → Demandante (Plan Básico)
-- ============================================
