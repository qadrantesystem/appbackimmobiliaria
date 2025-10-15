"""
🔍 Verificar estado de SendGrid y diagnóstico completo
"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://appbackimmobiliaria-production.up.railway.app"

print("🔍 DIAGNÓSTICO COMPLETO DE SENDGRID\n")
print("="*70)

# 1. Verificar configuración
print("\n1️⃣ Verificando configuración...")
response = requests.get(f"{BASE_URL}/api/v1/test/sendgrid", verify=False)
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    config = data.get('config', {})
    test_result = data.get('test_result', {})
    
    print(f"\n   📋 CONFIGURACIÓN:")
    print(f"      API Key configurada: {config.get('api_key_configured')}")
    print(f"      API Key prefix: {config.get('api_key_prefix')}")
    print(f"      Email remitente: {config.get('from_email')}")
    print(f"      Nombre remitente: {config.get('from_name')}")
    print(f"      SendGrid inicializado: {config.get('sendgrid_initialized')}")
    
    print(f"\n   📤 RESULTADO DE PRUEBA:")
    print(f"      Success: {test_result.get('success')}")
    print(f"      Message: {test_result.get('message')}")
    print(f"      Email destino: {test_result.get('email')}")
    print(f"      Status Code SendGrid: {test_result.get('status_code')}")
    
    # Interpretar status code
    status_code = test_result.get('status_code')
    print(f"\n   📊 INTERPRETACIÓN:")
    if status_code == 202:
        print(f"      ✅ SendGrid ACEPTÓ el email (202 Accepted)")
        print(f"      ⚠️  PERO puede que no lo envíe si:")
        print(f"         - El email remitente NO está verificado en SendGrid")
        print(f"         - El dominio NO está verificado")
        print(f"         - La cuenta está en modo sandbox")
    elif status_code == 200:
        print(f"      ✅ Email enviado correctamente")
    else:
        print(f"      ❌ Error: Status code {status_code}")
else:
    print(f"   ❌ Error: {response.text}")

print("\n" + "="*70)
print("\n🔧 SOLUCIONES POSIBLES:\n")
print("1. VERIFICAR EMAIL REMITENTE en SendGrid:")
print("   - Ve a: https://app.sendgrid.com/settings/sender_auth/senders")
print("   - Verifica que 'sistemas@qadrante2.com' esté verificado")
print("   - Si no está, agrega y verifica el email\n")

print("2. VERIFICAR DOMINIO en SendGrid:")
print("   - Ve a: https://app.sendgrid.com/settings/sender_auth/domains")
print("   - Verifica el dominio 'qadrante2.com'")
print("   - Configura los registros DNS requeridos\n")

print("3. REVISAR ACTIVIDAD en SendGrid:")
print("   - Ve a: https://app.sendgrid.com/email_activity")
print("   - Busca los emails enviados a 'alancairampoma@gmail.com'")
print("   - Verifica el estado (Delivered, Bounced, Dropped, etc.)\n")

print("4. MODO SANDBOX:")
print("   - Si tu cuenta está en modo sandbox, solo puedes enviar")
print("   - a emails verificados en SendGrid\n")

print("="*70)
