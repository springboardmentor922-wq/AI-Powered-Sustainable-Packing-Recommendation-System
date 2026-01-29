from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

def load_materials_data():
    """Load the materials database"""
    try:
        materials_df = pd.read_csv('materials_cleaned_engineered.csv')
        print(f"✓ Loaded materials database: {materials_df.shape}")
        return materials_df
    except FileNotFoundError:
        print("⚠ Materials database not found. Using sample data.")
        # Create sample data for demonstration
        return create_sample_data()

def create_sample_data():
    """Create sample materials data for demonstration"""
    data = {
        'material_name': ['Cardboard Box', 'Plastic Container', 'Biodegradable Wrap', 'Paper Bag', 'Foam Padding'],
        'material_type': ['Cardboard', 'Plastic', 'Biodegradable', 'Paper', 'Foam'],
        'strength': [70, 85, 60, 45, 30],
        'cost_per_unit': [2.5, 3.8, 4.2, 1.8, 2.1],
        'co2_emission_score': [25, 75, 15, 20, 60],
        'biodegradability': [90, 10, 95, 85, 5],
        'recyclability': [95, 70, 80, 90, 20],
        'environmental_score': [85, 35, 90, 80, 25],
        'cost_efficiency_index': [28.0, 22.4, 14.3, 25.0, 14.3],
        'co2_impact_index': [67.5, 11.7, 76.0, 72.0, 8.0],
        'material_suitability_score': [118.8, 44.1, 102.0, 81.0, 12.0]
    }
    return pd.DataFrame(data)

# Load data
materials_df = load_materials_data()

# ============================================================================
# TRAIN ML MODELS
# ============================================================================

def train_models():
    """Train the ML models for cost and CO2 prediction"""
    # Identify feature columns
    exclude_cols = ['material_name', 'material_type', 'cost_per_unit', 'co2_emission_score',
                    'co2_impact_index', 'cost_efficiency_index', 'material_suitability_score',
                    'environmental_score']

    feature_cols = [col for col in materials_df.columns
                    if col not in exclude_cols and materials_df[col].dtype in ['int64', 'float64']]

    if not feature_cols:
        feature_cols = ['strength', 'biodegradability', 'recyclability']

    X = materials_df[feature_cols].fillna(0)

    # Find cost and CO2 columns
    cost_col = 'cost_per_unit' if 'cost_per_unit' in materials_df.columns else None
    co2_col = 'co2_emission_score' if 'co2_emission_score' in materials_df.columns else None

    # Train Cost Prediction Model
    rf_cost = None
    if cost_col and cost_col in materials_df.columns:
        y_cost = materials_df[cost_col].fillna(materials_df[cost_col].median())
        X_train, X_test, y_train, y_test = train_test_split(X, y_cost, test_size=0.2, random_state=42)
        rf_cost = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
        rf_cost.fit(X_train, y_train)
        print(f"✓ Cost Model R² Score: {r2_score(y_test, rf_cost.predict(X_test)):.4f}")

    # Train CO2 Prediction Model
    rf_co2 = None
    if co2_col and co2_col in materials_df.columns:
        y_co2 = materials_df[co2_col].fillna(materials_df[co2_col].median())
        X_train, X_test, y_train, y_test = train_test_split(X, y_co2, test_size=0.2, random_state=42)
        rf_co2 = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
        rf_co2.fit(X_train, y_train)
        print(f"✓ CO2 Model R² Score: {r2_score(y_test, rf_co2.predict(X_test)):.4f}")

    return rf_cost, rf_co2, cost_col, co2_col

rf_cost, rf_co2, cost_col, co2_col = train_models()

# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class EcoPackRecommendationEngine:
    """AI-Powered Packaging Material Recommendation System"""

    def __init__(self, materials_df, cost_model=None, co2_model=None):
        self.materials_df = materials_df
        self.cost_model = cost_model
        self.co2_model = co2_model

    def get_recommendations(self, product_input, top_n=5, prioritize='balanced'):
        """Get top N packaging material recommendations"""

        filtered_materials = self.materials_df.copy()

        # Filter by material type if specified
        if 'material_type' in product_input and product_input['material_type']:
            material_type = product_input['material_type']
            if 'material_type' in filtered_materials.columns:
                filtered_materials = filtered_materials[
                    filtered_materials['material_type'].astype(str).str.contains(
                        material_type, case=False, na=False
                    )
                ]

        # Apply strength requirement
        if 'required_strength' in product_input:
            min_strength = product_input['required_strength']
            if 'strength' in filtered_materials.columns:
                filtered_materials = filtered_materials[
                    filtered_materials['strength'] >= min_strength
                ]

        # Calculate recommendation scores
        scores = []
        for idx, material in filtered_materials.iterrows():
            env_score = material.get('environmental_score', 50)
            cost_eff = material.get('cost_efficiency_index', 1)
            co2_impact = material.get('co2_impact_index', 50)
            suitability = material.get('material_suitability_score', 50)

            if prioritize == 'cost':
                final_score = (0.5 * cost_eff + 0.3 * suitability + 0.2 * env_score)
            elif prioritize == 'environment':
                final_score = (0.5 * env_score + 0.3 * co2_impact + 0.2 * suitability)
            else:  # balanced
                final_score = (0.3 * env_score + 0.3 * cost_eff + 0.2 * co2_impact + 0.2 * suitability)

            scores.append(final_score)

        filtered_materials['recommendation_score'] = scores
        recommendations = filtered_materials.nlargest(top_n, 'recommendation_score')

        # Prepare output
        output_cols = ['material_name', 'recommendation_score', 'environmental_score',
                      'cost_efficiency_index', 'co2_impact_index', 'material_suitability_score']

        if 'material_type' in recommendations.columns:
            output_cols.insert(1, 'material_type')

        if cost_col and cost_col in recommendations.columns:
            output_cols.append(cost_col)
        if co2_col and co2_col in recommendations.columns:
            output_cols.append(co2_col)

        output_cols = [col for col in output_cols if col in recommendations.columns]
        result = recommendations[output_cols].copy()
        result['rank'] = range(1, len(result) + 1)

        return result

# Initialize engine
engine = EcoPackRecommendationEngine(materials_df, rf_cost, rf_co2)

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """API endpoint for getting recommendations"""
    try:
        data = request.get_json()

        product_input = {
            'item_name': data.get('item_name', 'Product'),
            'product_category': data.get('product_category', 'General'),
            'material_type': data.get('material_type') if data.get('material_type') else None,
            'product_weight': float(data.get('product_weight', 1.0)),
            'fragility': data.get('fragility', 'Medium'),
            'required_strength': float(data.get('required_strength', 50)),
            'shipping_distance': data.get('shipping_distance', 'Regional')
        }

        top_n = int(data.get('top_n', 5))
        prioritize = data.get('prioritize', 'balanced')

        recommendations = engine.get_recommendations(product_input, top_n, prioritize)

        # Convert to dict for JSON response
        result = recommendations.to_dict('records')

        return jsonify({
            'success': True,
            'recommendations': result,
            'product_input': product_input
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/materials', methods=['GET'])
def get_materials():
    """Get all available materials"""
    try:
        materials = materials_df[['material_name', 'material_type']].to_dict('records')
        return jsonify({
            'success': True,
            'materials': materials
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
