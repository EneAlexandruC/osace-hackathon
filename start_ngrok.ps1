# Start the AI Classifier App with ngrok

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  AI Classifier - Simple Startup" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Check if ngrok is installed
Write-Host "[1/3] Checking ngrok..." -ForegroundColor Cyan
$ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokInstalled) {
    Write-Host "[ERROR] ngrok is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install ngrok from: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host "[OK] ngrok found!" -ForegroundColor Green
Write-Host ""

# Start Flask in background
Write-Host "[2/3] Starting Flask backend on port 5000..." -ForegroundColor Cyan
Write-Host "This serves both the API and frontend!" -ForegroundColor Gray
Write-Host ""

$flaskJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    & python backend/app.py
}

# Wait a bit for Flask to start
Start-Sleep -Seconds 3

# Check if Flask started successfully
if ($flaskJob.State -eq "Running") {
    Write-Host "[OK] Flask is running!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Flask failed to start" -ForegroundColor Red
    Write-Host "Check if port 5000 is already in use:" -ForegroundColor Yellow
    Write-Host "  netstat -ano | findstr :5000" -ForegroundColor Gray
    Stop-Job $flaskJob
    Remove-Job $flaskJob
    exit 1
}
Write-Host ""

# Start ngrok
Write-Host "[3/3] Starting ngrok tunnel..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop both Flask and ngrok" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Your app is starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The ngrok URL will appear below." -ForegroundColor Cyan
Write-Host "Open that URL in your browser!" -ForegroundColor Cyan
Write-Host ""

try {
    # Start ngrok (blocks until Ctrl+C)
    ngrok http 5000
}
finally {
    # Cleanup: Stop Flask when script exits
    Write-Host ""
    Write-Host "Stopping Flask..." -ForegroundColor Yellow
    Stop-Job $flaskJob -ErrorAction SilentlyContinue
    Remove-Job $flaskJob -ErrorAction SilentlyContinue
    Write-Host "Done!" -ForegroundColor Green
}
