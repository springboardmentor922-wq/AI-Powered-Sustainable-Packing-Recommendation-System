import pandas as pd
import numpy as np
import joblib

# =========================
# LOAD MODELS (once)
# =========================

rf_model = joblib.load("src/models/cost_model.pkl")
xgb_model = joblib.load("src/models/co2_model.pkl")
scaler = joblib.load("src/models/scaler.pkl")
label_encoder = joblib.load("src/models/label_encoder.pkl")

materials_df = pd.read_excel("data/materials_processed.xlsx")

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

    predicted_cost = rf_model.predict(user_input_scaled)[0]
    predicted_co2 = xgb_model.predict(user_input_scaled)[0]

    temp_df = materials_df.copy()

    temp_df["Predicted_Cost"] = predicted_cost
    temp_df["Predicted_CO2"] = predicted_co2

    temp_df["Final_Ranking_Score"] = (
        0.4 * temp_df["Material_Suitability_Score"] +
        0.3 * (1 - 0.5) +
        0.3 * (1 - 0.5)
    )

    top_materials = temp_df.sort_values(
        by="Final_Ranking_Score",
        ascending=False
    ).head(5)

    result = top_materials[["Material_Name", "Final_Ranking_Score"]]

    return result.to_dict(orient="records")
