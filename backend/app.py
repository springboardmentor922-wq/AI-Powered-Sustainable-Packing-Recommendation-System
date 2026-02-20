from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import webbrowser
import os
import threading
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import send_file


# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

CORS(app)

# ---------------- LOAD MODELS ----------------
cost_model = joblib.load(os.path.join(BASE_DIR, "../models/cost_model.pkl"))
co2_model = joblib.load(os.path.join(BASE_DIR, "../models/co2_model.pkl"))

rec_model = joblib.load(os.path.join(BASE_DIR, "../models/packaging_recommendation_model.pkl"))
category_encoder = joblib.load(os.path.join(BASE_DIR, "../models/category_encoder.pkl"))
packaging_encoder = joblib.load(os.path.join(BASE_DIR, "../models/packaging_encoder.pkl"))

# ---------------- LOAD MATERIAL DATABASE ----------------
materials_df = pd.read_csv(os.path.join(BASE_DIR, "../models/material_data.csv"))
# Dashboard analytics dataset (aggregated materials)
dashboard_df = pd.read_csv(os.path.join(BASE_DIR, "../models/dashboard_materials.csv"))

print("\n=========== MATERIAL DATASET LOADED ===========")
print(materials_df.columns.tolist())
print("==============================================\n")

# =========================================================
#            MATERIAL KNOWLEDGE ENGINE (FOR DASHBOARD ONLY)
# =========================================================

def normalize(col):
    return (col - col.min()) / (col.max() - col.min() + 1e-6)

materials_df["Protection_Score"] = (
    0.35 * normalize(materials_df["Tensile_Strength_MPa"]) +
    0.25 * normalize(materials_df["Weight_Capacity_kg"]) +
    0.20 * normalize(materials_df["Thickness_Micrometers"]) +
    0.20 * normalize(materials_df["Thermal_Stability_C"])
)

materials_df["Sustainability_Score"] = (
    0.30 * normalize(materials_df["Biodegradability_Score"]) +
    0.25 * normalize(materials_df["Recyclability_Percentage"]) +
    0.25 * (1 - normalize(materials_df["CO2_Emission_Score"])) +
    0.20 * (1 - normalize(materials_df["Environmental_Impact_Score"]))
)

materials_df["Material_Efficiency"] = (
    0.6 * materials_df["Protection_Score"] +
    0.4 * materials_df["Sustainability_Score"]
)

materials_df["EcoScore"] = (
    0.25 * normalize(materials_df["Biodegradability_Score"]) +
    0.20 * normalize(materials_df["Recyclability_Percentage"]) +
    0.20 * (1 - normalize(materials_df["CO2_Emission_Score"])) +
    0.20 * (1 - normalize(materials_df["Environmental_Impact_Score"])) +
    0.15 * normalize(materials_df["Tensile_Strength_MPa"])
)

# ---------------- AUTO OPEN BROWSER ----------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

# ---------------- PAGES ----------------
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/predict-page")
def predict_page():
    return render_template("predict.html")

@app.route("/result")
def result_page():
    return render_template("result.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/report")
def report_page():
    return render_template("reports.html")

@app.route("/material-details/<material>")
def material_details(material):

    df = materials_df[materials_df["Material_Type"] == material]

    if len(df) == 0:
        return jsonify({"error":"Material not found"})

    row = df.iloc[0]

    return jsonify({
        "strength": float(row["Tensile_Strength_MPa"]),
        "recyclability": float(row["Recyclability_Percentage"]),
        "co2": float(row["CO2_Emission_Score"]),
        "biodegradability": float(row["Biodegradability_Score"]),
        "thermal": float(row["Thermal_Stability_C"]),
        "weight_capacity": float(row["Weight_Capacity_kg"])
    })

@app.route("/dashboard-data")
def dashboard_data():

    df = dashboard_df.copy()

    # KPI values
    total_materials = len(df)
    avg_co2 = df["CO2_Emission_Score"].mean()
    avg_recycle = df["Recyclability_Percentage"].mean()
    best_material = df.sort_values("EcoScore", ascending=False).iloc[0]["Material_Type"]

    # Top 10 eco materials
    eco_top = df.sort_values("EcoScore", ascending=False).head(10)

    return jsonify({
        "kpis":{
            "total": int(total_materials),
            "avg_co2": float(avg_co2),
            "avg_recycle": float(avg_recycle),
            "best": best_material
        },
        "materials": df.to_dict(orient="records"),
        "eco_top":{
            "labels": eco_top["Material_Type"].tolist(),
            "values": eco_top["EcoScore"].tolist()
        }
    })



