@echo off
REM HoneyShield Test Runner (Windows Batch)
REM Runs all attack tests sequentially and generates report

setlocal enabledelayedexpansion

set TARGET_HOST=%1
if "%TARGET_HOST%"=="" set TARGET_HOST=localhost

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set DATE=%%c%%a%%b
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do set TIME=%%a%%b

set REPORT_FILE=test_report_%DATE%_%TIME%.txt

echo ===============================================
echo HoneyShield - Honeypot Test Suite
echo ===============================================
echo Target: %TARGET_HOST%
echo Report: %REPORT_FILE%
echo ===============================================
echo.

(
    echo Test Start: %date% %time%
    echo Target: %TARGET_HOST%
    echo ========================================
    echo.
    
    REM Test 1: SSH Brute Force
    echo TEST 1: SSH Brute Force Attack
    echo ========================================
    python tests\test_ssh.py
    if errorlevel 1 echo SSH test failed or honeypot not running
    echo.
    
    REM Test 2: HTTP Scan
    echo TEST 2: HTTP Request Scanning
    echo ========================================
    python tests\test_http.py
    if errorlevel 1 echo HTTP test failed or honeypot not running
    echo.
    
    REM Test 3: FTP Login Attempts
    echo TEST 3: FTP Login Brute Force
    echo ========================================
    python tests\test_ftp.py
    if errorlevel 1 echo FTP test failed or honeypot not running
    echo.
    
    REM Test 4: Telnet Login Attempts
    echo TEST 4: Telnet Login Attempts
    echo ========================================
    python tests\test_telnet.py
    if errorlevel 1 echo Telnet test failed or honeypot not running
    echo.
    
    REM Test 5: Database Validation
    echo TEST 5: Database Validation
    echo ========================================
    python tests\validate_db.py
    if errorlevel 1 echo Database validation failed
    echo.
    
    echo Test End: %date% %time%
    echo ========================================
) | tee %REPORT_FILE%

echo.
echo Test report saved to: %REPORT_FILE%
echo.
