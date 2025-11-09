# Test Suite Runner for PII/PCI Data Redaction Gateway
# Run all API endpoint tests with detailed output

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     PII/PCI Data Redaction Gateway - Test Suite          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if pytest is installed
Write-Host "[1/4] Checking dependencies..." -ForegroundColor Yellow
try {
    $pytestVersion = python -m pytest --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ pytest installed: $($pytestVersion)" -ForegroundColor Green
    } else {
        throw "pytest not found"
    }
} catch {
    Write-Host "  ✗ pytest not installed" -ForegroundColor Red
    Write-Host "`nInstalling pytest and requests..." -ForegroundColor Yellow
    pip install pytest requests pytest-html
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
}

# Check if server is running
Write-Host "`n[2/4] Checking if server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Server is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Server is not running" -ForegroundColor Red
    Write-Host "`nPlease start the server first:" -ForegroundColor Yellow
    Write-Host "  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
    Write-Host "`nOr run in a separate terminal:" -ForegroundColor Yellow
    Write-Host "  Start-Process powershell -ArgumentList '-NoExit', '-Command', 'uvicorn src.main:app --reload'" -ForegroundColor White
    
    $startServer = Read-Host "`nWould you like to start the server now? (y/n)"
    if ($startServer -eq 'y') {
        Write-Host "`nStarting server in background..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd $PWD; uvicorn src.main:app --reload --host 0.0.0.0 --port 8000'
        Write-Host "Waiting for server to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
            Write-Host "  ✓ Server started successfully" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Server failed to start" -ForegroundColor Red
            exit 1
        }
    } else {
        exit 1
    }
}

# Check test data files
Write-Host "`n[3/4] Checking test data files..." -ForegroundColor Yellow
$testFiles = @("input/test_chat.json", "input/test_transaction.json", "input/test_order.json")
$allFilesExist = $true

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file not found" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "`nError: Some test data files are missing" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "`n[4/4] Running test suite..." -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Run pytest with verbose output and show print statements
python -m pytest test_suite/ -v -s --tb=short --color=yes

$exitCode = $LASTEXITCODE

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "`n✓ All tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Some tests failed" -ForegroundColor Red
}

Write-Host "`nTest reports available in:" -ForegroundColor Yellow
Write-Host "  - Console output above" -ForegroundColor White
Write-Host "  - HTML report: test_suite/report.html (if generated)" -ForegroundColor White

Write-Host "`nFor more options, see: test_suite/README.md" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
