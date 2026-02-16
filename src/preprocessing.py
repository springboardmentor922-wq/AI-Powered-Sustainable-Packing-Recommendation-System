import pandas as pd
from sklearn.preprocessing import LabelEncoder

def load_and_preprocess_data(filepath):
    df = pd.read_excel(filepath)
    df = df.dropna()

    le = LabelEncoder()
    df['Category'] = le.fit_transform(df['Category'])
    df['Biodegradable'] = df['Biodegradable'].map({'Yes': 1, 'No': 0})

    # Feature Engineering
    df['CO2_Impact_Index'] = df['CO2_Emission_kg'] / df['Density_kg_m3']
    df['Cost_Efficiency_Index'] = df['Tensile_Strength_MPa'] / df['Cost_per_kg']
    df['Material_Suitability_Score'] = (
        df['Biodegradable'] * 2 +
        df['Cost_Efficiency_Index'] -
        df['CO2_Impact_Index']
    )

    return df