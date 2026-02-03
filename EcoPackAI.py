import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor




def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    num_cols = df.select_dtypes(include=[np.number]).columns
    cat_cols = df.select_dtypes(include=["object", "string"]).columns  # ✅ FIX

    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    df[cat_cols] = df[cat_cols].fillna("Unknown")

    return df




orders_df = clean_data(pd.read_csv("materials.cvs1.csv"))
materials_df = clean_data(pd.read_csv("materials_cvs2.csv"))




materials_df["Biodegradable_Binary"] = (
    materials_df["Biodegradable"].map({"Yes": 1, "No": 0}).fillna(0)
)

materials_df["CO2_Impact_Index"] = (
    materials_df["CO2_Emission_kg"] *
    (1.5 - 0.5 * materials_df["Biodegradable_Binary"])
)

materials_df["Cost_Efficiency_Index"] = (
    materials_df["Tensile_Strength_MPa"] /
    (materials_df["Cost_per_kg"] + 0.01)
)

materials_df["Material_Suitability_Score"] = (
    0.4 * materials_df["Tensile_Strength_MPa"] +
    0.3 * (1 - materials_df["CO2_Emission_kg"] /
           materials_df["CO2_Emission_kg"].max()) +
    0.3 * materials_df["Biodegradable_Binary"]
)

materials_df.to_csv("cleaned_materials_data.csv", index=False)




packaging_mapping = {
    "Kraft Paper Mailer": "Single-Ply Kraft Paper",
    "Mushroom Pkg (Mycelium)": "Food-Grade Mushroom Mycelium",
    "Wood Crate": "Lightweight Plywood",
    "PLA Bioplastic": "Medical-Grade PLA Bioplastic",
    "Honeycomb Paper": "Food-Grade Wax Paper",
    "Recycled PET Box": "Lightweight PET Plastic",
    "Bubble Wrap (LDPE)": "UV-Stabilized Polyurethane Foam",
    "Corrugated Cardboard": "Heavy-Duty Corrugated Cardboard",
    "Styrofoam (EPS)": "Double-Wall Cornstarch Foam"
}

orders_df["Material_Match"] = orders_df["Packaging_Used"].map(packaging_mapping)

merged_df = pd.merge(
    orders_df,
    materials_df,
    left_on="Material_Match",
    right_on="Material_Name",
    how="left"
).drop(columns=["Material_Match"])

merged_df = merged_df.rename(columns={
    "Category_x": "Product_Category",
    "Category_y": "Material_Category"
})

merged_df.to_csv("cleaned_and_merged_eco_data.csv", index=False)




features = [
    "Weight_kg",
    "Distance_km",
    "Fragility",
    "Moisture_Sens",
    "Shipping_Mode",
    "Product_Category"
]

X = merged_df[features]
y_cost = merged_df["Cost_USD"]
y_co2 = merged_df["CO2_Emission_kg_x"]

numeric_features = ["Weight_kg", "Distance_km", "Fragility"]
categorical_features = ["Shipping_Mode", "Product_Category", "Moisture_Sens"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])

cost_model = Pipeline([
    ("prep", preprocessor),
    ("model", RandomForestRegressor(n_estimators=120, random_state=42))
])

co2_model = Pipeline([
    ("prep", preprocessor),
    ("model", GradientBoostingRegressor(n_estimators=120, random_state=42))
])

X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)

_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

cost_model.fit(X_train, y_cost_train)
co2_model.fit(X_train, y_co2_train)



def ai_material_ranking(product_features: dict) -> pd.DataFrame:
    materials = pd.read_csv("cleaned_materials_data.csv")

    # -------------------------------------------------
    # 1. ML PREDICTION (PRODUCT + SHIPPING IMPACT)
    # -------------------------------------------------
    product_df = pd.DataFrame([product_features])

    shipping_cost = float(cost_model.predict(product_df)[0])
    shipping_co2  = float(abs(co2_model.predict(product_df)[0]))

    # -------------------------------------------------
    # 2. MATERIAL-SPECIFIC TOTAL IMPACT
    # -------------------------------------------------
    materials["Pred_Cost"] = (
        shipping_cost +
        (materials["Cost_per_kg"] * product_features["Weight_kg"])
    )

    materials["Pred_CO2"] = (
        shipping_co2 +
        materials["CO2_Emission_kg"]
    )

    # -------------------------------------------------
    # 3. SAFE NORMALIZATION (0–100)
    # -------------------------------------------------
    def safe_minmax(series):
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series))
        return 100 * (series - min_val) / (max_val - min_val)

    materials["Cost_Score"] = 100 - safe_minmax(materials["Pred_Cost"])
    materials["CO2_Score"] = 100 - safe_minmax(materials["Pred_CO2"])
    materials["Durability_Score"] = safe_minmax(materials["Tensile_Strength_MPa"])
    materials["Biodegradable_Score"] = materials["Biodegradable_Binary"] * 100

    # -------------------------------------------------
    # 4. FINAL ECOPACK SCORE (0–100, higher = better)
    # -------------------------------------------------
    materials["EcoPack_Score"] = (
        0.4 * materials["CO2_Score"] +
        0.3 * materials["Cost_Score"] +
        0.2 * materials["Durability_Score"] +
        0.1 * materials["Biodegradable_Score"]
    ).round(2)

    # -------------------------------------------------
    # 5. RETURN TOP 5
    # -------------------------------------------------
    return materials.sort_values("EcoPack_Score", ascending=False).head(5)[[
        "Material_Name",
        "Category",
        "Pred_Cost",
        "Pred_CO2",
        "Durability_Score",
        "Biodegradable_Score",
        "EcoPack_Score"
    ]]