# 🏢 PROYECTO QUADRANTE - SISTEMA INMOBILIARIO
## DOCUMENTO MAESTRO - Enero 2026

**Última actualización**: 16 de Enero 2026
**Versión**: 2.0.0
**Desarrollador**: Alan Cairampoma + Claude Sonnet 4.5

---

## 📂 REPOSITORIOS

### Backend - API REST
- **GitHub**: https://github.com/qadrantesystem/appbackimmobiliaria
- **Ruta local**: `C:\Users\acairamp\Documents\proyecto\appimmobilarioback\backend`
- **Producción**: https://appbackimmobiliaria-production.up.railway.app
- **Stack**: Python 3.11 + FastAPI + PostgreSQL + Railway
- **Último commit**: `8c89a1a` - "feat: Implementar búsqueda inteligente con combinaciones..."
- **Branch**: `main`

### Frontend - Web Application
- **GitHub**: https://github.com/qadrantesystem/appfrontinmobiliario
- **Ruta local**: `C:\Users\acairamp\Documents\proyecto\appimmobiliariaFront`
- **Servidor local**: http://localhost:3000
- **Stack**: Node.js + Express + Vanilla JavaScript + Leaflet Maps
- **Último commit**: `4c62739` - "feat: Implementar visualización de combinaciones inteligentes en frontend"
- **Branch**: `master`

---

## 🗄️ BASE DE DATOS

### PostgreSQL en Railway
- **Host**: autorack.proxy.rlwy.net
- **Puerto**: 2795
- **Database**: railway
- **Usuario**: postgres
- **Password**: EfbbYvQzfilaWTSzhfHbtXRLswmyoMvC
- **URL Completa**:
  ```
  postgresql://postgres:EfbbYvQzfilaWTSzhfHbtXRLswmyoMvC@autorack.proxy.rlwy.net:2795/railway
  ```

### Conexión desde Railway CLI
```bash
# Si el puerto 2795 está bloqueado por firewall, usa:
railway run bash
# O para queries directas:
railway run psql
```

### Tablas Principales
- `registro_x_inmueble_cab` - Propiedades (cabecera)
- `registro_x_inmueble_det` - Características (detalle - modelo EAV)
- `tipo_inmueble_mae` - Tipos de inmueble
- `distritos_mae` - Distritos
- `usuarios` - Usuarios del sistema
- `perfiles_mae` - Perfiles (4 tipos)

---

## 🚀 COMANDOS PARA LEVANTAR PROYECTOS

### Backend (Railway - Ya desplegado)
```bash
# El backend YA está en producción, no necesitas levantarlo localmente
# URL: https://appbackimmobiliaria-production.up.railway.app

# Para desarrollo local (opcional):
cd C:\Users\acairamp\Documents\proyecto\appimmobilarioback\backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Documentación API:
# http://localhost:8000/docs
```

### Frontend (Local - Puerto 3000)
```bash
cd C:\Users\acairamp\Documents\proyecto\appimmobiliariaFront
npm install
node server.js

# Acceder:
# http://localhost:3000
```

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS (ÚLTIMAS)

### ✅ Búsqueda Inteligente con Combinaciones (Backend) - 15/01/2026
**Archivos Backend**:
- `backend/app/services/busqueda_inteligente.py` - Lógica de combinaciones
- `backend/app/api/v1/propiedades.py` - Búsqueda pública
- `backend/app/api/v1/propiedades_busqueda_avanzada.py` - Búsqueda autenticada

**Características**:
- Combina oficinas contiguas cuando no hay una sola que cumpla el metraje
- Criterios: mismo edificio, piso, propietario, estado, transacción
- Parámetro: `incluir_combinaciones=true` (default)
- Retorna: individuales + combinaciones en un solo array

### ✅ Visualización de Combinaciones (Frontend) - 16/01/2026
**Archivos Frontend**:
- `frontend/js/pages/resultados.js` - Búsqueda pública
- `frontend/css/pages/resultados.css` - Estilos búsqueda pública
- `frontend/js/pages/dashboard/search/search-results.js` - Dashboard
- `frontend/css/pages/dashboard-search.css` - Estilos dashboard

