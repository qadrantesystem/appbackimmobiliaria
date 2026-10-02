# 🏢 CONTEXTO DEL SISTEMA — CUADRANTE (Portal Inmobiliario)

> Documento de contexto y visión. Fuente: explicación directa de Alan Cairampoma.
> Complementa `PROYECTO_QUADRANTE_MASTER.md` y `docs/flujos/` del repo back.

---

## 1. Qué es

**Cuadrante** es un **portal inmobiliario con búsqueda gratuita** y un **orden comercial
regulado**. Nació para dar a los **corredores** (hoy atados a planillas Excel y a prácticas
informales) una **alternativa ordenada, transparente y profesional**: buscar, publicar y
gestionar propiedades en un solo lugar, con **comisiones reguladas por Cuadrante**.

## 2. Misión

Profesionalizar el mercado inmobiliario peruano, **eliminando las prácticas informales
("criolladas")** y estableciendo procesos transparentes, con comisiones alineadas y no
"a la viveza" de cada uno.

### Propuesta de valor (diferenciadores)

- **Más allá del Excel masivo:** reemplazar las planillas por una **plataforma centralizada**.
- **Formalizar y centralizar a TODOS los corredores** — incluidos los **independientes
  ("mercenarios")** — bajo un mismo orden, con **seguimiento**.
- **CRM moderno y dinámico** con seguimiento de leads/oportunidades (pipeline).
- **Claridad de búsqueda:** encontrar lo que se busca **mejor que Urbania.pe** y otros
  portales del Perú.
- **Primer sistema que dibuja el "esqueleto" del edificio, 100% navegable:**
  se visualiza y configura la **torre por pisos y oficinas** de forma interactiva
  (clic en cada oficina: +101, +102… con metraje, equipamiento y ocupación).
- **Comisiones reguladas** y corredor asignado por Cuadrante (transparencia de márgenes).

## 3. Modelo de captación (embudo)

1. **Usuario entra al portal gratuito** sin registrarse.
2. Tiene una **búsqueda gratuita** y ve el **resultado esperado** (el impacto de encontrar
   lo que busca), pero la data se muestra **hasta cierto nivel**.
3. Ese resultado parcial lo **invita a registrarse**.
4. Al registrarse, **forma parte del "orden por Cuadrante"**: perfiles, comisiones y
   procesos regulados.

## 4. Perfiles del sistema

| Perfil | Rol | Notas |
|---|---|---|
| **demandante** | Busca inmuebles (alquiler/compra) | Búsqueda avanzada, favoritos, búsquedas guardadas con alertas, contacto |
| **ofertante** (propietario) | Publica y gestiona sus inmuebles | Publica, ve asignación de corredor y márgenes |
| **corredor** | Agente inmobiliario (propiedades de terceros) | **Requiere aprobación** para registrarse; pipeline CRM y comisiones |
| **administrativo** (admin) | Control total | Ve **todas las búsquedas/valor** de demandantes y corredores; aprueba corredores; asigna corredores; reportes |

> La aprobación de corredores y la asignación de corredores son la palanca central del
> "orden por Cuadrante".

## 5. Qué puede hacer cada perfil

- **Invitado (sin registro):** búsqueda limitada (p. ej. 3 vistas) + prompts para registrarse.
- **Demandante:** búsqueda avanzada, **favoritos**, búsquedas guardadas con alertas, contacto.
- **Ofertante:** publicar sus inmuebles, ver cómo Cuadrante le **asigna un corredor** con
  **márgenes de ganancia alineados**.
- **Corredor:** registrar inmuebles de clientes (con **datos del propietario real
  obligatorios**), pipeline CRM, gestión de comisiones.
- **Admin:** supervisión general, validación de propiedades, gestión de usuarios, reportes,
  visibilidad de la **búsqueda/valor** de todos.

## 6. Motor de Búsqueda Inteligente (corazón del producto)

Servicio: **`BusquedaInteligenteService`** (`back/app/services/busqueda_inteligente.py`).

Devuelve **dos cosas**:
1. **Individuales** — propiedades publicadas que cumplen los filtros.
2. **Combinaciones** — varias oficinas que **suman el metraje buscado**.

