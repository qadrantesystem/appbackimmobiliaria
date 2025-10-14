# 👨‍💼 FLUJO: ASIGNACIÓN DE PERFIL POR ADMIN

## 🎯 Objetivo
El Admin revisa la información del usuario y asigna el perfil correcto (Demandante, Propietario, o Corredor) basándose en su intención de uso y validaciones adicionales.

---

## 📊 Diagrama de Flujo

```
┌─────────────────────────┐
│ Admin recibe            │
│ notificación de         │
│ nuevo usuario           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Admin revisa:           │
│ - Datos del usuario     │
│ - Intención de uso      │
│ - Teléfono verificado   │
└──────────┬──────────────┘
           │
           ▼
      ┌────────┐
      │Decisión│
      └───┬────┘
          │
          ├─── Solo Buscar ─────────────► Perfil: DEMANDANTE
          │                               └─► Activo inmediato
          │
          ├─── Publicar Propiedad ──────► Perfil: PROPIETARIO
          │                               └─► Solicita documentos
          │
          ├─── Ofrecer como Corredor ───► Perfil: CORREDOR
          │                               └─► Solicita licencia
          │
          └─── Sospechoso ──────────────► Solicita más info
                                          └─► O rechaza

┌─────────────────────────┐
│ Admin asigna perfil     │
│ y cambia estado         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Usuario recibe          │
│ notificación            │
│ - Email                 │
│ - Push notification     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Usuario puede usar      │
│ funciones completas     │
│ según su perfil         │
└─────────────────────────┘
```

---

## 👨‍💼 Panel de Admin - Gestión de Usuarios

### Vista de Usuarios Pendientes:

```
┌─────────────────────────────────────────────────────────────┐
│ 🆕 USUARIOS PENDIENTES DE ASIGNACIÓN (3)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 👤 Juan Pérez García                                        │
│    📧 juan.perez@email.com  📱 +51 999 888 777             │
│    📅 Registrado: 15/01/2024 10:30                         │
│    🎯 Intención: ☑️ Buscar  ☐ Publicar  ☐ Corredor        │
│    ✅ Email verificado                                      │
│                                                             │
│    [Demandante] [Propietario] [Corredor] [Solicitar Info]  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 👤 María López Torres                                       │
│    📧 maria.lopez@email.com  📱 +51 987 654 321            │
│    📅 Registrado: 15/01/2024 11:15                         │
│    🎯 Intención: ☑️ Buscar  ☑️ Publicar  ☐ Corredor        │
│    ✅ Email verificado                                      │
│                                                             │
│    [Demandante] [Propietario] [Corredor] [Solicitar Info]  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 👤 Carlos Ruiz Sánchez                                      │
│    📧 carlos.ruiz@inmobiliaria.com  📱 +51 955 444 333     │
│    📅 Registrado: 15/01/2024 14:20                         │
│    🎯 Intención: ☐ Buscar  ☐ Publicar  ☑️ Corredor         │
│    ✅ Email verificado                                      │
│    ⚠️  Requiere validación de licencia                     │
│                                                             │
│    [Demandante] [Propietario] [Corredor] [Solicitar Info]  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Criterios de Asignación

### 1. Perfil: DEMANDANTE (usuario_id: 2)
**Asignar cuando:**
- ✅ Solo marcó "Buscar propiedad"
- ✅ No tiene intención de publicar
- ✅ Email verificado

**Validaciones:**
- Ninguna adicional requerida

**Acción:**
```sql
UPDATE usuarios 
SET perfil_id = 2, 
    estado = 'activo',
    perfil_asignado_at = NOW(),
    perfil_asignado_por = [admin_id]
