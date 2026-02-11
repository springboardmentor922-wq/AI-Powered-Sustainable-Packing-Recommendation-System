"""
EcoPackAI Backend - WORKING VERSION
Flask + Session Limits (Login Commented Out)
--------------------------------------------
Features:
- 3 recommendations per hour limit per session
- MySQL connection for saving history
- No login required (commented out)
"""

from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from functools import wraps
import secrets
import logging
import os
from dotenv import load_dotenv
from io import BytesIO
from pathlib import Path
import sys
import json

# PDF imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# ==========================================================
# PATH FIX (so ML works)
# ==========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# ==========================================================
# ML ENGINE (SINGLE SOURCE OF TRUTH)
# ==========================================================
try:
    from ml.notebooks.recommendation_engine import (
        generate_recommendations,
        materials_df,
        co2_model,
        cost_model,
        FEATURES_COST,
        FEATURES_CO2
    )
    ML_AVAILABLE = True
    print("✅ ML engine loaded successfully")
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️ ML engine not available: {e}")
    print("⚠️ Using mock data mode")

# ==========================================================
# LOCAL MODULES (Login/DB - COMMENTED OUT)
# ==========================================================
# from auth import login_user, register_email
# from recommender import save_recommendation, get_user_history
# from db import test_connection

# ==========================================================
# ENV + APP SETUP
# ==========================================================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY", secrets.token_urlsafe(32))

# Session config
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)  # 1 hour session
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# CORS setup
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
])

# Rate limiter setup
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcoPackAI")

# ==========================================================
# SESSION LIMIT TRACKER
# ==========================================================
def init_session():
    """Initialize session with tracking"""
    if "session_id" not in session:
        session.permanent = True
        session["session_id"] = secrets.token_urlsafe(16)
        session["recommendation_count"] = 0
        session["session_start"] = datetime.now().isoformat()
        logger.info(f"🆕 New session created: {session['session_id']}")

def check_recommendation_limit():
    """Check if user has exceeded recommendation limit (3 per hour)"""
    init_session()
    
    # Check session age
    session_start = datetime.fromisoformat(session.get("session_start", datetime.now().isoformat()))
    session_age = datetime.now() - session_start
    
    # Reset if session older than 1 hour
    if session_age > timedelta(hours=1):
        session["recommendation_count"] = 0
        session["session_start"] = datetime.now().isoformat()
        logger.info(f"🔄 Session reset: {session['session_id']}")
    
    # Check limit
    count = session.get("recommendation_count", 0)
    if count >= 3:
        remaining_time = timedelta(hours=1) - session_age
        minutes = int(remaining_time.total_seconds() / 60)
        return False, f"Limit reached: 3 recommendations per hour. Try again in {minutes} minutes."
    
    return True, None

def increment_recommendation_count():
    """Increment recommendation counter"""
    session["recommendation_count"] = session.get("recommendation_count", 0) + 1
    remaining = 3 - session["recommendation_count"]
    logger.info(f"📊 Session {session['session_id']}: {session['recommendation_count']}/3 used, {remaining} remaining")

# ==========================================================
# MOCK DATA (when ML not available)
# ==========================================================
MOCK_MATERIALS = [
    {
        "Material_Name": "Corrugated Cardboard",
        "Pred_Cost": 12.50,
        "Pred_CO2": 2.30,
        "Sustainability": 0.8500,
        "Biodegradable": True,
        "Tensile_Strength_MPa": 15.5
    },
    {
        "Material_Name": "Recycled Plastic",
        "Pred_Cost": 18.75,
        "Pred_CO2": 5.80,
        "Sustainability": 0.6200,
        "Biodegradable": False,
        "Tensile_Strength_MPa": 25.3
    },
    {
        "Material_Name": "Biodegradable Foam",
        "Pred_Cost": 22.30,
        "Pred_CO2": 3.10,
        "Sustainability": 0.7800,
        "Biodegradable": True,
        "Tensile_Strength_MPa": 12.8
    },
    {
        "Material_Name": "Wood Crates",
        "Pred_Cost": 35.00,
        "Pred_CO2": 4.20,
        "Sustainability": 0.7200,
        "Biodegradable": True,
        "Tensile_Strength_MPa": 40.0
    },
    {
        "Material_Name": "Molded Pulp",
        "Pred_Cost": 15.80,
        "Pred_CO2": 2.00,
        "Sustainability": 0.8900,
        "Biodegradable": True,
        "Tensile_Strength_MPa": 18.2
    }
]

