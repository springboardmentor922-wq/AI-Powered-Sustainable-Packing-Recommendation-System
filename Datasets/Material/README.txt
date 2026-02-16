ECO-FRIENDLY MATERIALS DATASET – INDIA EDITION
AI-Driven Sustainable Packaging Recommendation (9,000 Records, 30 Features)


1. OVERVIEW
-----------
This package contains an India-adapted eco-friendly materials dataset for training machine learning models that recommend sustainable packaging options. The data focuses on biodegradable, recyclable, and low-impact materials suitable for Indian food, agriculture, and e-commerce use cases.

Developed for: Campus placement preparation, internship projects, ML model training, and production-ready packaging recommendation systems.


2. INCLUDED FILES
-----------------

📦 MAIN DATASET (EXCEL)
   ├─ Eco_Friendly_Materials_India_Adapted_9000_Records.xlsx (1.71 MB)
   │  ├─ Sheet 1: Complete_Dataset (9,000 records × 30 features)
   │  ├─ Sheet 2: Summary (high-level metrics & overview)
   │  ├─ Sheet 3: Statistics (descriptive statistics for all numeric features)
   │  ├─ Sheet 4: Material_Types (30 material categories with distribution)
   │  ├─ Sheet 5: Regional_Analysis (5 Indian regions breakdown)
   │  ├─ Sheet 6: Feature_Dictionary (complete field descriptions)
   │  └─ Sheet 7: India_Certifications (certification reference guide)

📄 DOCUMENTATION FILES
   ├─ Dataset_Guide.md
   │  ├─ Detailed schema explanation
   │  ├─ Feature descriptions & purposes
   │  ├─ ML workflow examples (regression, recommendation, ranking)
   │  ├─ Data preparation tips
   │  └─ Python/R code snippets
   │
   ├─ Dataset_Summary_Metrics.csv
   │  ├─ Quick technical metrics
   │  ├─ Min/max/mean for all numeric features
   │  ├─ Count of categorical options
   │  └─ Data quality indicators
   │
   └─ README.txt (this file)
      ├─ Quick start guide
      ├─ File structure overview
      ├─ Use case examples
      └─ Contact/extension information


3. KEY CHARACTERISTICS
----------------------

DATA SCALE & STRUCTURE:
- Records: 9,000 eco-friendly material entries
- Features: 30 structured attributes
- Data Points: 270,000 (9,000 × 30)
- File Size: ~1.71 MB (Excel)
- Format: .xlsx (Excel 2016+, LibreOffice, Google Sheets compatible)

GEOGRAPHIC CONTEXT:
- Focus: India-specific (all 5 major regions)
  * North India (Delhi, Punjab, Haryana, Himachal Pradesh)
  * South India (Tamil Nadu, Andhra Pradesh, Karnataka, Telangana)
  * West India (Gujarat, Maharashtra, Goa, Rajasthan)
  * Central India (Madhya Pradesh, Chhattisgarh, Jharkhand)
  * East India (West Bengal, Odisha, Bihar, Assam)

CURRENCY & REGULATORY:
- Currency: Indian Rupees (₹)
- Price Range: ₹200–₹1,200/kg (average: ₹697.08/kg)
- Certifications: BIS, FSSAI, ISI, Eco-Mark India, plus international standards
- Tax System: GST-aware (18%, 12%, No GST categories)
- Standards: Indian compliance markers (BIS, ISI, FSSAI, Both, None)

DATA QUALITY:
✓ Completeness: 100% (zero missing values)
✓ Duplicates: 0 (Material_ID is unique)
✓ Outliers: All within realistic ranges
✓ Regional Balance: Evenly distributed across 5 regions (~20% each)
✓ Ready for Production: No data cleaning needed

5 PRIMARY ATTRIBUTES (FIXED ACROSS VERSIONS):
- Tensile_Strength_MPa (6.78–95.31 MPa, mean 32.93)
- Weight_Capacity_kg (20.41–126.00 kg, mean 52.96)
- Biodegradability_Score (52.50–100.00, mean 91.93)
- CO2_Emission_Score (54.20–100.00, mean 78.80)
- Recyclability_Percentage (32.00–100.00%, mean 72.35%)

These attributes remain semantically identical to original dataset for consistency.


4. TYPICAL USE CASES
--------------------

✅ MATERIAL RECOMMENDATION FOR INDIAN MARKET
   Input: Food product type, storage temperature, region, budget, required strength
   Output: Top-K recommended materials with scores

✅ COST OPTIMIZATION FOR INDIA
   Analyze INR pricing across 5 regions
   Include GST impact on total cost
   Balance sustainability with budget constraints

✅ COMPLIANCE VERIFICATION
   Check BIS, FSSAI, ISI certification requirements
   Verify Indian Standard compliance
   Ensure market eligibility

