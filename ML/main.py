import os
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 1. LOAD DATA
# ============================================================
_DEFAULT_DATASET_PATH = Path(__file__).resolve().parent / "dataset_with_material_references.csv"
DATASET_PATH = Path(os.getenv("ECOPACKAI_DATASET_PATH", str(_DEFAULT_DATASET_PATH)))

df = pd.read_csv(DATASET_PATH)

# Normalize categorical text
df['Main_Category'] = df['Main_Category'].str.upper().str.strip()
df['Packaging_Format'] = df['Packaging_Format'].str.upper().str.strip()

SUPPORTED_CATEGORIES = sorted(df['Main_Category'].unique())

# ============================================================
# 2. FEATURE ENGINEERING (SAFE)
# ============================================================

df['sustainability_score'] = df[
    ['Biodegradability_Score_Material',
     'Overall_Sustainability_Score',
     'Recyclability_Percentage_Material']
].mean(axis=1)

df['strength_score'] = df[
    ['Tensile_Strength_MPa',
     'Weight_Capacity_kg',
     'Thermal_Stability_C']
].mean(axis=1)

# Prevent division by zero
df['cost_efficiency'] = df['Weight_Capacity_kg'] / (df['Production_Cost_per_kg_INR'] + 1e-6)
df['eco_ratio'] = df['sustainability_score'] / (df['CO2_Emission_Packaging_kgCO2e'] + 1e-6)

# ============================================================
# 3. ML FEATURES & TARGETS
# ============================================================
ml_features = [
    'sustainability_score',
    'strength_score',
    'cost_efficiency',
    'eco_ratio',
    'Main_Category',
    'Packaging_Format'
]

targets = [
    'Production_Cost_per_kg_INR',
    'CO2_Emission_Packaging_kgCO2e'
]

data = df[
    ml_features + targets + [
        'Material_Name',
        'Primary_Material',
        'Shelf_Life_Days_Packaging',
        'Weight_Capacity_kg',
        'Overall_Sustainability_Score'
    ]
].dropna()

X = data[ml_features]
y_cost = data[targets[0]]
y_co2 = data[targets[1]]

print(f"✅ Clean ML dataset: {len(data):,} rows")

# ============================================================
# 4. PREPROCESSING & MODEL TRAINING
# ============================================================
numeric_cols = [
    'sustainability_score',
    'strength_score',
    'cost_efficiency',
    'eco_ratio'
]
categorical_cols = ['Main_Category', 'Packaging_Format']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
])

# Cost prediction model
cost_model = Pipeline([
    ('prep', preprocessor),
    ('rf', RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    ))
])

# CO2 prediction model
co2_model = Pipeline([
    ('prep', preprocessor),
    ('rf', RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    ))
])

# Train-test split
X_train, X_test, y_cost_train, y_cost_test = train_test_split(
    X, y_cost, test_size=0.2, random_state=42
)
_, _, y_co2_train, y_co2_test = train_test_split(
    X, y_co2, test_size=0.2, random_state=42
)

cost_model.fit(X_train, y_cost_train)
co2_model.fit(X_train, y_co2_train)

