-- ============================================
-- 🔗 TABLA: caracteristicas_x_inmueble_mae
-- Relación entre tipos de inmuebles y características
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS caracteristicas_x_inmueble_mae (
    id SERIAL PRIMARY KEY,
    tipo_inmueble_id INTEGER NOT NULL REFERENCES tipo_inmueble_mae(tipo_inmueble_id),
    caracteristica_id INTEGER NOT NULL REFERENCES caracteristicas_mae(caracteristica_id),
    requerido BOOLEAN DEFAULT false,
    visible_en_filtro BOOLEAN DEFAULT true,
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tipo_inmueble_id, caracteristica_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_carac_x_inmueble_tipo ON caracteristicas_x_inmueble_mae(tipo_inmueble_id);
CREATE INDEX IF NOT EXISTS idx_carac_x_inmueble_carac ON caracteristicas_x_inmueble_mae(caracteristica_id);

-- ============================================
-- 📊 INSERTAR FILAS
-- Todas las 51 características para tipo_inmueble_id = 1 (Oficina en Edificio)
-- ============================================

INSERT INTO caracteristicas_x_inmueble_mae (tipo_inmueble_id, caracteristica_id, orden) VALUES
-- Oficina en Edificio (tipo_inmueble_id = 1) tiene TODAS las características
(1, 1, 1), (1, 2, 2), (1, 3, 3), (1, 4, 4), (1, 5, 5),
(1, 6, 6), (1, 7, 7), (1, 8, 8), (1, 9, 9), (1, 10, 10),
(1, 11, 11), (1, 12, 12), (1, 13, 13), (1, 14, 14), (1, 15, 15),
(1, 16, 16), (1, 17, 17), (1, 18, 18), (1, 19, 19), (1, 20, 20),
(1, 21, 21), (1, 22, 22), (1, 23, 23), (1, 24, 24), (1, 25, 25),
(1, 26, 26), (1, 27, 27), (1, 28, 28), (1, 29, 29), (1, 30, 30),
(1, 31, 31), (1, 32, 32), (1, 33, 33), (1, 34, 34), (1, 35, 35),
(1, 36, 36), (1, 37, 37), (1, 38, 38), (1, 39, 39), (1, 40, 40),
(1, 41, 41), (1, 42, 42), (1, 43, 43), (1, 44, 44), (1, 45, 45),
(1, 46, 46), (1, 47, 47), (1, 48, 48), (1, 49, 49), (1, 50, 50),
(1, 51, 51)

ON CONFLICT (tipo_inmueble_id, caracteristica_id) DO NOTHING;

-- ============================================
-- 📈 RESULTADO: 51 relaciones creadas
-- Para tipo_inmueble_id = 1 (Oficina en Edificio)
-- ============================================

-- NOTA: Agregar más relaciones para otros tipos de inmuebles según necesidad
-- Ejemplo para Casa (tipo_inmueble_id = 2):
-- INSERT INTO caracteristicas_x_inmueble_mae (tipo_inmueble_id, caracteristica_id, orden) VALUES
-- (2, 1, 1), (2, 2, 2), (2, 9, 3), (2, 25, 4), etc.
