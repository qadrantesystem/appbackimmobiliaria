-- ================================================================
-- CREAR TABLA contactos_inmueble (Leads/Oportunidades CRM)
-- Ejecutar en DBeaver contra Railway PostgreSQL
-- ================================================================

-- 1. Crear tabla
CREATE TABLE contactos_inmueble (
    contacto_id     SERIAL PRIMARY KEY,
    registro_cab_id INTEGER NOT NULL REFERENCES registro_x_inmueble_cab(registro_cab_id) ON DELETE CASCADE,

    -- Datos del interesado
    usuario_id      INTEGER REFERENCES usuarios(usuario_id),
    nombre          VARCHAR(200) NOT NULL,
    email           VARCHAR(200) NOT NULL,
    telefono        VARCHAR(20),
    mensaje         TEXT,

    -- Tracking
    tipo_contacto   VARCHAR(20) DEFAULT 'registrado',  -- 'invitado' o 'registrado'
    estado          VARCHAR(20) DEFAULT 'nuevo',        -- 'nuevo', 'atendido', 'en_negociacion', 'cerrado'
    corredor_id     INTEGER REFERENCES usuarios(usuario_id),
    notas_corredor  TEXT,

    -- Metadata
    busqueda_id     INTEGER REFERENCES busqueda_x_inmueble_mov(busqueda_id),
    ip_address      VARCHAR(45),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    atendido_at     TIMESTAMP
);

-- 2. Indices para performance
CREATE INDEX idx_contactos_propiedad ON contactos_inmueble(registro_cab_id);
CREATE INDEX idx_contactos_corredor ON contactos_inmueble(corredor_id);
CREATE INDEX idx_contactos_estado ON contactos_inmueble(estado);
CREATE INDEX idx_contactos_created ON contactos_inmueble(created_at DESC);
CREATE INDEX idx_contactos_usuario ON contactos_inmueble(usuario_id);

-- 3. Verificar
SELECT 'Tabla contactos_inmueble creada exitosamente' AS resultado;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'contactos_inmueble'
ORDER BY ordinal_position;