WHERE usuario_id = [user_id];
```

---

### 2. Perfil: PROPIETARIO (usuario_id: 3)
**Asignar cuando:**
- ✅ Marcó "Publicar mi propiedad"
- ✅ Email verificado
- ✅ Teléfono válido

**Validaciones Adicionales:**
- 📄 Solicitar DNI o RUC
- 📄 Solicitar documento de propiedad (opcional al inicio)

**Modal de Solicitud:**
```
┌─────────────────────────────────────────┐
│ 📄 DOCUMENTOS REQUERIDOS - PROPIETARIO  │
├─────────────────────────────────────────┤
│                                         │
│ Para publicar propiedades necesitamos:  │
│                                         │
│ 1. ✅ DNI o RUC (obligatorio)           │
│    [Subir documento]                    │
│                                         │
│ 2. 📋 Documento de propiedad            │
│    (Opcional ahora, requerido antes     │
│     de publicar)                        │
│                                         │
│ [Enviar Solicitud al Usuario]          │
│                                         │
└─────────────────────────────────────────┘
```

**Acción:**
```sql
-- Asignar perfil
UPDATE usuarios 
SET perfil_id = 3, 
    estado = 'documentos_pendientes',
    perfil_asignado_at = NOW(),
    perfil_asignado_por = [admin_id]
WHERE usuario_id = [user_id];

-- Crear solicitud de documentos
INSERT INTO solicitud_documentos (
  usuario_id,
  tipo_documento,
  estado,
  solicitado_por,
  created_at
) VALUES
  ([user_id], 'DNI', 'pendiente', [admin_id], NOW());
```

---

### 3. Perfil: CORREDOR (usuario_id: 4)
**Asignar cuando:**
- ✅ Marcó "Ofrecer servicios como corredor"
- ✅ Email verificado
- ✅ Teléfono válido

**Validaciones OBLIGATORIAS:**
- 📄 Licencia de corredor vigente
- 📄 DNI o RUC
- 📄 Certificado de antecedentes (opcional)

**Modal de Solicitud:**
```
┌─────────────────────────────────────────┐
│ 🤝 DOCUMENTOS REQUERIDOS - CORREDOR     │
├─────────────────────────────────────────┤
│                                         │
│ Para operar como corredor necesitas:   │
│                                         │
│ 1. ✅ Licencia de Corredor Inmobiliario │
│    (Obligatorio - Ley N° 27796)         │
│    [Subir licencia]                     │
│                                         │
│ 2. ✅ DNI o RUC                         │
│    [Subir documento]                    │
│                                         │
│ 3. 📋 Certificado de Antecedentes       │
│    (Opcional pero recomendado)          │
│    [Subir certificado]                  │
│                                         │
│ ⚠️  Tu cuenta será revisada antes de    │
│    activarse como corredor.             │
│                                         │
│ [Enviar Solicitud al Usuario]          │
│                                         │
└─────────────────────────────────────────┘
```

**Acción:**
```sql
-- Asignar perfil pero mantener inactivo
UPDATE usuarios 
SET perfil_id = 4, 
    estado = 'documentos_pendientes',
    perfil_asignado_at = NOW(),
    perfil_asignado_por = [admin_id]
WHERE usuario_id = [user_id];

-- Crear solicitudes de documentos
INSERT INTO solicitud_documentos (
  usuario_id,
  tipo_documento,
  estado,
  obligatorio,
  solicitado_por,
  created_at
) VALUES
  ([user_id], 'LICENCIA_CORREDOR', 'pendiente', true, [admin_id], NOW()),
  ([user_id], 'DNI', 'pendiente', true, [admin_id], NOW()),
  ([user_id], 'ANTECEDENTES', 'pendiente', false, [admin_id], NOW());
```

---

## 📧 Notificaciones al Usuario

### Email: Perfil Asignado - DEMANDANTE
```
Asunto: ✅ Tu cuenta está activa

Hola Juan,

¡Excelente noticia! Tu cuenta ha sido activada.

Perfil asignado: DEMANDANTE

Ahora puedes:
✅ Buscar propiedades sin límites
✅ Usar filtros avanzados
✅ Contactar propietarios y corredores
✅ Guardar favoritos
✅ Recibir alertas personalizadas

[Explorar Propiedades]

---
Plataforma Inmobiliaria Profesional
```

### Email: Perfil Asignado - PROPIETARIO
```
Asunto: 📄 Documentos requeridos - Perfil Propietario

Hola María,

Tu perfil ha sido asignado como: PROPIETARIO

Para activar completamente tu cuenta y publicar propiedades,
necesitamos que subas los siguientes documentos:

