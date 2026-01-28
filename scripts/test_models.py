import joblib
import pandas as pd

df = pd.read_csv("E:/EcoPackAI/data/processed/packaging_materials_engineered.csv")

X = df[[
    "tensile_strength_mpa",
    "weight_capacity_kg",
    "density_g_cm3",
    "biodegradability_score",
    "recyclability_percentage",
    "biodegradation_time_days",
    "co2_impact_index",
    "cost_efficiency_index",
    "material_suitability_score"
]]

cost_model = joblib.load("E:/EcoPackAI/models/cost_model.pkl")
co2_model = joblib.load("E:/EcoPackAI/models/co2_model.pkl")

print("Cost preds:", cost_model.predict(X.head()))
print("CO2 preds:", co2_model.predict(X.head()))
