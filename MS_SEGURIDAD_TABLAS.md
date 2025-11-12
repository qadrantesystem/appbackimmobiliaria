# Microservicio de Seguridad - Tablas Simplificadas

## 📋 Descripción General
Microservicio de seguridad simple y efectivo basado en el modelo existente del sistema inmobiliario.

## 🔐 Tablas de Seguridad (Simplificadas)

### 1. usuarios (Ya existe - ajustes para PostgreSQL)
```sql
CREATE TABLE usuarios (
    usuario_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    dni VARCHAR(20),
    foto_perfil VARCHAR(500),
    tipo_persona VARCHAR(20) DEFAULT 'natural',
    tipo_documento VARCHAR(10) DEFAULT 'DNI',
    razon_social VARCHAR(255),
    ruc VARCHAR(11),
    representante_legal VARCHAR(255),
    perfil_id INTEGER NOT NULL REFERENCES perfiles(perfil_id),
    estado VARCHAR(20) DEFAULT 'pendiente',
    email_verificado BOOLEAN DEFAULT FALSE,
    plan_id INTEGER REFERENCES planes_mae(plan_id),
    fecha_inicio_suscripcion TIMESTAMP,
    fecha_fin_suscripcion TIMESTAMP,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_sesion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. perfiles (Ya existe - ajustes para PostgreSQL)
```sql
CREATE TABLE perfiles (
    perfil_id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255),
    permisos JSONB,  -- JSONB es más eficiente que JSON en PostgreSQL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. sesiones (Nueva - simple)
```sql
CREATE TABLE sesiones (
    sesion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL,
    fecha_expiracion TIMESTAMP NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. intentos_login (Nueva - simple)
```sql
CREATE TABLE intentos_login (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    exitoso BOOLEAN DEFAULT FALSE,
    fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. email_verification_tokens (Ya existe - ajustes para PostgreSQL)
```sql
CREATE TABLE email_verification_tokens (
    id BIGSERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. password_reset_tokens (Ya existe - ajustes para PostgreSQL)
```sql
CREATE TABLE password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 Índices Esenciales (PostgreSQL)
```sql
-- Índices para usuarios
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_estado ON usuarios(estado);

-- Índices para sesiones  
CREATE INDEX idx_sesiones_usuario ON sesiones(usuario_id);
CREATE INDEX idx_sesiones_activa ON sesiones(activa);
CREATE INDEX idx_sesiones_expiracion ON sesiones(fecha_expiracion);

-- Índices para intentos_login
CREATE INDEX idx_intentos_email ON intentos_login(email);
CREATE INDEX idx_intentos_fecha ON intentos_login(fecha_intento);

-- Índices para tokens
CREATE INDEX idx_email_tokens_usuario ON email_verification_tokens(usuario_id);
CREATE INDEX idx_email_tokens_email ON email_verification_tokens(email);
CREATE INDEX idx_password_tokens_usuario ON password_reset_tokens(usuario_id);
CREATE INDEX idx_password_tokens_email ON password_reset_tokens(email);

-- Índice GIN para JSONB (muy eficiente para consultas de permisos)
CREATE INDEX idx_perfiles_permisos ON perfiles USING GIN(permisos);
```

## 🔗 Relaciones (PostgreSQL)
1. **usuarios** ←→ **perfiles** (Muchos a Uno)
2. **usuarios** ←→ **sesiones** (Uno a Muchos) 
3. **usuarios** ←→ **tokens** (Uno a Muchos)

## 🚀 Funcionalidades Clave
- ✅ Login JWT simple
- ✅ Verificación de email  
- ✅ Recuperación de contraseña
- ✅ Control de sesiones
- ✅ Bloqueo por intentos fallidos
- ✅ Permisos por perfil (JSONB optimizado)

## 🎯 Ventajas de PostgreSQL
- **SERIAL/BIGSERIAL**: Auto-incremental eficiente
- **UUID**: Identificadores únicos globales
- **JSONB**: Más rápido que JSON con índices GIN
- **TIMESTAMP**: Precisión temporal completa
- **Índices optimizados**: Mejor rendimiento