**Características visuales**:
- Tarjetas verdes con borde grueso (#4CAF50)
- Badge animado "🔗 COMBINACIÓN DE X OFICINAS"
- Lista de oficinas incluidas
- Área total y precio total destacados
- Glosa descriptiva del backend

### ✅ Compartir por Email con PDFs (Backend) - 15/01/2026
**Archivo**:
- `backend/app/api/v1/emails.py` - Endpoint mejorado
- `backend/app/services/email_service.py` - Generación de PDFs

**Características**:
- Requiere autenticación (todos los perfiles)
- Límite: 10 propiedades por correo
- PDFs adjuntos en base64
- HTML responsive con thumbnails

### ✅ Compartir por WhatsApp (Backend - Preparado) - 15/01/2026
**Archivos**:
- `backend/app/api/v1/compartir.py` - Endpoint
- `backend/app/services/whatsapp_service.py` - Servicio

**Estado**: Código listo, pendiente configurar API de WhatsApp (Twilio/Meta)

### ✅ Mantenimientos Admin (Backend) - 15/01/2026
**Archivos**:
- `backend/app/api/v1/admin/tipos_inmueble.py` - CRUD Tipos
- `backend/app/api/v1/admin/distritos.py` - CRUD Distritos
- `backend/app/api/v1/admin/estados_crm.py` - CRUD Estados CRM
- `backend/app/api/v1/admin/carac_x_inmueble.py` - CRUD Relaciones

**Características**:
- Solo accesible para perfil_id = 4 (Administrador)
- CRUD completo (listar, crear, editar, eliminar)
- Paginación y búsqueda
- Validaciones de unicidad

---

## 🔧 CONFIGURACIÓN DE ENTORNO

### Backend - Variables de Entorno (.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:EfbbYvQzfilaWTSzhfHbtXRLswmyoMvC@autorack.proxy.rlwy.net:2795/railway

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@quadrante.com
FROM_NAME=Quadrante

# WhatsApp (opcional - pendiente configurar)
WHATSAPP_API_URL=https://api.twilio.com/...
WHATSAPP_API_TOKEN=your-token
WHATSAPP_FROM_NUMBER=+51999999999

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.com
```

### Frontend - Configuración API (js/config/api.js)
```javascript
const API_BASE_URL = 'https://appbackimmobiliaria-production.up.railway.app';
const API_URL = `${API_BASE_URL}/api/v1`;

const API_CONFIG = {
  BASE_URL: API_URL,
  TIMEOUT: 30000,
  HEADERS: {
    'Content-Type': 'application/json',
  }
};
```

---

## 📋 ENDPOINTS PRINCIPALES

### Autenticación
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/register` - Registro

### Búsqueda Pública (Sin autenticación)
- `GET /api/v1/propiedades` - Búsqueda con combinaciones
  - Params: `tipo_inmueble_id`, `distrito_id`, `area_min`, `area_max`, `incluir_combinaciones`

### Búsqueda Autenticada (Con token)
- `POST /api/v1/propiedades/buscar-avanzada` - Búsqueda avanzada con combinaciones

### Compartir (Requiere autenticación)
- `POST /api/v1/emails/enviar-fichas` - Enviar por email con PDFs
- `POST /api/v1/propiedades/compartir/whatsapp` - Enviar por WhatsApp (preparado)

### Admin (Solo perfil_id = 4)
- `GET /api/v1/admin/tipos-inmueble` - CRUD Tipos de inmueble
- `GET /api/v1/admin/distritos` - CRUD Distritos
- `GET /api/v1/admin/estados-crm` - CRUD Estados CRM
- `GET /api/v1/admin/carac-x-inmueble` - CRUD Relaciones características

---

## 👥 SISTEMA DE PERFILES

1. **Perfil 1 - Demandante**
   - Busca propiedades
   - Guarda favoritos
   - Recibe notificaciones

2. **Perfil 2 - Ofertante**
   - Publica propiedades
   - Gestiona sus propiedades
   - Suscripción premium

3. **Perfil 3 - Corredor**
   - Gestiona todas las propiedades
   - Intermediario
   - CRM completo

4. **Perfil 4 - Administrador**
   - Acceso total
   - Mantenimientos (CRUDs)
   - Gestión de usuarios
   - Dashboard de configuración

---

## 🔍 QUERY DE VERIFICACIÓN DE DATA PARA COMBINACIONES

```sql
-- Ver oficinas combinables (mismo edificio + piso + propietario)
SELECT
    r.padre_registro_cab_id AS edificio_id,
    rd.valor AS piso,
    r.propietario_id,
    r.transaccion,
    COUNT(*) AS cantidad_oficinas,
    SUM(r.area) AS area_total,
    STRING_AGG(r.nombre_inmueble || ' (' || r.area || 'm²)', ' + ' ORDER BY r.registro_cab_id) AS oficinas_detalle
FROM registro_x_inmueble_cab r
LEFT JOIN registro_x_inmueble_det rd
    ON r.registro_cab_id = rd.registro_cab_id
    AND rd.caracteristica_id = 110  -- Piso
WHERE r.tipo_inmueble_id = 1  -- Oficinas
  AND r.padre_registro_cab_id IS NOT NULL  -- Con edificio padre
  AND r.estado = 'publicado'
  AND rd.valor IS NOT NULL  -- Tiene piso asignado
GROUP BY r.padre_registro_cab_id, rd.valor, r.propietario_id, r.transaccion
HAVING COUNT(*) >= 2  -- Al menos 2 oficinas
ORDER BY edificio_id, piso;
```

**Propósito**: Verifica si hay oficinas en la BD que cumplan criterios para ser combinadas.

---

## 📝 ÚLTIMOS COMMITS

### Backend (main)
```
Commit: 8c89a1ad8ff0af40939bf1063a0153b34b6faf04
Fecha: 15/01/2026
Mensaje: feat: Implementar búsqueda inteligente con combinaciones de propiedades

Archivos modificados: 12 archivos
Líneas cambiadas: +2,089 / -47
```

### Frontend (master)
```
Commit: 4c6273987e8c9f7a5d3b2a1e8f6c9d4e7a2b5c8f
Fecha: 16/01/2026
Mensaje: feat: Implementar visualización de combinaciones inteligentes en frontend

Archivos modificados: 5 archivos
Líneas cambiadas: +1,141 / -57
```

---

## 🧪 TESTING PENDIENTE

### Búsqueda con Combinaciones
- [ ] Ejecutar query de verificación de data
- [ ] Abrir http://localhost:3000/busqueda
- [ ] Seleccionar "Oficinas" como tipo
- [ ] Ingresar área mínima: 600 m²
- [ ] Click en "Hacer MATCH"
- [ ] Verificar en resultados.html:
  - [ ] Tarjetas normales con borde gris
  - [ ] Tarjetas de combinación con borde VERDE
  - [ ] Badge "🔗 COMBINACIÓN DE X OFICINAS"
  - [ ] Lista de oficinas incluidas
  - [ ] Área total destacada en verde
  - [ ] Glosa descriptiva
- [ ] Hacer login (cualquier perfil)
- [ ] Ir a Dashboard → Búsquedas
- [ ] Repetir búsqueda
- [ ] Verificar mismos resultados

### Compartir
- [ ] Probar envío por email (desde dashboard)
- [ ] Configurar WhatsApp API y probar

### Mantenimientos Admin
- [ ] Login con perfil_id = 4
- [ ] Probar CRUD de Tipos de Inmueble
- [ ] Probar CRUD de Distritos
- [ ] Probar CRUD de Estados CRM
- [ ] Probar CRUD de Características x Tipo

---

## 🚧 PRÓXIMOS PASOS

### Corto Plazo (Enero 2026)
- [ ] Testing de búsqueda con combinaciones (requiere data)
- [ ] Configurar API de WhatsApp (Twilio/Meta)
- [ ] Poblar base de datos con más propiedades de prueba
- [ ] Botón "Compartir" en resultados públicos
- [ ] Botón "Comparar" propiedades

### Mediano Plazo (Febrero-Marzo 2026)
- [ ] Notificaciones push
- [ ] Chat interno
- [ ] Calendario de citas/visitas
- [ ] Tour virtual (360°)
- [ ] Dashboard de analytics para admin
- [ ] Reportes de gestión

### Largo Plazo (Q2 2026)
- [ ] PWA (Progressive Web App)
- [ ] Modo offline
- [ ] App móvil híbrida (Flutter/React Native)
- [ ] Integración con pasarelas de pago
- [ ] Firma digital de contratos
- [ ] IA para valoración de propiedades

---

## 🐛 ISSUES CONOCIDOS

### Backend
- WhatsApp Service requiere configurar API key de Twilio/Meta
- Validación de eliminación pendiente en algunos DELETE (validar que no esté en uso)
- Puerto 2795 bloqueado por firewall en algunas redes (usar Railway CLI)

### Frontend
- Carruseles de imágenes: En algunas tarjetas el carrusel no sincroniza bien los indicadores
- Mapa móvil: Performance baja con +50 marcadores
- Filtros avanzados: Algunos campos dinámicos no cargan en tipos específicos

---

## 📚 DOCUMENTACIÓN ADICIONAL

### En Backend
- `backend/STATUS_ENERO_2026.md` - Estado completo del backend
- `backend/README.md` - Instrucciones generales

### En Frontend
- `frontend/STATUS_ENERO_2026.md` - Estado completo del frontend
- `frontend/SISTEMA_CONFIGURACION_OFICINAS.md` - Configuración de edificios/oficinas
- `frontend/MODAL_CONFIGURAR_PISOS.md` - Modal de configuración de pisos

---

## 🔐 CREDENCIALES DE PRUEBA

### Usuario Administrador
```
Email: admin@quadrante.com
Password: (consultar con Alan)
Perfil: Administrador (perfil_id = 4)
```

### Usuario Demandante
```
Email: demandante@quadrante.com
Password: (consultar con Alan)
Perfil: Demandante (perfil_id = 1)
```

### Usuario Ofertante
```
Email: ofertante@quadrante.com
Password: (consultar con Alan)
Perfil: Ofertante (perfil_id = 2)
```

### Usuario Corredor
```
Email: corredor@quadrante.com
Password: (consultar con Alan)
Perfil: Corredor (perfil_id = 3)
```

---

## 📞 SOPORTE Y CONTACTO

- **Email**: alancairampoma@gmail.com
- **GitHub Backend**: https://github.com/qadrantesystem/appbackimmobiliaria/issues
- **GitHub Frontend**: https://github.com/qadrantesystem/appfrontinmobiliario/issues

---

## 💻 COMANDOS GIT ÚTILES

### Backend
```bash
cd C:\Users\acairamp\Documents\proyecto\appimmobilarioback\backend

# Ver estado
git status

# Ver commits recientes
git log --oneline -10

# Pull últimos cambios
git pull origin main

# Crear commit
git add .
git commit -m "feat: Descripción del cambio"
git push origin main
```

### Frontend
```bash
cd C:\Users\acairamp\Documents\proyecto\appimmobiliariaFront

# Ver estado
git status

# Ver commits recientes
git log --oneline -10

# Pull últimos cambios
git pull origin master

# Crear commit
git add .
git commit -m "feat: Descripción del cambio"
git push origin master
```

---

## 🎨 COLORES DEL SISTEMA

```css
/* Variables principales */
--azul-principal: #2C5282;
--azul-hover: #1e3a5f;
--verde-combinacion: #4CAF50;  /* NUEVO - Combinaciones */
--gris-claro: #f5f7fa;
--gris-medio: #6B7280;
--rojo-error: #EF4444;
--verde-exito: #10B981;
--amarillo-warning: #F59E0B;
```

---

## 📊 ESTRUCTURA DE RESPUESTA API (Combinaciones)

```json
{
  "success": true,
  "data": [
    {
      "tipo": "individual",
      "registro_cab_id": 5,
      "titulo": "Oficina moderna en San Isidro",
      "area": 650,
      "precio_venta": 520000,
      "distrito": "San Isidro"
    },
    {
      "tipo": "combinacion",
      "cantidad_oficinas": 2,
      "area_total": 600,
      "precio_venta_total": 480000,
      "glosa": "Combinación de 2 oficinas: Oficina 301 + Oficina 302",
      "edificio_id": 12,
      "piso": 3,
      "distrito": "San Isidro",
      "oficinas": [
        {
          "registro_cab_id": 25,
          "nombre": "Oficina 301",
          "area": 300,
          "precio_venta": 240000
        },
        {
          "registro_cab_id": 26,
          "nombre": "Oficina 302",
          "area": 300,
          "precio_venta": 240000
        }
      ]
    }
  ],
  "metadata": {
    "individuales": 10,
    "combinaciones": 5
  }
}
```

---

**Última actualización**: 16 de Enero 2026, 11:30 AM
**Próxima revisión**: Febrero 2026

---

## 🎯 PARA RETOMAR DESDE OTRO EQUIPO

1. **Clonar Repositorios**:
   ```bash
   # Backend
   git clone https://github.com/qadrantesystem/appbackimmobiliaria.git
   cd appbackimmobiliaria/backend
   pip install -r requirements.txt

   # Frontend
   git clone https://github.com/qadrantesystem/appfrontinmobiliario.git
   cd appfrontinmobiliario
   npm install
   ```

2. **Configurar Variables de Entorno**:
   - Backend: Crear `.env` con las credenciales de este documento
   - Frontend: Verificar `js/config/api.js` apunte a Railway

3. **Levantar Frontend**:
   ```bash
   cd appfrontinmobiliario
   node server.js
   # Abrir http://localhost:3000
   ```

4. **Verificar Backend**:
   ```bash
   # Backend ya está desplegado en Railway
   # Verificar: https://appbackimmobiliaria-production.up.railway.app/docs
   ```

5. **Testing de Combinaciones**:
   - Ejecutar query de verificación (ver arriba)
   - Probar búsqueda pública con área_min=600
   - Probar búsqueda autenticada (hacer login primero)

---

**FIN DEL DOCUMENTO MAESTRO**
