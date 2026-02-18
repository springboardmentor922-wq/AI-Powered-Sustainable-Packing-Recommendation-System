import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# =========================
# LOAD DATA
# =========================

print("Loading dataset...")
df = pd.read_excel("data/real_packaging_history.xlsx")

print("Dataset shape:", df.shape)

# =========================
# ENCODE CATEGORICAL FEATURES
# =========================

le_packaging = LabelEncoder()
df['Packaging_Used_Encoded'] = le_packaging.fit_transform(df['Packaging_Used'])

le_category = LabelEncoder()
df['Category_Encoded'] = le_category.fit_transform(df['Category'])

le_shipping = LabelEncoder()
df['Shipping_Mode_Encoded'] = le_shipping.fit_transform(df['Shipping_Mode'])

print("Categorical encoding completed.")

# =========================
# FEATURE SELECTION
# =========================

X = df[
    [
        'Distance_km',
        'Weight_kg',
        'Volumetric_Weight_kg',
        'Fragility',
        'Moisture_Sens',
        'Category_Encoded',
        'Shipping_Mode_Encoded',
        'Packaging_Used_Encoded'
    ]
]

y = df['CO2_Emission_kg']

print("Feature matrix shape:", X.shape)

# =========================
# TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Train shape:", X_train.shape)
print("Test shape:", X_test.shape)

# =========================
# FEATURE SCALING
# =========================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Scaling completed.")

# =========================
# XGBOOST MODEL
# =========================

xgb_model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6,
    random_state=42
)

print("Training XGBoost model...")
xgb_model.fit(X_train_scaled, y_train)

# =========================
# EVALUATION
# =========================

y_pred = xgb_model.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nCO2 Prediction Model Evaluation:")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R2   : {r2:.4f}")

# =========================
# SAVE MODEL
# =========================

joblib.dump(xgb_model, "src/models/co2_model.pkl")

print("\nCO2 model saved successfully.")
