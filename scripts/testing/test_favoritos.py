"""
⭐ Script para probar Favoritos
"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appbackimmobiliaria-production.up.railway.app"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvX2lkIjozLCJlbWFpbCI6Im9mZXJ0YW50ZUBlbWFpbC5jb20iLCJwZXJmaWxfaWQiOjIsImV4cCI6MTc2MDU0MzI4NSwidHlwZSI6ImFjY2VzcyJ9.TEnO93Ma-EDpIBoMJJiQA9kTREip5aoozpVvjRLxZcg"

headers = {"Authorization": f"Bearer {TOKEN}"}

print("⭐ PRUEBAS DE FAVORITOS\n")

# 1. Agregar favorito
print("1️⃣ Agregando favorito (Propiedad ID: 11)...")
response = requests.post(
    f"{BASE_URL}/api/v1/favoritos/",
    json={"registro_cab_id": 11, "notas": "Me encanta esta oficina!"},
    headers=headers,
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    favorito_id = data['favorito_id']
    print(f"   ✅ Favorito agregado con ID: {favorito_id}")
    print(f"   Notas: {data.get('notas')}")
else:
    print(f"   ❌ Error: {response.text}")
    favorito_id = None

# 2. Listar favoritos
print("\n2️⃣ Listando mis favoritos...")
response = requests.get(
    f"{BASE_URL}/api/v1/favoritos/",
    headers=headers,
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    favoritos = response.json()
    print(f"   ✅ Total favoritos: {len(favoritos)}")
    for fav in favoritos:
        print(f"      - ID: {fav['favorito_id']}, Propiedad: {fav['propiedad_titulo']}")
else:
    print(f"   ❌ Error: {response.text}")

# 3. Eliminar favorito
if favorito_id:
    print(f"\n3️⃣ Eliminando favorito ID: {favorito_id}...")
    response = requests.delete(
        f"{BASE_URL}/api/v1/favoritos/{favorito_id}",
        headers=headers,
        verify=False
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Favorito eliminado exitosamente")
    else:
        print(f"   ❌ Error: {response.text}")

# 4. Verificar que se eliminó
print("\n4️⃣ Verificando lista después de eliminar...")
response = requests.get(
    f"{BASE_URL}/api/v1/favoritos/",
    headers=headers,
    verify=False
)
if response.status_code == 200:
    favoritos = response.json()
    print(f"   ✅ Total favoritos: {len(favoritos)}")
else:
    print(f"   ❌ Error: {response.text}")

print("\n✅ Pruebas completadas")
