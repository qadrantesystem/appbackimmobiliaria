# Test endpoint con token
$token = "TU_TOKEN_AQUI"

$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/22" -Headers $headers -Method GET
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host $_.Exception.Response.StatusCode
}
