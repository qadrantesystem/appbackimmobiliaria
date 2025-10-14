-- ============================================
-- TABLA: registro_x_inmueble_favoritos
-- Descripción: Propiedades marcadas como favoritas por usuarios
-- ============================================

-- Eliminar tabla si existe
DROP TABLE IF EXISTS registro_x_inmueble_favoritos CASCADE;

-- Crear tabla
CREATE TABLE IF NOT EXISTS registro_x_inmueble_favoritos (
  favorito_id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
  registro_cab_id INTEGER NOT NULL REFERENCES registro_x_inmueble_cab(registro_cab_id) ON DELETE CASCADE,
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, registro_cab_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_favoritos_usuario ON registro_x_inmueble_favoritos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_favoritos_registro_cab ON registro_x_inmueble_favoritos(registro_cab_id);
CREATE INDEX IF NOT EXISTS idx_favoritos_created ON registro_x_inmueble_favoritos(created_at);

-- Comentarios
COMMENT ON TABLE registro_x_inmueble_favoritos IS 'Propiedades marcadas como favoritas por usuarios';
COMMENT ON COLUMN registro_x_inmueble_favoritos.usuario_id IS 'Usuario que marcó como favorito';
COMMENT ON COLUMN registro_x_inmueble_favoritos.registro_cab_id IS 'Propiedad marcada como favorita';

-- ============================================
-- 📊 INSERTAR FILAS (9 favoritos)
-- ============================================
-- USUARIOS EXISTENTES:
-- 2. demandante@email.com (Juan Pérez)
-- 3. ofertante@email.com (María García)
-- 5. ana.martinez@email.com (Ana Martínez)
-- ============================================

INSERT INTO registro_x_inmueble_favoritos (favorito_id, usuario_id, registro_cab_id, notas, created_at) VALUES

-- Usuario 2: Juan Pérez (Demandante) - 4 favoritos
(1, 2, 1, 'Me encanta la ubicación en San Isidro', '2025-01-13 15:36:00'),
(2, 2, 4, 'Departamento moderno, ideal para mí', '2025-01-11 16:36:00'),
(3, 2, 2, NULL, '2025-01-10 14:30:00'),
(4, 2, 6, 'Buena ubicación en Barranco', '2025-01-09 11:20:00'),

-- Usuario 3: María García (Ofertante) - 3 favoritos
(5, 3, 5, 'Excelente local comercial', '2025-01-13 18:51:00'),
(6, 3, 8, 'Casa con piscina, muy interesante', '2025-01-12 09:36:00'),
(7, 3, 10, 'Penthouse de lujo', '2025-01-08 10:15:00'),

-- Usuario 5: Ana Martínez (Demandante) - 2 favoritos
(8, 5, 8, 'Casa perfecta para mi familia', '2025-01-12 14:26:00'),
(9, 5, 9, 'Estudio en Barranco, bien ubicado', '2025-01-11 15:50:00')

ON CONFLICT (usuario_id, registro_cab_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('registro_x_inmueble_favoritos_favorito_id_seq', 9, true);

-- ============================================
-- 📈 RESULTADO: 9 favoritos creados
-- ============================================

-- ============================================
-- 📊 CONSULTAS ÚTILES
-- ============================================

-- Ver favoritos de un usuario
SELECT 
  f.favorito_id,
  f.notas,
  f.created_at,
  r.titulo,
  r.precio_alquiler,
  r.area,
  d.nombre as distrito,
  t.nombre as tipo_inmueble
FROM registro_x_inmueble_favoritos f
JOIN registro_x_inmueble_cab r ON f.registro_cab_id = r.registro_cab_id
JOIN distritos_mae d ON r.distrito_id = d.distrito_id
JOIN tipo_inmueble_mae t ON r.tipo_inmueble_id = t.tipo_inmueble_id
WHERE f.usuario_id = 2
ORDER BY f.created_at DESC;
