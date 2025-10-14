-- ============================================
-- TABLA: registro_x_inmueble_det
-- Descripción: Detalle de características dinámicas (formulario multipaso)
-- ============================================

DROP TABLE IF EXISTS registro_x_inmueble_det CASCADE;

CREATE TABLE IF NOT EXISTS registro_x_inmueble_det (
  registro_det_id SERIAL PRIMARY KEY,
  registro_cab_id INTEGER NOT NULL REFERENCES registro_x_inmueble_cab(registro_cab_id) ON DELETE CASCADE,
  caracteristica_id INTEGER NOT NULL REFERENCES caracteristicas_mae(caracteristica_id),
  valor TEXT NOT NULL,
  
  -- Auditoría
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_registro_det_cab ON registro_x_inmueble_det(registro_cab_id);
CREATE INDEX idx_registro_det_caracteristica ON registro_x_inmueble_det(caracteristica_id);

-- Comentarios
COMMENT ON TABLE registro_x_inmueble_det IS 'Detalle de características dinámicas del formulario multipaso';
COMMENT ON COLUMN registro_x_inmueble_det.registro_cab_id IS 'Referencia a la cabecera del registro';
COMMENT ON COLUMN registro_x_inmueble_det.caracteristica_id IS 'Característica seleccionada';
COMMENT ON COLUMN registro_x_inmueble_det.valor IS 'Valor de la característica (texto, boolean, número)';

-- ============================================
-- DATOS DE EJEMPLO (33 características)
-- ============================================

INSERT INTO registro_x_inmueble_det (registro_cab_id, caracteristica_id, valor) VALUES

-- Propiedad 1: Depto San Isidro (5 características)
(1, 1, 'true'),   -- Amoblado
(1, 5, 'true'),   -- Seguridad 24h
(1, 8, 'true'),   -- Gimnasio
(1, 12, 'true'),  -- Piscina
(1, 25, 'true'),  -- Mascotas permitidas

-- Propiedad 2: Casa Miraflores (4 características)
(2, 2, 'true'),   -- Jardín
(2, 3, 'true'),   -- Terraza
(2, 5, 'true'),   -- Seguridad 24h
(2, 25, 'true'),  -- Mascotas permitidas

-- Propiedad 3: Oficina San Isidro (3 características)
(3, 1, 'true'),   -- Amoblado
(3, 16, 'true'),  -- Internet de alta velocidad
(3, 18, 'true'),  -- Sala de reuniones

-- Propiedad 4: Depto Surco (4 características)
(4, 1, 'true'),   -- Amoblado
(4, 4, 'true'),   -- Balcón
(4, 8, 'true'),   -- Gimnasio
(4, 20, 'true'),  -- Ascensor

-- Propiedad 5: Local Comercial (2 características)
(5, 7, 'true'),   -- Estacionamiento
(5, 21, 'true'),  -- Esquina

-- Propiedad 6: Depto La Molina (5 características)
(6, 1, 'true'),   -- Amoblado
(6, 5, 'true'),   -- Seguridad 24h
(6, 8, 'true'),   -- Gimnasio
(6, 12, 'true'),  -- Piscina
(6, 25, 'true'),  -- Mascotas permitidas

-- Propiedad 7: Depto San Borja (3 características)
(7, 20, 'true'),  -- Ascensor
(7, 22, 'true'),  -- Cerca al metro
(7, 16, 'true'),  -- Internet incluido

-- Propiedad 8: Casa Surco (4 características)
(8, 2, 'true'),   -- Jardín
(8, 12, 'true'),  -- Piscina
(8, 5, 'true'),   -- Seguridad 24h
(8, 25, 'true'),  -- Mascotas permitidas

-- Propiedad 9: Estudio Barranco (2 características)
(9, 1, 'true'),   -- Amoblado
(9, 16, 'true'),  -- Internet incluido

-- Propiedad 10: Penthouse San Isidro (5 características)
(10, 3, 'true'),  -- Terraza
(10, 13, 'true'), -- Jacuzzi
(10, 8, 'true'),  -- Gimnasio
(10, 5, 'true'),  -- Seguridad 24h
(10, 14, 'true'); -- Vista panorámica

-- ============================================
-- VERIFICACIÓN
-- ============================================

SELECT COUNT(*) as total_caracteristicas FROM registro_x_inmueble_det;

-- Ver características por propiedad
SELECT 
  r.nombre_inmueble,
  COUNT(d.registro_det_id) as total_caracteristicas,
  string_agg(c.nombre, ', ') as caracteristicas
FROM registro_x_inmueble_cab r
LEFT JOIN registro_x_inmueble_det d ON r.registro_cab_id = d.registro_cab_id
LEFT JOIN caracteristicas_mae c ON d.caracteristica_id = c.caracteristica_id
GROUP BY r.registro_cab_id, r.nombre_inmueble
ORDER BY r.registro_cab_id;
