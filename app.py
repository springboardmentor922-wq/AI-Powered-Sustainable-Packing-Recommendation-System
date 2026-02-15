from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load models
class ModelLoader:
    def __init__(self, model_dir="deployment_models"):
        self.model_dir = model_dir
        self.load_models()
    
    def load_models(self):
        """Load all trained models and components"""
        try:
            # Load models
            self.co2_model = joblib.load(f"{self.model_dir}/co2_prediction_model.joblib")
            self.cost_model = joblib.load(f"{self.model_dir}/cost_prediction_model.joblib")
            
            # Load encoders
            self.co2_encoder = joblib.load(f"{self.model_dir}/co2_label_encoder.joblib")
            self.cost_encoder = joblib.load(f"{self.model_dir}/cost_label_encoder.joblib")
            
            # Load feature orders
            self.co2_feature_order = joblib.load(f"{self.model_dir}/co2_feature_order.joblib")
            self.cost_feature_order = joblib.load(f"{self.model_dir}/cost_feature_order.joblib")
            
            # Load materials database
            self.materials_df = joblib.load(f"{self.model_dir}/materials_database.joblib")
            
            # Load metadata
            self.metadata = joblib.load(f"{self.model_dir}/model_metadata.joblib")
            
            print("✅ All models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise

# Initialize models
try:
    models = ModelLoader()
except Exception as e:
    print(f"❌ Failed to load models: {e}")
    models = None

def get_recommendations(weight_kg, volume_m3, distance_km, shipping_mode, weight_co2=0.6, weight_cost=0.4):
    """Generate packaging recommendations"""
    if models is None:
        return []
    
    try:
        input_data = pd.DataFrame({
            'Weight_kg': [weight_kg],
            'Product_Volume_m3': [volume_m3], 
            'Distance_km': [distance_km],
            'Shipping_Mode': [shipping_mode]
        })
        
        recommendations = []
        for _, material in models.materials_df.iterrows():
            test_input = input_data.copy()
            test_input['Material_Name'] = material['Material_Name']
            test_input['Category'] = material['Category']
            test_input['Material_Density'] = material['Density_kg_m3']
            test_input['Cost_per_kg'] = material['Cost_per_kg']
            test_input['CO2_Emission_kg'] = material['CO2_Emission_kg']
            test_input['Biodegradable'] = material['Biodegradable']
            
            # Model is producing invalid constant output, using formula-based estimation
            # CO2 = (Weight * Material_CO2) + (Weight * Distance * Mode_Factor)
            # Cost = (Weight * Material_Cost) + (Weight * Distance * Mode_Cost_Factor)
            
            # Factors per kg/km
            mode_co2_factors = {
                'Air': 0.00113,
                'Road': 0.00018,
                'Rail': 0.00006,
                'Sea': 0.00002
            }
            mode_cost_factors = {
                'Air': 0.004,
                'Road': 0.0015,
                'Rail': 0.0008,
                'Sea': 0.0004
            }
            
            shipping_co2_factor = mode_co2_factors.get(shipping_mode, 0.00018)
            shipping_cost_factor = mode_cost_factors.get(shipping_mode, 0.0015)
            
            # Calculate Production CO2
            material_co2 = weight_kg * material['CO2_Emission_kg']
            # Calculate Shipping CO2
            transport_co2 = weight_kg * distance_km * shipping_co2_factor
            
            co2_pred = material_co2 + transport_co2
            
            # Calculate Material Cost
            material_cost = weight_kg * material['Cost_per_kg']
            # Calculate Shipping Cost
            transport_cost = weight_kg * distance_km * shipping_cost_factor
            
            cost_pred = material_cost + transport_cost
            
            recommendations.append({
                'Material_Name': material['Material_Name'],
                'Category': material['Category'],
                'Predicted_CO2_kg': float(co2_pred),
                'Predicted_Cost_USD': float(cost_pred),
                'Biodegradable': bool(material['Biodegradable'])
            })
        
        recommendations_df = pd.DataFrame(recommendations)
        
        if not recommendations_df.empty:
            # Normalize scores
            co2_min = recommendations_df['Predicted_CO2_kg'].min()
            co2_max = recommendations_df['Predicted_CO2_kg'].max()
            cost_min = recommendations_df['Predicted_Cost_USD'].min()
            cost_max = recommendations_df['Predicted_Cost_USD'].max()
            
            # Helper for safe division
            def normalize(val, min_val, max_val):
                if max_val == min_val:
                    return 0.0
                return (val - min_val) / (max_val - min_val)
            
            recommendations_df['CO2_Score'] = recommendations_df['Predicted_CO2_kg'].apply(
                lambda x: normalize(x, co2_min, co2_max)
            )
            recommendations_df['Cost_Score'] = recommendations_df['Predicted_Cost_USD'].apply(
                lambda x: normalize(x, cost_min, cost_max)
            )
            
            # Calculate combined score
            recommendations_df['Combined_Score'] = (
                weight_co2 * recommendations_df['CO2_Score'] + 
                weight_cost * recommendations_df['Cost_Score']
            )
            
            # Round values for display
            recommendations_df['Predicted_CO2_kg'] = recommendations_df['Predicted_CO2_kg'].round(3)
            recommendations_df['Predicted_Cost_USD'] = recommendations_df['Predicted_Cost_USD'].round(2)
            recommendations_df['Combined_Score'] = recommendations_df['Combined_Score'].round(3)
            
            return recommendations_df.sort_values('Combined_Score').head(5).to_dict('records')
        
        return []
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise e

@app.route('/')
def home():
    """Main page with interactive form"""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint for packaging recommendations"""
    print("DEBUG: Handling /recommend request", flush=True)
    try:
        if models is None:
            return jsonify({'error': 'Models not loaded. Please check server configuration.'}), 500
        
        data = request.get_json()
        
        # Validate input data
        required_fields = ['weight_kg', 'volume_m3', 'distance_km', 'shipping_mode', 'optimization']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate numeric values
        if data['weight_kg'] <= 0 or data['volume_m3'] <= 0 or data['distance_km'] <= 0:
            return jsonify({'error': 'Weight, volume, and distance must be positive values'}), 400
        
        # Set optimization weights
        if data['optimization'] == 'eco':
            weight_co2, weight_cost = 0.8, 0.2
        elif data['optimization'] == 'cost':
            weight_co2, weight_cost = 0.2, 0.8
        else:
            weight_co2, weight_cost = 0.6, 0.4
        
        recommendations = get_recommendations(
            data['weight_kg'], data['volume_m3'], data['distance_km'], 
            data['shipping_mode'], weight_co2, weight_cost
        )
        
        if not recommendations:
            return jsonify({'error': 'Unable to generate recommendations. Please check your input parameters.'}), 500
        
        return jsonify(recommendations)
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': models is not None,
        'model_version': models.metadata.get('model_version', 'unknown') if models else 'unknown'
    })

@app.route('/model-info')
def model_info():
    """Get model information and statistics"""
    if models is None:
        return jsonify({'error': 'Models not loaded'}), 500
    
    return jsonify({
        'model_version': models.metadata.get('model_version', 'unknown'),
        'training_date': models.metadata.get('training_date', 'unknown'),
        'co2_model_type': models.metadata.get('co2_model_type', 'unknown'),
        'cost_model_type': models.metadata.get('cost_model_type', 'unknown'),
        'co2_rmse': models.metadata.get('co2_rmse', 'unknown'),
        'co2_mae': models.metadata.get('co2_mae', 'unknown'),
        'cost_rmse': models.metadata.get('cost_rmse', 'unknown'),
        'cost_mae': models.metadata.get('cost_mae', 'unknown'),
        'total_materials': models.metadata.get('total_materials', 0),
        'categories': models.metadata.get('categories', [])
    })

if __name__ == '__main__':
    print("🚀 Starting Eco-Friendly Packaging Recommendation System...")
    print("📱 Access the web interface at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("📊 Model info: http://localhost:5000/model-info")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)