✅ SUSTAINABILITY RANKING
   Rate materials on biodegradability & CO2 impact
   Multi-objective optimization (strength vs cost vs impact)
   Support India's green initiatives

✅ REGIONAL SUPPLIER MATCHING
   Match materials to 5 Indian regions
   Optimize logistics & supply chains
   Regional cost analysis

✅ AGRICULTURAL APPLICATIONS
   Mulch film recommendations for different crops
   Regional agricultural product packaging
   Soil-biodegradable materials selection

✅ ML MODEL TRAINING
   Regression: Predict biodegradability/CO2 scores
   Recommendation systems: Content-based filtering
   Classification: Material category prediction
   Clustering: Find similar materials


5. QUICK START GUIDE
--------------------

STEP 1: LOAD DATASET (Python)
──────────────────────────────
import pandas as pd

df = pd.read_excel(
    "Eco_Friendly_Materials_India_Adapted_9000_Records.xlsx",
    sheet_name="Complete_Dataset"
)

# Check shape
print(df.shape)  # Output: (9000, 30)


STEP 2: EXPLORE DATA
────────────────────
# First 5 records
print(df.head())

# Dataset info
print(df.info())

# Statistical summary
print(df.describe())

# Unique values in key columns
print(df['Supplier_Region_India'].value_counts())
print(df['Certification'].value_counts())


STEP 3: ANALYZE 5 FIXED PRIMARY ATTRIBUTES
────────────────────────────────────────────
fixed_attrs = [
    'Tensile_Strength_MPa',
    'Weight_Capacity_kg',
    'Biodegradability_Score',
    'CO2_Emission_Score',
    'Recyclability_Percentage'
]

print(df[fixed_attrs].describe())


STEP 4: BUILD A SIMPLE RECOMMENDATION ENGINE
─────────────────────────────────────────────
# Filter materials for spice packaging in South India
spice_filter = (df['Food_Product_Type'] == 'Spices (Turmeric, Cumin, Coriander)') & \
               (df['Supplier_Region_India'] == 'South India') & \
               (df['Production_Cost_per_kg_INR'] <= 700)

recommended = df[spice_filter].nlargest(5, 'Biodegradability_Score')

print(recommended[['Material_ID', 'Material_Type', 'Biodegradability_Score', 'Cost']])


STEP 5: PREPARE FOR ML
──────────────────────
from sklearn.preprocessing import LabelEncoder

# Drop non-predictive columns
X = df.drop(columns=['Biodegradability_Score', 'Material_ID', 'Testing_Date'])
y = df['Biodegradability_Score']

# Encode categorical variables
for col in X.select_dtypes(include='object').columns:
    X[col] = LabelEncoder().fit_transform(X[col])

# Train a model (e.g., RandomForest)
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Feature importance
print(pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False))


6. FEATURE CATEGORIES (30 TOTAL)
--------------------------------

IDENTIFICATION & CORE (2 features):
- Material_ID, Material_Type

FIXED ML ATTRIBUTES (5 features):
- Tensile_Strength_MPa, Weight_Capacity_kg, Biodegradability_Score,
  CO2_Emission_Score, Recyclability_Percentage

COST & PHYSICAL PROPERTIES (11 features):
- Thickness_Micrometers, Production_Cost_per_kg_INR, Shelf_Life_Days,
  Moisture_Barrier_g_m2_day, Oxygen_Barrier_cc_m2_day, Processing_Temperature_C,
  Density_g_cm3, Biodegradation_Time_Days, Water_Absorption_Percentage,
  Thermal_Stability_C, Environmental_Impact_Score

APPLICATION CONTEXT (6 features):
- Application_Type, Manufacturing_Method, Additives_Used,
  Food_Product_Type, Barrier_Property, Storage_Temperature

REGIONAL & REGULATORY (6 features):
- Supplier_Region_India, Certification, Market_State, Testing_Date,
  GST_Applicable (NEW), Indian_Standard (NEW)


7. DATA PREPARATION TIPS FOR ML
--------------------------------

ENCODING CATEGORICAL VARIABLES:
- Use LabelEncoder() for tree-based models (XGBoost, RandomForest, LightGBM)
- Use one-hot encoding for linear models (Ridge, Lasso, LogisticRegression)
- Use target encoding for high-cardinality features

NORMALIZATION / SCALING:
- StandardScaler for algorithms: KNN, SVM, Neural Networks
- MinMaxScaler for models requiring 0-1 range: Neural Networks
- No scaling needed for tree-based models

HANDLING DATES:
- Extract features: year, month, day_of_week, day_of_year
- Or use as split criterion (time-series validation)

