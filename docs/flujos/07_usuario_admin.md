# 👨‍💼 FLUJO: USUARIO ADMIN

## 🎯 Objetivo
Monitorear, regular y supervisar TODA la actividad de la plataforma para garantizar transparencia y prevenir malas prácticas.

---

## 📊 Dashboard Admin - Tabs Disponibles

### Tab 1: Super Dashboard 📊
### Tab 2: Gestión de Usuarios 👥
### Tab 3: Cola de Atención 📥
### Tab 4: Suscripciones 💳
### Tab 5: Mantenimiento ⚙️
### Tab 6: Reportes 📄

---

## 📊 Tab 1: Super Dashboard

```
PANEL DE ADMINISTRACIÓN

MÉTRICAS GENERALES
- Usuarios totales: 1,245
- Propiedades activas: 456
- Transacciones este mes: 23
- Reportes pendientes: 3

USUARIOS POR PERFIL
- Demandantes: 845 (68%)
- Propietarios: 325 (26%)
- Corredores: 75 (6%)

ACTIVIDAD HOY
- Nuevos registros: 12
- Propiedades publicadas: 8
- Consultas enviadas: 45

ALERTAS
⚠️ 3 usuarios pendientes de asignación de perfil
⚠️ 2 corredores con licencia por vencer
⚠️ 1 reporte de propiedad sospechosa
```

---

## ✅ Permisos del Admin

### Puede Hacer TODO:
- ✅ Asignar y cambiar perfiles de usuario
- ✅ Aprobar/Rechazar registros
- ✅ Validar documentos
- ✅ Suspender/Reactivar usuarios
- ✅ Editar/Eliminar cualquier propiedad
- ✅ Ver toda la información (incluido propietarios ocultos)
- ✅ Gestionar reportes y disputas
- ✅ Ver estadísticas completas
- ✅ Configurar parámetros del sistema
- ✅ Exportar datos

---

## 👥 Gestión de Usuarios

### Panel de Usuarios:

```
GESTIÓN DE USUARIOS

Filtros:
[Todos ▼] [Activos] [Pendientes] [Suspendidos]

Buscar: [Nombre, email, DNI...]

USUARIOS (1,245)

ID    Nombre              Email                   Perfil        Estado          Acciones
1245  María López         maria@email.com         Demandante    Activo          [Ver] [Editar]
1244  Juan Pérez          juan@email.com          Propietario   Activo          [Ver] [Editar]
1243  Carlos Ruiz         carlos@inmob.com        Corredor      Activo          [Ver] [Editar]
1242  Ana Torres          ana@email.com           Genérico      Pendiente       [Asignar]
1241  Luis Gómez          luis@email.com          Corredor      Suspendido      [Ver] [Reactivar]
```

### Detalle de Usuario:

```
USUARIO #1243 - Carlos Ruiz

INFORMACIÓN BÁSICA
- Nombre: Carlos Ruiz Sánchez
- Email: carlos@inmobiliaria.com
- Teléfono: +51 955 444 333
- DNI: 87654321
- Perfil: Corredor
- Estado: Activo
- Registrado: 15/12/2023

DOCUMENTOS
- Licencia CIP-12345: ✅ Verificada (Vence: 31/12/2025)
- DNI: ✅ Verificado
- Antecedentes: ✅ Verificado

ACTIVIDAD
- Propiedades registradas: 8
- Operaciones cerradas: 12
- Comisiones generadas: S/ 18,750
- Reportes recibidos: 0
- Última actividad: Hoy, 10:30 AM

HISTORIAL DE PERFILES
- 15/12/2023: Genérico → Corredor (por Admin #1)

ACCIONES
[Editar] [Suspender] [Cambiar Perfil] [Ver Propiedades] [Historial Completo]
```

---

## 🏠 Gestión de Propiedades

### Panel de Propiedades:

