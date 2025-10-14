-- ============================================
-- 🔍 TABLA: busqueda_x_inmueble_mov
-- Historial de búsquedas realizadas + Búsquedas guardadas para alertas
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS busqueda_x_inmueble_mov (
    busqueda_id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(usuario_id),
    sesion_id VARCHAR(100),
    
    -- Criterios de búsqueda
    tipo_inmueble_id INTEGER REFERENCES tipo_inmueble_mae(tipo_inmueble_id),
    distritos_ids INTEGER[],
    transaccion VARCHAR(20),
    precio_min DECIMAL(12, 2),
    precio_max DECIMAL(12, 2),
    area_min DECIMAL(10, 2),
    area_max DECIMAL(10, 2),
    habitaciones INTEGER[],
    banos INTEGER[],
    parqueos_min INTEGER,
    antiguedad_max INTEGER,
    implementacion VARCHAR(50),
    filtros_avanzados JSONB,
    
    -- Resultados
    cantidad_resultados INTEGER,
    
    -- NUEVO: Campos para búsquedas guardadas (alertas)
    es_guardada BOOLEAN DEFAULT false,
    nombre_busqueda VARCHAR(100),
    frecuencia_alerta VARCHAR(20) CHECK (frecuencia_alerta IN ('inmediata', 'diaria', 'semanal')),
    alerta_activa BOOLEAN DEFAULT false,
    ultima_notificacion TIMESTAMP,
    total_notificaciones INTEGER DEFAULT 0,
    
    -- Auditoría
    fecha_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_busqueda_usuario ON busqueda_x_inmueble_mov(usuario_id);
CREATE INDEX IF NOT EXISTS idx_busqueda_fecha ON busqueda_x_inmueble_mov(fecha_busqueda);
CREATE INDEX IF NOT EXISTS idx_busqueda_tipo ON busqueda_x_inmueble_mov(tipo_inmueble_id);
CREATE INDEX IF NOT EXISTS idx_busqueda_guardada ON busqueda_x_inmueble_mov(es_guardada, alerta_activa) WHERE es_guardada = true;

-- Comentarios
COMMENT ON COLUMN busqueda_x_inmueble_mov.es_guardada IS 'true = búsqueda guardada para alertas, false = búsqueda histórica';
COMMENT ON COLUMN busqueda_x_inmueble_mov.nombre_busqueda IS 'Nombre descriptivo solo si es_guardada = true';
COMMENT ON COLUMN busqueda_x_inmueble_mov.frecuencia_alerta IS 'Frecuencia de notificaciones solo si es_guardada = true';
COMMENT ON COLUMN busqueda_x_inmueble_mov.alerta_activa IS 'Si la alerta está activa (puede pausarse)';

-- ============================================
-- 📊 INSERTAR FILAS (15 búsquedas históricas)
-- ============================================
-- USUARIOS EXISTENTES:
-- 2. demandante@email.com (Juan Pérez)
-- 3. ofertante@email.com (María García)
-- 5. ana.martinez@email.com (Ana Martínez)
-- ============================================

INSERT INTO busqueda_x_inmueble_mov (usuario_id, sesion_id, tipo_inmueble_id, distritos_ids, transaccion, precio_max, area_min, area_max, parqueos_min, antiguedad_max, implementacion, filtros_avanzados, cantidad_resultados, fecha_busqueda, ip_address) VALUES

-- Búsquedas de Juan Pérez (usuario_id = 2)
(2, NULL, 1, ARRAY[1, 2, 3], 'alquiler', 5000, 400, 600, 6, 10, 'Implementada',
 '{"AREAS_COMUNES_EDIFICIO": {"9": true, "8": true}, "ASCENSORES": {"20": true}}'::jsonb,
 3, '2025-01-13 15:30:00', '192.168.1.100'),

(2, NULL, 1, ARRAY[1, 3], 'compra', 800000, 350, 500, 5, 5, NULL,
 '{"AREAS_COMUNES_EDIFICIO": {"15": true}}'::jsonb,
 2, '2025-01-12 10:15:00', '192.168.1.100'),

(2, NULL, 1, ARRAY[1, 2, 3, 4], 'alquiler', 6000, 450, 550, 8, 5, 'Amoblado FULL',
 '{"AREAS_COMUNES_EDIFICIO": {"9": true, "11": true, "15": true}, "IMPLEMENTACION_DETALLE": {"29": true, "30": true}}'::jsonb,
 1, '2025-01-11 16:30:00', '192.168.1.100'),

(2, NULL, 1, ARRAY[1], 'alquiler', 4500, 400, 500, 7, 6, 'Implementada',
 '{"AREAS_COMUNES_EDIFICIO": {"8": true, "9": true}}'::jsonb,
 2, '2025-01-10 14:00:00', '192.168.1.100'),

-- Búsquedas de María García (usuario_id = 3)
(3, NULL, 1, ARRAY[4], 'alquiler', 4000, 300, 450, 4, 8, 'Semi Implementada',
 '{}'::jsonb,
 4, '2025-01-13 18:45:00', '192.168.1.105'),

(3, NULL, 1, ARRAY[3, 4], 'alquiler', 3500, 280, 400, 5, 10, NULL,
 '{"CERCANIA_ESTRATEGICA": {"40": true, "41": true}}'::jsonb,
 3, '2025-01-12 09:30:00', '192.168.1.105'),

(3, NULL, 1, ARRAY[1, 3], 'compra', 700000, 350, 450, 6, 5, 'Implementada',
 '{"IMPLEMENTACION_DETALLE": {"25": true, "27": true}}'::jsonb,
 2, '2025-01-08 17:20:00', '192.168.1.105'),

-- Búsquedas de Ana Martínez (usuario_id = 5)
(5, NULL, 2, ARRAY[5], 'compra', 500000, 200, 300, 2, 20, NULL,
 '{}'::jsonb,
 2, '2025-01-12 14:20:00', '192.168.1.110'),

(5, NULL, 3, ARRAY[2, 6], 'compra', 350000, 100, 140, 2, 12, NULL,
 '{}'::jsonb,
 2, '2025-01-11 15:45:00', '192.168.1.110'),

(5, NULL, 4, ARRAY[2], 'alquiler', 2500, 60, 100, 0, NULL, NULL,
 '{}'::jsonb,
 3, '2025-01-10 16:00:00', '192.168.1.115'),

(5, NULL, 4, ARRAY[2, 4], 'alquiler', 2000, 70, 90, 0, NULL, NULL,
 '{}'::jsonb,
 2, '2025-01-09 12:00:00', '192.168.1.115'),

-- Búsquedas de usuarios invitados (sin login)
(NULL, 'sess_abc123xyz789', 3, ARRAY[2], 'alquiler', 2000, 80, 150, 1, 15, NULL,
 '{}'::jsonb,
 5, '2025-01-14 09:00:00', '192.168.1.200'),

(NULL, 'sess_def456uvw012', 1, ARRAY[1], 'compra', 1000000, 500, NULL, 10, 3, NULL,
 '{"SOPORTE_EDIFICIO": {"32": true, "34": true}}'::jsonb,
 1, '2025-01-13 11:00:00', '192.168.1.201'),

(NULL, 'sess_ghi789rst345', 6, ARRAY[7], 'alquiler', 4000, 500, NULL, 3, NULL, NULL,
 '{}'::jsonb,
 1, '2025-01-09 10:30:00', '192.168.1.202'),

(NULL, 'sess_jkl012mno678', 1, ARRAY[4], 'alquiler', 3000, 250, 350, 4, 8, NULL,
 '{}'::jsonb,
 3, '2025-01-14 08:15:00', '192.168.1.203');

-- ============================================
-- 💾 BÚSQUEDAS GUARDADAS (con alertas)
-- ============================================

INSERT INTO busqueda_x_inmueble_mov (
  usuario_id, tipo_inmueble_id, distritos_ids, transaccion, 
  precio_min, precio_max, area_min, area_max, habitaciones, banos, parqueos_min,
  filtros_avanzados, cantidad_resultados,
  es_guardada, nombre_busqueda, frecuencia_alerta, alerta_activa,
  ultima_notificacion, total_notificaciones, fecha_busqueda, ip_address
) VALUES

-- Usuario 2: Juan Pérez - Demandante
(2, 1, ARRAY[1], 'alquiler', 1500, 2500, 70, 120, ARRAY[2, 3], ARRAY[2], 1,
 '{"amoblado": true, "mascotas": true}'::jsonb, 12,
 true, 'Deptos San Isidro 2-3 hab', 'diaria', true,
 '2024-01-24 08:00:00', 5, '2024-01-15 10:30:00', '192.168.1.100'),

(2, 2, ARRAY[2], 'alquiler', 3000, 5000, 150, 250, ARRAY[3, 4], ARRAY[2, 3], 2,
 '{"jardin": true}'::jsonb, 8,
 true, 'Casas Miraflores con jardín', 'semanal', true,
 '2024-01-22 08:00:00', 2, '2024-01-16 14:20:00', '192.168.1.100'),

-- Usuario 5: Ana Martínez - Demandante
(5, 1, ARRAY[5], 'alquiler', 1800, 2800, 80, 120, ARRAY[2, 3], ARRAY[2], 1,
 '{"amoblado": true, "seguridad_24h": true, "gimnasio": true}'::jsonb, 9,
 true, 'Deptos amoblados La Molina', 'diaria', true,
 '2024-01-24 08:00:00', 4, '2024-01-19 16:30:00', '192.168.1.115'),

(5, 2, ARRAY[4], 'alquiler', 2500, 4000, 120, 200, ARRAY[3, 4], ARRAY[2, 3], 2,
 '{"jardin": true, "mascotas": true}'::jsonb, 0,
 true, 'Casas Surco para familia', 'semanal', false,  -- PAUSADA
 NULL, 0, '2024-01-20 10:00:00', '192.168.1.115');

-- ============================================
-- 📈 RESULTADO: 15 búsquedas históricas + 4 búsquedas guardadas = 19 total
-- ============================================
