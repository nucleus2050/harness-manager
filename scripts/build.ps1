$ErrorActionPreference = "Stop"

python -m pip install -e .[dev]
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --name SkillPkgManager `
  --paths src `
  src/skillpkg/__main__.py

Write-Host "Built dist\SkillPkgManager\SkillPkgManager.exe"
