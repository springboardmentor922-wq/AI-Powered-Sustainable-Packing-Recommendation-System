from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models
cost_model = joblib.load(os.path.join(BASE_DIR, "models/cost_model.pkl"))
co2_model = joblib.load(os.path.join(BASE_DIR, "models/co2_model.pkl"))

# Load ranked materials
materials_df = pd.read_csv(os.path.join(BASE_DIR, "data/materials_ranked.csv"))

# =========================
# Health check
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "EcoPackAI backend running successfully"})


# =========================
# Material-level prediction
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    features = [[
        data["tensile_strength_mpa"],
        data["weight_capacity_kg"],
        data["density_g_cm3"],
        data["biodegradability_score"],
        data["recyclability_percentage"],
        data["biodegradation_time_days"],
        data["co2_impact_index"],
        data["cost_efficiency_index"],
        data["material_suitability_score"]
    ]]

    cost_pred = cost_model.predict(features)[0]
    co2_pred = co2_model.predict(features)[0]

    return jsonify({
        "predicted_cost": round(float(cost_pred), 4),
        "predicted_co2": round(float(co2_pred), 4)
    })


# =========================
# General top recommendations
# =========================
@app.route("/recommend", methods=["GET"])
def recommend():
    top_n = int(request.args.get("top", 5))
    top_materials = materials_df.head(top_n)

    return jsonify(top_materials.to_dict(orient="records"))


# =========================
# PRODUCT-BASED RECOMMENDATION
# =========================
@app.route("/product-recommend", methods=["POST"])
def product_recommend():

    data = request.json

    product_name = data["product_name"]
    length = float(data["length"])
    breadth = float(data["breadth"])
    height = float(data["height"])
    weight = float(data.get("weight", 1))

    # Surface Area calculation (cm²)
    surface_area = 2 * ((length * breadth) + (length * height) + (breadth * height))

    df = materials_df.copy()

    # -------------------------
    # Step 1: Soft engineering filter
    # -------------------------
    filtered_df = df[df["weight_capacity_kg"] >= (weight / 1000)]  # scaled safety

    if surface_area < 1000:
        filtered_df = filtered_df[filtered_df["tensile_strength_mpa"] >= 0.25]
    elif surface_area < 5000:
        filtered_df = filtered_df[filtered_df["tensile_strength_mpa"] >= 0.40]
    else:
        filtered_df = filtered_df[filtered_df["tensile_strength_mpa"] >= 0.55]

    # -------------------------
    # Step 2: Fallback if empty
    # -------------------------
    if filtered_df.empty:
        filtered_df = df.copy()

    # -------------------------
    # Step 3: Rank by AI score
    # -------------------------
    top_materials = filtered_df.sort_values(
        "ai_recommendation_score", ascending=False
    ).head(5)

    results = top_materials[[
        "material_type",
        "ai_recommendation_score",
        "predicted_cost",
        "predicted_co2",
        "biodegradability_score",
        "recyclability_percentage",
        "tensile_strength_mpa",
        "weight_capacity_kg"
    ]]

    return jsonify({
        "product": product_name,
        "surface_area_cm2": surface_area,
        "recommendations": results.to_dict(orient="records")
    })



# =========================
# Run server
# =========================
if __name__ == "__main__":
    app.run(debug=True)
