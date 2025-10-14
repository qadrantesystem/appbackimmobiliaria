# 📝 FLUJO: REGISTRO DE USUARIO

## 🎯 Objetivo
Registrar usuarios con datos básicos y establecer términos claros desde el inicio. El perfil específico será asignado por el Admin posteriormente.

---

## 📊 Diagrama de Flujo

```
┌──────────────────┐
│ Usuario hace     │
│ clic en          │
│ "Registrarse"    │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────┐
│ PASO 1: Datos Básicos       │
│ - Nombre completo           │
│ - Email                     │
│ - Teléfono                  │
│ - Contraseña                │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ PASO 2: Preguntas Clave     │
│ ¿Qué buscas en la plataforma?│
│ □ Buscar propiedad          │
│ □ Publicar mi propiedad     │
│ □ Ofrecer servicios como    │
│   corredor                  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ PASO 3: Términos y          │
│ Condiciones                 │
│ - Términos generales        │
│ - Política de privacidad    │
│ - Acuerdo anti-criolladas   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ PASO 4: Verificación Email  │
│ - Envío de código           │
│ - Validación                │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Usuario Registrado          │
│ Perfil: "usuario_generico"  │
│ Estado: "pendiente_perfil"  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Notificación al Admin       │
│ "Nuevo usuario requiere     │
│  asignación de perfil"      │
└────────┬────────────────────┘
         │
         ▼
    [Flujo 03: Asignación de Perfil]
```

---

## 📋 PASO 1: Datos Básicos

### Campos Obligatorios:
```json
{
  "nombre_completo": "string (min 3 caracteres)",
  "email": "string (formato email válido)",
  "telefono": "string (formato +51 999 999 999)",
  "password": "string (min 8 caracteres, 1 mayúscula, 1 número)"
}
```

### Validaciones:
- ✅ Email único (no registrado previamente)
- ✅ Teléfono válido peruano
- ✅ Contraseña segura
- ✅ Nombre completo (no apodos)

---

## 📋 PASO 2: Preguntas Clave

### Pregunta Principal:
**"¿Qué buscas en nuestra plataforma?"**

Opciones (puede seleccionar múltiples):
- 🔍 **Buscar una propiedad para alquilar o comprar**
- 🏠 **Publicar mi propiedad**
- 🤝 **Ofrecer servicios como corredor inmobiliario**

### Propósito:
Esta información ayuda al Admin a asignar el perfil correcto más rápidamente.

---

## 📋 PASO 3: Términos y Condiciones

### 📄 Documentos a Aceptar:

#### 1. Términos Generales de Uso
```
TÉRMINOS Y CONDICIONES - PLATAFORMA INMOBILIARIA

1. OBJETIVO DE LA PLATAFORMA
   Profesionalizar el mercado inmobiliario peruano mediante
   procesos transparentes y verificados.

2. COMPROMISO DEL USUARIO
   - Proporcionar información veraz
   - No realizar prácticas fraudulentas
   - Respetar los derechos de propiedad
   - Cumplir con las regulaciones peruanas

3. TIPOS DE USUARIO
   - Demandante: Busca propiedades
   - Propietario: Publica propiedades propias
   - Corredor: Intermedia (requiere licencia)

[Leer términos completos]
☑️ Acepto los términos y condiciones
```

#### 2. Política de Privacidad
```
POLÍTICA DE PRIVACIDAD

Protegemos tus datos personales según la Ley N° 29733.

Datos que recopilamos:
- Información de contacto
- Historial de búsquedas
- Interacciones con propiedades

Uso de datos:
- Mejorar tu experiencia
- Conectarte con propiedades relevantes
- Comunicaciones importantes

[Leer política completa]
☑️ Acepto la política de privacidad
```

#### 3. Acuerdo Anti-Criolladas ⭐
```
COMPROMISO DE TRANSPARENCIA

Esta plataforma NO tolera:
❌ Publicar propiedades ajenas sin autorización
❌ Ocultar información relevante
❌ Inflar precios artificialmente
❌ Intermediarios no autorizados
❌ Documentación falsa

Si eres CORREDOR:
✅ Debes declarar al propietario real
✅ Debes tener licencia vigente
✅ Comisiones claras desde el inicio

Incumplimiento = Suspensión permanente

☑️ Me comprometo a actuar con transparencia
```

### Validación:
- ✅ Usuario debe marcar las 3 casillas
- ✅ Scroll completo en cada documento
- ✅ Timestamp de aceptación guardado

---

## 📋 PASO 4: Verificación de Email

### Proceso:
1. Sistema envía código de 6 dígitos al email
2. Usuario ingresa el código
3. Código válido por 15 minutos
4. Máximo 3 intentos

### Email de Verificación:
```
Asunto: Verifica tu cuenta - Plataforma Inmobiliaria

Hola [Nombre],

Tu código de verificación es:

    [ 1 2 3 4 5 6 ]

Este código expira en 15 minutos.

Si no solicitaste este registro, ignora este email.

---
Plataforma Inmobiliaria Profesional
Cambiando el mercado inmobiliario peruano
```

---

## 💾 Datos Guardados en la BD

### Tabla: `usuarios`
```sql
INSERT INTO usuarios (
  nombre_completo,
  email,
  telefono,
  password_hash,
  perfil_id,  -- 1 (usuario_generico)
  estado,     -- 'pendiente_perfil'
  intencion_uso,  -- JSON con respuestas
  terminos_aceptados_at,
  email_verificado,
  created_at
) VALUES (
  'Juan Pérez García',
  'juan.perez@email.com',
  '+51 999 888 777',
  '$2b$12$...',  -- hash bcrypt
  1,  -- perfil genérico
  'pendiente_perfil',
  '{"buscar": true, "publicar": false, "corredor": false}',
  '2024-01-15 10:30:00',
  true,
  '2024-01-15 10:30:00'
);
```

---

## 🔔 Notificación al Admin

### Dashboard Admin recibe:
```
🆕 NUEVO USUARIO REGISTRADO

Nombre: Juan Pérez García
Email: juan.perez@email.com
Teléfono: +51 999 888 777
Intención: Buscar propiedad
Fecha: 15/01/2024 10:30

[Asignar Perfil] [Ver Detalles]
```

---

## 🎯 Estado Post-Registro

### Usuario puede:
- ✅ Iniciar sesión
- ✅ Ver propiedades ilimitadas
- ✅ Buscar con filtros básicos
- ⏳ Espera asignación de perfil para funciones avanzadas

### Mensaje en la app:
```
👋 ¡Bienvenido, Juan!

Tu cuenta está siendo revisada por nuestro equipo.
Pronto recibirás tu perfil definitivo.

Mientras tanto, puedes explorar propiedades.

⏱️ Tiempo estimado: 24 horas
```

---

## 🔄 Siguiente Paso
➡️ [Flujo 03: Asignación de Perfil por Admin](./03_asignacion_perfil.md)
