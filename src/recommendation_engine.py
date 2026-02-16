import pandas as pd
import numpy as np
import joblib
import psycopg2

# =========================
# LOAD MODELS
# =========================

rf_model = joblib.load("src/models/cost_model.pkl")
xgb_model = joblib.load("src/models/co2_model.pkl")
scaler = joblib.load("src/models/scaler.pkl")
label_encoder = joblib.load("src/models/label_encoder.pkl")

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

    query = "SELECT * FROM materials;"
    df = pd.read_sql(query, conn)
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

def get_recommendations(distance, packaging_type):

    # Encode packaging type
    try:
        packaging_encoded = label_encoder.transform([packaging_type])[0]
    except:
        packaging_encoded = 0

    user_input = pd.DataFrame(
        [[distance, packaging_encoded]],
        columns=["Distance_km", "Packaging_Used_Encoded"]
    )

    user_input_scaled = scaler.transform(user_input)

    base_cost = rf_model.predict(user_input_scaled)[0]
    base_co2 = xgb_model.predict(user_input_scaled)[0]

    temp_df = materials_df.copy()

    # =========================
    # MATERIAL-AWARE ADJUSTMENT
    # =========================

    # Use engineered indices instead of raw cost_per_kg
    temp_df["Adjusted_Cost"] = base_cost * (1 - temp_df["cost_efficiency_index"])
    temp_df["Adjusted_CO2"] = base_co2 * temp_df["co2_impact_index"]

    # Normalize
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
