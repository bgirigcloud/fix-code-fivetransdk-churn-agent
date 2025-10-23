# Quick Start: Deploy to GCP Cloud Run

## 🚀 Quick Deployment (5 minutes)

### Step 1: Prerequisites Check
```powershell
# Check if gcloud is installed
gcloud --version

# Check if Docker is running
docker --version

# Login to GCP
gcloud auth login
gcloud auth configure-docker
```

### Step 2: Deploy
```powershell
# Navigate to churn_agent directory
cd churn_agent

# Run deployment script
.\deploy.ps1
```

That's it! You'll get a URL like: `https://churn-agent-xxxxx-uc.a.run.app`

---

## 📋 Detailed Steps

### 1. Install Prerequisites (First Time Only)

**Google Cloud SDK:**
- Download: https://cloud.google.com/sdk/docs/install
- Or via Chocolatey: `choco install gcloudsdk`

**Docker Desktop:**
- Download: https://www.docker.com/products/docker-desktop
- Or via Chocolatey: `choco install docker-desktop`

### 2. Authenticate with GCP
```powershell
gcloud auth login
gcloud config set project hackathon-475722
gcloud auth configure-docker
```

### 3. Deploy
```powershell
# Option A: Use the PowerShell script (easiest)
.\deploy.ps1

# Option B: Manual deployment
docker build -t gcr.io/hackathon-475722/churn-agent:latest .
docker push gcr.io/hackathon-475722/churn-agent:latest
gcloud run deploy churn-agent --image gcr.io/hackathon-475722/churn-agent:latest --region us-central1 --allow-unauthenticated --memory 2Gi --cpu 2
```

### 4. Test Locally First (Optional)
```powershell
# Build Docker image
docker build -t churn-agent:local .

# Run locally
docker run -p 8080:8080 churn-agent:local

# Open browser to http://localhost:8080
```

---

## 🔧 Customization

### Change Region
```powershell
.\deploy.ps1 -Region "europe-west1"
```

### Increase Resources
Edit `deploy.ps1` and change:
```powershell
--memory 4Gi
--cpu 4
```

### Add Environment Variables
```powershell
gcloud run deploy churn-agent --set-env-vars "VAR1=value1,VAR2=value2"
```

---

## 💰 Cost

- **Pay only for actual usage**
- Scales to zero when not in use
- Estimated: $10-30/month for moderate usage
- First 2 million requests/month are free

---

## 📊 Monitor Your App

### View Logs
```powershell
gcloud run services logs read churn-agent --region us-central1 --limit 50
```

### View in Console
https://console.cloud.google.com/run?project=hackathon-475722

### View Metrics
- Requests per second
- Response times
- Error rates
- Container instances

---

## 🐛 Troubleshooting

### "Docker is not running"
- Start Docker Desktop
- Wait for it to fully start
- Try again

### "Permission denied"
```powershell
gcloud auth login
gcloud auth configure-docker
```

### "Out of memory"
```powershell
.\deploy.ps1
# Then increase memory in Cloud Console or redeploy with --memory 4Gi
```

### "Build failed"
```powershell
# Check Docker is running
docker ps

# Check internet connection
ping google.com

# Try building locally first
docker build -t test .
```

---

## 🔄 Update Deployment

After making code changes:
```powershell
.\deploy.ps1
```

Cloud Run automatically handles:
- Zero-downtime deployment
- Traffic migration
- Rollback if needed

---

## 🗑️ Cleanup

### Stop Service (to save costs)
```powershell
gcloud run services delete churn-agent --region us-central1
```

### Delete Container Images
```powershell
gcloud container images delete gcr.io/hackathon-475722/churn-agent:latest
```

---

## ✅ What Gets Deployed

- ✅ Streamlit app
- ✅ Trained ML model
- ✅ All Python dependencies
- ✅ Auto-scaling (0-10 instances)
- ✅ HTTPS endpoint
- ✅ Load balancing
- ✅ Health checks

---

## 🔗 Useful Links

- **Your GCP Console**: https://console.cloud.google.com/run?project=hackathon-475722
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Streamlit Docs**: https://docs.streamlit.io

---

## 📞 Need Help?

Check `DEPLOYMENT.md` for detailed documentation.
