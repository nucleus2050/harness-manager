$ErrorActionPreference = "Stop"

python -m pip install -e .[dev]
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --name SkillPkgManager `
  --icon src/skillpkg/resources/app.ico `
  --paths src `
  src/skillpkg/__main__.py

Write-Host "Built dist\SkillPkgManager\SkillPkgManager.exe"
