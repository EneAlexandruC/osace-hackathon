# Quick Setup Script for Robot vs Human Classifier
# Run this script to set up the project quickly
#
# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Robot vs Human CNN Classifier" -ForegroundColor Cyan
Write-Host "Quick Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Python not found! Please install Python 3.8 or higher" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Install backend dependencies
Write-Host ""
Write-Host "[2/5] Installing backend dependencies..." -ForegroundColor Yellow
$pipInstall =pip install -r .\backend\requirements.txt 2>&1
$pipExitCode = $LASTEXITCODE

if ($pipExitCode -eq 0) {
    Write-Host "  [OK] Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to install dependencies" -ForegroundColor Red
    Write-Host "  Error: $pipInstall" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host ""
Write-Host "[3/5] Creating directory structure..." -ForegroundColor Yellow
$rootPath = $PSScriptRoot
$directories = @(
    "data\raw\human",
    "data\raw\robot",
    "data\train\human",
    "data\train\robot",
    "data\val\human",
    "data\val\robot",
    "data\test\human",
    "data\test\robot",
    "backend\uploads",
    "model"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $rootPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
}
Write-Host "  [OK] Directory structure created!" -ForegroundColor Green

# Prepare dataset
Write-Host ""
Write-Host "[4/5] Running dataset preparation..." -ForegroundColor Yellow
$modelPath = Join-Path $PSScriptRoot "model"
Push-Location $modelPath
python prepare_dataset.py
Pop-Location

# Check if images exist
$humanPath = Join-Path $rootPath "data\raw\human"
$robotPath = Join-Path $rootPath "data\raw\robot"
$humanImages = @(Get-ChildItem $humanPath -File -ErrorAction SilentlyContinue)
$robotImages = @(Get-ChildItem $robotPath -File -ErrorAction SilentlyContinue)

Write-Host ""
if ($humanImages.Count -eq 0 -or $robotImages.Count -eq 0) {
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host "IMPORTANT: ADD IMAGES!" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please add images to:" -ForegroundColor White
    Write-Host "  data\raw\human\ - images of humans" -ForegroundColor White
    Write-Host "  data\raw\robot\ - images of robots" -ForegroundColor White
    Write-Host ""
    Write-Host "Recommended sources:" -ForegroundColor White
    Write-Host "  Kaggle datasets" -ForegroundColor White
    Write-Host "  Google Images (bulk download)" -ForegroundColor White
    Write-Host "  Custom collection (at least 200 images per class)" -ForegroundColor White
    Write-Host ""
    Write-Host "After adding images, run:" -ForegroundColor Cyan
    Write-Host "  python model\prepare_dataset.py" -ForegroundColor Cyan
    Write-Host "  python model\train.py" -ForegroundColor Cyan
    Write-Host ""
}
else {
    Write-Host "  [OK] Found $($humanImages.Count) human images and $($robotImages.Count) robot images" -ForegroundColor Green
    
    # Train model
    Write-Host ""
    Write-Host "[5/5] Training model (this may take a while)..." -ForegroundColor Yellow
    Write-Host "  Note: You can skip this by pressing Ctrl+C and train later" -ForegroundColor Gray
    Push-Location $modelPath
    python train.py
    $trainExitCode = $LASTEXITCODE
    Pop-Location
    
    if ($trainExitCode -eq 0) {
        Write-Host "  [OK] Model training completed!" -ForegroundColor Green
    }
    else {
        Write-Host "  [WARNING] Model training had issues (exit code: $trainExitCode)" -ForegroundColor Yellow
        Write-Host "  You can try training again later with: python model\train.py" -ForegroundColor Yellow
    }
}

# Final instructions
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "[OK] Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host ""

if ($humanImages.Count -eq 0 -or $robotImages.Count -eq 0) {
    Write-Host "1. Add images to data\raw\human\ and data\raw\robot\" -ForegroundColor Yellow
    Write-Host "2. Run: python model\prepare_dataset.py" -ForegroundColor Yellow
    Write-Host "3. Run: python model\train.py" -ForegroundColor Yellow
    Write-Host "4. Run: python backend\app.py" -ForegroundColor Yellow
}
else {
    Write-Host "1. Start the server: python backend\app.py" -ForegroundColor Cyan
}

Write-Host "2. Open browser: http://localhost:5000" -ForegroundColor Cyan
Write-Host "3. Upload an image and test the classifier!" -ForegroundColor Cyan
Write-Host ""
Write-Host "For help, check README.md" -ForegroundColor Gray
Write-Host ""
