import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# =========================
# LOAD DATA
# =========================

df = pd.read_excel("../../data/real_packaging_history.xlsx")

# Encode categorical feature
label_encoder = LabelEncoder()
df['Packaging_Used_Encoded'] = label_encoder.fit_transform(df['Packaging_Used'])

# Features and targets
X = df[['Distance_km', 'Packaging_Used_Encoded']]
y_cost = df['Cost_USD']
y_co2 = df['CO2_Emission_kg']

# Train-test split
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train models
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_cost_train)

xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
xgb_model.fit(X_train_scaled, y_co2_train)

# =========================
# SAVE MODELS
# =========================

joblib.dump(rf_model, "cost_model.pkl")
joblib.dump(xgb_model, "co2_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("Models trained and saved successfully.")
