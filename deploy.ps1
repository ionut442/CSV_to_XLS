# CSV Merge Wizard - Vercel Deployment Script (PowerShell)

Write-Host "🚀 Preparing CSV Merge Wizard for Vercel deployment..." -ForegroundColor Green

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version 2>$null
    Write-Host "✅ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if all required files exist
$requiredFiles = @("main.py", "requirements.txt", "vercel.json", "index.html")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Required file missing: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Test the application
Write-Host "🧪 Testing application..." -ForegroundColor Yellow
try {
    python -c "import main; print('✅ Application imports successfully')"
    Write-Host "✅ Application test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Application test failed" -ForegroundColor Red
    exit 1
}

# Deploy to Vercel
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Yellow
vercel --prod

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your application should now be live on Vercel" -ForegroundColor Cyan 