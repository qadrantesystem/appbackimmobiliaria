# Test directo del endpoint tipos-inmueble
$url = "https://appbackimmobiliaria-production.up.railway.app/api/v1/tipos-inmueble"

Write-Host "Probando: $url`n" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri $url -Method GET
    $statusCode = $response.StatusCode
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "Status Code: $statusCode" -ForegroundColor Green
    Write-Host "Content-Type: $($response.Headers['Content-Type'])" -ForegroundColor Yellow
    Write-Host "`nRespuesta completa:" -ForegroundColor Yellow
    $content | ConvertTo-Json -Depth 5
    Write-Host "`nTotal items: $($content.Count)" -ForegroundColor Cyan
    
} catch {
    Write-Host "ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nStatus Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
}
