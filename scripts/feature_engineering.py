# ================================
# MODULE 2: FEATURE ENGINEERING
# Step 1: Load & Validate Dataset
# ================================

import pandas as pd
import numpy as np

# Load cleaned dataset
materials_path = "E:/EcoPackAI/data/processed/packaging_materials_clean.csv"
df = pd.read_csv(materials_path)

# Display structure
print("\nDataset shape:", df.shape)
print("\nColumns:\n", df.columns)

# Summary statistics (evaluation requirement)
print("\nSummary statistics:\n", df.describe())

# Check missing values
print("\nMissing values per column:\n", df.isnull().sum())

# ================================
# Step 2: Feature Scaling
# ================================

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()

scale_cols = [
    "tensile_strength_mpa",
    "weight_capacity_kg",
    "density_g_cm3",
    "biodegradability_score",
    "biodegradation_time_days",
    "co2_emission_score",
    "recyclability_percentage",
    "production_cost_per_kg"
]

df_scaled = df.copy()
df_scaled[scale_cols] = scaler.fit_transform(df_scaled[scale_cols])

print("\n Features normalized successfully.")
print(df_scaled[scale_cols].head())

# ================================
# Step 3: Feature Engineering
# ================================

# CO2 Impact Index (lower CO2, higher biodegradability & recyclability is better)
df_scaled["co2_impact_index"] = (
    (1 - df_scaled["co2_emission_score"]) * 0.5 +
    df_scaled["biodegradability_score"] * 0.3 +
    df_scaled["recyclability_percentage"] * 0.2
)

# Cost Efficiency Index (lower cost, higher performance is better)
df_scaled["cost_efficiency_index"] = (
    (1 - df_scaled["production_cost_per_kg"]) * 0.4 +
    df_scaled["tensile_strength_mpa"] * 0.3 +
    df_scaled["weight_capacity_kg"] * 0.3
)

# Material Suitability Score (overall ranking score)
df_scaled["material_suitability_score"] = (
    df_scaled["co2_impact_index"] * 0.4 +
    df_scaled["cost_efficiency_index"] * 0.4 +
    df_scaled["tensile_strength_mpa"] * 0.1 +
    df_scaled["weight_capacity_kg"] * 0.1
)

print("\n Feature engineering completed.")
print(df_scaled[[
    "material_id",
    "co2_impact_index",
    "cost_efficiency_index",
    "material_suitability_score"
]].head())

# ================================
# Step 4: Save engineered dataset
# ================================

output_path = "E:/EcoPackAI/data/processed/packaging_materials_engineered.csv"
df_scaled.to_csv(output_path, index=False)

print("\n Feature-engineered dataset saved successfully.")
