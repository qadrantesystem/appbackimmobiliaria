# Test latitud y longitud en response
$API = "https://appbackimmobiliaria-production.up.railway.app/api/v1"

Write-Host "`nTEST: Verificar latitud y longitud en propiedades`n" -ForegroundColor Cyan

# 1. Endpoint publico
Write-Host "1. GET /propiedades?limit=2" -ForegroundColor Yellow
$props = Invoke-RestMethod -Uri "$API/propiedades?limit=2" -Method GET

if ($props.data -and $props.data.Count -gt 0) {
    $primera = $props.data[0]
    Write-Host "Primera propiedad:" -ForegroundColor Green
    Write-Host "  ID: $($primera.registro_cab_id)" -ForegroundColor White
    Write-Host "  Titulo: $($primera.titulo)" -ForegroundColor White
    Write-Host "  Latitud: $($primera.latitud)" -ForegroundColor Cyan
    Write-Host "  Longitud: $($primera.longitud)" -ForegroundColor Cyan
    
    if ($primera.latitud -and $primera.longitud) {
        Write-Host "`n  OK - Latitud y longitud presentes en la respuesta" -ForegroundColor Green
    } else {
        Write-Host "`n  ERROR - Faltan coordenadas" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR - No hay propiedades" -ForegroundColor Red
}

Write-Host ""
