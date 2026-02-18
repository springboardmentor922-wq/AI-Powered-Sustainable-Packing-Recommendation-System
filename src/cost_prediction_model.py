import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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
# FEATURE SELECTION (RICH FEATURES)
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

y = df['Cost_USD']

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
# RANDOM FOREST MODEL
# =========================

rf_model = RandomForestRegressor(
    n_estimators=150,
    random_state=42
)

print("Training RandomForest model...")
rf_model.fit(X_train_scaled, y_train)

# =========================
# EVALUATION
# =========================

y_pred = rf_model.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nCost Prediction Model Evaluation:")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R2   : {r2:.4f}")

# =========================
# SAVE MODEL & ARTIFACTS
# =========================

joblib.dump(rf_model, "src/models/cost_model.pkl")
joblib.dump(scaler, "src/models/scaler.pkl")
joblib.dump(le_packaging, "src/models/label_encoder.pkl")
joblib.dump(le_category, "src/models/category_encoder.pkl")
joblib.dump(le_shipping, "src/models/shipping_encoder.pkl")

print("\nModel and preprocessing artifacts saved successfully.")
