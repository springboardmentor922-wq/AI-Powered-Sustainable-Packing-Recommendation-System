import pandas as pd
import numpy as np
import joblib
import psycopg2

# =========================
# LOAD MODELS & ENCODERS
# =========================

rf_model = joblib.load("src/models/cost_model.pkl")
xgb_model = joblib.load("src/models/co2_model.pkl")
scaler = joblib.load("src/models/scaler.pkl")

le_packaging = joblib.load("src/models/label_encoder.pkl")
le_category = joblib.load("src/models/category_encoder.pkl")
le_shipping = joblib.load("src/models/shipping_encoder.pkl")

# =========================
# LOAD MATERIALS FROM DB
# =========================

def load_materials_from_db():
    conn = psycopg2.connect(
        host="localhost",
        database="Ecopackai_db",
        user="postgres",
        password="boorgir"
    )
    df = pd.read_sql("SELECT * FROM materials;", conn)
    conn.close()
    return df

materials_df = load_materials_from_db()

# =========================
# NORMALIZATION FUNCTION
# =========================

def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-6)

# =========================
# MAIN FUNCTION
# =========================

def get_recommendations(
    distance,
    packaging_type,
    category,
    weight,
    volumetric_weight,
    fragility,
    moisture,
    shipping_mode
):

    # =========================
    # ENCODE CATEGORICAL INPUTS
    # =========================

    try:
        packaging_encoded = le_packaging.transform([packaging_type])[0]
    except:
        packaging_encoded = 0

    try:
        category_encoded = le_category.transform([category])[0]
    except:
        category_encoded = 0

    try:
        shipping_encoded = le_shipping.transform([shipping_mode])[0]
    except:
        shipping_encoded = 0

    # =========================
    # BUILD FEATURE VECTOR (8 FEATURES)
    # =========================

    user_input = pd.DataFrame(
        [[
            distance,
            weight,
            volumetric_weight,
            fragility,
            moisture,
            category_encoded,
            shipping_encoded,
            packaging_encoded
        ]],
        columns=[
            "Distance_km",
            "Weight_kg",
            "Volumetric_Weight_kg",
            "Fragility",
            "Moisture_Sens",
            "Category_Encoded",
            "Shipping_Mode_Encoded",
            "Packaging_Used_Encoded"
        ]
    )

    user_input_scaled = scaler.transform(user_input)

    # =========================
    # ML PREDICTIONS
    # =========================

    base_cost = rf_model.predict(user_input_scaled)[0]
    base_co2 = xgb_model.predict(user_input_scaled)[0]

    temp_df = materials_df.copy()

    # =========================
    # MATERIAL-ADJUSTED IMPACT
    # =========================

    temp_df["Adjusted_Cost"] = base_cost * (1 - temp_df["cost_efficiency_index"])
    temp_df["Adjusted_CO2"] = base_co2 * temp_df["co2_impact_index"]

    temp_df["Cost_Score"] = 1 - normalize(temp_df["Adjusted_Cost"])
    temp_df["CO2_Score"] = 1 - normalize(temp_df["Adjusted_CO2"])

    # =========================
    # FINAL RANKING
    # =========================

    temp_df["Final_Ranking_Score"] = (
        0.4 * temp_df["material_suitability_score"] +
        0.3 * temp_df["Cost_Score"] +
        0.3 * temp_df["CO2_Score"]
    )

    top_materials = temp_df.sort_values(
        by="Final_Ranking_Score",
        ascending=False
    ).head(5)

    result = top_materials[
        [
            "material_name",
            "Final_Ranking_Score",
            "Adjusted_Cost",
            "Adjusted_CO2"
        ]
    ]

    return result.to_dict(orient="records")
