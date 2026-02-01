import pandas as pd
import numpy as np
import joblib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "final_ecopack_dataset_fe.csv"

cost_model = joblib.load(MODEL_DIR / "cost_model.pkl")
co2_model  = joblib.load(MODEL_DIR / "co2_model.pkl")

FEATURES_COST = joblib.load(MODEL_DIR / "features_cost.pkl")
FEATURES_CO2 = joblib.load(MODEL_DIR / "features_co2.pkl")

df = pd.read_csv(DATA_PATH)

# Materials dataframe
materials_df = (
    df[[
        "Material_ID",
        "Material_Name",
        "Category_material",
        "Density_kg_m3",
        "Tensile_Strength_MPa",
        "Cost_per_kg",
        "CO2_Emission_kg_material",
        "Biodegradable"
    ]]
    .drop_duplicates()
    .reset_index(drop=True)
)

# Categorical columns + Fragility
cat_cols = ["Category_item", "Moisture_Sens", "Shipping_Mode", 
            "Packaging_Used", "Material_Name", "Category_material", 
            "Biodegradable", "sustainability_rating"]
ordinal_cols = ["Fragility"]

# Quick summary print
print("\n🟦 Categorical Columns & Unique Values\n")
for col in cat_cols:
    uniques = df[col].value_counts()
    print(f"{col}:")
    print(uniques.to_frame(name="Count"))
    print("-"*40)

print("\n🟨 Ordinal Column - Fragility\n")
frag_counts = df["Fragility"].value_counts().sort_index()
print(frag_counts.to_frame(name="Count"))

# Expand shipment input across all materials
def expand_shipment_with_materials(shipment, materials_df):
    shipment_df = pd.DataFrame([shipment])
    shipment_df["_key"] = 1
    materials_df["_key"] = 1
    expanded = shipment_df.merge(materials_df, on="_key").drop("_key", axis=1)
    return expanded
  
# Normalized helper 
def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-6)
    
# Generate top-K recommendations
def generate_recommendations(
    materials_df,
    co2_model,
    cost_model,
    shipment_inputs,
    features_cost,
    features_co2,
    top_k=3,
    sort_by="Sustainability"
):
    df = expand_shipment_with_materials(shipment_inputs, materials_df)

    # -----------------------------
    # Derived features
    parcel_volume_m3 = (
        shipment_inputs["Length_cm"] / 100
        * shipment_inputs["Width_cm"] / 100
        * shipment_inputs["Height_cm"] / 100
    )

    df["Item_Volume_m3"] = parcel_volume_m3
    df["Volumetric_Weight_kg"] = (
        shipment_inputs["Length_cm"]
        * shipment_inputs["Width_cm"]
        * shipment_inputs["Height_cm"]
    ) / 5000

    df["Weight_kg"] = shipment_inputs["Weight_kg"]
    df["Fragility"] = shipment_inputs["Fragility"]
    df["Moisture_Sens"] = shipment_inputs["Moisture_Sens"]
    df["Distance_km"] = shipment_inputs["Distance_km"]
    df["Shipping_Mode"] = shipment_inputs["Shipping_Mode"]
    df["Category_item"] = shipment_inputs["Category_item"]

    df["Biodegradable"] = df["Biodegradable"].map(lambda x: 1 if x == "Yes" else 0)

    # -----------------------------
    # MODEL PREDICTIONS (THIS IS THE FIX)
    X_cost = df[features_cost]
    X_co2  = df[features_co2]

    df["Pred_Cost"] = cost_model.predict(X_cost)
    df["Pred_CO2"]  = co2_model.predict(X_co2)

    # -----------------------------
    # Normalization helpers
    def normalize(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-6)

    df["Env_Impact"] = 1 - normalize(df["Pred_CO2"])
    df["Cost_Eff"]   = 1 - normalize(df["Pred_Cost"])

    df["Mat_Suit"] = (
        normalize(df["Tensile_Strength_MPa"]) * 0.6 +
        normalize(df["Density_kg_m3"]) * 0.4
    )

    df["Sustainability"] = (
        df["Env_Impact"] * 0.5 +
        df["Cost_Eff"] * 0.3 +
        df["Biodegradable"] * 0.2
    )

    ascending = sort_by in ["Pred_Cost", "Pred_CO2"]
    return df.sort_values(sort_by, ascending=ascending).head(top_k) 
    
# Example usage
shipment_input = {
    "Category_item": "Electronics",
    "Weight_kg": 5.0,
    "Volumetric_Weight_kg": 6.2,
    "Item_Volume_m3": 0.018,
    "Fragility": 8,
    "Moisture_Sens": True,
    "Distance_km": 1200,
    "Shipping_Mode": "Air",
    "Length_cm": 30,
    "Width_cm": 20,
    "Height_cm": 15,
    "Shelf_Life_Days": 5
}

final_recommendations = generate_recommendations(
    materials_df=materials_df,
    co2_model=co2_model,
    cost_model=cost_model,
    shipment_inputs=shipment_input,
    features_cost=FEATURES_COST,
    features_co2=FEATURES_CO2,
    top_k=5
)


final_recommendations[[
    "Material_Name",
    "Pred_Cost",
    "Pred_CO2",
    "Biodegradable",
    "Tensile_Strength_MPa",
    "Sustainability"
]]