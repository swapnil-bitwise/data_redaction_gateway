# Test Runner with Output Capture
# Captures all test output to test_run_log.txt for analysis

Write-Host "`n=== Running Test Suite with Output Capture ===" -ForegroundColor Cyan

$logFile = "test_suite/test_run_log.txt"

Write-Host "Running tests and capturing output to $logFile..." -ForegroundColor Yellow
Write-Host ""

# Run pytest and capture all output
$output = python -m pytest test_suite/test_api_endpoints.py -v --tb=short --color=no 2>&1

# Save to file
$output | Out-File -FilePath $logFile -Encoding utf8

# Also display to console
$output

Write-Host "`n=== Test output saved to $logFile ===" -ForegroundColor Cyan
Write-Host ""

# Count failures
$failedTests = ($output | Select-String "FAILED").Count
$passedTests = ($output | Select-String "PASSED").Count

Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Passed: $passedTests" -ForegroundColor $(if ($passedTests -gt 0) { "Green" } else { "Gray" })
Write-Host "  Failed: $failedTests" -ForegroundColor $(if ($failedTests -gt 0) { "Red" } else { "Green" })

if ($failedTests -gt 0) {
    Write-Host "`nAnalyzing failures..." -ForegroundColor Yellow
    
    # Extract failure summary
    $failureLines = $output | Select-String "FAILED"
    
    Write-Host "`nFailed Tests:" -ForegroundColor Red
    foreach ($line in $failureLines) {
        Write-Host "  - $($line.Line)" -ForegroundColor Red
    }
    
    Write-Host "`nRun analysis script to generate detailed report:" -ForegroundColor Cyan
    Write-Host "  python analyze_failures.py" -ForegroundColor White
}

Write-Host ""