```
GESTIÓN DE PROPIEDADES

Filtros:
[Todas ▼] [Activas] [Pendientes] [Suspendidas] [Reportadas]

PROPIEDADES (456)

ID   Título                    Propietario      Corredor        Estado      Acciones
456  Depto San Isidro          Juan Pérez       Carlos Ruiz     Activo      [Ver] [Editar]
455  Casa Miraflores           María López      -               Activo      [Ver] [Editar]
454  Depto Surco               Ana Torres       Luis Gómez      Pendiente   [Aprobar]
453  Casa La Molina            ⚠️ Sin datos     Pedro Silva     Reportada   [Revisar]
```

### Detalle de Propiedad:

```
PROPIEDAD #456 - Depto San Isidro

INFORMACIÓN
- Título: Departamento en San Isidro
- Tipo: Departamento
- Distrito: San Isidro
- Precio: S/ 1,800/mes
- Estado: Activo
- Estado CRM: Negociación

PROPIETARIO REAL
- Nombre: Juan Pérez García
- DNI: 12345678
- Teléfono: +51 999 888 777
- Email: juan.perez@email.com
- Usuario ID: 1244

CORREDOR ASIGNADO
- Nombre: Carlos Ruiz Sánchez
- Licencia: CIP-12345
- Comisión: 5%
- Usuario ID: 1243

ESTADÍSTICAS
- Vistas: 89
- Contactos: 7
- Favoritos: 12
- Publicado: hace 15 días

DOCUMENTOS
- Autorización corredor: ✅ Verificada
- Escritura: ✅ Verificada

HISTORIAL
- 10/01/2024: Creada por Corredor #1243
- 12/01/2024: Lead → Contacto
- 15/01/2024: Contacto → Propuesta
- 20/01/2024: Propuesta → Negociación

ACCIONES
[Editar] [Suspender] [Eliminar] [Ver Tracking Completo]
```

---

## 📋 Validación de Documentos

### Documentos Pendientes:

```
DOCUMENTOS PENDIENTES DE VALIDACIÓN (8)

Usuario: Ana Torres (Propietario)
Documento: Escritura - Casa Surco
Subido: hace 2 horas
[Ver Documento] [Aprobar] [Rechazar]

Usuario: Luis Gómez (Corredor)
Documento: Licencia CIP-98765
Subido: hace 5 horas
[Ver Documento] [Aprobar] [Rechazar]
```

### Validar Documento:

```
VALIDAR DOCUMENTO

Usuario: Ana Torres
Tipo: Escritura de Propiedad
Propiedad: Casa Surco

[Vista previa del documento]

Verificación:
☑️ Documento legible
☑️ Datos coinciden con usuario
☑️ Propiedad coincide con registro
☑️ Documento vigente

Decisión:
(•) Aprobar
( ) Rechazar

Notas:
[Documento válido, todo en orden]

[Guardar Decisión]
```

---

## 🚨 Gestión de Reportes

### Reportes Pendientes:

```
REPORTES Y ALERTAS (3)

⚠️ ALTA PRIORIDAD
Reporte #453
Tipo: Propiedad sospechosa
Propiedad: Casa La Molina
Reportado por: Usuario #1240
Motivo: "El corredor no proporciona datos del propietario"
Fecha: Hoy, 9:00 AM
[Investigar]

⚠️ MEDIA PRIORIDAD
Reporte #452
Tipo: Usuario sospechoso
Usuario: Pedro Silva (Corredor)
Motivo: Múltiples propiedades sin documentación
Fecha: Ayer, 3:00 PM
[Investigar]
```

### Investigar Reporte:

```
INVESTIGACIÓN - Reporte #453

DETALLES DEL REPORTE
- Tipo: Propiedad sospechosa
- Propiedad: Casa La Molina (#453)
- Reportado por: María Gómez (#1240)
- Fecha: 25/01/2024 9:00 AM
- Motivo: "El corredor no proporciona datos del propietario"

INFORMACIÓN DE LA PROPIEDAD
- Corredor: Pedro Silva (#1241)
- Propietario registrado: ⚠️ "Propietario Anónimo"
- Documentos: ❌ Sin autorización
- Fecha publicación: hace 3 días

HISTORIAL DEL CORREDOR
- Propiedades registradas: 5
- Propiedades sin propietario: 4 (80%)
- Reportes previos: 2

EVIDENCIA
- No hay autorización firmada
- Propietario no identificado
- Corredor evade preguntas sobre propietario

DECISIÓN
(•) Suspender propiedad
(•) Suspender corredor
( ) Solicitar información adicional
( ) Desestimar reporte

Motivo de la sanción:
[Violación grave: Ocultar información del propietario]

Duración suspensión:
(•) 30 días
( ) Permanente

Notificar a:
☑️ Corredor
☑️ Usuario reportante
☑️ Interesados en la propiedad

[Aplicar Sanción]
```

