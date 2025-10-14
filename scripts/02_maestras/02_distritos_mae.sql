-- ============================================
-- 📍 TABLA: distritos_mae
-- Catálogo de distritos de Lima
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS distritos_mae (
    distrito_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100),
    provincia VARCHAR(100),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    activo BOOLEAN DEFAULT true,
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice
CREATE INDEX IF NOT EXISTS idx_distritos_activo ON distritos_mae(activo);

-- ============================================
-- 📊 INSERTAR FILAS (10 distritos de Lima)
-- ============================================

INSERT INTO distritos_mae (distrito_id, nombre, ciudad, provincia, latitud, longitud, orden) VALUES
(1, 'San Isidro', 'Lima', 'Lima', -12.0969, -77.0347, 1),
(2, 'Miraflores', 'Lima', 'Lima', -12.1196, -77.0283, 2),
(3, 'San Borja', 'Lima', 'Lima', -12.0894, -76.9969, 3),
(4, 'Surco', 'Lima', 'Lima', -12.1391, -76.9897, 4),
(5, 'La Molina', 'Lima', 'Lima', -12.0797, -76.9397, 5),
(6, 'Barranco', 'Lima', 'Lima', -12.1461, -77.0208, 6),
(7, 'Jesús María', 'Lima', 'Lima', -12.0725, -77.0419, 7),
(8, 'Lince', 'Lima', 'Lima', -12.0833, -77.0333, 8),
(9, 'Magdalena', 'Lima', 'Lima', -12.0908, -77.0650, 9),
(10, 'Pueblo Libre', 'Lima', 'Lima', -12.0769, -77.0633, 10)

ON CONFLICT (distrito_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('distritos_mae_distrito_id_seq', (SELECT MAX(distrito_id) FROM distritos_mae));

-- ============================================
-- 📈 RESULTADO: 10 distritos creados
-- ============================================
