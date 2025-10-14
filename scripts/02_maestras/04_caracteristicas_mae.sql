-- ============================================
-- 🏷️ TABLA: caracteristicas_mae
-- Catálogo de características de inmuebles
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS caracteristicas_mae (
    caracteristica_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo_input VARCHAR(20) NOT NULL CHECK (tipo_input IN ('checkbox', 'number', 'select', 'range')),
    unidad VARCHAR(20),
    categoria VARCHAR(100),
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_caracteristicas_categoria ON caracteristicas_mae(categoria);
CREATE INDEX IF NOT EXISTS idx_caracteristicas_activo ON caracteristicas_mae(activo);

-- ============================================
-- 📊 INSERTAR FILAS (51 características reales)
-- ============================================

-- ÁREAS COMUNES DEL EDIFICIO (18 características)
INSERT INTO caracteristicas_mae (caracteristica_id, nombre, descripcion, tipo_input, unidad, categoria, orden) VALUES
(1, 'Parqueos Simples', 'Espacios de estacionamiento estándar', 'number', 'unid', 'AREAS_COMUNES_EDIFICIO', 1),
(2, 'Parqueos Dobles', 'Espacios de estacionamiento dobles', 'number', 'unid', 'AREAS_COMUNES_EDIFICIO', 2),
(3, 'Depósito metraje', 'Área de depósito disponible', 'number', 'm²', 'AREAS_COMUNES_EDIFICIO', 3),
(4, 'Parqueos para Bicicletas', 'Estacionamiento para bicicletas', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 4),
(5, 'Parqueos Vehículos Eléctricos', 'Estacionamiento con carga para vehículos eléctricos', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 5),
(6, 'Parqueos de visita', 'Estacionamiento para visitantes', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 6),
(7, 'Locales Comerciales', 'Locales comerciales en el edificio', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 7),
(8, 'Cafetería', 'Cafetería dentro del edificio', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 8),
(9, 'GYM', 'Gimnasio en el edificio', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 9),
(10, 'Oficina Trámite Documentos', 'Oficina administrativa para trámites', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 10),
(11, 'Salas de Reuniones', 'Salas de reuniones compartidas', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 11),
(12, 'SUM', 'Salón de usos múltiples', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 12),
(13, 'Comedor', 'Comedor común', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 13),
(14, 'Depósitos', 'Número de depósitos disponibles', 'number', 'unid', 'AREAS_COMUNES_EDIFICIO', 14),
(15, 'Rooftop', 'Terraza en la azotea', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 15),
(16, 'Espacios After Office', 'Áreas de esparcimiento después del trabajo', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 16),
(17, 'Duchas y Vestuarios', 'Duchas y vestuarios disponibles', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 17),
(18, 'Helipuerto', 'Helipuerto en el edificio', 'checkbox', NULL, 'AREAS_COMUNES_EDIFICIO', 18),

-- ASCENSORES (3 características)
(19, 'Montacarga', 'Ascensor de carga', 'checkbox', NULL, 'ASCENSORES', 1),
(20, 'De Sótano directo a Oficina', 'Ascensor directo desde sótano', 'checkbox', NULL, 'ASCENSORES', 2),
(21, 'De Sótano a Piso 1 (con trasbordo)', 'Ascensor con trasbordo en piso 1', 'checkbox', NULL, 'ASCENSORES', 3),

-- IMPLEMENTACIÓN DETALLE (10 características)
(22, 'Pisos', 'Piso de la oficina', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 1),
(23, 'Falso Techo', 'Falso techo instalado', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 2),
(24, 'Luminarias', 'Sistema de iluminación', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 3),
(25, 'Aire Acondicionado', 'Sistema de aire acondicionado', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 4),
(26, 'Red Contra Incendios Sprinklers', 'Sistema contra incendios con sprinklers', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 5),
(27, 'Fibra Óptica / Telefonía', 'Conexión de fibra óptica y telefonía', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 6),
(28, 'Tabiques y Mamparas', 'Divisiones de espacios', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 7),
(29, 'Mobiliario / Escritorios', 'Mobiliario de oficina incluido', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 8),
(30, 'Sillas', 'Sillas de oficina incluidas', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 9),
(31, 'Rollers', 'Cortinas roller instaladas', 'checkbox', NULL, 'IMPLEMENTACION_DETALLE', 10),

-- SOPORTE DEL EDIFICIO (7 características)
(32, 'Generador / Grupo Electrógeno', 'Sistema de generación eléctrica de respaldo', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 1),
(33, 'Encendido manual', 'Generador con encendido manual', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 2),
(34, 'Encendido automático', 'Generador con encendido automático', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 3),
(35, 'Chiller para AACC', 'Sistema chiller para aire acondicionado', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 4),
(36, 'Cuartos Técnicos / Condensadores', 'Espacios técnicos para equipos', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 5),
(37, 'Fibra Óptica', 'Conexión de fibra óptica', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 6),
(38, 'Recepción / Seguridad 24h7', 'Recepción y seguridad las 24 horas', 'checkbox', NULL, 'SOPORTE_EDIFICIO', 7),

-- CERCANÍA ESTRATÉGICA (6 características)
(39, 'Avenidas importantes', 'Ubicado en avenidas principales', 'checkbox', NULL, 'CERCANIA_ESTRATEGICA', 1),
(40, 'Estaciones Tren Eléctrico', 'Cerca de estaciones del tren eléctrico', 'checkbox', NULL, 'CERCANIA_ESTRATEGICA', 2),
(41, 'Bancos o Financieras', 'Cerca de entidades bancarias', 'checkbox', NULL, 'CERCANIA_ESTRATEGICA', 3),
(42, 'Parqueo Público', 'Estacionamiento público cercano', 'checkbox', NULL, 'CERCANIA_ESTRATEGICA', 4),
(43, 'Hoteles', 'Hoteles en la zona', 'checkbox', NULL, 'CERCANIA_ESTRATEGICA', 5),
(44, 'Restaurantes, Copias, Servicios', 'Servicios complementarios cercanos', 'checkbox', NULL, 'CERCANIA_ESTRATEGICA', 6),

-- VISTA DE LA OFICINA (7 características)
(45, 'Frente con doble altura', 'Fachada con doble altura', 'checkbox', NULL, 'VISTA_OFICINA', 1),
(46, 'Doble frente (esquina)', 'Ubicación en esquina con dos frentes', 'checkbox', NULL, 'VISTA_OFICINA', 2),
(47, 'Vista frente al parque', 'Vista hacia parque o área verde', 'checkbox', NULL, 'VISTA_OFICINA', 3),
(48, 'Vista interior', 'Vista hacia el interior del edificio', 'checkbox', NULL, 'VISTA_OFICINA', 4),
(49, 'Vista frontal', 'Vista hacia la calle principal', 'checkbox', NULL, 'VISTA_OFICINA', 5),
(50, 'Vista posterior', 'Vista hacia la parte posterior', 'checkbox', NULL, 'VISTA_OFICINA', 6),
(51, 'Rooftop / Duchas y Vestuarios', 'Terraza con duchas y vestuarios', 'checkbox', NULL, 'VISTA_OFICINA', 7)

ON CONFLICT (caracteristica_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('caracteristicas_mae_caracteristica_id_seq', (SELECT MAX(caracteristica_id) FROM caracteristicas_mae));

-- ============================================
-- 📈 RESULTADO: 51 características creadas
-- Agrupadas en 6 categorías
-- ============================================
