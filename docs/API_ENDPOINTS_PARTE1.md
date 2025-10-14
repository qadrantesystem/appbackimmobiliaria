# 🚀 API ENDPOINTS - PARTE 1: AUTH, USUARIOS, PERFILES

**Base URL:** `http://localhost:3000/api`

---

## 🔐 1. AUTENTICACIÓN

### 1.1. Registro de Usuario
**Endpoint:** `POST /api/auth/register`

**Body:**
```json
{
  "email": "usuario@email.com",
  "password": "123456",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+51 987654321",
  "dni": "12345678"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "data": {
    "usuario_id": 6,
    "email": "usuario@email.com",
    "nombre": "Juan",
    "apellido": "Pérez",
    "perfil_id": 1,
    "estado": "activo"
  }
}
```

---

### 1.2. Login
**Endpoint:** `POST /api/auth/login`

**Body:**
```json
{
  "email": "demandante@email.com",
  "password": "123456"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "usuario": {
      "usuario_id": 2,
      "email": "demandante@email.com",
      "nombre": "Juan",
      "apellido": "Pérez",
      "perfil_id": 1,
      "perfil_nombre": "demandante"
    }
  }
}
```

---

### 1.3. Verificar Token
**Endpoint:** `GET /api/auth/verify`  
**Headers:** `Authorization: Bearer {token}`

---

### 1.4. Logout
**Endpoint:** `POST /api/auth/logout`  
**Headers:** `Authorization: Bearer {token}`

---

## 👥 2. USUARIOS

### 2.1. Mi Perfil
**Endpoint:** `GET /api/usuarios/me`  
**Headers:** `Authorization: Bearer {token}`

### 2.2. Actualizar Perfil
**Endpoint:** `PUT /api/usuarios/me`  
**Headers:** `Authorization: Bearer {token}`

### 2.3. Cambiar Contraseña
**Endpoint:** `PUT /api/usuarios/me/password`  
**Headers:** `Authorization: Bearer {token}`

### 2.4. Listar Usuarios (Admin)
**Endpoint:** `GET /api/usuarios?page=1&limit=10`  
**Headers:** `Authorization: Bearer {token}`

---

## 🎭 3. PERFILES

### 3.1. Listar Perfiles
**Endpoint:** `GET /api/perfiles`

### 3.2. Asignar Perfil (Admin)
**Endpoint:** `POST /api/usuarios/:id/perfil`  
**Headers:** `Authorization: Bearer {token}`
