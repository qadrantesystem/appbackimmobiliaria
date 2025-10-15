-- ============================================
-- TABLA: registro_x_inmueble_tracking
-- Descripción: Seguimiento de cambios de estado en el pipeline CRM
-- ============================================

DROP TABLE IF EXISTS registro_x_inmueble_tracking CASCADE;

CREATE TABLE IF NOT EXISTS registro_x_inmueble_tracking (
  tracking_id SERIAL PRIMARY KEY,
  registro_cab_id INTEGER NOT NULL REFERENCES registro_x_inmueble_cab(registro_cab_id) ON DELETE CASCADE,
  estado_anterior VARCHAR(50),
  estado_nuevo VARCHAR(50) NOT NULL,
  usuario_id INTEGER REFERENCES usuarios(usuario_id),
  corredor_id INTEGER REFERENCES usuarios(usuario_id),
  motivo TEXT,
  metadata_json JSONB,
  ip_address VARCHAR(45),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_tracking_registro_cab ON registro_x_inmueble_tracking(registro_cab_id);
CREATE INDEX idx_tracking_usuario ON registro_x_inmueble_tracking(usuario_id);
CREATE INDEX idx_tracking_corredor ON registro_x_inmueble_tracking(corredor_id);
CREATE INDEX idx_tracking_created ON registro_x_inmueble_tracking(created_at);
CREATE INDEX idx_tracking_estado_nuevo ON registro_x_inmueble_tracking(estado_nuevo);

-- Comentarios
COMMENT ON TABLE registro_x_inmueble_tracking IS 'Seguimiento de cambios de estado en el pipeline CRM';
COMMENT ON COLUMN registro_x_inmueble_tracking.registro_cab_id IS 'Propiedad que cambió de estado';
COMMENT ON COLUMN registro_x_inmueble_tracking.usuario_id IS 'Usuario que realizó el cambio';
COMMENT ON COLUMN registro_x_inmueble_tracking.corredor_id IS 'Corredor asignado si aplica';

-- ============================================
-- DATOS DE EJEMPLO (15 cambios de estado)
-- ============================================

INSERT INTO registro_x_inmueble_tracking (
  registro_cab_id, estado_anterior, estado_nuevo, usuario_id, corredor_id, 
  motivo, metadata_json, ip_address, created_at
) VALUES

-- Propiedad 1: Depto San Isidro
(1, NULL, 'lead', 3, NULL, 'Propiedad registrada por propietario',
 '{"accion": "registro_inicial", "origen": "formulario_web"}', 
 '192.168.1.100', '2024-01-15 10:30:00'),

(1, 'lead', 'contacto', 3, NULL, 'Recibió 8 consultas de interesados',
 '{"accion": "consultas_recibidas", "total_consultas": 8}',
 '192.168.1.100', '2024-01-18 14:20:00'),

-- Propiedad 2: Casa Miraflores
(2, NULL, 'lead', 4, 4, 'Propiedad registrada por corredor',
 '{"accion": "registro_inicial", "propietario": "María López Torres"}',
 '192.168.1.105', '2024-01-16 14:20:00'),

(2, 'lead', 'contacto', 4, 4, 'Cliente interesado agendó visita',
 '{"accion": "visita_agendada", "fecha_visita": "2024-01-20"}',
 '192.168.1.105', '2024-01-19 10:00:00'),

(2, 'contacto', 'propuesta', 4, 4, 'Cliente hizo oferta formal',
 '{"accion": "oferta_recibida", "monto_oferta": 420000}',
 '192.168.1.105', '2024-01-22 16:30:00'),

-- Propiedad 3: Oficina San Isidro
(3, NULL, 'lead', 5, NULL, 'Propiedad registrada',
 '{"accion": "registro_inicial"}',
 '192.168.1.110', '2024-01-17 09:15:00'),

-- Propiedad 4: Depto Surco
(4, NULL, 'lead', 4, 4, 'Propiedad registrada por corredor',
 '{"accion": "registro_inicial", "propietario": "Ana Torres Vega"}',
 '192.168.1.105', '2024-01-18 11:45:00'),

(4, 'lead', 'contacto', 4, 4, 'Múltiples consultas recibidas',
 '{"accion": "consultas_multiples", "total": 15}',
 '192.168.1.105', '2024-01-20 09:00:00'),

(4, 'contacto', 'propuesta', 4, 4, 'Cliente muy interesado',
 '{"accion": "propuesta_enviada"}',
 '192.168.1.105', '2024-01-22 14:00:00'),

(4, 'propuesta', 'negociacion', 4, 4, 'Negociando precio',
 '{"accion": "negociacion_precio", "precio_pedido": 2200, "oferta_cliente": 2000}',
 '192.168.1.105', '2024-01-23 11:00:00'),

-- Propiedad 8: Casa Surco con Piscina
(8, NULL, 'lead', 4, 4, 'Propiedad registrada',
 '{"accion": "registro_inicial", "propietario": "Sofía López Méndez"}',
 '192.168.1.105', '2024-01-22 15:40:00'),

(8, 'lead', 'contacto', 4, 4, 'Cliente interesado',
 '{"accion": "contacto_inicial"}',
 '192.168.1.105', '2024-01-23 10:00:00'),

(8, 'contacto', 'propuesta', 4, 4, 'Propuesta enviada',
 '{"accion": "propuesta_formal"}',
 '192.168.1.105', '2024-01-24 09:00:00'),

(8, 'propuesta', 'pre_cierre', 4, 4, 'Acuerdo alcanzado',
 '{"accion": "acuerdo_verbal", "precio_final": 560000}',
 '192.168.1.105', '2024-01-25 16:00:00'),

-- Propiedad 10: Penthouse San Isidro (CERRADO)
(10, 'pre_cierre', 'cerrado_ganado', 4, 4, 'Contrato firmado',
 '{"accion": "contrato_firmado", "precio_final": 850000, "comision": 42500}',
 '192.168.1.105', '2024-01-24 10:30:00');

-- Reiniciar secuencia
SELECT setval('registro_x_inmueble_tracking_tracking_id_seq', 15, true);

-- ============================================
-- RESULTADO: 15 cambios de estado
-- ============================================

-- Ver historial de una propiedad
SELECT 
  t.tracking_id,
  t.estado_anterior,
  t.estado_nuevo,
  t.motivo,
  t.metadata,
  t.created_at,
  u.nombre_completo as usuario
FROM registro_x_inmueble_tracking t
LEFT JOIN usuarios u ON t.usuario_id = u.usuario_id
WHERE t.registro_cab_id = 1
ORDER BY t.created_at ASC;
