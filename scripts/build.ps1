$ErrorActionPreference = "Stop"

python -m pip install -e .[dev]
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --name HarnessManager `
  --icon src/harness_manager/resources/app.ico `
  --paths src `
  src/harness_manager/__main__.py

Write-Host "Built dist\HarnessManager\HarnessManager.exe"
