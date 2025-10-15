"""
🏠 Script para registrar propiedad con imágenes
"""
import requests
import json
from pathlib import Path
import urllib3

# Deshabilitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appbackimmobiliaria-production.up.railway.app"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvX2lkIjozLCJlbWFpbCI6Im9mZXJ0YW50ZUBlbWFpbC5jb20iLCJwZXJmaWxfaWQiOjIsImV4cCI6MTc2MDU0MzI4NSwidHlwZSI6ImFjY2VzcyJ9.TEnO93Ma-EDpIBoMJJiQA9kTREip5aoozpVvjRLxZcg"

# Datos de la propiedad
propiedad_data = {
    "propietario_real_nombre": "Carlos Mendoza",
    "propietario_real_dni": "45678912",
    "propietario_real_telefono": "987123456",
    "propietario_real_email": "carlos.mendoza@email.com",
    "tipo_inmueble_id": 1,  # Oficina
    "distrito_id": 1,  # San Isidro
    "nombre_inmueble": "Oficina Premium Torre Empresarial",
    "direccion": "Av. Javier Prado Este 456, Piso 12",
    "latitud": -12.0931,
    "longitud": -77.0465,
    "area": 485.50,
    "habitaciones": 0,
    "banos": 2,
    "parqueos": 6,
    "antiguedad": 2,
    "transaccion": "alquiler",
    "precio_alquiler": 5500,
    "moneda": "USD",
    "titulo": "Oficina Premium en Torre Empresarial - San Isidro",
    "descripcion": "Moderna oficina en torre empresarial de primer nivel. Cuenta con acabados de lujo, amplios ventanales con vista panorámica, sistema de climatización central, seguridad 24/7 y estacionamiento techado. Ideal para empresas que buscan prestigio y comodidad.",
    "caracteristicas": [
        {"caracteristica_id": 9, "valor": "true"},   # Gimnasio
        {"caracteristica_id": 11, "valor": "true"},  # Sala de reuniones
        {"caracteristica_id": 15, "valor": "true"},  # Seguridad 24h
        {"caracteristica_id": 20, "valor": "true"}   # Ascensores
    ]
}

# Ruta de las fotos
foto_dir = Path(r"C:\Users\acairamp\Documents\proyecto\appimmobilarioback\foto\immuebles")

print("🏠 Registrando propiedad con imágenes...")
print(f"📸 Cargando fotos desde: {foto_dir}")

# Preparar archivos
files = []

# Agregar JSON de propiedad
files.append(('propiedad_json', (None, json.dumps(propiedad_data), 'application/json')))

# Imagen principal (foto1)
foto_principal_path = foto_dir / "foto1.jpeg"
if foto_principal_path.exists():
    files.append(('imagen_principal', (foto_principal_path.name, open(foto_principal_path, 'rb'), 'image/jpeg')))
    print(f"✅ Imagen principal: {foto_principal_path.name}")
else:
    print(f"❌ No se encontró: {foto_principal_path}")
    exit(1)

# Galería (foto2 a foto5) - IMPORTANTE: usar el mismo nombre de campo para cada archivo
galeria_files = []
for i in range(2, 6):
    foto_path = foto_dir / f"foto{i}.jpeg"
    if foto_path.exists():
        files.append(('imagenes_galeria', (foto_path.name, open(foto_path, 'rb'), 'image/jpeg')))
        print(f"✅ Galería {i-1}: {foto_path.name}")

all_files = files

print("\n📤 Enviando request al servidor...")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/propiedades/con-imagenes",
        files=all_files,
        headers={"Authorization": f"Bearer {TOKEN}"},
        verify=False
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print("\n✅ ¡PROPIEDAD REGISTRADA EXITOSAMENTE!")
        print(f"\n📋 Detalles:")
        print(f"   ID: {result['data']['registro_cab_id']}")
        print(f"   Título: {result['data']['titulo']}")
        print(f"   Estado: {result['data']['estado']}")
        print(f"   Imagen Principal: {result['data']['imagen_principal']}")
        print(f"   Total Galería: {result['data']['total_imagenes_galeria']}")
        print(f"   Características: {result['data']['total_caracteristicas']}")
        print(f"\n🖼️ URLs de Imágenes:")
        print(f"   Principal: {result['data']['imagen_principal']}")
        for idx, url in enumerate(result['data']['imagenes_galeria'], 1):
            print(f"   Galería {idx}: {url}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    # Cerrar archivos
    for item in files:
        if len(item) > 1 and hasattr(item[1][1], 'close'):
            item[1][1].close()

print("\n✅ Proceso completado")
