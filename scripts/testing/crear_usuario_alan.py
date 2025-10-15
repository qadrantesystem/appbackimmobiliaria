"""
👤 Crear usuario Alan Cairampoma
"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appbackimmobiliaria-production.up.railway.app"

print("👤 CREANDO USUARIO ALAN CAIRAMPOMA\n")
print("="*60)

# Datos del usuario
usuario_data = {
    "email": "alancairampoma@gmail.com",
    "password": "Alan123!",
    "nombre": "Alan",
    "apellido": "Cairampoma",
    "telefono": "999888777",
    "dni": "12345678",
    "perfil_id": 2  # Ofertante
}

print("\n📝 Datos del usuario:")
print(f"   Email: {usuario_data['email']}")
print(f"   Nombre: {usuario_data['nombre']} {usuario_data['apellido']}")
print(f"   Perfil: Ofertante")
print(f"   Password: {usuario_data['password']}")

print("\n📤 Registrando usuario...")
response = requests.post(
    f"{BASE_URL}/api/v1/auth/register",
    json=usuario_data,
    verify=False
)

print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ USUARIO CREADO EXITOSAMENTE!")
    print(f"\n📧 Se envió un código de verificación a: {usuario_data['email']}")
    print(f"\n⏰ Revisa tu email (bandeja de entrada o SPAM)")
    print(f"\n🔐 Una vez que recibas el código, ingrésalo para verificar tu cuenta")
    print(f"\n📋 Datos de acceso:")
    print(f"   Email: {usuario_data['email']}")
    print(f"   Password: {usuario_data['password']}")
else:
    print(f"\n❌ Error: {response.text}")

print("\n" + "="*60)