def get_mock_recommendations(sort_by="Sustainability"):
    """Return mock data sorted by criterion"""
    import copy
    recommendations = copy.deepcopy(MOCK_MATERIALS)
    
    # Sort by criterion
    if sort_by == "Sustainability":
        recommendations.sort(key=lambda x: x["Sustainability"], reverse=True)
    elif sort_by == "CO2":
        recommendations.sort(key=lambda x: x["Pred_CO2"])
    elif sort_by == "Cost":
        recommendations.sort(key=lambda x: x["Pred_Cost"])
    
    return recommendations

# ==========================================================
# AUTH ROUTES (COMMENTED OUT)
# ==========================================================
# @app.route("/api/auth/register", methods=["POST"])
# def register():
#     data = request.get_json()
#     email = data.get("email")
#     if not email:
#         return jsonify({"error": "Email required"}), 400
#     result, status = register_email(email)
#     return jsonify(result), status

# @app.route("/api/auth/login", methods=["POST"])
# def login():
#     data = request.get_json()
#     email = data.get("email")
#     password = data.get("password")
#     if not email or not password:
#         return jsonify({"error": "Email and password required"}), 400
#     result, status = login_user(email, password)
#     if status == 200:
#         session.permanent = True
#         session["user_email"] = email
#         session["session_id"] = secrets.token_urlsafe(16)
#     return jsonify(result), status

# @app.route("/api/auth/logout", methods=["POST"])
# def logout():
#     email = session.get("user_email")
#     session.clear()
#     logger.info(f"🚪 Logged out: {email}")
#     return jsonify({"success": True})

