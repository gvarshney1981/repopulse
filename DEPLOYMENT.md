# RepoPulse Deployment Guide - Railway

## Quick Deploy to Railway

### Prerequisites
- Railway account (free at [railway.app](https://railway.app))
- Git repository with RepoPulse code

### Deployment Steps

1. **Fork/Clone this repository**
   ```bash
   git clone <your-repo-url>
   cd RepoPulse
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your RepoPulse repository
   - Railway will automatically detect it's a Python app

3. **Configure Environment Variables (Optional)**
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add any custom configuration if needed

4. **Access Your App**
   - Railway will provide a URL like: `https://your-app-name.railway.app`
   - Your RepoPulse will be live at this URL

### What Railway Does Automatically
- ✅ Detects Python application
- ✅ Installs dependencies from `requirements.txt`
- ✅ Uses `gunicorn` to run the app
- ✅ Provides HTTPS automatically
- ✅ Handles scaling and restarts

### Files Used for Deployment
- `app.py` - Entry point for the application
- `requirements.txt` - Python dependencies
- `railway.json` - Railway-specific configuration
- `Procfile` - Alternative deployment configuration

### Troubleshooting
- Check Railway logs if deployment fails
- Ensure all dependencies are in `requirements.txt`
- Verify `app.py` imports the Flask app correctly

### Custom Domain (Optional)
- In Railway dashboard, go to "Settings"
- Add custom domain under "Domains" section
- Configure DNS as instructed

## Local Testing Before Deploy
```bash
pip install -r requirements.txt
python app.py
```

Your app should be ready for Railway deployment! 🚀 