# =========================================================
#                    PREDICTION API
# =========================================================
@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    # -------- Input Parsing --------
    weight = float(data["weight"])
    length = float(data["length"])
    width = float(data["width"])
    height = float(data["height"])
    fragility = float(data["fragility"])
    moisture = int(data["moisture"])
    distance = float(data["distance"])

    # -------- Feature Engineering --------
    volume = length * width * height
    surface_area = 2 * (length * width + width * height + height * length)
    adjusted_area = surface_area * 1.2
    handling_risk = (fragility * 0.6) + ((distance / 3000) * 0.4)

    # -------- Category Encoding (Safe) --------
    try:
        category_encoded = category_encoder.transform([data["category"]])[0]
    except:
        category_encoded = 0

    # -------- Recommendation Model --------
    features_rec = np.array([[
        weight,
        volume,
        surface_area,
        handling_risk,
        moisture,
        category_encoded
    ]])

    # Best class
    pred_class = rec_model.predict(features_rec)[0]
    best_material = packaging_encoder.inverse_transform([pred_class])[0]

    # Probabilities for Top-5
    probs = rec_model.predict_proba(features_rec)[0]
    classes = packaging_encoder.classes_

    top_indices = np.argsort(probs)[::-1][:5]

    top5_list = []
    for idx in top_indices:
        top5_list.append({
            "Material_Type": str(classes[idx]),
            "Confidence": float(round(probs[idx], 4))
        })

    # -------- Cost & CO₂ Prediction --------
    features_cost = np.array([[weight, volume, adjusted_area, handling_risk, moisture, distance]])

    cost_pred = float(round(cost_model.predict(features_cost)[0], 2))
    co2_pred = float(round(co2_model.predict(features_cost)[0], 2))

    return jsonify({
        "recommended_material": str(best_material),
        "top_5_materials": top5_list,
        "predicted_cost_usd": cost_pred,
        "predicted_co2_kg": co2_pred
    })

# ---------------- MATERIAL DATABASE ----------------
@app.route("/materials")
def materials():
    return materials_df.to_json(orient="records")

# =========================================================
#                ANALYTICS DASHBOARD DATA
# =========================================================
@app.route("/analytics-data")
def analytics_data():

    df = dashboard_df.copy()

    # Eco ranking (top 10 only)
    top_eco = df.sort_values("Biodegradability_Score", ascending=False).head(10)

    # Recyclability buckets
    bins = [0,20,40,60,80,100]
    labels = ["0-20","20-40","40-60","60-80","80-100"]
    recycle_dist = pd.cut(df["Recyclability_Percentage"], bins=bins, labels=labels).value_counts().sort_index()

    # Strength vs CO2
    scatter = df[["Tensile_Strength_MPa","CO2_Emission_Score"]]

    # KPI values
    kpis = {
        "total_materials": int(len(df)),
        "avg_co2": float(df["CO2_Emission_Score"].mean()),
        "avg_recyclability": float(df["Recyclability_Percentage"].mean()),
        "best_material": str(df.sort_values("Biodegradability_Score",ascending=False).iloc[0]["Material_Type"])
    }

    return jsonify({
        "kpis":kpis,
        "eco_bar":{
            "labels":top_eco["Material_Type"].tolist(),
            "values":top_eco["Biodegradability_Score"].tolist()
        },
        "recycle_pie":{
            "labels":recycle_dist.index.astype(str).tolist(),
            "values":recycle_dist.values.tolist()
        },
        "strength_scatter":{
            "x":scatter["Tensile_Strength_MPa"].tolist(),
            "y":scatter["CO2_Emission_Score"].tolist()
        }
    })



# =========================================================
#                  PDF REPORT DOWNLOAD
# =========================================================
@app.route("/download-report", methods=["POST"])
def download_report():

    data = request.json

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setFont("Helvetica", 12)

    y = 800
    pdf.drawString(200, y, "EcoPackAI Sustainability Report")
    y -= 40

    pdf.drawString(50, y, f"Recommended Material: {data['recommended_material']}")
    y -= 30

    pdf.drawString(50, y, f"Predicted Cost: ${data['predicted_cost_usd']}")
    y -= 30

    pdf.drawString(50, y, f"CO2 Emission: {data['predicted_co2_kg']} kg")
    y -= 40

    pdf.drawString(50, y, "Top 5 Materials:")
    y -= 25

    for m in data["top_5_materials"]:
        pdf.drawString(70, y, f"{m['Material_Type']} - {round(m['Confidence']*100,2)}%")
        y -= 20

    y -= 30
    pdf.drawString(50, y, "This recommendation is generated using machine learning")
    y -= 20
    pdf.drawString(50, y, "considering packaging protection, cost efficiency, and environmental impact.")

    pdf.save()

    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="EcoPackAI_Report.pdf",
                     mimetype="application/pdf")

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    print("EcoPackAI AI Server Running...")
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, use_reloader=False)