@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Always return authenticated (no login required)"""
    init_session()
    return jsonify({
        "authenticated": True,
        "session_id": session.get("session_id"),
        "recommendations_used": session.get("recommendation_count", 0),
        "recommendations_remaining": 3 - session.get("recommendation_count", 0)
    })

# ==========================================================
# RECOMMENDATION (WITH SESSION LIMITS)
# ==========================================================
@app.route("/api/recommend", methods=["POST"])
@limiter.limit("3 per hour")  # Rate limit: 3 per hour
def recommend():
    """Generate recommendations with session limit"""
    
    # Check session limit
    allowed, error_msg = check_recommendation_limit()
    if not allowed:
        return jsonify({
            "error": error_msg,
            "limit_reached": True,
            "recommendations_used": session.get("recommendation_count", 0)
        }), 429  # Too Many Requests
    
    data = request.get_json()

    # Validate required fields
    required = [
        "Category_item", "Weight_kg", "Fragility",
        "Moisture_Sens", "Distance_km", "Shipping_Mode",
        "Length_cm", "Width_cm", "Height_cm"
    ]

    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Prepare shipment data
    shipment = {
        "Category_item": data["Category_item"],
        "Weight_kg": float(data["Weight_kg"]),
        "Fragility": int(data["Fragility"]),
        "Moisture_Sens": bool(data["Moisture_Sens"]),
        "Distance_km": float(data["Distance_km"]),
        "Shipping_Mode": data["Shipping_Mode"],
        "Length_cm": float(data["Length_cm"]),
        "Width_cm": float(data["Width_cm"]),
        "Height_cm": float(data["Height_cm"]),
    }

    top_k = int(data.get("top_k", 5))
    sort_by = data.get("sort_by", "Sustainability")

    # Generate recommendations
    try:
        if ML_AVAILABLE:
            # REAL ML CALL
            df = generate_recommendations(
                materials_df=materials_df,
                co2_model=co2_model,
                cost_model=cost_model,
                shipment_inputs=shipment,
                features_cost=FEATURES_COST,
                features_co2=FEATURES_CO2,
                top_k=top_k,
                sort_by=sort_by
            )
            recommendations = df.to_dict("records")
            logger.info(f"✅ ML recommendations generated")
        else:
            # MOCK DATA
            recommendations = get_mock_recommendations(sort_by)[:top_k]
            logger.info(f"⚠️ Using mock recommendations")
        
        # Increment counter
        increment_recommendation_count()
        
        # Save to session
        session["last_recommendation"] = recommendations
        
        # (Optional) Save to MySQL - COMMENTED OUT
        # save_recommendation(
        #     email=session.get("user_email", "guest"),
        #     session_id=session["session_id"],
        #     shipment=shipment,
        #     k_value=top_k,
        #     sort_by=sort_by,
        #     recommendations=recommendations
        # )

        return jsonify({
            "status": "success",
            "recommendations": recommendations,
            "session_info": {
                "used": session["recommendation_count"],
                "remaining": 3 - session["recommendation_count"]
            }
        })
    
    except Exception as e:
        logger.error(f"❌ Recommendation error: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================================
# PDF GENERATION
# ==========================================================
@app.route("/api/generate-pdf", methods=["POST"])
def generate_pdf():
    """Generate PDF report from last recommendation"""
    data = session.get("last_recommendation")
    if not data:
        return jsonify({"error": "No recommendation available"}), 400

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            "title",
            fontSize=24,
            alignment=1,
            textColor=colors.HexColor("#2E7D32"),
            spaceAfter=20
        )
        elements.append(Paragraph("🌱 EcoPackAI Recommendation Report", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Date
        date_style = ParagraphStyle("date", fontSize=10, alignment=1)
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
        elements.append(Spacer(1, 0.5 * inch))

        # Table
        table_data = [["#", "Material", "Cost ($)", "CO₂ (kg)", "Sustainability", "Bio"]]
        for idx, r in enumerate(data, 1):
            table_data.append([
                str(idx),
                r["Material_Name"],
                f"${r['Pred_Cost']:.2f}",
                f"{r['Pred_CO2']:.2f}",
                f"{r['Sustainability']:.4f}",
                "✓" if r.get("Biodegradable") else "✗"
            ])

        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgreen),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 12),
            ("BOTTOMPADDING", (0,0), (-1,0), 12),
            ("BACKGROUND", (0,1), (-1,-1), colors.beige),
            ("GRID", (0,0), (-1,-1), 1, colors.grey)
        ]))

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"EcoPackAI_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    
    except Exception as e:
        logger.error(f"❌ PDF generation error: {e}")
        return jsonify({"error": "PDF generation failed"}), 500

# ==========================================================
# HISTORY (COMMENTED OUT)
# ==========================================================
# @app.route("/api/history", methods=["GET"])
# def history():
#     return jsonify({
#         "history": get_user_history(session.get("user_email", "guest"))
#     })

# ==========================================================
# HEALTH CHECK
# ==========================================================
@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "ml_available": ML_AVAILABLE,
        "materials_loaded": len(materials_df) if ML_AVAILABLE else len(MOCK_MATERIALS),
        "timestamp": datetime.utcnow().isoformat(),
        "session_limit": "3 recommendations per hour"
    })

# ==========================================================
# RUN
# ==========================================================
if __name__ == "__main__":
    logger.info("🌱 EcoPackAI Backend Starting")
    logger.info(f"✅ ML Engine: {'Available' if ML_AVAILABLE else 'Mock Mode'}")
    logger.info("🔒 Session Limit: 3 recommendations per hour")
    logger.info("🚫 Login: Disabled (commented out)")
    
    # Test DB connection (commented out)
    # if test_connection():
    #     logger.info("✅ MySQL connected")
    # else:
    #     logger.warning("⚠️ MySQL not connected (optional)")

    app.run(debug=True, host="0.0.0.0", port=5000)