$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$flet = Join-Path $projectRoot "venv\Scripts\flet.exe"

if (-not (Test-Path -LiteralPath $flet)) {
    throw "No se encuentra Flet en $flet"
}

$distRoot = Join-Path $projectRoot "dist"

Push-Location $projectRoot
try {
    & $flet pack app.py `
        --onedir `
        --name "EvaluacionCDD-portable" `
        --distpath $distRoot `
        --add-data "assets:assets" "data:data" `
        --product-name "Evaluacion CDD" `
        --file-description "Aplicacion de evaluacion de la competencia digital docente" `
        --product-version "1.0.0" `
        --file-version "1.0.0.0" `
        --company-name "TFM CDD" `
        --copyright "2026 TFM CDD" `
        --yes
} finally {
    Pop-Location
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$results = Join-Path $distRoot "EvaluacionCDD-portable\results"
New-Item -ItemType Directory -Path $results -Force | Out-Null

Write-Host "Versión portable creada en: dist\EvaluacionCDD-portable"
