# Dashboard Launcher Script for Windows
# Run this script to start the Streamlit dashboard

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Data Redaction Gateway - Metrics Dashboard" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if streamlit is installed
$streamlitCheck = Get-Command streamlit -ErrorAction SilentlyContinue
if (-not $streamlitCheck) {
    Write-Host "ERROR: Streamlit is not installed" -ForegroundColor Red
    Write-Host "Installing dashboard requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install requirements. Please run: pip install -r requirements.txt" -ForegroundColor Red
        exit 1
    }
}

# Check if API is accessible
Write-Host "Checking API connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/metrics/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ API is accessible" -ForegroundColor Green
} catch {
    Write-Host "⚠ WARNING: Cannot connect to API at http://127.0.0.1:8000" -ForegroundColor Yellow
    Write-Host "Make sure the Data Redaction Gateway API is running" -ForegroundColor Yellow
    Write-Host "You can change the API URL in the dashboard sidebar" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Streamlit dashboard..." -ForegroundColor Green
Write-Host "Dashboard will open in your browser at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
streamlit run app.py --server.port 8501 --server.address localhost
