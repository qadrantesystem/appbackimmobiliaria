-- ============================================
-- 📊 TABLA: estados_crm_mae
-- Catálogo de estados del pipeline CRM
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS estados_crm_mae (
    estado_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    color VARCHAR(20),
    icono VARCHAR(50),
    orden INTEGER NOT NULL,
    es_final BOOLEAN DEFAULT false,
    es_ganado BOOLEAN DEFAULT false,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_estados_crm_codigo ON estados_crm_mae(codigo);
CREATE INDEX IF NOT EXISTS idx_estados_crm_orden ON estados_crm_mae(orden);
CREATE INDEX IF NOT EXISTS idx_estados_crm_activo ON estados_crm_mae(activo);

-- ============================================
-- 📊 INSERTAR FILAS (7 estados del pipeline CRM)
-- ============================================

INSERT INTO estados_crm_mae (estado_id, codigo, nombre, descripcion, color, icono, orden, es_final, es_ganado) VALUES

(1, 'lead', 'Lead', 'Nuevo registro sin contacto inicial', '#6c757d', 'fa-user-plus', 1, false, false),

(2, 'contacto', 'Contacto', 'Primer contacto realizado, interés confirmado', '#17a2b8', 'fa-phone', 2, false, false),

(3, 'propuesta', 'Propuesta', 'Propuesta formal enviada al cliente', '#ffc107', 'fa-file-alt', 3, false, false),

(4, 'negociacion', 'Negociación', 'En proceso de negociación de términos y precio', '#fd7e14', 'fa-handshake', 4, false, false),

(5, 'pre_cierre', 'Pre-cierre', 'Acuerdo alcanzado, pendiente de firma/pago', '#20c997', 'fa-check-circle', 5, false, false),

(6, 'cerrado_ganado', 'Cerrado Ganado', 'Venta/alquiler cerrado exitosamente', '#28a745', 'fa-trophy', 6, true, true),

(7, 'cerrado_perdido', 'Cerrado Perdido', 'Oportunidad perdida o cancelada', '#dc3545', 'fa-times-circle', 7, true, false)

ON CONFLICT (estado_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('estados_crm_mae_estado_id_seq', (SELECT MAX(estado_id) FROM estados_crm_mae));

-- ============================================
-- 📈 RESULTADO: 7 estados CRM creados
-- Pipeline: Lead → Contacto → Propuesta → Negociación → Pre-cierre → Cerrado Ganado/Perdido
-- ============================================
