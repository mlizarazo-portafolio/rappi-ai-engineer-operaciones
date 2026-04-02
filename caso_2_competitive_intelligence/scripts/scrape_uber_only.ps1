# Terminal 1: solo Uber Eats -> scrape_parallel_uber.csv
# Uso: .\scripts\scrape_uber_only.ps1
# Opcional: -Headed para ver el navegador

param(
    [switch]$Headed,
    [double]$Delay = 6.0
)

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Caso = Join-Path $Root "caso_2_competitive_intelligence"
$Out = Join-Path $Root "data\caso_2_competitive_intelligence\output\scrape_parallel_uber.csv"

Set-Location $Caso
$pyArgs = @(
    "-m", "competitive_intel", "scrape",
    "-o", $Out,
    "--platforms", "uber_eats",
    "--delay", "$Delay",
    "--browser", "firefox"
)
if ($Headed) { $pyArgs += "--headed" }
& python @pyArgs
Write-Host "Listo: $Out"
