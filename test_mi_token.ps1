$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvX2lkIjoyMCwiZW1haWwiOiJhbGFuY2FpcmFtcG9tYUBnbWFpbC5jb20iLCJwZXJmaWxfaWQiOjQsImV4cCI6MTc2MDk5NDQyMSwidHlwZSI6ImFjY2VzcyJ9.KOUvADF8EyVQhT6pirKg6cQmddmNzzwn8ZGzHp6_XHo"

$headers = @{
    "Authorization" = "Bearer $token"
}

Write-Host "🔑 Probando token..." -ForegroundColor Cyan
Write-Host "🌐 URL: https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/22"
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "https://appbackimmobiliaria-production.up.railway.app/api/v1/propiedades/22" -Headers $headers -Method GET
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 RESPUESTA:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ ERROR!" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Message: $($_.Exception.Message)"
    
    if ($_.ErrorDetails.Message) {
        Write-Host "Detail:" -ForegroundColor Yellow
        $_.ErrorDetails.Message
    }
}
