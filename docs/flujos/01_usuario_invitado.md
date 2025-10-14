# 👤 FLUJO: USUARIO INVITADO

## 🎯 Objetivo
Permitir que usuarios no registrados exploren propiedades de manera limitada para incentivar el registro.

---

## 📊 Diagrama de Flujo

```
┌─────────────────┐
│  Usuario llega  │
│   a la app      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Pantalla de Bienvenida │
│  - Ver propiedades      │
│  - Búsqueda básica      │
└────────┬────────────────┘
         │
         ▼
    ┌────────┐
    │ Acción │
    └───┬────┘
        │
        ├─── Ver Propiedad ──────► Puede ver hasta 3 propiedades
        │                          └─► Luego pide registro
        │
        ├─── Buscar ───────────────► Búsqueda limitada (sin filtros avanzados)
        │
        ├─── Contactar ────────────► ❌ Requiere registro
        │
        ├─── Guardar Favorito ─────► ❌ Requiere registro
        │
        ├─── Guardar Búsqueda ─────► ❌ Requiere registro
        │
        └─── Registrarse ──────────► Va a flujo 02_registro_usuario.md
```

---

## 🔄 Diagrama de Secuencia

```mermaid
sequenceDiagram
    actor Invitado
    participant App
    participant Backend
    participant DB

    Invitado->>App: Abre la aplicación
    App->>Backend: GET /propiedades?destacadas=true
    Backend->>DB: SELECT * FROM propiedades WHERE destacado=true LIMIT 10
    DB-->>Backend: Propiedades destacadas
    Backend-->>App: Lista de propiedades
    App-->>Invitado: Muestra propiedades

    Invitado->>App: Busca "Deptos San Isidro"
    App->>Backend: GET /propiedades?distrito=3&tipo=1
    Backend->>DB: SELECT * FROM propiedades WHERE distrito_id=3
    DB-->>Backend: Resultados (sin datos contacto)
    Backend-->>App: Lista filtrada
    App-->>Invitado: Muestra resultados

    Invitado->>App: Click en propiedad #1
    App->>Backend: GET /propiedades/1
    Backend->>DB: SELECT * FROM propiedades WHERE propiedad_id=1
    DB-->>Backend: Detalles (limitados)
    Backend-->>App: Datos de propiedad
    App-->>Invitado: Muestra detalle (sin contacto)

    Note over Invitado,App: Contador: 1 de 3 vistas

    Invitado->>App: Click en propiedad #2
    App-->>Invitado: Muestra detalle
    Note over Invitado,App: Contador: 2 de 3 vistas

    Invitado->>App: Click en propiedad #3
    App-->>Invitado: Muestra detalle
    Note over Invitado,App: Contador: 3 de 3 vistas

    Invitado->>App: Intenta ver propiedad #4
    App-->>Invitado: Modal "Límite alcanzado - Regístrate"

    Invitado->>App: Click "Guardar Favorito"
    App-->>Invitado: Modal "Requiere registro"

    Invitado->>App: Click "Contactar"
    App-->>Invitado: Modal "Requiere registro"

    Invitado->>App: Click "Registrarse"
    App->>App: Redirige a registro
```

---

## ✅ Permisos del Usuario Invitado

### 🟢 Puede Hacer:
- ✅ Ver listado de propiedades (máximo 3 detalles completos)
- ✅ Búsqueda básica por distrito y tipo
- ✅ Ver precios y ubicación general
- ✅ Ver imágenes principales

### 🔴 NO Puede Hacer:
- ❌ Ver datos de contacto del propietario/corredor
- ❌ Enviar mensajes o consultas
- ❌ Guardar favoritos (lo invita a registrarse)
- ❌ Guardar búsquedas (lo invita a registrarse)
- ❌ Ver historial de búsquedas
- ❌ Acceder a filtros avanzados
- ❌ Ver todas las imágenes de la propiedad
- ❌ Registrar propiedades

---

## 🔔 Mensajes al Usuario Invitado

### Después de ver 3 propiedades:
```
🔒 ¡Regístrate para seguir explorando!

Has alcanzado el límite de visualización.
Crea tu cuenta GRATIS para:
  ✅ Ver propiedades ilimitadas
  ✅ Contactar directamente
  ✅ Guardar favoritos
  ✅ Recibir alertas personalizadas

[Registrarse Ahora] [Iniciar Sesión]
```

### Al intentar contactar:
```
🔒 Registro requerido

Para contactar al propietario necesitas una cuenta.
Es GRATIS y toma solo 2 minutos.

[Crear Cuenta] [Ya tengo cuenta]
```

### Al intentar guardar favorito:
```
🔒 Regístrate para guardar favoritos

Crea tu cuenta GRATIS para:
  ✅ Guardar propiedades favoritas
  ✅ Guardar tus búsquedas
  ✅ Recibir alertas personalizadas
  ✅ Contactar propietarios

[Registrarse Ahora] [Iniciar Sesión]
```

### Al intentar guardar búsqueda:
```
🔒 Guarda tus búsquedas

Regístrate para guardar esta búsqueda y
recibir notificaciones de nuevas propiedades.

[Crear Cuenta Gratis]
```

---

## 📱 Pantallas

### 1. Home - Usuario Invitado
- Banner: "Regístrate gratis y encuentra tu propiedad ideal"
- Listado de propiedades destacadas
- Barra de búsqueda básica
- Botón: "Registrarse" (destacado)

### 2. Detalle de Propiedad (Limitado)
- Imágenes: Solo la principal
- Precio: Visible
- Ubicación: Solo distrito (no dirección exacta)
- Características: Básicas (área, habitaciones, baños)
- Contacto: Botón "Registrarse para contactar"

---

## 🎯 Objetivo de Conversión
**Convertir al usuario invitado en usuario registrado** mostrando el valor de la plataforma pero limitando funcionalidades clave.

---

## 🔄 Siguiente Paso
➡️ [Flujo 02: Registro de Usuario](./02_registro_usuario.md)
