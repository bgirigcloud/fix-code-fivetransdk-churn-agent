# Deploying Churn Agent to GCP Cloud Run

This guide will help you deploy your Streamlit Churn Prediction Agent to Google Cloud Run.

## Prerequisites

1. **Google Cloud Platform Account**
   - Have a GCP account with billing enabled
   - Your project ID: `hackathon-475722`

2. **Install Google Cloud SDK**
   ```powershell
   # Download from: https://cloud.google.com/sdk/docs/install
   # Or install via Chocolatey:
   choco install gcloudsdk
   ```

3. **Install Docker Desktop**
   ```powershell
   # Download from: https://www.docker.com/products/docker-desktop
   # Or install via Chocolatey:
   choco install docker-desktop
   ```

4. **Authenticate with GCP**
   ```powershell
   gcloud auth login
   gcloud config set project hackathon-475722
   ```

## Deployment Options

### Option 1: Quick Deploy (PowerShell Script - Recommended for Windows)

```powershell
# Navigate to the churn_agent directory
cd churn_agent

# Run the deployment script
.\deploy.ps1
```

**With custom parameters:**
```powershell
.\deploy.ps1 -ProjectId "your-project-id" -Region "us-central1"
```

### Option 2: Manual Deployment Steps

1. **Enable Required APIs**
   ```powershell
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Configure Docker Authentication**
   ```powershell
   gcloud auth configure-docker
   ```

3. **Build Docker Image**
   ```powershell
   docker build -t gcr.io/hackathon-475722/churn-agent:latest .
   ```

4. **Push to Google Container Registry**
   ```powershell
   docker push gcr.io/hackathon-475722/churn-agent:latest
   ```

5. **Deploy to Cloud Run**
   ```powershell
   gcloud run deploy churn-agent `
       --image gcr.io/hackathon-475722/churn-agent:latest `
       --region us-central1 `
       --platform managed `
       --allow-unauthenticated `
       --memory 2Gi `
       --cpu 2 `
       --timeout 300 `
       --max-instances 10
   ```

6. **Get Service URL**
   ```powershell
   gcloud run services describe churn-agent --region us-central1 --format 'value(status.url)'
   ```

### Option 3: Using Cloud Build (CI/CD)

1. **Submit Build to Cloud Build**
   ```powershell
   cd ..  # Go to project root
   gcloud builds submit --config churn_agent/cloudbuild.yaml
   ```

## Configuration

### Environment Variables

You can set environment variables during deployment:

```powershell
gcloud run deploy churn-agent `
    --image gcr.io/hackathon-475722/churn-agent:latest `
    --set-env-vars PROJECT_ID=hackathon-475722,DATASET_ID=saas `
    --region us-central1
```

### Resource Limits

Current configuration:
- **Memory**: 2GB (Streamlit + ML model needs good memory)
- **CPU**: 2 vCPUs (for faster predictions)
- **Timeout**: 300 seconds (5 minutes for SHAP calculations)
- **Max Instances**: 10 (auto-scaling)
- **Min Instances**: 0 (cost-effective, cold starts)

Adjust in `deploy.ps1` or command line as needed.

## Cost Estimation

Cloud Run pricing (as of 2025):
- **CPU**: ~$0.00002400/vCPU-second
- **Memory**: ~$0.00000250/GB-second
- **Requests**: First 2 million requests free per month

**Estimated monthly cost** (with moderate usage):
- ~$10-30/month for occasional usage
- Auto-scales to zero when not in use

## Post-Deployment

### Access Your App
After deployment, you'll receive a URL like:
```
https://churn-agent-XXXXX-uc.a.run.app
```

### View Logs
```powershell
gcloud run services logs read churn-agent --region us-central1
```

### Update Deployment
To update after making changes:
```powershell
.\deploy.ps1
```

### Delete Service (to stop costs)
```powershell
gcloud run services delete churn-agent --region us-central1
```

## Troubleshooting

### Build Fails
- Ensure Docker Desktop is running
- Check internet connection
- Verify GCP authentication: `gcloud auth list`

### Memory Issues
- Increase memory in deployment command:
  ```powershell
  --memory 4Gi
  ```

### Timeout Issues
- Increase timeout:
  ```powershell
  --timeout 600
  ```

### Authentication Issues
```powershell
gcloud auth login
gcloud auth configure-docker
```

### BigQuery Connection Issues
- Ensure the service account has BigQuery permissions
- Add `key.json` to the container or use Workload Identity

## Security

### Using Service Account Key (for BigQuery)

1. **Create Service Account**
   ```powershell
   gcloud iam service-accounts create churn-agent-sa `
       --display-name "Churn Agent Service Account"
   ```

2. **Grant BigQuery Permissions**
   ```powershell
   gcloud projects add-iam-policy-binding hackathon-475722 `
       --member "serviceAccount:churn-agent-sa@hackathon-475722.iam.gserviceaccount.com" `
       --role "roles/bigquery.dataEditor"
   ```

3. **Mount key.json as Secret**
   ```powershell
   # Create secret
   gcloud secrets create bigquery-key --data-file=key.json
   
   # Deploy with secret
   gcloud run deploy churn-agent `
       --image gcr.io/hackathon-475722/churn-agent:latest `
       --update-secrets /app/key.json=bigquery-key:latest
   ```

### Public Access
The deployment script allows unauthenticated access. To require authentication:
```powershell
gcloud run deploy churn-agent --no-allow-unauthenticated
```

## Monitoring

### View Metrics
```powershell
# Open Cloud Console
gcloud run services describe churn-agent --region us-central1
```

Visit: https://console.cloud.google.com/run

## Next Steps

1. ✅ Deploy the application
2. ✅ Test the deployment URL
3. ✅ Set up continuous deployment with Cloud Build
4. ✅ Configure custom domain (optional)
5. ✅ Set up monitoring and alerts

## Support

For issues or questions:
- GCP Cloud Run Docs: https://cloud.google.com/run/docs
- Streamlit Deployment: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app
