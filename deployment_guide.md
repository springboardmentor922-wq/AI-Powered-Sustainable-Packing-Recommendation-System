# 🚀 EcoPackAI - Complete Setup & Deployment Guide

## 📌 Overview

This guide covers:
1. **Local Development** - Running on your machine
2. **Session Limits** - How the 3 recommendations/hour works
3. **CMD Operations** - All command-line instructions
4. **Deployment** - Publishing to production

---

## 🏠 LOCAL DEVELOPMENT SETUP

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Web browser**
- **Terminal/Command Prompt**

---

### Step 1: Backend Setup

**1.1 Navigate to backend folder**

```bash
cd backend
```

**1.2 Create Virtual Environment**

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal.

**1.3 Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required packages:**
```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
python-dotenv==1.0.0
reportlab==4.0.7
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
xgboost==2.0.2
```

**1.4 Create .env File**

Create `backend/.env`:

```env
# Flask Secret Key (REQUIRED)
APP_SECRET_KEY=your-secret-key-here

# MySQL (OPTIONAL - commented out in code)
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your-password
# DB_NAME=ecopackdb
```

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy output to `APP_SECRET_KEY`.

**1.5 Start Backend Server**

```bash
python app.py
```

**Expected Output:**
```
🌱 EcoPackAI Backend Starting
✅ ML Engine: Available (or Mock Mode)
🔒 Session Limit: 3 recommendations per hour
🚫 Login: Disabled (commented out)
 * Running on http://0.0.0.0:5000
```

**Keep this terminal running!**

---

### Step 2: Frontend Setup

**2.1 Open NEW Terminal**

Navigate to frontend:

```bash
cd frontend
```

**2.2 Start Frontend Server**

**Option A - Python HTTP Server (Recommended):**

**Windows:**
```cmd
python -m http.server 3000
```

**Mac/Linux:**
```bash
python3 -m http.server 3000
```

**Option B - VS Code Live Server:**
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

**Expected Output:**
```
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
```

**Keep this terminal running!**

**2.3 Open in Browser**

Navigate to: **http://localhost:3000**

---

## 🔒 HOW SESSION LIMITS WORK

### The 3 Recommendations Per Hour System

**How It Works:**

1. **First Visit:**
   - System creates a session with unique ID
   - Counter starts at 0/3
   - Session valid for 1 hour

2. **Generate Recommendations:**
   - Counter increments: 1/3, 2/3, 3/3
   - Each generation uses 1 quota

3. **Limit Reached:**
   - After 3 generations, you get:
   ```
   "Limit reached: 3 recommendations per hour. Try again in X minutes."
   ```

4. **Reset:**
   - After 1 hour, counter resets to 0/3
   - You can generate 3 more recommendations

### How to Check Your Quota

**Method 1 - UI Display:**

Add this to your `index.html` (inside `<header>` or `<nav>`):

```html
<div id="sessionInfo" class="session-info"></div>
```

The frontend automatically shows:
```
📊 Recommendations: 2/3 used | 1 remaining
```

**Method 2 - API Call:**

```bash
curl http://localhost:5000/api/auth/status
```

**Response:**
```json
{
  "authenticated": true,
  "session_id": "abc123...",
  "recommendations_used": 2,
  "recommendations_remaining": 1
}
```

### How to Reset Session (for Testing)

**Method 1 - Clear Browser Cookies:**
1. Open Developer Tools (F12)
2. Go to Application → Cookies
3. Delete `session` cookie
4. Refresh page

**Method 2 - Incognito/Private Window:**
- Opens new session automatically
- Fresh 3/3 quota

**Method 3 - Wait 1 Hour:**
- Session auto-expires
- Counter resets

### Customizing Session Limits

**Change limit from 3 to 5:**

Edit `backend/app.py`:

```python
# Line ~95
def check_recommendation_limit():
    # ...
    if count >= 5:  # Changed from 3 to 5
        # ...
```

**Change timeout from 1 hour to 2 hours:**

Edit `backend/app.py`:

```python
# Line ~51
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)  # Changed

# Line ~99
if session_age > timedelta(hours=2):  # Changed
```

---

## 💻 CMD OPERATIONS GUIDE

### Backend Operations

**Start Backend:**
```bash
cd backend
python app.py
```

**Stop Backend:**
- Press `Ctrl+C` in terminal

**Check if Backend Running:**
```bash
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "ml_available": true,
  "materials_loaded": 15,
  "session_limit": "3 recommendations per hour"
}
```

**View Backend Logs:**
- Logs appear in the terminal where you ran `python app.py`
- Look for:
  - `✅` = Success
  - `⚠️` = Warning
  - `❌` = Error

**Test Recommendation API:**

```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "Category_item": "Electronics",
    "Weight_kg": 2.5,
    "Fragility": 3,
    "Moisture_Sens": false,
    "Distance_km": 500,
    "Shipping_Mode": "Road",
    "Length_cm": 30,
    "Width_cm": 20,
    "Height_cm": 15,
    "top_k": 5,
    "sort_by": "Sustainability"
  }'
```

---

### Frontend Operations

**Start Frontend:**
```bash
cd frontend
python -m http.server 3000
```

**Stop Frontend:**
- Press `Ctrl+C` in terminal

