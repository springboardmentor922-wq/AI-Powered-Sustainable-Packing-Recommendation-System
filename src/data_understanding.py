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
