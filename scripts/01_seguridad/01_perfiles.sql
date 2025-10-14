-- ============================================
-- 👥 TABLA: perfiles
-- Tipos de usuario del sistema
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS perfiles (
    perfil_id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    permisos JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 📊 INSERTAR FILAS (Datos reales)
-- ============================================

INSERT INTO perfiles (perfil_id, nombre, descripcion, permisos) VALUES
(1, 'demandante', 'Usuario que busca inmuebles para alquilar o comprar', 
 '{"buscar": true, "guardar_favoritos": true, "contactar": true, "publicar": false, "ver_historial": true}'::jsonb),

(2, 'ofertante', 'Usuario propietario que publica y gestiona inmuebles', 
 '{"buscar": true, "guardar_favoritos": true, "contactar": true, "publicar": true, "gestionar_propiedades": true, "ver_estadisticas": true}'::jsonb),

(3, 'corredor', 'Agente inmobiliario que gestiona leads y propiedades de terceros', 
 '{"buscar": true, "publicar": true, "gestionar_propiedades": true, "ver_estadisticas": true, "pipeline_crm": true, "asignar_leads": true, "comisiones": true}'::jsonb),

(4, 'admin', 'Administrador del sistema con acceso completo', 
 '{"all": true, "gestionar_usuarios": true, "gestionar_planes": true, "ver_reportes": true, "moderar_contenido": true, "mantenimiento_maestras": true, "aprobar_suscripciones": true}'::jsonb)

ON CONFLICT (perfil_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('perfiles_perfil_id_seq', (SELECT MAX(perfil_id) FROM perfiles));

-- ============================================
-- 📈 RESULTADO: 4 perfiles creados
-- ============================================