---

## 📊 Estadísticas y Reportes

### Dashboard Estadístico:

```
ESTADÍSTICAS GENERALES

CRECIMIENTO
- Usuarios nuevos (mes): 145 (+12%)
- Propiedades nuevas (mes): 89 (+8%)
- Transacciones (mes): 23 (+15%)

POR DISTRITO (Top 5)
1. San Isidro: 89 propiedades
2. Miraflores: 76 propiedades
3. Surco: 65 propiedades
4. La Molina: 54 propiedades
5. San Borja: 43 propiedades

TIPOS DE PROPIEDAD
- Departamentos: 245 (54%)
- Casas: 156 (34%)
- Oficinas: 32 (7%)
- Locales: 23 (5%)

CORREDORES MÁS ACTIVOS
1. Carlos Ruiz: 12 operaciones
2. Ana Torres: 9 operaciones
3. Luis Gómez: 7 operaciones

TASA DE CONVERSIÓN
- Lead → Contacto: 45%
- Contacto → Propuesta: 35%
- Propuesta → Negociación: 60%
- Negociación → Cierre: 50%

[Exportar Reporte] [Ver Gráficos]
```

---

## ⚙️ Configuración del Sistema

### Parámetros:

```
CONFIGURACIÓN

LÍMITES Y RESTRICCIONES
- Propiedades por Demandante: [1]
- Propiedades por Propietario: [Ilimitado]
- Propiedades por Corredor: [Ilimitado]
- Vistas gratis (Invitado): [3]
- Días para validar documento: [5]

COMISIONES
- Comisión mínima corredor: [3]%
- Comisión máxima corredor: [10]%
- Comisión plataforma: [2]%

VALIDACIONES
☑️ Requiere documento para propietarios
☑️ Requiere licencia para corredores
☑️ Validación manual de documentos
☑️ Verificación de email obligatoria

NOTIFICACIONES
☑️ Email a admin por nuevo usuario
☑️ Email a admin por nuevo reporte
☑️ Alerta de licencia por vencer (30 días)

[Guardar Cambios]
```

---

## 🔄 Acciones Masivas

```
ACCIONES MASIVAS

Seleccionar usuarios: [5 seleccionados]

Acciones disponibles:
- Cambiar perfil
- Suspender
- Reactivar
- Enviar email
- Exportar datos

[Ejecutar Acción]
```

---

## 📧 Comunicaciones

### Enviar Email Masivo:

```
ENVIAR EMAIL

Para: [Todos los Corredores ▼]

Asunto:
[Recordatorio: Renovación de Licencias]

Mensaje:
Estimados corredores,

Les recordamos que deben mantener su licencia 
vigente para operar en la plataforma.

Corredores con licencia por vencer:
- Carlos Ruiz: Vence en 11 meses
- Luis Gómez: Vence en 2 meses ⚠️

[Enviar] [Programar] [Guardar Borrador]
```

---

## 💳 Tab 4: Suscripciones

**Ver flujo completo:** [08_suscripciones_planes.md](./08_suscripciones_planes.md)

### Panel de Suscripciones Pendientes