### Idea de negocio (según Alan)
> Necesito **1000 m²** de oficinas. En el edificio **"El Sol"** hay **3 oficinas contiguas**
> que suman 1000 m². Si no, como **alternativa**, el metraje puede encontrarse entre
> **pisos consecutivos** (4, 5, 6), **una oficina por piso** que suma 1000 m² —
> **todo dentro del mismo edificio**, sin salir a buscar a otro.

### Reglas deseadas
- Las combinaciones deben quedarse **dentro del mismo edificio** (misma transacción).
- **Opción A — mismo piso (contiguas):** oficinas al lado que suman el metraje.
- **Opción B — pisos consecutivos:** combinación que abarque pisos contiguos
  (ej. 4-5-6), típicamente **1 oficina por piso**.
- Ordenar por **área total más cercana al objetivo**.

### Estado actual del código (⚠️ gap)
- Hoy agrupa por **`(edificio, piso, transacción)`** → **solo combina oficinas del MISMO PISO**.
  → **La Opción B (pisos consecutivos) NO está implementada.**
- Solo aplica a **oficinas** (`tipo_inmueble_id == 1`) y **solo si se envía `area_min`**.
- Máximo **4 oficinas** por combinación (evita explosión combinatoria).
- No hay **radio geográfico**; la "proximidad" hoy es **distrito + coordenadas** para el mapa.
- `_obtener_piso()` usa `caracteristica_id == 112` **hardcodeado**.

### Mejora propuesta
- Agrupar por **edificio** (no por piso) y permitir combos con **pisos consecutivos**
  (contigüidad de pisos), manteniendo misma transacción y mismo edificio.

## 7. Funcionalidades clave

- **Registro de inmuebles** (dos tipos): **oficina/individual** y **edificio completo**
  (con oficinas y sótanos, alta masiva).
- **Edificio rápido** (cabecera mínima desde el formulario de oficina).
- **Favoritos** — por cada perfil.
- **Ficha PDF + envío por correo/WhatsApp** — seleccionas inmuebles que te gustaron y el
  back genera **fichas PDF A4** (`generar_ficha_pdf`) y las **envía por correo**
  (`POST /api/v1/emails/enviar-fichas`), o genera **URLs** para compartir por **WhatsApp**
  (`POST /api/v1/emails/generar-fichas-urls`).
  - ⚠️ Hoy el botón "Enviar fichas" está en la pestaña **Búsquedas**; falta agregarlo en **Favoritos**.
- **Estadísticas de búsqueda** — qué buscó cada usuario (valor para admin/Cuadrante).
- **Portal oficial** — edificios, características y catálogos, **todo en un solo lugar**.
- **Comisiones reguladas** — márgenes alineados y corredor asignado por Cuadrante.

## 8. Arquitectura (resumen)

- **Back:** FastAPI + PostgreSQL (Railway). Repo `qadrantesystem/appbackimmobiliaria`.
- **Front:** Node/Express + Vanilla JS + Leaflet (mapas). Repo `qadrantesystem/appfrontinmobiliaria`.
- **Tablas clave:** `registro_x_inmueble_cab` (propiedades), `registro_x_inmueble_det`
  (características, modelo EAV), `tipo_inmueble_mae`, `distritos_mae`, `usuarios`, `perfiles_mae`.
- **Credenciales:** viven en variables de entorno / `.env` — **nunca** en documentación.

## 9. Pendientes / mejoras candidatas

- [ ] Implementar **combinaciones por pisos consecutivos** (mismo edificio).
- [ ] Evaluar **radio geográfico** (lat/lng + haversine) para búsqueda proximal real.
- [ ] Modelar **contigüidad física real** (posición de oficina en el plano), no solo "mismo piso".
- [ ] Sacar credenciales/secretos de los `.md` del repo.
- [ ] Poda por precio antes de generar combinaciones (rendimiento).
- [ ] Unificar naming "Cuadrante" vs "Qadrante"/"Quadrante" en docs.

---

*Generado el 2026-10-02 a partir del contexto entregado por Alan.*
