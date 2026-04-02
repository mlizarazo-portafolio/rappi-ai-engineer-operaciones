# Cuando terminen las dos terminales: fusiona Uber + Rappi en scrape_latest.csv

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Caso = Join-Path $Root "caso_2_competitive_intelligence"
$DataOut = Join-Path $Root "data\caso_2_competitive_intelligence\output"
$Uber = Join-Path $DataOut "scrape_parallel_uber.csv"
$Rappi = Join-Path $DataOut "scrape_parallel_rappi.csv"
$Merged = Join-Path $DataOut "scrape_latest.csv"

foreach ($f in @($Uber, $Rappi)) {
    if (-not (Test-Path $f)) { throw "Falta archivo: $f" }
}

Set-Location $Caso
python -m competitive_intel merge-scrapes $Uber $Rappi -o $Merged
Write-Host "Fusionado en: $Merged"
