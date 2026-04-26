#!/bin/bash
# HoneyShield Test Runner
# Runs all attack tests sequentially and generates report

set -e

TARGET_HOST="${1:-localhost}"
REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).txt"

echo "==============================================="
echo "HoneyShield - Honeypot Test Suite"
echo "==============================================="
echo "Target: $TARGET_HOST"
echo "Report: $REPORT_FILE"
echo "==============================================="
echo ""

{
    echo "Test Start: $(date)"
    echo "Target: $TARGET_HOST"
    echo "========================================"
    echo ""
    
    # Test 1: SSH Brute Force
    echo "TEST 1: SSH Brute Force Attack"
    echo "========================================"
    python3 tests/test_ssh.py || echo "SSH test failed or honeypot not running"
    echo ""
    
    # Test 2: HTTP Scan
    echo "TEST 2: HTTP Request Scanning"
    echo "========================================"
    python3 tests/test_http.py || echo "HTTP test failed or honeypot not running"
    echo ""
    
    # Test 3: FTP Login Attempts
    echo "TEST 3: FTP Login Brute Force"
    echo "========================================"
    python3 tests/test_ftp.py || echo "FTP test failed or honeypot not running"
    echo ""
    
    # Test 4: Telnet Login Attempts
    echo "TEST 4: Telnet Login Attempts"
    echo "========================================"
    python3 tests/test_telnet.py || echo "Telnet test failed or honeypot not running"
    echo ""
    
    # Test 5: Database Validation
    echo "TEST 5: Database Validation"
    echo "========================================"
    python3 tests/validate_db.py || echo "Database validation failed"
    echo ""
    
    echo "Test End: $(date)"
    echo "========================================"
    
} | tee "$REPORT_FILE"

echo ""
echo "Test report saved to: $REPORT_FILE"
echo ""
