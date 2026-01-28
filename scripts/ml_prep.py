# ================================
# MODULE 3: ML DATASET PREPARATION
# Step 1: Feature & Target Setup
# ================================

import pandas as pd
from sklearn.model_selection import train_test_split

# Load engineered dataset
data_path = "E:/EcoPackAI/data/processed/packaging_materials_engineered.csv"
df = pd.read_csv(data_path)

# Feature set (X)
X = df[[
    "tensile_strength_mpa",
    "weight_capacity_kg",
    "density_g_cm3",
    "biodegradability_score",
    "biodegradation_time_days",
    "recyclability_percentage"
]]

# Targets
y_cost = df["production_cost_per_kg"]
y_co2 = df["co2_emission_score"]

print("Features and targets selected.")

# ================================
# Step 2: Train-Test Split
# ================================

X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

print("Train-test split completed.")
print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# ================================
# Step 3: ML Pipelines
# ================================

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Pipeline for cost prediction
cost_pipeline = Pipeline(steps=[
    ("scaler", StandardScaler())
])

# Pipeline for CO2 prediction
co2_pipeline = Pipeline(steps=[
    ("scaler", StandardScaler())
])

# Fit pipelines on training data
X_cost_train = cost_pipeline.fit_transform(X_train)
X_cost_test = cost_pipeline.transform(X_test)

X_co2_train = co2_pipeline.fit_transform(X_train)
X_co2_test = co2_pipeline.transform(X_test)

print(" ML pipelines created and applied successfully.")

import joblib

joblib.dump(cost_pipeline, "E:/EcoPackAI/models/cost_pipeline.pkl")
joblib.dump(co2_pipeline, "E:/EcoPackAI/models/co2_pipeline.pkl")

print(" Pipelines saved successfully.")
