# Test endpoints públicos
$baseUrl = "https://appbackimmobiliaria-production.up.railway.app/api/v1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST ENDPOINTS PÚBLICOS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Test Tipos de Inmueble
Write-Host "1. TIPOS DE INMUEBLE" -ForegroundColor Yellow
Write-Host "GET $baseUrl/tipos-inmueble`n" -ForegroundColor Gray
try {
    $tiposInmueble = Invoke-RestMethod -Uri "$baseUrl/tipos-inmueble" -Method GET
    Write-Host "✅ SUCCESS - Total: $($tiposInmueble.Count) tipos" -ForegroundColor Green
    $tiposInmueble | ForEach-Object {
        Write-Host "   - ID: $($_.tipo_inmueble_id) | Nombre: $($_.nombre) | Activo: $($_.activo)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ ERROR: $_" -ForegroundColor Red
}

# 2. Test Distritos
Write-Host "`n2. DISTRITOS" -ForegroundColor Yellow
Write-Host "GET $baseUrl/distritos`n" -ForegroundColor Gray
try {
    $distritos = Invoke-RestMethod -Uri "$baseUrl/distritos" -Method GET
    Write-Host "✅ SUCCESS - Total: $($distritos.Count) distritos" -ForegroundColor Green
    Write-Host "`nPrimeros 10 distritos:" -ForegroundColor Cyan
    $distritos | Select-Object -First 10 | ForEach-Object {
        Write-Host "   - ID: $($_.distrito_id) | Nombre: $($_.nombre)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ ERROR: $_" -ForegroundColor Red
}

# 3. Test Características (público también)
Write-Host "`n3. CARACTERÍSTICAS" -ForegroundColor Yellow
Write-Host "GET $baseUrl/caracteristicas`n" -ForegroundColor Gray
try {
    $caracteristicas = Invoke-RestMethod -Uri "$baseUrl/caracteristicas" -Method GET
    Write-Host "✅ SUCCESS - Total: $($caracteristicas.Count) características" -ForegroundColor Green
    Write-Host "`nPrimeras 5 características:" -ForegroundColor Cyan
    $caracteristicas | Select-Object -First 5 | ForEach-Object {
        Write-Host "   - ID: $($_.caracteristica_id) | Nombre: $($_.nombre) | Categoría: $($_.categoria)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ ERROR: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "FIN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
