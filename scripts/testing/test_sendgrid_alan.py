"""
📧 Test SendGrid - Envío directo a alancairampoma@gmail.com
"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appbackimmobiliaria-production.up.railway.app"
EMAIL_DESTINO = "alancairampoma@gmail.com"

print("📧 TEST SENDGRID - Envío a Alan\n")
print("="*60)

# 1. Verificar configuración
print("\n1️⃣ Verificando configuración de SendGrid...")
response = requests.get(
    f"{BASE_URL}/api/v1/test/sendgrid",
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ SendGrid configurado")
    print(f"   📧 Remitente: {data.get('config', {}).get('from_email')}")
    print(f"   🔑 API Key: {'Configurada' if data.get('config', {}).get('api_key_configured') else 'NO configurada'}")
else:
    print(f"   ❌ Error: {response.text}")

# 2. Enviar email de prueba directo
print(f"\n2️⃣ Enviando email de prueba a {EMAIL_DESTINO}...")
response = requests.post(
    f"{BASE_URL}/api/v1/test/send-email?email={EMAIL_DESTINO}",
    verify=False
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ {data.get('message')}")
    print(f"   📧 Email enviado exitosamente")
    print(f"   ⏰ Revisa tu bandeja de entrada (y spam si no aparece)")
else:
    print(f"   ❌ Error: {response.text}")

print("\n" + "="*60)
print("✅ Test completado")
print("\n💡 Si no llega el email:")
print("   1. Revisa la carpeta de SPAM/Correo no deseado")
print("   2. Espera 1-2 minutos")
print("   3. Verifica los logs de Railway para ver si hay errores")
