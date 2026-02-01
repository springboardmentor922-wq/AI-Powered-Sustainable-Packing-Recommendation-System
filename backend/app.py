"""
EcoPackAI Backend
Flask + MySQL Auth + Real ML Engine
"""

from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import secrets
import logging
import os
from dotenv import load_dotenv
from io import BytesIO
from pathlib import Path
import sys

# ==========================================================
# PATH FIX (so ML works)
# ==========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# ==========================================================
# ML ENGINE (SINGLE SOURCE OF TRUTH)
# ==========================================================
from ml.notebooks.recommendation_engine import (
    generate_recommendations,
    materials_df,
    co2_model,
    cost_model,
    FEATURES_COST,
    FEATURES_CO2
)

# ==========================================================
# LOCAL MODULES
# ==========================================================
from auth import login_user, register_email
from recommender import save_recommendation, get_user_history
from db import test_connection

# ==========================================================
# ENV + APP SETUP
# ==========================================================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY") 

if not app.secret_key:
    raise RuntimeError("🚨 APP_SECRET_KEY not found in .env! Set it before running Flask.")

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000"
])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcoPackAI")

# ==========================================================
# AUTH DECORATOR
# ==========================================================
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_email" not in session:
            return jsonify({"error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return wrapper

# ==========================================================
# AUTH ROUTES
# ==========================================================
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    result, status = register_email(email)
    return jsonify(result), status


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    result, status = login_user(email, password)

    if status == 200:
        session.permanent = True
        session["user_email"] = email
        session["session_id"] = secrets.token_urlsafe(16)

    return jsonify(result), status


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    email = session.get("user_email")
    session.clear()
    logger.info(f"🚪 Logged out: {email}")
    return jsonify({"success": True})


@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    if "user_email" in session:
        return jsonify({
            "authenticated": True,
            "email": session["user_email"]
        })
    return jsonify({"authenticated": False}), 401

# ==========================================================
# RECOMMENDATION
# ==========================================================
@app.route("/api/recommend", methods=["POST"])
# @require_auth
def recommend():
    data = request.get_json()

    required = [
        "Category_item", "Weight_kg", "Fragility",
        "Moisture_Sens", "Distance_km", "Shipping_Mode",
        "Length_cm", "Width_cm", "Height_cm"
    ]

    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

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

    # 🔥 REAL ML CALL
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

    # 💾 SAVE HISTORY
    save_recommendation(
        email=session["user_email"],
        session_id=session["session_id"],
        shipment=shipment,
        k_value=top_k,
        recommendations=recommendations
    )

    session["last_recommendation"] = recommendations

    return jsonify({
        "status": "success",
        "recommendations": recommendations
    })

# ==========================================================
# HISTORY
# ==========================================================
@app.route("/api/history", methods=["GET"])
@require_auth
def history():
    return jsonify({
        "history": get_user_history(session["user_email"])
    })

# ==========================================================
# PDF
# ==========================================================
@app.route("/api/generate-pdf", methods=["GET"])
@require_auth
def generate_pdf():
    data = session.get("last_recommendation")
    if not data:
        return jsonify({"error": "No recommendation available"}), 400

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = ParagraphStyle(
        "title",
        fontSize=24,
        alignment=1,
        textColor=colors.HexColor("#2E7D32")
    )

    elements.append(Paragraph("🌱 EcoPackAI Recommendation Report", title))
    elements.append(Spacer(1, 0.3 * inch))

    table_data = [["Material", "Cost", "CO₂", "Sustainability"]]
    for r in data:
        table_data.append([
            r["Material_Name"],
            f"${r['Pred_Cost']:.2f}",
            f"{r['Pred_CO2']:.2f}",
            f"{r['Sustainability']:.3f}"
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgreen)
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="EcoPackAI_Report.pdf"
    )

# ==========================================================
# HEALTH
# ==========================================================
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "mysql": test_connection(),
        "materials_loaded": len(materials_df),
        "timestamp": datetime.utcnow().isoformat()
    })

# ==========================================================
# RUN
# ==========================================================
if __name__ == "__main__":
    logger.info("🌱 EcoPackAI Backend Starting")
    if test_connection():
        logger.info("✅ MySQL connected")
    else:
        logger.error("❌ MySQL connection failed")

    app.run(debug=True, port=5000)