# HoneyShield Dashboard startup script for PowerShell

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   HoneyShield Dashboard" -ForegroundColor Cyan
Write-Host "   Starting React Development Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] npm install failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "[*] Starting React development server..." -ForegroundColor Green
Write-Host "[*] Dashboard will open at http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host ""

# Start npm development server
npm start

Read-Host "Press Enter to exit"