DEALING WITH IMBALANCE (if any):
- Check: df['Certification'].value_counts()
- Use class_weight parameter if needed
- Consider SMOTE for synthetic oversampling

REGIONAL MODELING:
- Train separate models per region for better accuracy
- Cross-validate using regional folds


8. RECOMMENDED MODELING APPROACHES
-----------------------------------

🎯 PREDICTION TASK: Biodegradability Score
   Model: RandomForestRegressor, GradientBoostingRegressor, Neural Network
   Metrics: RMSE, MAE, R² Score

🎯 RECOMMENDATION TASK: Top-K Materials
   Model: Content-based filtering, Similarity scoring
   Approach: Calculate material similarity using fixed attributes + cost

🎯 RANKING TASK: Multi-Objective Optimization
   Objective: Maximize biodegradability & recyclability, minimize CO2 & cost
   Tools: Pandas ranking, scikit-pareto, pygmo (if advanced needed)

🎯 CLASSIFICATION TASK: Material Category
   Model: RandomForest, SVM, Neural Network
   Target: Predict Material_Type from properties

🎯 CLUSTERING TASK: Find Similar Materials
   Model: K-Means, DBSCAN, Hierarchical Clustering
   Use: Normalized fixed attributes + cost


9. EXTENSION & CUSTOMIZATION
-----------------------------

TO ADD MORE RECORDS:
1. Maintain Material_ID format: IND_MAT_XXXXX
2. Keep regional distribution ~20% each (or adjust deliberately)
3. Ensure values are within observed ranges (see Statistics sheet)
4. Add Testing_Date within recent timeframe

TO ADD NEW FEATURES:
1. Keep 5 fixed attributes unchanged
2. Add new columns following naming convention: Feature_Name_Unit
3. Document in Feature_Dictionary
4. Update Dataset_Guide.md with descriptions

TO ADAPT FOR OTHER REGIONS:
1. Replace Supplier_Region_India with target country regions
2. Convert costs to local currency
3. Update certifications to local standards
4. Adjust food products to local context


10. TECHNICAL SPECIFICATIONS
-----------------------------

FILE FORMAT:
- Primary: .xlsx (Excel 2016+, LibreOffice Calc, Google Sheets)
- Support: Can export sheets as .csv for R, Python, etc.

CHARACTER ENCODING:
- UTF-8 (supports Indian language characters if future expansion)

DATE FORMAT:
- YYYY-MM-DD (ISO standard)

CURRENCY:
- INR (₹) for all cost-related fields

NUMERIC PRECISION:
- Float: 2 decimal places
- Integer: Whole numbers only
- Percentages: 0–100 range

COMPATIBILITY:
- Python: pandas, numpy, scikit-learn, TensorFlow, PyTorch
- R: data.table, dplyr, tidyverse, caret
- Excel: Native support
- Google Sheets: Import .xlsx directly
- SQL: Can be loaded into any SQL database


11. NOTES & DISCLAIMERS
-----------------------

✓ SYNTHETIC DATA FOR EXPERIMENTATION
  This is curated/synthetic data designed for model prototyping and learning.
  Real-world deployments should source validated material specifications.

✓ QUALITY GUARANTEE
  100% complete, zero missing values, balanced across regions.
  All values within realistic material science ranges.

✓ 5 FIXED ATTRIBUTES POLICY
  These attributes are intentionally kept consistent with the original version
  to maintain backward compatibility with existing models and analyses.

✓ INDIA-SPECIFIC CONTEXT
  All prices in INR, certifications India-recognized, applications Indian food market.
  For other countries, adapt currency, certifications, and applications accordingly.


12. CONTACT & SUPPORT
---------------------

For questions about:
- Dataset structure → Refer to Feature_Dictionary sheet in Excel
- ML workflows → See Dataset_Guide.md for examples
- Quick stats → Check Dataset_Summary_Metrics.csv
- Feature details → Read Dataset_Guide.md Section 2

To customize:
- Add columns with appropriate naming conventions
- Maintain 5 fixed attributes unchanged
- Document changes in a separate changelog


13. VERSION HISTORY
-------------------

v1.0 (2025-12-31) – CURRENT
- Initial India-adapted dataset
- 9,000 records, 30 features
- 5 regions, 100% completeness
- Ready for production ML training


═══════════════════════════════════════════════════════════════════════════════

                        🚀 GET STARTED NOW! 🚀

Your dataset is production-ready for:
  ✓ ML model training
  ✓ Recommendation systems
  ✓ Campus projects & internship portfolios
  ✓ Published research & papers
  ✓ Business analytics

Happy modeling! 🌱📊💻

═══════════════════════════════════════════════════════════════════════════════

Generated: December 31, 2025
Eco-Friendly Materials Dataset – India Edition v1.0
