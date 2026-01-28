# ================================
# MODULE 4: MODEL TRAINING
# Step 1: Load data & pipelines
# ================================

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split

# Load engineered dataset
data_path = "E:/EcoPackAI/data/processed/packaging_materials_engineered.csv"
df = pd.read_csv(data_path)

# Feature set
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


# Targets
y_cost = df["production_cost_per_kg"]
y_co2 = df["co2_emission_score"]

# Train-test split
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

# Load pipelines
cost_pipeline = joblib.load("E:/EcoPackAI/models/cost_pipeline.pkl")
co2_pipeline = joblib.load("E:/EcoPackAI/models/co2_pipeline.pkl")

# Apply scaling
X_cost_train = X_train
X_cost_test = X_test

X_co2_train = X_train
X_co2_test = X_test

print("Data loaded and transformed successfully.")

# ================================
# Step 2: Train ML Models
# ================================

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# Random Forest for cost prediction
cost_model = RandomForestRegressor(
    n_estimators=400,
    max_depth=12,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

# XGboost for co2 emission prediction
co2_model = XGBRegressor(
    n_estimators=350,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    objective="reg:squarederror",
    random_state=42
)

cost_model.fit(X_cost_train, y_cost_train)
co2_model.fit(X_co2_train, y_co2_train)
print("Models trained successfully.")


# ================================
# Step 3: Model Evaluation
# ================================

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Predictions
cost_preds = cost_model.predict(X_cost_test)
co2_preds = co2_model.predict(X_co2_test)

# Cost model evaluation
cost_rmse = np.sqrt(mean_squared_error(y_cost_test, cost_preds))
cost_mae = mean_absolute_error(y_cost_test, cost_preds)
cost_r2 = r2_score(y_cost_test, cost_preds)

# CO2 model evaluation
co2_rmse = np.sqrt(mean_squared_error(y_co2_test, co2_preds))
co2_mae = mean_absolute_error(y_co2_test, co2_preds)
co2_r2 = r2_score(y_co2_test, co2_preds)

print("\nCOST MODEL METRICS")
print("RMSE:", round(cost_rmse, 4))
print("MAE:", round(cost_mae, 4))
print("R2 Score:", round(cost_r2, 4))

print("\nCO2 MODEL METRICS")
print("RMSE:", round(co2_rmse, 4))
print("MAE:", round(co2_mae, 4))
print("R2 Score:", round(co2_r2, 4))


# ================================
# SAVE FINAL HIGH-ACCURACY MODELS
# ================================


joblib.dump(cost_model, "E:/EcoPackAI/models/cost_model.pkl")
joblib.dump(co2_model, "E:/EcoPackAI/models/co2_model.pkl")

print("Final models saved in E:/EcoPackAI/models/")

# ================================
# FINAL AI RECOMMENDATION EXPORT
# ================================

# Use full dataset for recommendation
df_full = df.copy()

X_full = df_full[[
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

# Predict using trained models
df_full["predicted_cost"] = cost_model.predict(X_full)
df_full["predicted_co2"] = co2_model.predict(X_full)

# Normalize predictions
df_full["predicted_cost_norm"] = (
    (df_full["predicted_cost"] - df_full["predicted_cost"].min()) /
    (df_full["predicted_cost"].max() - df_full["predicted_cost"].min())
)

df_full["predicted_co2_norm"] = (
    (df_full["predicted_co2"] - df_full["predicted_co2"].min()) /
    (df_full["predicted_co2"].max() - df_full["predicted_co2"].min())
)

# Final AI recommendation score
df_full["ai_recommendation_score"] = (
    (1 - df_full["predicted_cost_norm"]) * 0.4 +
    (1 - df_full["predicted_co2_norm"]) * 0.4 +
    df_full["material_suitability_score"] * 0.2
)

# Rank materials
df_ranked = df_full.sort_values("ai_recommendation_score", ascending=False)

# Save ranked materials
output_path = "E:/EcoPackAI/data/processed/materials_ranked.csv"
df_ranked.to_csv(output_path, index=False)

print("materials_ranked.csv generated successfully.")
