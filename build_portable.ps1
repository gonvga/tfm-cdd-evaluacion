param(
    [ValidatePattern("^\d+\.\d+\.\d+$")]
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$flet = Join-Path $projectRoot "venv\Scripts\flet.exe"

if (-not (Test-Path -LiteralPath $flet)) {
    throw "No se encuentra Flet en $flet"
}

$distRoot = Join-Path $projectRoot "dist"
$portableName = "EvaluacionCDD-portable"
$portablePath = Join-Path $distRoot $portableName
$zipPath = Join-Path $distRoot "EvaluacionCDD-portable-windows.zip"

Push-Location $projectRoot
try {
    & $flet pack app.py `
        --onedir `
        --name $portableName `
        --distpath $distRoot `
        --add-data "assets:assets" "data:data" `
        --product-name "Evaluacion CDD" `
        --file-description "Aplicacion de evaluacion de la competencia digital docente" `
        --product-version $Version `
        --file-version "$Version.0" `
        --company-name "TFM CDD" `
        --copyright "2026 TFM CDD" `
        --yes
} finally {
    Pop-Location
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$results = Join-Path $portablePath "results"
New-Item -ItemType Directory -Path $results -Force | Out-Null

$readme = Join-Path $projectRoot "LEEME.txt"
Copy-Item -LiteralPath $readme -Destination (Join-Path $portablePath "LEEME.txt") -Force

$compressed = $false
for ($attempt = 1; $attempt -le 5; $attempt++) {
    try {
        Start-Sleep -Seconds 2
        Compress-Archive `
            -Path $portablePath `
            -DestinationPath $zipPath `
            -CompressionLevel Optimal `
            -Force `
            -ErrorAction Stop
        $compressed = $true
        break
    } catch {
        Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
        if ($attempt -eq 5) {
            throw "No se pudo comprimir la aplicación después de 5 intentos: $($_.Exception.Message)"
        }
        Write-Warning "El portable sigue en uso. Nuevo intento de compresión ($($attempt + 1)/5)..."
    }
}

if (-not $compressed -or -not (Test-Path -LiteralPath $zipPath)) {
    throw "No se creó el archivo ZIP de distribución."
}

Write-Host "Archivo para distribuir creado en: dist\EvaluacionCDD-portable-windows.zip"

Write-Host "Versión portable creada en: dist\EvaluacionCDD-portable"