# ============================================================
# 5. AI RECOMMENDATION ENGINE
# ============================================================
def recommend_sustainable_packaging(
    category,
    budget,
    co2_limit,
    product_weight,
    shelf_life,
    top_n=5
):
    candidates = df[df['Main_Category'] == category].copy()
    if candidates.empty:
        return pd.DataFrame()

    # ML predictions
    ml_input = candidates[ml_features]
    candidates['predicted_cost'] = cost_model.predict(ml_input)
    candidates['predicted_co2'] = co2_model.predict(ml_input)

    # HARD PRACTICAL FILTERING
    candidates = candidates[
        (candidates['predicted_cost'] <= budget) &
        (candidates['predicted_co2'] <= co2_limit) &
        (candidates['Weight_Capacity_kg'] >= product_weight)
    ]

    if candidates.empty:
        return pd.DataFrame()

    # PRODUCT-AWARE SCORING
    weight_factor = min(product_weight / 5, 2.0)
    shelf_factor = np.minimum(
        candidates['Shelf_Life_Days_Packaging'] / shelf_life, 1
    )

    candidates['ai_score_raw'] = (
        0.35 * candidates['Overall_Sustainability_Score'] +
        0.25 * candidates['Weight_Capacity_kg'] * weight_factor +
        0.20 * shelf_factor * 100 +
        0.15 * (budget - candidates['predicted_cost']) / budget * 100 +
        0.05 * (co2_limit - candidates['predicted_co2']) / co2_limit * 100
    )

    # Normalize AI score (0–100)
    scaler = MinMaxScaler(feature_range=(0, 100))
    candidates['ai_score'] = scaler.fit_transform(
        candidates[['ai_score_raw']]
    )

    return candidates.sort_values('ai_score', ascending=False).head(top_n)

# ============================================================
# 6. INTERACTIVE RECOMMENDER
# ============================================================
def interactive_recommendation():
    print("\n" + "=" * 75)
    print("🎯 INTERACTIVE AI PACKAGING RECOMMENDER")
    print("=" * 75)

    category = input(
        f"Product category {tuple(c.title() for c in SUPPORTED_CATEGORIES)}: "
    ).strip().upper()

    if category not in SUPPORTED_CATEGORIES:
        print("\n❌ Invalid category entered.")
        print("✅ Supported categories:")
        for c in SUPPORTED_CATEGORIES:
            print(f"   • {c.title()}")
        return

    product_name = input("Product name: ").strip()
    product_weight = float(input("Product weight (kg) [default 2]: ") or 2)
    budget = float(input("Budget per kg ₹ [default 400]: ") or 400)
    max_co2 = float(input("Max CO₂ kg [default 2.5]: ") or 2.5)
    shelf_life = int(input("Required shelf life (days) [default 180]: ") or 180)

    recs = recommend_sustainable_packaging(
        category, budget, max_co2, product_weight, shelf_life
    )

    if recs.empty:
        print("\n❌ No packaging meets all constraints.")
        return

    print(f"\n🏆 TOP PACKAGING OPTIONS FOR: {product_name}")
    print("-" * 90)

    for i, (_, row) in enumerate(recs.iterrows(), 1):
        print(f"\n{i}. {row['Material_Name']} ({row['Primary_Material']})")
        print(f"   💰 Predicted Cost: ₹{row['predicted_cost']:.0f}/kg")
        print(f"   🌿 Predicted CO₂: {row['predicted_co2']:.2f} kg")
        print(f"   ⭐ Sustainability: {row['Overall_Sustainability_Score']:.0f}%")
        print(f"   📊 AI Suitability Score: {row['ai_score']:.1f}/100")

        print("   🧠 Why this material?")
        print("   • Fits product weight requirements")
        print("   • Meets budget and CO₂ limits")
        print("   • Suitable shelf life")
        print("   • High sustainability and recyclability")

# ============================================================
# 7. RUN SYSTEM
# ============================================================
if __name__ == "__main__":
    print("🤖 EcoPackAI – AI-Powered Sustainable Packaging Recommender")
    print("=" * 75)
    print(f"✅ Dataset Loaded: {df.shape[0]:,} materials")
    print(f"📦 Supported Categories: {', '.join(SUPPORTED_CATEGORIES)}")
    print("🔧 Engineering features...")
    print(f"✅ Cost Model R²: {r2_score(y_cost_test, cost_model.predict(X_test)):.3f}")
    print(f"✅ CO₂ Model R²: {r2_score(y_co2_test, co2_model.predict(X_test)):.3f}")

    while True:
        interactive_recommendation()
        if input("\nAnother recommendation? (y/n): ").lower() != 'y':
            break

    print("\n👋 Thank you for using EcoPackAI!")
