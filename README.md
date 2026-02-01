# 🌱 EcoPackAI
## AI‑Powered Sustainable Packaging Recommendation System

---

## 📌 What is EcoPackAI?

EcoPackAI is a **simple AI-based decision system** that helps you choose the **best packaging material** for a shipment based on:

- Cost 💰  
- CO₂ emissions 🌍  
- Sustainability 🌱  

You **do NOT choose the packaging material** yourself.  
The system **predicts and recommends** the best options automatically.

---

## 🧠 How the System Works (In Simple Words)

1. You enter shipment details (weight, size, distance, etc.)  
2. The system:
   - Tests your shipment against many packaging materials
   - Predicts cost and CO₂ for each
3. It ranks materials using a sustainability score  
4. You see **Top Recommended Packaging Materials**

No ML knowledge required.

---

## 🧱 Project Structure

```
ecopackai-clean/
├── backend/
│   └── app.py                      # Flask API + ML integration (500 lines)
├── frontend/
│   ├── index.html                  # Main UI (clean, modern)
│   ├── css/
│   │   └── styles.css              # Beautiful styling (1000+ lines)
│   └── js/
│       └── app.js                  # Frontend logic (600 lines)
├── ml/                             # ⬅️ YOUR ML MODELS GO HERE
│   └── models/
│       ├── cost_model.pkl          # (Optional) Your trained model
│       └── co2_model.pkl           # (Optional) Your trained model
├── data/                           # ⬅️ YOUR DATASET GOES HERE
│   └── processed/
│       └── final_ecopack_dataset_fe.csv  # (Optional) Your data
├── .env                            # ⬅️ Environment variables (REQUIRED)
├── requirements.txt                # ⬅️ Python dependencies
├── README.md                       # This file
├── SETUP.md                        # Complete setup commands
└── QUICKSTART.md                   # 2-minute start guide
```

> 🔹 **Backend**: Flask API (Python)  
> 🔹 **Frontend**: Pure HTML/CSS/JavaScript (no frameworks!)  
> 🔹 **Authentication**: Simple session-based (no OAuth complexity)  
> 🔹 **ML Integration**: Auto-loads your models OR uses mock data

---

## 🏗️ System Architecture 

```
┌─────────────────────────────────────────────────────────────────┐
│                      🌱 EcoPackAI System                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│   HTML/CSS/JS    │◄────────►│   Flask Backend  │
│   Frontend       │   HTTP   │   (Port 5000)    │
│  localhost:3000  │          │                  │
└──────────────────┘          └─────────┬────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
              ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
              │  Session  │      │   Your    │      │    ML     │
              │   Data    │      │  Dataset  │      │  Models   │
              │ In-Memory │      │   .csv    │      │   .pkl    │
              └───────────┘      └───────────┘      └───────────┘
```

**Flow:**
1. User opens browser → HTML/CSS/JS loads
2. Frontend sends API request to Flask backend
3. Backend validates session → Loads ML models
4. ML models predict cost/CO₂ for materials
5. Backend returns top recommendations
6. Frontend displays results + PDF download option

---

## ⚙️ How to Set Up EcoPackAI (Complete Guide)

### 🎯 Prerequisites

- **Python 3.8+** installed
- **Web browser** (Chrome, Firefox, Safari, Edge)
- **Terminal/Command Prompt**

That's it! No database setup, no OAuth, no complexity.

---

### ✅ Step 1: Download the Project

Extract the ZIP file or navigate to project:

```bash
cd ecopackai-clean
```

---

### ✅ Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal.

---

### ✅ Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (cross-origin requests)
- Flask-Limiter (rate limiting)
- Pandas, NumPy (data processing)
- Scikit-learn, XGBoost (ML models)
- ReportLab (PDF generation)
- Gunicorn (production server)

---

### ✅ Step 4: Generate Secret Key

Run this command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
k3vX9pLmQ7rT2nB8jH4yF6wD1sA5zE0cU
```

Copy this key!

---

### ✅ Step 5: Create .env File

Create a `.env` file in the project root:

```env
# REQUIRED
SECRET_KEY=paste-your-key-from-step-4-here

