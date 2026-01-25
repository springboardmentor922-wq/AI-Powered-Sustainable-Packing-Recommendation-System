import pandas as pd

# Load datasets
materials_df = pd.read_excel("data/materials_database_600.xlsx")
history_df = pd.read_excel("data/real_packaging_history.xlsx")

# View first rows
print(materials_df.head())
print(history_df.head())

# =========================
# DATA CLEANING - STEP 1
# =========================

print("\nMissing values in history dataset:")
print(history_df.isnull().sum())


# =========================
# DATA CLEANING - STEP 2
# Handle Missing Values
# =========================

# Fill missing numerical values with mean
numerical_cols = [
    'Distance_km',
    'Cost_USD',
    'CO2_Emission_kg'
]


for col in numerical_cols:
    history_df[col].fillna(history_df[col].mean(), inplace=True)

# Fill missing categorical values with mode
history_df['Packaging_Used'].fillna(
    history_df['Packaging_Used'].mode()[0], inplace=True
)

print("\nMissing values after cleaning:")
print(history_df.isnull().sum())


# =========================
# DATA CLEANING - STEP 3
# Remove duplicate rows
# =========================

# Count duplicates before removal
duplicates_before = history_df.duplicated().sum()
print(f"\nDuplicate rows before removal: {duplicates_before}")

# Remove duplicates
history_df.drop_duplicates(inplace=True)

# Count duplicates after removal
duplicates_after = history_df.duplicated().sum()
print(f"Duplicate rows after removal: {duplicates_after}")


# =========================
# DATA CLEANING - STEP 4
# Basic data validation
# =========================

# Check for negative values
print("\nNegative value check:")

print("Negative Distance_km:", (history_df['Distance_km'] < 0).sum())
print("Negative Cost_USD:", (history_df['Cost_USD'] < 0).sum())
print("Negative CO2_Emission_kg:", (history_df['CO2_Emission_kg'] < 0).sum())



# =========================
# MATERIALS DATASET CLEANING
# STEP 1: Check missing values
# =========================

print("\nMissing values in materials dataset:")
print(materials_df.isnull().sum())


# =========================
# MATERIALS DATASET CLEANING
# STEP 2: Handle missing values
# =========================

# Fill missing numerical values with mean
material_numerical_cols = [
    'Density_kg_m3',
    'Tensile_Strength_MPa',
    'CO2_Emission_kg',
    'Cost_per_kg'
]

for col in material_numerical_cols:
    materials_df[col].fillna(materials_df[col].mean(), inplace=True)

# Fill missing categorical values with mode
materials_df['Category'].fillna(
    materials_df['Category'].mode()[0], inplace=True
)

materials_df['Biodegradable'].fillna(
    materials_df['Biodegradable'].mode()[0], inplace=True
)

print("\nMissing values in materials dataset after cleaning:")
print(materials_df.isnull().sum())



# =========================
# MATERIALS DATASET CLEANING
# STEP 3: Encode categorical values
# =========================

# Encode Biodegradable: Yes -> 1, No -> 0
materials_df['Biodegradable'] = materials_df['Biodegradable'].map({
    'Yes': 1,
    'No': 0
})

# Encode Category using label encoding
materials_df['Category_Encoded'] = materials_df['Category'].astype('category').cat.codes

# Display encoded columns
print("\nEncoded materials dataset preview:")
print(materials_df[['Category', 'Category_Encoded', 'Biodegradable']].head())
