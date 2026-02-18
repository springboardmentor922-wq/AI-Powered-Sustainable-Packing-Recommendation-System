import pandas as pd

# Load cleaned history dataset
history_df = pd.read_excel("data/real_packaging_history.xlsx")

# Display basic info
print("Dataset shape:", history_df.shape)
print("\nColumns:")
print(history_df.columns)



from sklearn.preprocessing import LabelEncoder

# Encode Packaging_Used
label_encoder = LabelEncoder()
history_df['Packaging_Used_Encoded'] = label_encoder.fit_transform(
    history_df['Packaging_Used']
)

# Preview encoding
print("\nPackaging encoding preview:")
print(
    history_df[['Packaging_Used', 'Packaging_Used_Encoded']]
    .drop_duplicates()
    .head()
)



# =========================
# ML DATASET PREPARATION
# STEP 3: Define features and targets
# =========================

# Feature matrix
X = history_df[['Distance_km', 'Packaging_Used_Encoded']]

# Target variables
y_cost = history_df['Cost_USD']
y_co2 = history_df['CO2_Emission_kg']

# Verify shapes
print("\nFeature matrix shape (X):", X.shape)
print("Cost target shape (y_cost):", y_cost.shape)
print("CO2 target shape (y_co2):", y_co2.shape)



from sklearn.model_selection import train_test_split

# =========================
# ML DATASET PREPARATION
# STEP 4: Train-Test Split
# =========================

# Split for cost prediction
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

# Split for CO2 prediction (use same X split)
_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

# Verify shapes
print("\nTrain-test split shapes:")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)
print("y_cost_train:", y_cost_train.shape)
print("y_cost_test:", y_cost_test.shape)
print("y_co2_train:", y_co2_train.shape)
print("y_co2_test:", y_co2_test.shape)



from sklearn.preprocessing import StandardScaler

# =========================
# ML DATASET PREPARATION
# STEP 5: Feature Scaling
# =========================

scaler = StandardScaler()

# Fit scaler on training data
X_train_scaled = scaler.fit_transform(X_train)

# Transform test data
X_test_scaled = scaler.transform(X_test)

# Verify scaling
print("\nScaled feature sample (first 5 rows):")
print(X_train_scaled[:5])
