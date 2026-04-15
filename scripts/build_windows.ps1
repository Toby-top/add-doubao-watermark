$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

$env:PYTHONPATH = "src"

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Windows uses ';' in --add-data.
$DataArg = "src\add_doubao_watermark\assets;add_doubao_watermark\assets"

pyinstaller -F pyinstaller_entry.py -n doubao-watermark --clean --paths src --add-data $DataArg
pyinstaller -F -w pyinstaller_gui_entry.py -n doubao-watermark-gui --clean --paths src --add-data $DataArg

$Version = python -c "import sys; sys.path.insert(0,'src'); import add_doubao_watermark as p; print(p.__version__)"
$Arch = $env:PROCESSOR_ARCHITECTURE
if (-not $Arch) { $Arch = "x64" }

$ZipName = "doubao-watermark-$Version-windows-$Arch.zip"
$ZipPath = Join-Path "dist" $ZipName
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }

Compress-Archive -Path "dist\doubao-watermark.exe","dist\doubao-watermark-gui.exe" -DestinationPath $ZipPath
Write-Host "Built: $ZipPath"

