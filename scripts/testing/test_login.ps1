# Script para obtener token de autenticación
$baseUrl = "https://appbackimmobiliaria-production.up.railway.app"

# Login como admin
$loginBody = @{
    email = "admin@matchproperty.com"
    password = "Admin123!"
} | ConvertTo-Json

Write-Host "🔐 Obteniendo token de admin..." -ForegroundColor Cyan

$response = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"

if ($response.success) {
    $token = $response.data.access_token
    Write-Host "✅ Token obtenido exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "TOKEN:" -ForegroundColor Yellow
    Write-Host $token
    Write-Host ""
    Write-Host "Usuario: $($response.data.usuario.nombre) $($response.data.usuario.apellido)" -ForegroundColor Cyan
    Write-Host "Perfil: $($response.data.usuario.perfil)" -ForegroundColor Cyan
    
    # Guardar en archivo
    $token | Out-File -FilePath "token.txt" -Encoding UTF8
    Write-Host ""
    Write-Host "✅ Token guardado en token.txt" -ForegroundColor Green
} else {
    Write-Host "❌ Error en login: $($response.message)" -ForegroundColor Red
}
