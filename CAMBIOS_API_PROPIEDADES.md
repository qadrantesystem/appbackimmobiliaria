# 📋 Actualización API - Nuevos Campos en Propiedades

**Fecha**: 18 de Octubre, 2025  
**Versión**: v1  
**Autor**: Backend Team

---

## 🎯 Resumen

Se han agregado **4 nuevos campos** al endpoint de listado de propiedades para mostrar información adicional en la tabla del frontend.

---

## 📍 Endpoints Afectados

### 1. `GET /api/v1/propiedades`
**Descripción**: Lista todas las propiedades públicas (con filtros)  
**Autenticación**: No requiere

### 2. `GET /api/v1/propiedades/mis-propiedades`
**Descripción**: Lista las propiedades del usuario autenticado  
**Autenticación**: Requerida (Bearer Token)

---

## ✨ Nuevos Campos Agregados

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `direccion` | `string` | Dirección completa de la propiedad | `"Av. Conquistadores 741"` |
| `telefono` | `string` | Teléfono del propietario | `"+51 900 999 888"` |
| `email` | `string` (opcional) | Email del propietario | `"patricia.vargas@email.com"` |
| `estado_crm` | `string` | Estado en el CRM de ventas | `"lead"`, `"contactado"`, `"visita_programada"`, `"negociacion"`, `"cerrado_ganado"`, `"cerrado_perdido"` |

---

## 📦 Estructura JSON Completa

### Request
```http
GET /api/v1/propiedades?page=1&limit=12
Authorization: Bearer <token> (opcional)
```

### Response
```json
{
  "success": true,
  "data": [
    {
      "registro_cab_id": 10,
      "titulo": "Penthouse de lujo en San Isidro",
      "tipo_inmueble": "Departamento",
      "distrito": "San Isidro",
      
      // ✅ NUEVOS CAMPOS
      "direccion": "Av. Conquistadores 741",
      "telefono": "+51 900 999 888",
      "email": "patricia.vargas@email.com",
      
      "transaccion": "venta",
      "precio_alquiler": null,
      "precio_venta": "850000.00",
      "moneda": "PEN",
      "area": "200.00",
      "habitaciones": 4,
      "banos": 4,
      "parqueos": 3,
      "imagen_principal": "https://...",
      "imagenes": ["https://...", "https://..."],
      "estado": "publicado",
      
      // ✅ NUEVO CAMPO
      "estado_crm": "cerrado_ganado",
      
      "vistas": 145,
      "contactos": 25,
      "created_at": "2024-01-24T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 50,
    "total_pages": 5
  }
}
```

---

## 🎨 Sugerencias de Implementación Frontend

### 1. **Tabla de Propiedades**

Agregar las siguientes columnas:

```jsx
// Ejemplo con React/TypeScript
const columns = [
  { field: 'registro_cab_id', header: 'ID' },
  { field: 'titulo', header: 'Título' },
  { field: 'tipo_inmueble', header: 'Tipo' },
  { field: 'distrito', header: 'Distrito' },
  
  // ✅ NUEVAS COLUMNAS
  { field: 'direccion', header: 'Dirección' },
  { field: 'telefono', header: 'Teléfono' },
  { field: 'email', header: 'Correo' },
  
  { field: 'transaccion', header: 'Transacción' },
  { field: 'precio_venta', header: 'Precio' },
  { field: 'area', header: 'Área m²' },
  { field: 'habitaciones', header: 'Hab.' },
  { field: 'banos', header: 'Baños' },
  { field: 'estado', header: 'Estado' },
  
  // ✅ NUEVA COLUMNA
  { field: 'estado_crm', header: 'Estado CRM' },
  
  { field: 'vistas', header: 'Vistas' },
  { field: 'contactos', header: 'Contactos' }
];
```

### 2. **Badges para Estado CRM**

Recomendamos usar badges de colores según el estado:

```jsx
const getEstadoCRMBadge = (estado_crm) => {
  const badges = {
    'lead': { color: 'gray', label: 'Lead' },
    'contactado': { color: 'blue', label: 'Contactado' },
    'visita_programada': { color: 'yellow', label: 'Visita Programada' },
    'negociacion': { color: 'orange', label: 'En Negociación' },
    'cerrado_ganado': { color: 'green', label: 'Cerrado - Ganado' },
    'cerrado_perdido': { color: 'red', label: 'Cerrado - Perdido' }
  };
  
  return badges[estado_crm] || { color: 'gray', label: estado_crm };
};
```

### 3. **TypeScript Interface**

```typescript
interface Propiedad {
  registro_cab_id: number;
  titulo: string;
  tipo_inmueble: string;
  distrito: string;
  
  // ✅ NUEVOS CAMPOS
  direccion: string;
  telefono: string;
  email?: string;
  
  transaccion: 'alquiler' | 'venta' | 'ambos';
  precio_alquiler?: number;
  precio_venta?: number;
  moneda: 'PEN' | 'USD';
  area: number;
  habitaciones?: number;
  banos?: number;
  parqueos?: number;
  imagen_principal?: string;
  imagenes?: string[];
  estado: 'borrador' | 'publicado' | 'pausado' | 'cerrado';
  
  // ✅ NUEVO CAMPO
  estado_crm: 'lead' | 'contactado' | 'visita_programada' | 'negociacion' | 'cerrado_ganado' | 'cerrado_perdido';
  
  vistas: number;
  contactos: number;
  created_at: string;
}
```

---

## 🔍 Valores Posibles de `estado_crm`

| Valor | Descripción | Color Sugerido |
|-------|-------------|----------------|
| `lead` | Prospecto inicial | Gris |
| `contactado` | Ya se hizo contacto | Azul |
| `visita_programada` | Visita agendada | Amarillo |
| `negociacion` | En proceso de negociación | Naranja |
| `cerrado_ganado` | Venta/Alquiler exitoso | Verde |
| `cerrado_perdido` | No se concretó | Rojo |

---

## 📞 Contacto con Propietario

Los campos `telefono` y `email` son del **propietario real** de la propiedad, úsalos para:

- 📱 Botón "Llamar" con link `tel:${telefono}`
- 📧 Botón "Enviar email" con link `mailto:${email}`
- 💬 Mostrar información de contacto en el detalle

**Ejemplo:**
```jsx
<a href={`tel:${propiedad.telefono}`} className="btn-call">
  📞 {propiedad.telefono}
</a>

{propiedad.email && (
  <a href={`mailto:${propiedad.email}`} className="btn-email">
    📧 {propiedad.email}
  </a>
)}
```

---

## ✅ Testing

### Endpoint de Prueba
```bash
curl -X GET "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades?page=1&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Credenciales de Prueba
- **Email**: `alancairampoma@gmail.com`
- **Password**: `Matias123`

---

## 📝 Notas Adicionales

1. El campo `email` es **opcional** - verificar que existe antes de mostrarlo
2. El `telefono` siempre está presente
3. La `direccion` es obligatoria
4. El `estado_crm` siempre tiene un valor válido

---

## 🚀 Próximos Pasos

1. Actualizar el TypeScript interface en el frontend
2. Agregar columnas en la tabla de propiedades
3. Implementar badges para `estado_crm`
4. Agregar botones de contacto (tel/email)
5. Probar con datos reales del API

---

## 💡 ¿Preguntas?

Contactar al equipo de backend para cualquier duda o ajuste adicional.

**Endpoint documentación completa**: `/docs` (Swagger UI)
