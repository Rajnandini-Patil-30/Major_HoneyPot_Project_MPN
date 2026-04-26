@echo off
REM HoneyShield Dashboard startup script for Windows

echo.
echo ===================================
echo   HoneyShield Dashboard
echo   Starting React Development Server
echo ===================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [*] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed!
        pause
        exit /b 1
    )
)

echo [*] Starting React development server...
echo [*] Dashboard will open at http://localhost:3000
echo.
echo.

REM Start npm development server
npm start

pause
