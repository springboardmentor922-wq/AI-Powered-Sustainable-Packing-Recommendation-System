import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np

# =========================
# LOAD DATA
# =========================

df = pd.read_excel("data/real_packaging_history.xlsx")

# Encode categorical feature
label_encoder = LabelEncoder()
df['Packaging_Used_Encoded'] = label_encoder.fit_transform(df['Packaging_Used'])

# Features and target
X = df[['Distance_km', 'Packaging_Used_Encoded']]
y = df['Cost_USD']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =========================
# RANDOM FOREST MODEL
# =========================

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

rf_model.fit(X_train_scaled, y_train)

# Predictions
y_pred = rf_model.predict(X_test_scaled)

# =========================
# EVALUATION
# =========================

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nCost Prediction Model Evaluation:")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R2   : {r2:.3f}")


import pickle

print(type(rf_model))
print(hasattr(rf_model, "predict"))

with open("cost_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)

print("Cost model saved successfully")