1. ✅ DNI o RUC (obligatorio)

Puedes subirlos desde tu perfil en:
[Mi Cuenta] > [Documentos]

Una vez validados, podrás publicar tus propiedades.

Tiempo de validación: 24-48 horas

---
Plataforma Inmobiliaria Profesional
```

### Email: Perfil Asignado - CORREDOR
```
Asunto: 🤝 Validación de Corredor - Documentos Requeridos

Hola Carlos,

Tu solicitud para operar como CORREDOR está en proceso.

Documentos requeridos:
1. ✅ Licencia de Corredor Inmobiliario (obligatorio)
2. ✅ DNI o RUC (obligatorio)
3. 📋 Certificado de Antecedentes (opcional)

Sube tus documentos en:
[Mi Cuenta] > [Documentos]

⚠️ IMPORTANTE:
- Solo corredores con licencia vigente pueden operar
- Deberás declarar al propietario real en cada publicación
- Las comisiones deben ser transparentes

Tiempo de validación: 3-5 días hábiles

---
Plataforma Inmobiliaria Profesional
```

---

## 🔄 Cambio de Perfil

### ¿Puede un usuario cambiar de perfil?

**SÍ, bajo estas condiciones:**

1. **Demandante → Propietario**
   - Usuario solicita desde su perfil
   - Admin valida y solicita documentos
   
2. **Demandante → Corredor**
   - Usuario solicita desde su perfil
   - Admin valida licencia y documentos
   
3. **Propietario → Corredor**
   - Usuario solicita desde su perfil
   - Admin valida licencia adicional

4. **Corredor → Propietario/Demandante**
   - Solo si renuncia a operar como corredor
   - Admin debe aprobar

### Historial de Cambios:
```sql
CREATE TABLE historial_perfiles (
  historial_id SERIAL PRIMARY KEY,
  usuario_id INTEGER REFERENCES usuarios(usuario_id),
  perfil_anterior_id INTEGER REFERENCES perfiles(perfil_id),
  perfil_nuevo_id INTEGER REFERENCES perfiles(perfil_id),
  motivo TEXT,
  cambiado_por INTEGER REFERENCES usuarios(usuario_id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚨 Casos Especiales

### Usuario Sospechoso
**Señales de alerta:**
- Email temporal o sospechoso
- Datos inconsistentes
- Múltiples registros desde misma IP
- Teléfono no válido

**Acción:**
```
[Solicitar Información Adicional]
[Suspender Temporalmente]
[Rechazar Registro]
```

### Usuario Rechazado
```sql
UPDATE usuarios 
SET estado = 'rechazado',
    motivo_rechazo = 'Datos inconsistentes',
    rechazado_por = [admin_id],
    rechazado_at = NOW()
WHERE usuario_id = [user_id];
```

**Email de Rechazo:**
```
Asunto: Registro no aprobado

Hola [Nombre],

Lamentamos informarte que tu registro no ha sido aprobado.

Motivo: [Motivo específico]

Si crees que esto es un error, puedes contactarnos en:
soporte@plataformainmobiliaria.com

---
Plataforma Inmobiliaria Profesional
```

---

## 📊 Métricas para Admin

### Dashboard de Asignaciones:
```
┌─────────────────────────────────────┐
│ 📊 ESTADÍSTICAS DE PERFILES         │
├─────────────────────────────────────┤
│                                     │
│ Pendientes: 3                       │
│ Asignados hoy: 12                   │
│ Rechazados: 1                       │
│                                     │
│ Por perfil:                         │
│ 🔍 Demandantes: 45 (60%)            │
│ 🏠 Propietarios: 25 (33%)           │
│ 🤝 Corredores: 5 (7%)               │
│                                     │
│ Tiempo promedio asignación: 4 hrs   │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔄 Siguientes Flujos

Según el perfil asignado:
- ➡️ [Flujo 04: Usuario Demandante](./04_usuario_demandante.md)
- ➡️ [Flujo 05: Usuario Propietario](./05_usuario_propietario.md)
- ➡️ [Flujo 06: Usuario Corredor](./06_usuario_corredor.md)
