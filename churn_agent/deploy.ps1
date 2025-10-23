# PowerShell Deployment script for GCP Cloud Run
# Usage: .\deploy.ps1 [-ProjectId "your-project-id"] [-Region "us-central1"]

param(
    [string]$ProjectId = "hackathon-475722",
    [string]$Region = "us-central1",
    [string]$ServiceName = "churn-agent"
)

$ErrorActionPreference = "Stop"

$ImageName = "gcr.io/$ProjectId/$ServiceName"

Write-Host "=========================================="
Write-Host "Deploying Churn Agent to GCP Cloud Run"
Write-Host "=========================================="
Write-Host "Project ID: $ProjectId"
Write-Host "Region: $Region"
Write-Host "Service Name: $ServiceName"
Write-Host ""

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "ERROR: gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set the project
Write-Host "Setting GCP project..."
gcloud config set project $ProjectId

# Enable required APIs
Write-Host ""
Write-Host "Enabling required GCP APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Authenticate Docker with GCP
Write-Host ""
Write-Host "Configuring Docker authentication..."
gcloud auth configure-docker --quiet

# Build the Docker image
Write-Host ""
Write-Host "Building Docker image..."
docker build -t "${ImageName}:latest" .

# Push to Google Container Registry
Write-Host ""
Write-Host "Pushing image to Google Container Registry..."
docker push "${ImageName}:latest"

# Deploy to Cloud Run
Write-Host ""
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $ServiceName `
    --image "${ImageName}:latest" `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 0 `
    --set-env-vars "PROJECT_ID=$ProjectId"

# Get the service URL
Write-Host ""
Write-Host "=========================================="
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================="
$ServiceUrl = gcloud run services describe $ServiceName --region $Region --format 'value(status.url)'
Write-Host "Service URL: $ServiceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now access your Churn Prediction Agent at the URL above!" -ForegroundColor Green