```
┌─────────────────────────────────────────────────────────┐
│ 💳 GESTIÓN DE SUSCRIPCIONES                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Filtros: [Pendientes ▼] [Todos los planes ▼] [Buscar] │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ID │ Usuario │ Plan │ Monto │ Estado │ Fecha │ Acc. ││
│ ├────┼─────────┼──────┼───────┼────────┼───────┼──────┤│
│ │ 15 │ Juan P. │Premium│S/ 49 │Pendiente│14/01 │[Ver] ││
│ │ 14 │ María L.│Profes.│S/ 99 │Activa  │12/01 │[Ver] ││
│ │ 13 │ Carlos R│Premium│S/ 49 │Rechazada│10/01│[Ver] ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ KPIs:                                                   │
│ • Pendientes de aprobación: 3                          │
│ • Activas este mes: 12                                 │
│ • Rechazadas este mes: 2                               │
│ • Revenue mensual: S/ 1,245                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Aprobar/Rechazar Suscripción

```
┌─────────────────────────────────────────────────────────┐
│ 💳 SUSCRIPCIÓN #15 - PENDIENTE                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Usuario: Juan Pérez (juan.perez@email.com)            │
│ Plan solicitado: PREMIUM (S/ 49/mes)                   │
│ Fecha solicitud: 14/01/2025 10:30 AM                   │
│                                                         │
│ Comprobante de pago:                                   │
│ ┌─────────────────────────────────────────────────┐   │
│ │ [Imagen del comprobante]                         │   │
│ │                                                  │   │
│ │ Número operación: 123456789                     │   │
│ │ Banco: BCP                                       │   │
│ │ Monto: S/ 49.00                                  │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ Notas del admin:                                       │
│ [_________________________________________________]    │
│                                                         │
│ [✅ Aprobar]  [❌ Rechazar]  [Volver]                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Tab 5: Mantenimiento

### Layout: Menú Lateral + Formulario Central + Lista

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO DEL SISTEMA                                    │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  GESTIÓN DE TIPOS DE INMUEBLE                   │
│              │                                                  │
│ • Planes     │  ┌────────────────────────────────────────────┐ │
│ • Distritos  │  │ Nombre: [Departamento            ]         │ │
│ • Tipos      │  │ Descripción: [Vivienda en edificio...]    │ │
│ • Caract.    │  │ Icono: [🏢]                                │ │
│ • Estados    │  │ Activo: [✓]                                │ │
│              │  │                                            │ │
│              │  │ [Guardar] [Cancelar]                       │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
│              │  LISTA DE TIPOS DE INMUEBLE                     │
│              │  ┌────────────────────────────────────────────┐ │
│              │  │ ID │ Nombre      │ Icono │ Estado │ Acc.  │ │
│              │  ├────┼─────────────┼───────┼────────┼───────┤ │
│              │  │ 1  │ Departamento│ 🏢    │ Activo │[Editar]│ │
│              │  │ 2  │ Casa        │ 🏠    │ Activo │[Editar]│ │
│              │  │ 3  │ Oficina     │ 🏢    │ Activo │[Editar]│ │
│              │  │ 4  │ Local Com.  │ 🏪    │ Activo │[Editar]│ │
│              │  │ 5  │ Terreno     │ 🌳    │ Activo │[Editar]│ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

### Sección: Planes de Suscripción

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO > PLANES DE SUSCRIPCIÓN                        │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  EDITAR PLAN: PREMIUM                           │
│              │                                                  │
│ • Planes ◄   │  ┌────────────────────────────────────────────┐ │
│ • Distritos  │  │ Nombre: [Premium                 ]         │ │
│ • Tipos      │  │ Precio: [S/ 49.00]                         │ │
│ • Caract.    │  │ Duración: [30] días                        │ │
│ • Estados    │  │                                            │ │
│              │  │ Límites:                                   │ │
│              │  │ • Búsquedas: [Ilimitado ▼]                 │ │
│              │  │ • Registros: [5]                           │ │
│              │  │                                            │ │
│              │  │ Características:                           │ │
│              │  │ [✓] Alertas de búsqueda                    │ │
│              │  │ [✓] Soporte prioritario                    │ │
│              │  │ [✓] Estadísticas avanzadas                 │ │
│              │  │ [ ] Asignación de corredor                 │ │
│              │  │                                            │ │
│              │  │ Activo: [✓]                                │ │
│              │  │                                            │ │
│              │  │ [Guardar] [Cancelar]                       │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
│              │  LISTA DE PLANES                                │
│              │  ┌────────────────────────────────────────────┐ │
│              │  │ ID │ Nombre  │ Precio │ Búsq. │ Reg. │Acc.│ │
│              │  ├────┼─────────┼────────┼───────┼──────┼────┤ │
│              │  │ 1  │ Básico  │ Gratis │ 10    │ 1    │[Ed]│ │
│              │  │ 2  │ Premium │ S/ 49  │ ∞     │ 5    │[Ed]│ │
│              │  │ 3  │ Profes. │ S/ 99  │ ∞     │ ∞    │[Ed]│ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

