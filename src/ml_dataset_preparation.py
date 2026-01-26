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