# Optional - Only if you have your own ML models
DATASET_PATH=data/processed/final_ecopack_dataset_fe.csv
ML_MODELS_PATH=ml/models
```

---

## 🚀 Running EcoPackAI

### Terminal 1: Start Backend

```bash
cd backend
python app.py
```

**Expected output:**
```
🌱 EcoPackAI Backend Starting...
✅ ML Models: True
✅ Materials: 15
📚 Health: http://localhost:5000/api/health
 * Running on http://0.0.0.0:5000
```

**Leave this running!**

---

### Terminal 2: Start Frontend

**Mac/Linux:**
```bash
cd frontend
python3 -m http.server 3000
```

**Windows:**
```bash
cd frontend
python -m http.server 3000
```

---

### Open Browser

Go to: **http://localhost:3000**

---

## 📍 Where to Update URLs

### For Local Development
✅ **Nothing to change!** Works immediately.

### For Deployment

**1. Frontend** (`frontend/js/app.js` line 6):
```javascript
const API_URL = 'https://YOUR-BACKEND.onrender.com';  // ← UPDATE
```

**2. Backend** (`backend/app.py` line 35):
```python
CORS(app, origins=[
    'http://localhost:3000',
    'https://YOUR-FRONTEND.netlify.app'  # ← ADD
])
```

---

## 🧠 ML Models

### Without Your Models (Works Immediately!)
- Uses intelligent mock data
- 15 realistic materials
- Perfect for testing

### With Your Models
1. Place models in `ml/models/`:
   - `cost_model.pkl`
   - `co2_model.pkl`

2. Place dataset in `data/processed/`:
   - `final_ecopack_dataset_fe.csv`

3. Update `.env`

4. Restart backend

5. **Customize `backend/app.py` line 150** to match your features!

---

## 🌐 Deployment

### Backend → Render.com
1. Push to GitHub
2. Create Web Service
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn backend.app:app`
5. Add env: `SECRET_KEY`

### Frontend → Netlify.com
1. Update API_URL in `frontend/js/app.js`
2. Drag `frontend` folder to Netlify
3. Update CORS in backend
4. Done!

---

## 🐛 Troubleshooting

**Backend won't start:**
```bash
# Check virtual environment is activated
pip install -r requirements.txt
```

**Frontend can't connect:**
```bash
# Check backend is running
curl http://localhost:5000/api/health
```

**CORS error:**
```python
# Add your URL to backend/app.py line 35
```

---

## 📚 Complete Documentation

- **README.md** - This file (overview)
- **SETUP.md** - All commands reference
- **QUICKSTART.md** - 2-minute start guide
- **Code comments** - Extensive in all files

---

**🌱 Start Now:** Open **QUICKSTART.md** for fastest setup! 🚀

# 🌱 EcoPackAI - MySQL Edition
## AI-Powered Sustainable Packaging with Complete Authentication

---

## 🎯 What's New in This Version?

✅ **MySQL Database** - Full database integration  
✅ **Email/Password Authentication** - Secure login system  
✅ **Bcrypt Hashing** - Password security  
✅ **3-Attempt Lockout** - Account protection  
✅ **Recommendation History** - All queries saved to MySQL  
✅ **Fixed Sorting** - Properly sorts by Sustainability/CO₂/Cost  
✅ **Fixed UI Colors** - Best recommendation card matches theme  
✅ **Session Management** - Secure user sessions  

---

## 📁 Project Structure

```
ecopackai-mysql/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── auth.py                 # Authentication logic (bcrypt + lockout)
│   ├── db.py                   # MySQL connection
│   ├── recommender.py          # ML wrapper + history saver
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (CREATE THIS)
│   └── .env.example            # Template
├── frontend/
│   ├── login.html              # Login page
│   ├── index.html              # Main app (copy from uploads)
│   ├── css/
│   │   ├── login.css           # Login page styles
│   │   └── styles.css          # Main app styles (copy from uploads)
│   └── js/
│       ├── login.js            # Login logic
│       └── app.js              # Main app logic
├── ml/
│   └── notebooks/
│       └── recommendation_engine.py  # Your ML engine
├── sql/
│   └── schema.sql              # Database schema
└── README.md                   # This file
```

