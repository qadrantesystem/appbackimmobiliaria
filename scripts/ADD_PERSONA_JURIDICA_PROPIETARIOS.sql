-- ============================================
-- MIGRACIÓN: Soporte Persona Jurídica en Propietarios
-- Fecha: 2026-03-25
-- Autor: Claude Opus 4.6
-- ============================================

-- 1. Agregar campos de persona jurídica
ALTER TABLE propietarios ADD COLUMN IF NOT EXISTS tipo_persona VARCHAR(20) DEFAULT 'natural';
ALTER TABLE propietarios ADD COLUMN IF NOT EXISTS tipo_documento VARCHAR(10) DEFAULT 'DNI';
ALTER TABLE propietarios ADD COLUMN IF NOT EXISTS razon_social VARCHAR(255);
ALTER TABLE propietarios ADD COLUMN IF NOT EXISTS ruc VARCHAR(11);
ALTER TABLE propietarios ADD COLUMN IF NOT EXISTS representante_legal VARCHAR(255);

-- 2. Crear índice en RUC para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_propietarios_ruc ON propietarios(ruc) WHERE ruc IS NOT NULL;

-- 3. Asegurar que propietarios existentes tengan tipo_persona='natural'
UPDATE propietarios SET tipo_persona = 'natural' WHERE tipo_persona IS NULL;
UPDATE propietarios SET tipo_documento = 'DNI' WHERE tipo_documento IS NULL;

-- ROLLBACK (si es necesario revertir):
-- ALTER TABLE propietarios DROP COLUMN IF EXISTS tipo_persona;
-- ALTER TABLE propietarios DROP COLUMN IF EXISTS tipo_documento;
-- ALTER TABLE propietarios DROP COLUMN IF EXISTS razon_social;
-- ALTER TABLE propietarios DROP COLUMN IF EXISTS ruc;
-- ALTER TABLE propietarios DROP COLUMN IF EXISTS representante_legal;
-- DROP INDEX IF EXISTS idx_propietarios_ruc;
