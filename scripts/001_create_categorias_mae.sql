-- ==========================================
-- Script: Crear tabla categorias_mae
-- Descripción: Normalizar categorías de características
-- Autor: Sistema
-- Fecha: 2025-01-02
-- ==========================================

-- 1️⃣ CREAR TABLA categorias_mae
CREATE TABLE IF NOT EXISTS categorias_mae (
    categoria_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2️⃣ INSERTAR CATEGORÍAS EXISTENTES (desde caracteristicas_mae)
INSERT INTO categorias_mae (nombre, orden, activo)
SELECT DISTINCT
    categoria as nombre,
    MIN(orden_categoria) as orden,
    true as activo
FROM caracteristicas_mae
WHERE categoria IS NOT NULL
GROUP BY categoria
ORDER BY MIN(orden_categoria)
ON CONFLICT (nombre) DO NOTHING;

-- 3️⃣ AGREGAR COLUMNA categoria_id a caracteristicas_mae
ALTER TABLE caracteristicas_mae
ADD COLUMN IF NOT EXISTS categoria_id INTEGER REFERENCES categorias_mae(categoria_id);

-- 4️⃣ MIGRAR DATOS: Actualizar categoria_id basado en categoria (VARCHAR)
UPDATE caracteristicas_mae c
SET categoria_id = cat.categoria_id
FROM categorias_mae cat
WHERE c.categoria = cat.nombre;

-- 5️⃣ ÍNDICES PARA RENDIMIENTO
CREATE INDEX IF NOT EXISTS idx_caracteristicas_categoria_id
ON caracteristicas_mae(categoria_id);

CREATE INDEX IF NOT EXISTS idx_categorias_activo
ON categorias_mae(activo);

CREATE INDEX IF NOT EXISTS idx_categorias_orden
ON categorias_mae(orden);

-- 6️⃣ TRIGGER PARA updated_at
CREATE OR REPLACE FUNCTION update_categorias_mae_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_categorias_mae_updated_at
BEFORE UPDATE ON categorias_mae
FOR EACH ROW
EXECUTE FUNCTION update_categorias_mae_updated_at();

-- ==========================================
-- COMENTARIOS EN COLUMNAS
-- ==========================================
COMMENT ON TABLE categorias_mae IS 'Catálogo de categorías para agrupar características';
COMMENT ON COLUMN categorias_mae.categoria_id IS 'ID único de la categoría';
COMMENT ON COLUMN categorias_mae.nombre IS 'Nombre de la categoría (único)';
COMMENT ON COLUMN categorias_mae.descripcion IS 'Descripción detallada de la categoría';
COMMENT ON COLUMN categorias_mae.orden IS 'Orden de presentación en UI';
COMMENT ON COLUMN categorias_mae.activo IS 'Estado activo/inactivo de la categoría';

COMMENT ON COLUMN caracteristicas_mae.categoria_id IS 'FK a categorias_mae (reemplaza columna categoria VARCHAR)';

-- ==========================================
-- VERIFICACIÓN
-- ==========================================
-- Ver categorías creadas:
-- SELECT * FROM categorias_mae ORDER BY orden;

-- Ver características con nueva relación:
-- SELECT c.caracteristica_id, c.nombre, cat.nombre as categoria, c.categoria as categoria_old
-- FROM caracteristicas_mae c
-- LEFT JOIN categorias_mae cat ON c.categoria_id = cat.categoria_id
-- LIMIT 10;

-- ==========================================
-- NOTAS IMPORTANTES
-- ==========================================
-- ⚠️ NO ELIMINAR LA COLUMNA 'categoria' (VARCHAR) TODAVÍA
-- Mantenerla por compatibilidad mientras se actualizan las APIs
-- Una vez probado todo, ejecutar:
-- ALTER TABLE caracteristicas_mae DROP COLUMN categoria;
-- ALTER TABLE caracteristicas_mae DROP COLUMN orden_categoria;
