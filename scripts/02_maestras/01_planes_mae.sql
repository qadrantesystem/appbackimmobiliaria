-- ============================================
-- 💳 TABLA: planes_mae
-- Catálogo de planes de suscripción
-- ============================================

-- Crear tabla
CREATE TABLE IF NOT EXISTS planes_mae (
    plan_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_mensual DECIMAL(10, 2),
    precio_anual DECIMAL(10, 2),
    moneda VARCHAR(3) DEFAULT 'USD',
    max_propiedades INTEGER,
    max_imagenes_por_propiedad INTEGER,
    destacar_propiedades BOOLEAN DEFAULT false,
    soporte_prioritario BOOLEAN DEFAULT false,
    caracteristicas JSONB,
    activo BOOLEAN DEFAULT true,
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 📊 INSERTAR FILAS (4 planes reales)
-- ============================================

INSERT INTO planes_mae (plan_id, nombre, descripcion, precio_mensual, precio_anual, max_propiedades, max_imagenes_por_propiedad, destacar_propiedades, soporte_prioritario, caracteristicas, orden) VALUES

(1, 'Gratuito', 'Plan básico para comenzar a publicar propiedades', 
 0, 0, 3, 5, false, false,
 '{"publicaciones": 3, "imagenes": 5, "destacar": false, "soporte": "email", "estadisticas_basicas": true, "anuncios": true}'::jsonb, 1),

(2, 'Básico', 'Ideal para propietarios individuales', 
 29.99, 299.99, 10, 15, false, false,
 '{"publicaciones": 10, "imagenes": 15, "destacar": false, "soporte": "email", "estadisticas_avanzadas": true, "anuncios": false, "badge_verificado": true}'::jsonb, 2),

(3, 'Profesional', 'Para agentes inmobiliarios y pequeñas inmobiliarias', 
 79.99, 799.99, 50, 30, true, true,
 '{"publicaciones": 50, "imagenes": 30, "destacar": true, "destacados_simultaneos": 5, "soporte": "prioritario", "estadisticas_avanzadas": true, "anuncios": false, "badge_verificado": true, "tours_virtuales": true, "api_access": true}'::jsonb, 3),

(4, 'Empresarial', 'Solución completa para grandes inmobiliarias', 
 199.99, 1999.99, NULL, 100, true, true,
 '{"publicaciones": "ilimitadas", "imagenes": 100, "destacar": true, "destacados_simultaneos": 20, "soporte": "dedicado", "estadisticas_avanzadas": true, "anuncios": false, "badge_verificado": true, "tours_virtuales": true, "api_access": true, "multi_usuario": true, "branding_personalizado": true, "reportes_personalizados": true}'::jsonb, 4)

ON CONFLICT (plan_id) DO NOTHING;

-- Resetear secuencia
SELECT setval('planes_mae_plan_id_seq', (SELECT MAX(plan_id) FROM planes_mae));

-- ============================================
-- 📈 RESULTADO: 4 planes creados
-- ============================================
