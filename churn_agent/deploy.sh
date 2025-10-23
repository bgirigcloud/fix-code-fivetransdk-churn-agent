#!/bin/bash

# Deployment script for GCP Cloud Run
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Configuration
PROJECT_ID="${1:-hackathon-475722}"
REGION="${2:-us-central1}"
SERVICE_NAME="churn-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=========================================="
echo "Deploying Churn Agent to GCP Cloud Run"
echo "=========================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service Name: ${SERVICE_NAME}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo "Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo ""
echo "Enabling required GCP APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image
echo ""
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Push to Google Container Registry
echo ""
echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars PROJECT_ID=${PROJECT_ID}

# Get the service URL
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "You can now access your Churn Prediction Agent at the URL above!"
