-- =====================================================
-- AGREGAR CAMPO AUTORIZADO A TABLA USUARIOS
-- Para sistema de suscripciones y autorización
-- =====================================================

-- 1. Agregar campo autorizado
ALTER TABLE usuarios 
ADD COLUMN autorizado BOOLEAN DEFAULT FALSE NOT NULL;

-- 2. Agregar comentario descriptivo
COMMENT ON COLUMN usuarios.autorizado IS 'Usuario autorizado por admin para módulos especiales de suscripción';

-- 3. Crear índice para optimización de consultas
CREATE INDEX idx_usuarios_autorizado ON usuarios(autorizado)
WHERE perfil_id IN (2, 3);

-- 4. Actualizar usuarios existentes según lógica de negocio
UPDATE usuarios SET autorizado = TRUE WHERE perfil_id = 1; -- Demandantes siempre autorizados
UPDATE usuarios SET autorizado = TRUE WHERE perfil_id = 4; -- Admins siempre autorizados  
UPDATE usuarios SET autorizado = FALSE WHERE perfil_id IN (2, 3); -- Ofertantes/Corredores requieren aprobación

-- 5. Verificar cambios
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    col_description(pgc_catalog.pg_description.objoid, pg_catalog.pg_description.objsubid, column_name) as description
FROM information_schema.columns 
LEFT JOIN pg_catalog.pg_description ON pg_catalog.pg_description.objoid = (SELECT oid FROM pg_class WHERE relname = 'usuarios') 
    AND pg_catalog.pg_description.objsubid = ordinal_position 
WHERE table_name = 'usuarios' AND column_name = 'autorizado';

-- =====================================================
-- RESULTADO ESPERADO:
-- - campo autorizado agregado
-- - usuarios existentes actualizados
-- - índice creado para rendimiento
-- =====================================================
