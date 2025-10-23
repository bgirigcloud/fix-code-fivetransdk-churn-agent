# 🚀 Cloud Run Deployment - Complete Guide

Your Streamlit Churn Prediction Agent is ready to deploy to Google Cloud Run!

## 📁 Files Created

- ✅ **Dockerfile** - Container configuration
- ✅ **deploy.ps1** - PowerShell deployment script (Windows)
- ✅ **deploy.sh** - Bash deployment script (Linux/Mac)
- ✅ **cloudbuild.yaml** - CI/CD configuration
- ✅ **.dockerignore** - Files to exclude from container
- ✅ **.streamlit/config.toml** - Streamlit configuration
- ✅ **DEPLOYMENT.md** - Detailed deployment guide
- ✅ **QUICKSTART.md** - Quick start guide
- ✅ **test_docker.ps1** - Local Docker testing script

## 🎯 Choose Your Deployment Method

### Method 1: One-Command Deploy (Easiest) ⭐
```powershell
cd churn_agent
.\deploy.ps1
```

### Method 2: Test Locally First
```powershell
cd churn_agent
.\test_docker.ps1
# Then deploy
.\deploy.ps1
```

### Method 3: Manual Step-by-Step
See `DEPLOYMENT.md` for complete instructions

## 📋 Prerequisites

1. **Google Cloud SDK** - [Install here](https://cloud.google.com/sdk/docs/install)
2. **Docker Desktop** - [Install here](https://www.docker.com/products/docker-desktop)
3. **GCP Project** - You already have `hackathon-475722`

## ⚡ Quick Setup (First Time)

```powershell
# 1. Install gcloud (if not installed)
# Download from: https://cloud.google.com/sdk/docs/install

# 2. Login to GCP
gcloud auth login

# 3. Set your project
gcloud config set project hackathon-475722

# 4. Configure Docker
gcloud auth configure-docker

# 5. Deploy!
cd churn_agent
.\deploy.ps1
```

## 🎉 What You Get

After deployment:
- ✅ **Public URL**: `https://churn-agent-xxxxx-uc.a.run.app`
- ✅ **Auto-scaling**: 0 to 10 instances
- ✅ **HTTPS**: Automatic SSL certificate
- ✅ **Load balancing**: Built-in
- ✅ **Monitoring**: In GCP Console
- ✅ **Pay-per-use**: Only pay when active

## 💡 Usage

1. **Access your app**: Visit the URL provided after deployment
2. **Make predictions**: Use the manual input form or upload CSV
3. **View explanations**: See SHAP waterfall plots
4. **Monitor**: Check logs and metrics in GCP Console

## 🔄 Update Your App

Made changes? Just redeploy:
```powershell
.\deploy.ps1
```

Cloud Run handles zero-downtime updates automatically!

## 💰 Estimated Costs

- **Minimal usage**: ~$5-10/month
- **Moderate usage**: ~$10-30/month  
- **Scales to zero**: No cost when idle
- **First 2M requests**: Free per month

## 📊 Monitor Your App

```powershell
# View logs
gcloud run services logs read churn-agent --region us-central1 --limit 50

# View in browser
# Visit: https://console.cloud.google.com/run?project=hackathon-475722
```

## 🐛 Troubleshooting

### Docker not running?
Start Docker Desktop and wait for it to be ready.

### Authentication issues?
```powershell
gcloud auth login
gcloud auth configure-docker
```

### Build fails?
Check `DEPLOYMENT.md` troubleshooting section.

### Need more memory?
Edit `deploy.ps1` and change `--memory 4Gi`

## 📚 Documentation

- **Quick Start**: See `QUICKSTART.md`
- **Detailed Guide**: See `DEPLOYMENT.md`
- **Test Docker**: Run `.\test_docker.ps1`

## 🔗 Useful Commands

```powershell
# Deploy
.\deploy.ps1

# Test locally
.\test_docker.ps1

# View logs
gcloud run services logs read churn-agent

# Delete service
gcloud run services delete churn-agent --region us-central1

# View service details
gcloud run services describe churn-agent --region us-central1
```

## ✅ Deployment Checklist

- [ ] Google Cloud SDK installed
- [ ] Docker Desktop installed and running
- [ ] Authenticated with GCP (`gcloud auth login`)
- [ ] Docker configured (`gcloud auth configure-docker`)
- [ ] In correct directory (`cd churn_agent`)
- [ ] Run deployment (`.\deploy.ps1`)
- [ ] Test the URL provided
- [ ] Share with your team! 🎉

## 🎓 Next Steps

1. ✅ Deploy to Cloud Run
2. ✅ Test your app
3. ✅ Configure custom domain (optional)
4. ✅ Set up CI/CD with Cloud Build
5. ✅ Add monitoring alerts
6. ✅ Scale as needed

## 📞 Support

- **Cloud Run Issues**: https://cloud.google.com/run/docs
- **Streamlit Issues**: https://docs.streamlit.io
- **Check logs**: `gcloud run services logs read churn-agent`

---

**Ready to deploy?** Just run:
```powershell
cd churn_agent
.\deploy.ps1
```

🚀 Your app will be live in ~5 minutes!
