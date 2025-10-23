# Test Docker Build Locally
# This script tests if the Docker image builds correctly

Write-Host "=========================================="
Write-Host "Testing Docker Build for Cloud Run"
Write-Host "=========================================="
Write-Host ""

$ImageName = "churn-agent:test"

# Check Docker is running
Write-Host "1. Checking Docker status..."
try {
    docker ps | Out-Null
    Write-Host "   ✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Docker is not running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again"
    exit 1
}

# Build the image
Write-Host ""
Write-Host "2. Building Docker image..."
Write-Host "   This may take a few minutes on first build..."
try {
    docker build -t $ImageName . 2>&1 | Out-Default
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Build successful" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "   ✗ Build failed" -ForegroundColor Red
    exit 1
}

# Check image size
Write-Host ""
Write-Host "3. Checking image size..."
$ImageSize = docker images $ImageName --format "{{.Size}}"
Write-Host "   Image size: $ImageSize"

# Test container startup
Write-Host ""
Write-Host "4. Testing container startup..."
Write-Host "   Starting container on port 8080..."
Write-Host "   Press Ctrl+C to stop after verifying it works"
Write-Host ""

docker run --rm -p 8080:8080 $ImageName
