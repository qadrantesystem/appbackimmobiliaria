-- ============================================
-- 💳 TABLA: suscripciones
-- Suscripciones de usuarios a planes
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS suscripciones (
    suscripcion_id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id),
    plan_id INTEGER NOT NULL REFERENCES planes_mae(plan_id),
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    monto_pagado DECIMAL(10, 2) NOT NULL,
    metodo_pago VARCHAR(50),
    transaccion_id VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'activa' CHECK (estado IN ('activa', 'cancelada', 'expirada', 'suspendida')),
    auto_renovar BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelada_at TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_suscripciones_usuario ON suscripciones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_suscripciones_estado ON suscripciones(estado);
CREATE INDEX IF NOT EXISTS idx_suscripciones_fecha_fin ON suscripciones(fecha_fin);

-- ============================================
-- 📊 INSERTAR FILAS (5 suscripciones - una por usuario)
-- ============================================
-- USUARIOS EXISTENTES:
-- 1. admin@inmobiliaria.com       → Admin (sin plan necesario)
-- 2. demandante@email.com         → Demandante (Plan Básico - ID 1)
-- 3. ofertante@email.com          → Ofertante (Plan Premium - ID 2)
-- 4. corredor@inmobiliaria.com    → Corredor (sin plan necesario)
-- 5. ana.martinez@email.com       → Demandante (Plan Básico - ID 1)
-- ============================================

INSERT INTO suscripciones (suscripcion_id, usuario_id, plan_id, fecha_inicio, fecha_fin, monto_pagado, metodo_pago, transaccion_id, estado, auto_renovar) VALUES

-- Suscripción 1: Demandante Juan Pérez - Plan Básico (Gratis)
(1, 2, 1, '2024-01-15 10:00:00', '2099-12-31 23:59:59', 0, NULL, NULL, 'activa', false),

-- Suscripción 2: Ofertante María García - Plan Premium
(2, 3, 2, '2024-02-01 10:00:00', '2025-02-01 10:00:00', 49.00, 'tarjeta_credito', 'TXN-2024-02-001-ABC123', 'activa', true),

-- Suscripción 3: Demandante Ana Martínez - Plan Básico (Gratis)
(3, 5, 1, '2024-04-20 10:00:00', '2099-12-31 23:59:59', 0, NULL, NULL, 'activa', false)

ON CONFLICT (suscripcion_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('suscripciones_suscripcion_id_seq', (SELECT MAX(suscripcion_id) FROM suscripciones));

-- ============================================
-- 📈 RESULTADO: 3 suscripciones creadas
-- ============================================
-- NOTA: Admin y Corredor no necesitan suscripciones (acceso por perfil)
-- ============================================