**Change Port (if 3000 is busy):**
```bash
python -m http.server 8080  # Use port 8080 instead
```

Then update `frontend/js/app.js`:
```javascript
// Change localhost:3000 references to localhost:8080
```

**Test Frontend Access:**
```bash
curl http://localhost:3000
```

Should return HTML of your page.

---

### Common CMD Issues

**Problem: "Port 5000 already in use"**

**Windows:**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**Mac/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
```

**Problem: "Python not found"**

Try:
```bash
python3 app.py  # Use python3 instead
```

**Problem: "Module not found"**

```bash
# Ensure venv is activated
pip install -r requirements.txt
```

---

## 🌐 DEPLOYMENT GUIDE

### Option 1: Deploy to Render.com

**Step 1: Prepare Backend**

**1.1 Create `requirements.txt`** (already have this)

**1.2 Create `render.yaml`:**

```yaml
services:
  - type: web
    name: ecopackai-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: APP_SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.10.0
```

**1.3 Add gunicorn to requirements:**

```bash
pip install gunicorn
pip freeze > requirements.txt
```

**Step 2: Deploy Backend**

1. Go to https://render.com
2. Sign up / Login
3. Click **New** → **Web Service**
4. Connect your GitHub repo
5. Select `backend` folder
6. Click **Create Web Service**
7. Copy your URL: `https://your-app.onrender.com`

**Step 3: Update Frontend**

Edit `frontend/js/app.js`:

```javascript
const CONFIG = {
    API_URL: 'https://your-app.onrender.com',  // Your Render URL
    // ...
};
```

**Step 4: Deploy Frontend to Netlify**

1. Go to https://netlify.com
2. Drag `frontend` folder to Netlify
3. Your site is live at: `https://your-site.netlify.app`

**Step 5: Update CORS**

Edit `backend/app.py`:

```python
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "https://your-site.netlify.app"  # Add your Netlify URL
])
```

Redeploy backend.

---

### Option 2: Deploy to Vercel

**Backend (using Vercel Serverless):**

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

**Deploy:**
```bash
vercel --prod
```

**Frontend:**

```bash
cd frontend
vercel --prod
```

---

### Option 3: Deploy to Heroku

**Backend:**

Create `Procfile`:
```
web: gunicorn app:app
```

**Deploy:**
```bash
heroku login
heroku create ecopackai-backend
git push heroku main
```

**Frontend:**

Deploy to Netlify or Vercel (as above).

---

## 🔧 TROUBLESHOOTING

### Backend Won't Start

**Check 1: Python Version**
```bash
python --version  # Should be 3.8+
```

**Check 2: Dependencies**
```bash
pip install -r requirements.txt
```

**Check 3: Port Conflict**
```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000   # Windows
```

**Check 4: .env File**
```bash
# Ensure .env exists
ls -la .env  # Mac/Linux
dir .env     # Windows
```

---

### Frontend Can't Connect

**Check 1: Backend Running**
```bash
curl http://localhost:5000/api/health
```

**Check 2: CORS Settings**

Verify `app.py` has:
```python
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",  # Live Server
    "http://127.0.0.1:5500"
])
```

**Check 3: API URL**

Verify `frontend/js/app.js`:
```javascript
API_URL: 'http://localhost:5000'
```

---

### Session Limit Not Working

**Check 1: Cookies Enabled**
- Browser must allow cookies
- Check in incognito mode

**Check 2: Server Logs**

Look for:
```
🆕 New session created: abc123...
📊 Session abc123: 1/3 used, 2 remaining
```

**Check 3: Test Session API**

```bash
curl -c cookies.txt http://localhost:5000/api/auth/status
curl -b cookies.txt -X POST http://localhost:5000/api/recommend ...
```

---

## 📊 MONITORING & LOGS

### View Session Activity

**Backend logs show:**
```
🆕 New session created: abc123
📊 Session abc123: 1/3 used, 2 remaining
📊 Session abc123: 2/3 used, 1 remaining
📊 Session abc123: 3/3 used, 0 remaining
🔄 Session reset: abc123
```

### Health Check Endpoint

```bash
curl http://localhost:5000/api/health
```

**Returns:**
```json
{
  "status": "healthy",
  "ml_available": true,
  "materials_loaded": 15,
  "timestamp": "2024-02-09T10:30:00",
  "session_limit": "3 recommendations per hour"
}
```

---

## 🎯 QUICK REFERENCE

### Start Both Servers (Windows)

**Terminal 1 - Backend:**
```cmd
cd backend
venv\Scripts\activate
python app.py
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
python -m http.server 3000
```

### Start Both Servers (Mac/Linux)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python3 -m http.server 3000
```

### URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/api/health
- **Session Status:** http://localhost:5000/api/auth/status

---

## 📝 SUMMARY

✅ **Login:** Commented out (not required)
✅ **Session Limits:** 3 recommendations per hour
✅ **Reset:** Automatic after 1 hour
✅ **Backend:** Flask on port 5000
✅ **Frontend:** Python HTTP server on port 3000
✅ **Deployment:** Render.com (backend) + Netlify (frontend)

---

**Need Help?**

- Check logs in terminal
- Use `curl` to test endpoints
- Clear browser cookies/cache
- Restart both servers

**Your EcoPackAI is ready to use! 🌱**