### Sección: Distritos

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO > DISTRITOS                                    │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  AGREGAR NUEVO DISTRITO                         │
│              │                                                  │
│ • Planes     │  ┌────────────────────────────────────────────┐ │
│ • Distritos◄ │  │ Nombre: [San Miguel              ]         │ │
│ • Tipos      │  │ Zona: [Lima Centro ▼]                      │ │
│ • Caract.    │  │ Activo: [✓]                                │ │
│ • Estados    │  │                                            │ │
│              │  │ [Guardar] [Cancelar]                       │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
│              │  LISTA DE DISTRITOS (43)                        │
│              │  ┌────────────────────────────────────────────┐ │
│              │  │ ID │ Nombre      │ Zona        │ Estado │A│ │
│              │  ├────┼─────────────┼─────────────┼────────┼─┤ │
│              │  │ 1  │ San Isidro  │ Lima Centro │ Activo │E│ │
│              │  │ 2  │ Miraflores  │ Lima Centro │ Activo │E│ │
│              │  │ 3  │ Surco       │ Lima Moderna│ Activo │E│ │
│              │  │ 4  │ La Molina   │ Lima Este   │ Activo │E│ │
│              │  │ 5  │ San Borja   │ Lima Centro │ Activo │E│ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

### Sección: Características

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO > CARACTERÍSTICAS                              │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  AGREGAR CARACTERÍSTICA                         │
│              │                                                  │
│ • Planes     │  ┌────────────────────────────────────────────┐ │
│ • Distritos  │  │ Nombre: [Gimnasio                ]         │ │
│ • Tipos      │  │ Tipo dato: [Checkbox ▼]                    │ │
│ • Caract. ◄  │  │ Categoría: [Amenidades ▼]                  │ │
│ • Estados    │  │ Icono: [🏋️]                                 │ │
│              │  │                                            │ │
│              │  │ Aplica a tipos de inmueble:                │ │
│              │  │ [✓] Departamento                           │ │
│              │  │ [✓] Casa                                   │ │
│              │  │ [ ] Oficina                                │ │
│              │  │ [ ] Local Comercial                        │ │
│              │  │                                            │ │
│              │  │ Requerido: [ ]                             │ │
│              │  │ Activo: [✓]                                │ │
│              │  │                                            │ │
│              │  │ [Guardar] [Cancelar]                       │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
│              │  LISTA DE CARACTERÍSTICAS (51)                  │
│              │  ┌────────────────────────────────────────────┐ │
│              │  │ ID │ Nombre    │ Tipo    │ Categoría │ Acc│ │
│              │  ├────┼───────────┼─────────┼───────────┼────┤ │
│              │  │ 1  │ Amoblado  │ Checkbox│ General   │[Ed]│ │
│              │  │ 2  │ Piscina   │ Checkbox│ Amenidades│[Ed]│ │
│              │  │ 3  │ Gimnasio  │ Checkbox│ Amenidades│[Ed]│ │
│              │  │ 4  │ Seguridad │ Checkbox│ Seguridad │[Ed]│ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