---

## 🚀 Complete Setup Guide

### Step 1: MySQL Setup

**1.1 Install MySQL** (if not installed)

**1.2 Create Database**

```bash
# Login to MySQL
mysql -u root -p

# Run the schema
source sql/schema.sql
```

**Or manually:**

```sql
CREATE DATABASE IF NOT EXISTS ecopackdb;
USE ecopackdb;

-- Run the contents of sql/schema.sql
```

**1.3 Verify Tables**

```sql
SHOW TABLES;
-- Should show: users, recommendation_history

SELECT * FROM users;
-- Should show test@ecopackai.com
```

---

### Step 2: Backend Setup

**2.1 Create Virtual Environment**

```bash
cd backend
python -m venv venv

# Activate
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

**2.2 Install Dependencies**

```bash
pip install -r requirements.txt
```

**2.3 Create .env File**

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

**Edit `.env`:**

```env
APP_SECRET_KEY=Uh84IqEQ_5duV4R3d2glAW8-zcDp8veSlkWsJZWBM-s

DB_HOST=localhost
DB_PORT=3306
DB_USER=ecopackai
DB_PASSWORD=Yawalkarag@21       # YOUR ACTUAL PASSWORD
DB_NAME=ecopackdb

FLASK_ENV=development
```

**2.4 Test Database Connection**

```bash
python db.py
```

Expected: `✅ Database connection successful!`

**2.5 Start Backend**

```bash
python app.py
```

Expected:
```
🌱 EcoPackAI Backend Starting...
✅ MySQL connected
📚 API: http://localhost:5000/api/health
 * Running on http://0.0.0.0:5000
```

---

### Step 3: Add Your ML Engine

**3.1 Copy Your ML Files**

```bash
# Copy your recommendation_engine.py
cp /path/to/your/recommendation_engine.py ml/notebooks/
```

**3.2 Verify it has these exports:**

```python
# ml/notebooks/recommendation_engine.py should export:
- generate_recommendations
- materials_df
- co2_model
- cost_model
- FEATURES_COST
- FEATURES_CO2
```

---

### Step 4: Frontend Setup

**4.1 Copy Missing Files**

Copy these from your uploads:
- `index.html` → `frontend/index.html`
- `styles.css` → `frontend/css/styles.css`

**4.2 Start Frontend**

```bash
cd frontend

# Option 1: Python HTTP Server
python -m http.server 3000

# Option 2: Live Server (VS Code extension)
# Right-click index.html → "Open with Live Server"
```

---

## 🔐 Authentication Flow

### First-Time Login

1. User enters email: `test@ecopackai.com`
2. User enters any password: `mypassword123`
3. System **hashes and stores** the password
4. User is logged in ✅

### Subsequent Logins

1. User enters email: `test@ecopackai.com`
2. User enters password: `mypassword123`
3. System **verifies hash**
4. User is logged in ✅

### Failed Attempts

1. Wrong password attempt 1: ⚠️ 2 attempts remaining
2. Wrong password attempt 2: ⚠️ 1 attempt remaining
3. Wrong password attempt 3: 🔒 **ACCESS DENIED**
   - Login form disappears
   - Red X and "ACCESS DENIED" message shown
   - Account locked in database

### Unlock Account

```sql
-- Run in MySQL
UPDATE users SET is_locked = FALSE, failed_attempts = 0 WHERE email = 'test@ecopackai.com';
```

---

## 🎯 Using the App

### 1. Open Login Page

```
http://localhost:3000/login.html
```

### 2. Login

- Email: `test@ecopackai.com`
- Password: (any password for first time)

### 3. Use Main App

- Fill in shipment details
- Choose optimization goal (🌱 Sustainability / 🌍 CO₂ / 💰 Cost)
- Click "Generate AI Recommendations"
- View results (properly sorted!)
- Download PDF

### 4. Check History

All recommendations are saved to MySQL:

```sql
SELECT * FROM recommendation_history;
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error: "MySQL connection failed"**

