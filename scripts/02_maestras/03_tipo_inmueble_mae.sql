-- ============================================
-- 🏢 TABLA: tipo_inmueble_mae
-- Catálogo de tipos de inmuebles
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS tipo_inmueble_mae (
    tipo_inmueble_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    icono VARCHAR(50),
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice
CREATE INDEX IF NOT EXISTS idx_tipo_inmueble_activo ON tipo_inmueble_mae(activo);

-- ============================================
-- 📊 INSERTAR FILAS (12 tipos de inmuebles)
-- ============================================

INSERT INTO tipo_inmueble_mae (tipo_inmueble_id, nombre, descripcion, icono, orden) VALUES
(1, 'Oficina en Edificio', 'Oficinas corporativas en edificios empresariales', 'fa-building', 1),
(2, 'Casa', 'Casas independientes unifamiliares', 'fa-home', 2),
(3, 'Departamento', 'Departamentos en edificios residenciales', 'fa-door-closed', 3),
(4, 'Local Comercial', 'Locales para negocios y comercio', 'fa-store', 4),
(5, 'Terreno', 'Terrenos urbanos y rurales', 'fa-map', 5),
(6, 'Almacén', 'Almacenes industriales y logísticos', 'fa-warehouse', 6),
(7, 'Cochera', 'Estacionamientos y cocheras', 'fa-car', 7),
(8, 'Habitación', 'Habitaciones individuales en casas compartidas', 'fa-bed', 8),
(9, 'Oficina Independiente', 'Oficinas en casas o locales independientes', 'fa-briefcase', 9),
(10, 'Consultorio', 'Consultorios médicos y profesionales', 'fa-stethoscope', 10),
(11, 'Depósito', 'Depósitos y espacios de almacenamiento', 'fa-box', 11),
(12, 'Edificio Completo', 'Edificios completos para inversión', 'fa-city', 12)

ON CONFLICT (tipo_inmueble_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('tipo_inmueble_mae_tipo_inmueble_id_seq', (SELECT MAX(tipo_inmueble_id) FROM tipo_inmueble_mae));

-- ============================================
-- 📈 RESULTADO: 12 tipos de inmuebles creados
-- ============================================
