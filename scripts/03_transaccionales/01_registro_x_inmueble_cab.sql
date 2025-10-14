-- ============================================
-- TABLA: registro_x_inmueble_cab
-- Descripción: Cabecera de propiedades registradas (formulario multipaso)
-- ============================================

DROP TABLE IF EXISTS registro_x_inmueble_cab CASCADE;

CREATE TABLE IF NOT EXISTS registro_x_inmueble_cab (
  registro_cab_id SERIAL PRIMARY KEY,
  
  -- Usuario que registra (propietario directo o corredor)
  usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
  
  -- Datos del propietario real (campos de texto, no FK)
  propietario_real_nombre VARCHAR(200) NOT NULL,
  propietario_real_dni VARCHAR(20) NOT NULL,
  propietario_real_telefono VARCHAR(20) NOT NULL,
  propietario_real_email VARCHAR(100),
  
  -- Corredor asignado (si aplica)
  corredor_asignado_id INTEGER REFERENCES usuarios(usuario_id),
  comision_corredor DECIMAL(5, 2),
  
  -- Datos básicos del inmueble
  tipo_inmueble_id INTEGER NOT NULL REFERENCES tipo_inmueble_mae(tipo_inmueble_id),
  distrito_id INTEGER NOT NULL REFERENCES distritos_mae(distrito_id),
  nombre_inmueble VARCHAR(200) NOT NULL,
  direccion VARCHAR(300) NOT NULL,
  latitud DECIMAL(10, 8),
  longitud DECIMAL(11, 8),
  
  -- Características básicas
  area DECIMAL(10, 2) NOT NULL,
  habitaciones INTEGER,
  banos INTEGER,
  parqueos INTEGER,
  antiguedad INTEGER,
  
  -- Precios
  transaccion VARCHAR(20) CHECK (transaccion IN ('venta', 'alquiler', 'ambos')),
  precio_venta DECIMAL(12, 2),
  precio_alquiler DECIMAL(10, 2),
  moneda VARCHAR(3) DEFAULT 'PEN',
  
  -- Descripción
  titulo VARCHAR(200) NOT NULL,
  descripcion TEXT,
  
  -- Imágenes
  imagen_principal VARCHAR(500),
  imagenes TEXT[],
  
  -- Documentos
  documentos_url TEXT[],
  documentos_verificados BOOLEAN DEFAULT false,
  verificado_por INTEGER REFERENCES usuarios(usuario_id),
  verificado_at TIMESTAMP,
  
  -- Estado CRM
  estado_crm VARCHAR(50) DEFAULT 'lead' CHECK (estado_crm IN ('lead', 'contacto', 'propuesta', 'negociacion', 'pre_cierre', 'cerrado_ganado', 'cerrado_perdido')),
  
  -- Estado de publicación
  estado VARCHAR(20) DEFAULT 'borrador' CHECK (estado IN ('borrador', 'publicado', 'pausado', 'cerrado', 'rechazado')),
  motivo_rechazo TEXT,
  
  -- Métricas
  vistas INTEGER DEFAULT 0,
  contactos INTEGER DEFAULT 0,
  compartidos INTEGER DEFAULT 0,
  
  -- Auditoría
  created_by INTEGER REFERENCES usuarios(usuario_id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_by INTEGER REFERENCES usuarios(usuario_id),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_registro_cab_usuario ON registro_x_inmueble_cab(usuario_id);
CREATE INDEX idx_registro_cab_corredor ON registro_x_inmueble_cab(corredor_asignado_id);
CREATE INDEX idx_registro_cab_tipo ON registro_x_inmueble_cab(tipo_inmueble_id);
CREATE INDEX idx_registro_cab_distrito ON registro_x_inmueble_cab(distrito_id);
CREATE INDEX idx_registro_cab_estado_crm ON registro_x_inmueble_cab(estado_crm);
CREATE INDEX idx_registro_cab_estado ON registro_x_inmueble_cab(estado);
CREATE INDEX idx_registro_cab_propietario_dni ON registro_x_inmueble_cab(propietario_real_dni);

-- Comentarios
COMMENT ON TABLE registro_x_inmueble_cab IS 'Cabecera de propiedades registradas con formulario multipaso';
COMMENT ON COLUMN registro_x_inmueble_cab.usuario_id IS 'Usuario que registra (propietario directo o corredor)';
COMMENT ON COLUMN registro_x_inmueble_cab.propietario_real_nombre IS 'Nombre del propietario real (texto, no FK)';
COMMENT ON COLUMN registro_x_inmueble_cab.corredor_asignado_id IS 'Corredor asignado si aplica';
COMMENT ON COLUMN registro_x_inmueble_cab.estado_crm IS 'Estado en el pipeline CRM';
COMMENT ON COLUMN registro_x_inmueble_cab.estado IS 'Estado de publicación';

-- ============================================
-- DATOS DE EJEMPLO (10 propiedades)
-- ============================================

INSERT INTO registro_x_inmueble_cab (
  registro_cab_id, usuario_id, propietario_real_nombre, propietario_real_dni, propietario_real_telefono, propietario_real_email,
  corredor_asignado_id, comision_corredor, tipo_inmueble_id, distrito_id, nombre_inmueble, direccion, latitud, longitud,
  area, habitaciones, banos, parqueos, antiguedad, transaccion, precio_alquiler, precio_venta,
  titulo, descripcion, imagen_principal, imagenes, estado_crm, estado, vistas, contactos,
  created_by, created_at
) VALUES

-- Propiedad 1: Departamento en San Isidro (Registrado por ofertante)
(1, 3, 'Juan Pérez García', '12345678', '+51 999 888 777', 'juan.perez@email.com',
 NULL, NULL, 3, 1, 'Depto San Isidro Premium', 'Av. Javier Prado 123', -12.0931, -77.0465,
 85, 2, 2, 1, 5, 'alquiler', 1800, NULL,
 'Hermoso departamento en San Isidro', 'Departamento moderno y acogedor en zona premium de San Isidro.',
 'https://imagekit.io/sala.jpg', ARRAY['sala.jpg', 'cocina.jpg', 'habitacion.jpg'],
 'contacto', 'publicado', 45, 8,
 3, '2024-01-15 10:30:00'),

-- Propiedad 2: Casa en Surco (Registrada por corredor)
(2, 4, 'María López Torres', '87654321', '+51 988 777 666', 'maria.lopez@email.com',
 4, 5.0, 2, 4, 'Casa Surco con Jardín', 'Calle Los Pinos 456', -12.1197, -77.0282,
 180, 3, 3, 2, 10, 'venta', NULL, 450000,
 'Casa espaciosa en Surco', 'Casa de 3 pisos con amplio jardín y terraza.',
 'https://imagekit.io/casa_fachada.jpg', ARRAY['fachada.jpg', 'sala.jpg', 'jardin.jpg'],
 'propuesta', 'publicado', 67, 12,
 4, '2024-01-16 14:20:00'),

-- Propiedad 3: Oficina en San Borja (Registrada por demandante que también ofrece)
(3, 5, 'Carlos Ruiz Sánchez', '11223344', '+51 977 666 555', 'carlos.ruiz@email.com',
 NULL, NULL, 1, 3, 'Oficina San Borja', 'Av. República de Panamá 789', -12.0964, -77.0364,
 120, NULL, 2, 3, 3, 'alquiler', 3500, NULL,
 'Oficina moderna en San Borja', 'Oficina implementada con mobiliario moderno.',
 'https://imagekit.io/oficina.jpg', ARRAY['oficina1.jpg', 'oficina2.jpg'],
 'lead', 'publicado', 23, 3,
 5, '2024-01-17 09:15:00'),

-- Propiedad 4: Departamento en La Molina (Registrada por corredor)
(4, 4, 'Ana Torres Vega', '55667788', '+51 966 555 444', 'ana.torres@email.com',
 4, 5.0, 3, 5, 'Depto La Molina Moderno', 'Av. Primavera 321', -12.1391, -76.9897,
 95, 2, 2, 1, 2, 'alquiler', 2200, NULL,
 'Departamento moderno en La Molina', 'Depto nuevo con acabados de primera.',
 'https://imagekit.io/depto_surco.jpg', ARRAY['sala_surco.jpg', 'cocina_surco.jpg'],
 'negociacion', 'publicado', 89, 15,
 4, '2024-01-18 11:45:00'),

-- Propiedad 5: Local Comercial en Miraflores (Registrada por propietario)
(5, 3, 'Luis Gómez Paredes', '99887766', '+51 955 444 333', 'luis.gomez@email.com',
 NULL, NULL, 4, 2, 'Local Comercial Miraflores', 'Av. Larco 654', -12.1208, -77.0301,
 80, NULL, 1, NULL, 8, 'alquiler', 4000, NULL,
 'Local comercial en zona comercial', 'Local en esquina con alta afluencia.',
 'https://imagekit.io/local.jpg', ARRAY['local_frente.jpg', 'local_interior.jpg'],
 'lead', 'publicado', 34, 5,
 3, '2024-01-19 16:30:00'),

-- Propiedad 6: Departamento en Barranco (Registrada por corredor)
(6, 4, 'Carmen Silva Rojas', '44556677', '+51 944 333 222', 'carmen.silva@email.com',
 4, 5.0, 3, 6, 'Depto Barranco', 'Av. Grau 987', -12.0823, -76.9414,
 110, 3, 2, 2, 4, 'alquiler', 2500, NULL,
 'Departamento amplio en Barranco', 'Depto con vista a parque y áreas verdes.',
 'https://imagekit.io/depto_molina.jpg', ARRAY['sala_molina.jpg', 'habitacion_molina.jpg'],
 'contacto', 'publicado', 56, 9,
 4, '2024-01-20 10:00:00'),

-- Propiedad 7: Habitación en Jesús María (Registrada por propietario)
(7, 5, 'Pedro Ramírez Castro', '33445566', '+51 933 222 111', 'pedro.ramirez@email.com',
 NULL, NULL, 8, 7, 'Habitación Jesús María', 'Av. San Felipe 147', -12.0931, -76.9964,
 20, 1, 1, NULL, 6, 'alquiler', 600, NULL,
 'Habitación cómoda en Jesús María', 'Habitación en casa compartida, cerca al metro.',
 'https://imagekit.io/depto_sanborja.jpg', ARRAY['sala_sb.jpg', 'habitacion_sb.jpg'],
 'lead', 'publicado', 28, 4,
 5, '2024-01-21 13:20:00'),

-- Propiedad 8: Casa en Surco (Registrada por corredor)
(8, 4, 'Sofía López Méndez', '22334455', '+51 922 111 000', 'sofia.lopez@email.com',
 4, 5.0, 2, 4, 'Casa Surco con Piscina', 'Calle Las Magnolias 258', -12.1431, -76.9797,
 220, 4, 3, 3, 7, 'venta', NULL, 580000,
 'Casa con piscina en Surco', 'Casa amplia con piscina y jardín grande.',
 'https://imagekit.io/casa_surco.jpg', ARRAY['casa_fachada_surco.jpg', 'piscina.jpg'],
 'pre_cierre', 'publicado', 102, 18,
 4, '2024-01-22 15:40:00'),

-- Propiedad 9: Departamento en Barranco (Registrada por propietario)
(9, 3, 'Roberto Díaz Flores', '11998877', '+51 911 000 999', 'roberto.diaz@email.com',
 NULL, NULL, 3, 6, 'Estudio Barranco', 'Av. Grau 369', -12.1464, -77.0197,
 45, 1, 1, NULL, 3, 'alquiler', 1200, NULL,
 'Estudio moderno en Barranco', 'Estudio ideal para estudiantes o profesionales.',
 'https://imagekit.io/estudio.jpg', ARRAY['estudio_sala.jpg', 'estudio_cocina.jpg'],
 'lead', 'publicado', 19, 2,
 3, '2024-01-23 09:10:00'),

-- Propiedad 10: Departamento en San Isidro (Registrada por corredor)
(10, 4, 'Patricia Vargas Luna', '66778899', '+51 900 999 888', 'patricia.vargas@email.com',
 4, 5.0, 3, 1, 'Penthouse San Isidro', 'Av. Conquistadores 741', -12.0897, -77.0397,
 200, 4, 4, 3, 1, 'venta', NULL, 850000,
 'Penthouse de lujo en San Isidro', 'Penthouse con terraza, jacuzzi y vista panorámica.',
 'https://imagekit.io/penthouse.jpg', ARRAY['penthouse_sala.jpg', 'terraza.jpg', 'jacuzzi.jpg'],
 'cerrado_ganado', 'publicado', 145, 25,
 4, '2024-01-24 10:30:00');

-- Reiniciar secuencia
SELECT setval('registro_x_inmueble_cab_registro_cab_id_seq', 10, true);

-- ============================================
-- TRIGGER: Actualizar updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_registro_cab_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_registro_cab_timestamp
BEFORE UPDATE ON registro_x_inmueble_cab
FOR EACH ROW
EXECUTE FUNCTION update_registro_cab_timestamp();

-- ============================================
-- VERIFICACIÓN
-- ============================================

SELECT COUNT(*) as total_propiedades FROM registro_x_inmueble_cab;

SELECT 
  CONCAT(u.nombre, ' ', u.apellido) as registrado_por,
  COUNT(r.registro_cab_id) as total_propiedades,
  SUM(CASE WHEN r.corredor_asignado_id IS NOT NULL THEN 1 ELSE 0 END) as con_corredor
FROM registro_x_inmueble_cab r
JOIN usuarios u ON r.usuario_id = u.usuario_id
GROUP BY u.usuario_id, u.nombre, u.apellido
ORDER BY total_propiedades DESC;