### Sección: Estados CRM

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚙️ MANTENIMIENTO > ESTADOS CRM                                  │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ 📋 MAESTRAS  │  EDITAR ESTADO: NEGOCIACIÓN                     │
│              │                                                  │
│ • Planes     │  ┌────────────────────────────────────────────┐ │
│ • Distritos  │  │ Nombre: [Negociación             ]         │ │
│ • Tipos      │  │ Descripción: [Cliente negociando precio]   │ │
│ • Caract.    │  │ Color: [#FFA500] 🟠                        │ │
│ • Estados ◄  │  │ Icono: [💬]                                │ │
│              │  │ Orden: [4]                                 │ │
│              │  │ Activo: [✓]                                │ │
│              │  │                                            │ │
│              │  │ [Guardar] [Cancelar]                       │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
│              │  LISTA DE ESTADOS CRM (7)                       │
│              │  ┌────────────────────────────────────────────┐ │
│              │  │ Ord│ Nombre      │ Color │ Icono │ Estado │ │
│              │  ├────┼─────────────┼───────┼───────┼────────┤ │
│              │  │ 1  │ Lead        │ 🔵    │ 📋    │ Activo │ │
│              │  │ 2  │ Contacto    │ 🟢    │ 📞    │ Activo │ │
│              │  │ 3  │ Propuesta   │ 🟡    │ 📄    │ Activo │ │
│              │  │ 4  │ Negociación │ 🟠    │ 💬    │ Activo │ │
│              │  │ 5  │ Pre-cierre  │ 🟣    │ 🤝    │ Activo │ │
│              │  │ 6  │ Cerrado ✅  │ 🟢    │ ✅    │ Activo │ │
│              │  │ 7  │ Cerrado ❌  │ 🔴    │ ❌    │ Activo │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## 📄 Tab 6: Reportes

(Contenido existente del documento)

---

## 📊 Queries para Mantenimiento

### Planes
```sql
-- Listar planes
SELECT * FROM planes_mae ORDER BY precio ASC;

-- Crear plan
INSERT INTO planes_mae (nombre, descripcion, precio, duracion_dias, limite_busquedas, limite_registros, activo)
VALUES ('Premium', 'Plan con búsquedas ilimitadas', 49.00, 30, -1, 5, true);

-- Actualizar plan
UPDATE planes_mae SET precio = 45.00 WHERE plan_id = 2;
```

### Distritos
```sql
-- Listar distritos
SELECT * FROM distritos_mae ORDER BY nombre ASC;

-- Crear distrito
INSERT INTO distritos_mae (nombre, zona, activo)
VALUES ('San Miguel', 'Lima Centro', true);
```

### Tipos de Inmueble
```sql
-- Listar tipos
SELECT * FROM tipo_inmueble_mae ORDER BY nombre ASC;

-- Crear tipo
INSERT INTO tipo_inmueble_mae (nombre, descripcion, icono, activo)
VALUES ('Departamento', 'Vivienda en edificio', '🏢', true);
```

### Características
```sql
-- Listar características
SELECT * FROM caracteristicas_mae ORDER BY categoria, nombre ASC;

-- Crear característica
INSERT INTO caracteristicas_mae (nombre, tipo_dato, categoria, icono, requerido, activo)
VALUES ('Gimnasio', 'checkbox', 'Amenidades', '🏋️', false, true);

-- Asignar a tipo de inmueble
INSERT INTO caracteristicas_x_inmueble_mae (tipo_inmueble_id, caracteristica_id)
VALUES (1, 15);  -- Gimnasio para Departamento
```

### Estados CRM
```sql
-- Listar estados
SELECT * FROM estados_crm_mae ORDER BY orden ASC;

-- Crear estado
INSERT INTO estados_crm_mae (nombre, descripcion, color, icono, orden, activo)
VALUES ('Negociación', 'Cliente negociando precio', '#FFA500', '💬', 4, true);
```

---

## ✅ Validación con Tablas

**Tab 5: Mantenimiento**
- ✅ `planes_mae` - CRUD completo
- ✅ `distritos_mae` - CRUD completo
- ✅ `tipo_inmueble_mae` - CRUD completo
- ✅ `caracteristicas_mae` - CRUD completo
- ✅ `caracteristicas_x_inmueble_mae` - Relaciones
- ✅ `estados_crm_mae` - CRUD completo

**Tab 4: Suscripciones**
- ✅ `suscripciones` - Aprobar/Rechazar
- ✅ `planes_mae` - Planes disponibles
- ✅ `usuarios` - Usuarios

**Estado:** ✅ TODAS LAS TABLAS EXISTEN
