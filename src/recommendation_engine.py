import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# =========================
# LOAD DATA
# =========================

materials_df = pd.read_excel("data/materials_processed.xlsx")

history_df = pd.read_excel("data/real_packaging_history.xlsx")

# Encode packaging type
label_encoder = LabelEncoder()
history_df['Packaging_Used_Encoded'] = label_encoder.fit_transform(
    history_df['Packaging_Used']
)

# =========================
# TRAIN COST MODEL
# =========================

X = history_df[['Distance_km', 'Packaging_Used_Encoded']]
y_cost = history_df['Cost_USD']
y_co2 = history_df['CO2_Emission_kg']

X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_cost_train)

xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
xgb_model.fit(X_train_scaled, y_co2_train)

# =========================
# USER INPUT (SIMULATION)
# =========================

user_distance = 500
user_packaging_type = history_df['Packaging_Used'].iloc[0]

user_packaging_encoded = label_encoder.transform([user_packaging_type])[0]

user_input = np.array([[user_distance, user_packaging_encoded]])
user_input_scaled = scaler.transform(user_input)

# Predictions
predicted_cost = rf_model.predict(user_input_scaled)[0]
predicted_co2 = xgb_model.predict(user_input_scaled)[0]

# =========================
# RANKING LOGIC
# =========================

# Normalize predicted values
materials_df['Predicted_Cost'] = predicted_cost
materials_df['Predicted_CO2'] = predicted_co2

# Normalize predicted cost & CO2
materials_df['Predicted_Cost_Normalized'] = (
    materials_df['Predicted_Cost'] - materials_df['Predicted_Cost'].min()
) / (
    materials_df['Predicted_Cost'].max() - materials_df['Predicted_Cost'].min() + 1e-6
)

materials_df['Predicted_CO2_Normalized'] = (
    materials_df['Predicted_CO2'] - materials_df['Predicted_CO2'].min()
) / (
    materials_df['Predicted_CO2'].max() - materials_df['Predicted_CO2'].min() + 1e-6
)

# Final Ranking Score
materials_df['Final_Ranking_Score'] = (
    0.4 * materials_df['Material_Suitability_Score'] +
    0.3 * (1 - materials_df['Predicted_Cost_Normalized']) +
    0.3 * (1 - materials_df['Predicted_CO2_Normalized'])
)

# Display Top 5
top_materials = materials_df.sort_values(
    by='Final_Ranking_Score',
    ascending=False
).head(5)

print("\nTop 5 Recommended Materials:")
print(top_materials[['Material_Name', 'Final_Ranking_Score']])
