# EcoPackAI - Sustainable Packaging Recommendation System

An AI-powered web application that recommends sustainable packaging materials based on product specifications and environmental impact analysis.

## Features

- **AI-Powered Recommendations**: Machine learning models analyze materials based on environmental impact, cost efficiency, and suitability
- **Interactive Web Interface**: Modern, responsive frontend built with Bootstrap
- **RESTful API**: Flask backend providing recommendation endpoints
- **Sustainability Metrics**: Comprehensive scoring system including CO₂ impact, biodegradability, and recyclability
- **Customizable Criteria**: Filter by material type, strength requirements, and optimization priorities

## Project Structure

```
ecopackai/
├── app.py                 # Flask backend application
├── templates/
│   └── index.html         # Frontend interface
├── requirements.txt       # Python dependencies
├── materials_cleaned_engineered.csv  # Materials database (optional)
└── README.md             # This file
```

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Add materials database**
   - Place your `materials_cleaned_engineered.csv` file in the project root
   - If not available, the application will use sample data for demonstration

## Usage

### Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

### Using the Web Interface

1. **Enter Product Details**:
   - Product name and category
   - Preferred material type (optional)
   - Product weight, fragility, and strength requirements
   - Shipping distance

2. **Set Preferences**:
   - Number of recommendations (3, 5, or 10)
   - Optimization priority (Balanced, Cost, or Environment)

3. **Get Recommendations**:
   - Click "Get Recommendations" to receive AI-powered suggestions
   - View detailed scores and sustainability metrics
   - Best recommendation is highlighted with ranking

### API Usage

The application provides RESTful API endpoints:

#### Get Recommendations
```http
POST /api/recommend
Content-Type: application/json

{
  "item_name": "iPhone 15",
  "product_category": "Electronics",
  "material_type": "Cardboard",
  "product_weight": 2.5,
  "fragility": "Medium",
  "required_strength": 70,
  "shipping_distance": "Regional",
  "top_n": 5,
  "prioritize": "balanced"
}
```

#### Get Available Materials
```http
GET /api/materials
```

## Recommendation Algorithm

The system uses a multi-criteria decision analysis approach:

### Scoring Components
- **Environmental Score**: Based on biodegradability, recyclability, and CO₂ emissions
- **Cost Efficiency Index**: Strength-to-cost ratio
- **CO₂ Impact Index**: Environmental impact assessment
- **Material Suitability Score**: Overall material performance

### Optimization Priorities
- **Balanced**: Equal weighting of environmental, cost, and suitability factors
- **Cost Priority**: Emphasizes cost efficiency and suitability
- **Environment Priority**: Prioritizes environmental impact and CO₂ reduction

## Data Requirements

The system expects a materials database with the following key columns:
- `material_name`: Name of the packaging material
- `material_type`: Category (Cardboard, Plastic, Biodegradable, etc.)
- `strength`: Material strength rating (0-100)
- `cost_per_unit`: Cost per unit
- `co2_emission_score`: CO₂ emission rating
- `biodegradability`: Biodegradability percentage
- `recyclability`: Recyclability percentage
- `environmental_score`: Overall environmental rating

## Machine Learning Models

The application trains two Random Forest models:
1. **Cost Prediction Model**: Predicts material costs based on properties
2. **CO₂ Prediction Model**: Predicts environmental impact

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Visualization**: Matplotlib, Seaborn

## Development

### Adding New Materials
1. Update the materials database CSV file
2. Ensure required columns are present
3. Restart the application to reload data

### Customizing the Algorithm
Modify the scoring logic in the `EcoPackRecommendationEngine.get_recommendations()` method in `app.py`.

### Extending the API
Add new endpoints in `app.py` following the existing pattern.

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For questions or issues, please check the code comments or create an issue in the repository.
