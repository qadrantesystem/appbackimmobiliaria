"""
📧 Script para probar conexión y envío con SendGrid
"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appbackimmobiliaria-production.up.railway.app"

print("📧 PRUEBAS DE SENDGRID\n")
print("="*60)

# 1. Verificar configuración de SendGrid
print("\n1️⃣ Verificando configuración de SendGrid...")
response = requests.get(
    f"{BASE_URL}/api/v1/test/sendgrid",
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ SendGrid configurado correctamente")
    print(f"   📧 Email remitente: {data.get('config', {}).get('from_email')}")
    print(f"   👤 Nombre remitente: {data.get('config', {}).get('from_name')}")
    print(f"   🔑 API Key configurada: {data.get('config', {}).get('api_key_configured')}")
else:
    print(f"   ❌ Error: {response.text}")

# 2. Enviar email de prueba
print("\n2️⃣ Enviando email de prueba...")
email_destino = input("   Ingresa tu email para recibir el test: ").strip()

if email_destino:
    response = requests.post(
        f"{BASE_URL}/api/v1/test/send-email",
        json={"email": email_destino},
        verify=False
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data.get('message')}")
        print(f"   📧 Email enviado a: {email_destino}")
        print(f"   ⏰ Revisa tu bandeja de entrada (y spam)")
    else:
        print(f"   ❌ Error: {response.text}")
else:
    print("   ⚠️ No se ingresó email, saltando prueba de envío")

# 3. Registrar usuario nuevo para probar email de verificación
print("\n3️⃣ Probando email de verificación (registro de usuario)...")
test_email = input("   Ingresa email para crear usuario de prueba (o Enter para saltar): ").strip()

if test_email:
    import random
    random_num = random.randint(1000, 9999)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": test_email,
            "password": "Test123!",
            "nombre": "Usuario",
            "apellido": "Prueba",
            "telefono": f"99999{random_num}",
            "dni": f"7777{random_num}",
            "perfil_id": 1
        },
        verify=False
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Usuario registrado: {data.get('data', {}).get('email')}")
        print(f"   📧 Email de verificación enviado")
        print(f"   ⏰ Revisa tu bandeja de entrada para verificar")
    else:
        print(f"   ❌ Error: {response.text}")
else:
    print("   ⚠️ Saltando prueba de registro")

print("\n" + "="*60)
print("✅ Pruebas de SendGrid completadas")
print("\n💡 Notas:")
print("   - Si no llega el email, revisa la carpeta de SPAM")
print("   - Verifica que el email esté en la lista de remitentes verificados de SendGrid")
print("   - Los emails pueden tardar 1-2 minutos en llegar")
