# KernHell 1-Click Update Script
# Usage: Right-click > Run with PowerShell
# Or run: .\install_update.ps1

Write-Host "🔥 KernHell Update Utility 🔥" -ForegroundColor Cyan
Write-Host "================================"

# 1. Activate Venv (if exists)
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activating Virtual Environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "[!] No 'venv' found. Installing in current environment..." -ForegroundColor DarkYellow
}

# 2. Uninstall Clean
Write-Host "[*] Cleaning old installations..." -ForegroundColor Yellow
pip uninstall kernhell -y | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Host "    (No previous version found, continuing...)" -ForegroundColor Gray }

# 3. Remove Build Artifacts
Write-Host "[*] Removing build artifacts..." -ForegroundColor Yellow
Remove-Item -Recurse -Force "kernhell.egg-info" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue

# 4. Install Dependencies
Write-Host "[*] Installing Dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt | Out-Null

# 5. Install KernHell (Editable Mode)
Write-Host "[*] Installing KernHell v2.0..." -ForegroundColor Yellow
pip install -e .

# 6. Verify
Write-Host "`n[*] Verification:" -ForegroundColor Cyan
$ver = kernhell version 2>&1
if ($?) {
    Write-Host "✅ SUCCESS: $ver" -ForegroundColor Green
    Write-Host "`nReady to rock! Try: kernhell help" -ForegroundColor Cyan
} else {
    Write-Host "❌ ERROR: Installation failed." -ForegroundColor Red
    exit 1
}

Read-Host "Press Enter to exit..."
