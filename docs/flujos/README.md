# 🚀 FLUJOS DE USUARIO - SISTEMA INMOBILIARIO

> **Misión**: Profesionalizar el mercado inmobiliario peruano eliminando las "criolladas" y estableciendo procesos transparentes y regulados.

---

## 📋 ÍNDICE DE FLUJOS (7 documentos)

### 👤 Flujos de Registro y Autenticación (3)

1. **[Usuario Invitado](./01_usuario_invitado.md)** ✅
   - Búsqueda limitada sin registro
   - Límite de 3 vistas
   - Prompts para registro
   - **Incluye:** Diagrama de secuencia

2. **[Registro de Usuario](./02_registro_usuario.md)** ✅
   - Proceso de registro
   - Validación de email
   - Asignación de perfil inicial

3. **[Asignación de Perfil por Admin](./03_asignacion_perfil.md)** ✅
   - Cambio de roles
   - Validación de corredores
   - Aprobaciones

---

### 🔍 Flujos por Tipo de Usuario (4)

4. **[Usuario Demandante/Buscador](./04_usuario_demandante.md)** ✅
   - Búsqueda avanzada
   - Favoritos
   - Búsquedas guardadas con alertas
   - Contacto con propietarios
   - **Incluye:** Diagrama de secuencia (búsqueda, favoritos, contacto)

5. **[Usuario Propietario](./05_usuario_propietario.md)** ✅
   - Registro de propiedades propias
   - Gestión de publicaciones
   - Estadísticas
   - **Incluye:** Diagrama de secuencia (registro multipaso)

6. **[Usuario Corredor](./06_usuario_corredor.md)** ✅
   - Registro de propiedades de clientes
   - Datos del propietario real OBLIGATORIOS
   - Pipeline CRM
   - Gestión de comisiones
   - **Incluye:** Diagrama de secuencia (registro para cliente)

7. **[Usuario Admin](./07_usuario_admin.md)** ✅
   - Supervisión general
   - Validación de propiedades
   - Gestión de usuarios
   - Reportes

---

## 🗑️ FLUJOS ELIMINADOS (5)

Los siguientes flujos fueron eliminados por estar duplicados:

- ❌ `08_registro_propiedad_propietario.md` → Ya está en `05_usuario_propietario.md`
- ❌ `09_registro_propiedad_corredor.md` → Ya está en `06_usuario_corredor.md`
- ❌ `10_validacion_propiedades.md` → Proceso interno, no flujo de usuario
- ❌ `11_pipeline_crm.md` → Ya integrado en `06_usuario_corredor.md`
- ❌ `12_interacciones_seguimiento.md` → Ya está en `04_usuario_demandante.md`

---

## 🎯 PRINCIPIOS FUNDAMENTALES

✅ **Transparencia Total** - Propietario real siempre identificado  
✅ **Regulación de Corredores** - No pueden registrar propiedades como propias  
✅ **Protección de Usuarios** - Términos y condiciones claros  
✅ **Monitoreo Admin** - Supervisión de todos los procesos  

---

## 📊 ESTRUCTURA DE BASE DE DATOS

Ver `backend/docs/ESTRUCTURA_BD.md` para detalles completos de:
- Tablas de cabecera y detalle
- Búsquedas guardadas con alertas
- Tracking de estados CRM
- Favoritos de usuarios