```bash
# Check MySQL is running
mysql -u root -p

# Verify credentials in .env
# Test connection
python db.py
```

**Error: "Module not found"**

```bash
pip install -r requirements.txt
```

### Frontend Won't Connect

**CORS Error**

Update `backend/app.py` line 40:

```python
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:5500",  # Add Live Server port
])
```

### Sorting Not Working

✅ **FIXED!** The backend now properly sorts by the selected criterion.

Verify in `backend/recommender.py` line 50:
```python
sort_by=sort_by  # This is now passed correctly
```

### Best Card Color Wrong

✅ **FIXED!** Update `frontend/css/styles.css`:

```css
.best-recommendation-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    /* Now matches dark theme */
}
```

---

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255),           -- Bcrypt hash
    failed_attempts INT DEFAULT 0,        -- Track attempts
    is_locked BOOLEAN DEFAULT FALSE,      -- Lock after 3 fails
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```

### Recommendation History Table

```sql
CREATE TABLE recommendation_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    session_id VARCHAR(100),
    created_at TIMESTAMP,
    
    -- Shipment details
    product_category VARCHAR(100),
    weight_kg FLOAT,
    fragility INT,
    shipping_mode VARCHAR(50),
    distance_km FLOAT,
    moisture_sensitive BOOLEAN,
    length_cm FLOAT,
    width_cm FLOAT,
    height_cm FLOAT,
    
    -- Request params
    k_value INT,
    sort_by VARCHAR(50),
    
    -- Results (JSON)
    recommendations JSON,
    
    FOREIGN KEY (email) REFERENCES users(email)
);
```

---

## 🔧 Configuration

### Change Session Timeout

`backend/app.py` line 24:

```python
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)  # 1 hour
```

### Change Lockout Attempts

`backend/auth.py` line 15:

```python
MAX_ATTEMPTS = 5  # Allow 5 attempts instead of 3
```

### Add More Test Users

```sql
INSERT INTO users (email, password_hash, failed_attempts, is_locked)
VALUES ('user@example.com', NULL, 0, FALSE);
```

---

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login (sets password on first login) |
| `/api/auth/logout` | POST | Logout |
| `/api/auth/status` | GET | Check if authenticated |
| `/api/recommend` | POST | Generate recommendations |
| `/api/history` | GET | Get user history |
| `/api/generate-pdf` | POST | Download PDF report |
| `/api/health` | GET | Health check |

---

## ✅ Features Checklist

- [x] MySQL database integration
- [x] Email/password authentication
- [x] Bcrypt password hashing
- [x] 3-attempt account lockout
- [x] First-time password setup
- [x] Session management
- [x] Recommendation history saving
- [x] Proper sorting (Sustainability/CO₂/Cost)
- [x] Fixed best card color (dark theme)
- [x] PDF report generation
- [x] Logout functionality
- [x] Authentication guards on all routes

---

## 🚀 Next Steps

1. ✅ Test login flow
2. ✅ Generate recommendations
3. ✅ Verify sorting works correctly
4. ✅ Check recommendation history in MySQL
5. ✅ Test PDF download
6. ✅ Test account lockout (3 failed attempts)
7. Deploy to production (Render + MySQL cloud)

---

## 📞 Support

**Common Issues:**

1. **Can't login**: Check MySQL is running and credentials in `.env`
2. **Sorting wrong**: Verify `sort_by` parameter is passed in `app.py`
3. **Colors wrong**: Update CSS with dark theme colors
4. **ML engine not found**: Copy `recommendation_engine.py` to `ml/notebooks/`

---

**🌱 Your complete EcoPackAI with MySQL authentication is ready!**

**Start with:** `python backend/app.py` then open `http://localhost:3000/login.html`