# Test endpoint características agrupadas
$loginUrl = "https://appbackimmobiliaria-production.up.railway.app/api/v1/auth/login"
$caracteristicasUrl = "https://appbackimmobiliaria-production.up.railway.app/api/v1/caracteristicas-x-inmueble/tipo-inmueble/1/agrupadas"

Write-Host "=== LOGIN ===" -ForegroundColor Cyan
$loginBody = @{
    email = "alancairampoma@gmail.com"
    password = "Matias123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri $loginUrl -Method POST -Body $loginBody -ContentType "application/json"
$token = $loginResponse.data.access_token
Write-Host "✅ Token obtenido`n" -ForegroundColor Green

Write-Host "=== PROBANDO ENDPOINT ===" -ForegroundColor Cyan
$headers = @{ "Authorization" = "Bearer $token" }
$response = Invoke-RestMethod -Uri $caracteristicasUrl -Method GET -Headers $headers

Write-Host "✅ ENDPOINT FUNCIONANDO!" -ForegroundColor Green
Write-Host "`nRespuesta:" -ForegroundColor Yellow
$response | ConvertTo-Json -Depth 5
