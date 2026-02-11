import pandas as pd
import numpy as np
import joblib

# =========================
# LOAD PROCESSED MATERIALS
# =========================

materials_df = pd.read_excel("data/materials_processed.xlsx")

# =========================
# LOAD TRAINED MODELS
# =========================

rf_model = joblib.load("src/models/cost_model.pkl")
xgb_model = joblib.load("src/models/co2_model.pkl")
scaler = joblib.load("src/models/scaler.pkl")
label_encoder = joblib.load("src/models/label_encoder.pkl")

# =========================
# USER INPUT (SIMULATION)
# =========================

user_distance = 500
user_packaging_type = materials_df['Category'].iloc[0]

# Encode packaging type safely
try:
    user_packaging_encoded = label_encoder.transform([user_packaging_type])[0]
except:
    user_packaging_encoded = 0

user_input = pd.DataFrame(
    [[user_distance, user_packaging_encoded]],
    columns=["Distance_km", "Packaging_Used_Encoded"]
)

user_input_scaled = scaler.transform(user_input)

# =========================
# PREDICTIONS
# =========================

predicted_cost = rf_model.predict(user_input_scaled)[0]
predicted_co2 = xgb_model.predict(user_input_scaled)[0]

# =========================
# RANKING LOGIC
# =========================

materials_df["Predicted_Cost"] = predicted_cost
materials_df["Predicted_CO2"] = predicted_co2

# Normalize predicted values
materials_df["Predicted_Cost_Normalized"] = 0
materials_df["Predicted_CO2_Normalized"] = 0

materials_df["Final_Ranking_Score"] = (
    0.4 * materials_df["Material_Suitability_Score"] +
    0.3 * (1 - materials_df["Predicted_Cost_Normalized"]) +
    0.3 * (1 - materials_df["Predicted_CO2_Normalized"])
)

top_materials = materials_df.sort_values(
    by="Final_Ranking_Score",
    ascending=False
).head(5)

print("\nTop 5 Recommended Materials:")
print(top_materials[["Material_Name", "Final_Ranking_Score"]])
