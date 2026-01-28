#import files
import pandas as pd
import numpy as np

# loading the raw packaging materials dataset
materials_path = "E:/EcoPackAI/data/raw/packaging_materials.xlsx"
materials_df = pd.read_excel(materials_path)

# Standardizing column names for ML compatability
materials_df.columns = (
    materials_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Renaming columns for final schema
materials_df = materials_df.rename(columns={
    "material_type": "material_type",
    "tensile_strength_mpa": "tensile_strength_mpa",
    "weight_capacity_kg": "weight_capacity_kg",
    "density_g_cm3": "density_g_cm3",
    "biodegradability_score": "biodegradability_score",
    "biodegradation_time_days": "biodegradation_time_days",
    "co2_emission_score": "co2_emission_score",
    "recyclability_percentage": "recyclability_percentage",
    "production_cost_per_kg_inr": "production_cost_per_kg"
})

# Keep only REQUIRED columns (drop optional/unwanted ones)
materials_df = materials_df[[
    "material_type",
    "tensile_strength_mpa",
    "weight_capacity_kg",
    "density_g_cm3",
    "biodegradability_score",
    "biodegradation_time_days",
    "co2_emission_score",
    "recyclability_percentage",
    "production_cost_per_kg"
]]

# Add primary key for database usage
materials_df.insert(0, "material_id", range(1, len(materials_df) + 1))

# Handle missing numerical values using median (evaluation requirement)
numeric_cols = materials_df.select_dtypes(include=[np.number]).columns
materials_df[numeric_cols] = materials_df[numeric_cols].fillna(
    materials_df[numeric_cols].median()
)

# Save cleaned & standardized dataset
output_path = "E:/EcoPackAI/data/processed/packaging_materials_clean.csv"
materials_df.to_csv(output_path, index=False)


# ================================
# PRODUCTS DATASET CLEANING
# ================================

# Loading the raw products dataset
products_path = "E:/EcoPackAI/data/raw/products.xlsx"
products_df = pd.read_excel(products_path)

# Standardizing column names for ML compatibility
products_df.columns = (
    products_df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Rename columns if required (safe mapping)
products_df = products_df.rename(columns={
    "weight_(kg)": "weight_kg"
})

# Keep only REQUIRED columns (drop unwanted ones)
products_df = products_df[[
    "category",
    "weight_kg",
    "fragility",
    "shipping_mode"
]]

# Add required new columns
products_df.insert(0, "product_id", range(1, len(products_df) + 1))
products_df["product_name"] = "Product_" + products_df["product_id"].astype(str)
products_df["industry_type"] = products_df["category"]
products_df["cost_sensitivity"] = 3
products_df["environmental_priority"] = 3

# Normalize fragility scale (1–5)
products_df["fragility"] = products_df["fragility"].astype(int)
products_df["fragility"] = products_df["fragility"].clip(1, 5)

# Handle missing numerical values
numeric_cols = products_df.select_dtypes(include=[np.number]).columns
products_df[numeric_cols] = products_df[numeric_cols].fillna(
    products_df[numeric_cols].median()
)

# Handle missing categorical values
products_df.fillna("Unknown", inplace=True)

# Save cleaned & standardized dataset
products_output_path = "E:/EcoPackAI/data/processed/products_clean.csv"
products_df.to_csv(products_output_path, index=False)
