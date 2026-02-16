# Eco-Friendly Materials Dataset – India Edition (9,000 Records, 30 Features)

This guide explains the structure, fields, and usage patterns of the **Eco_Friendly_Materials_India_Adapted_9000_Records.xlsx** dataset. It is designed for ML model training focused on sustainable packaging recommendations for the Indian market.

---

## 1. File Overview

- **File name**: `Eco_Friendly_Materials_India_Adapted_9000_Records.xlsx`
- **Rows**: 9,000 materials
- **Columns**: 30 features
- **Target use cases**:
  - Material recommendation for Indian food and FMCG packaging
  - Cost and GST-aware optimization
  - Compliance and certification–aware selection
  - Sustainability scoring and ranking
  - Region-aware sourcing and logistics modeling

Main sheets:
- `Complete_Dataset`: Core data (9,000 × 30)
- `Summary`: High-level metrics
- `Statistics`: Numeric feature statistics
- `Material_Types`: Distribution of material types
- `Regional_Analysis`: Per-region breakdown (5 Indian regions)
- `Feature_Dictionary`: Human-readable descriptions of all features
- `India_Certifications`: Reference for certification labels

---

## 2. Schema and Feature Description

Below is the logical schema (summarized; details are also in `Feature_Dictionary` sheet).

### 2.1 Identification & Core Properties

- **Material_ID** (string)
  - Format: `IND_MAT_XXXXX`
  - Unique identifier for each material record.

- **Material_Type** (categorical)
  - 30 eco-friendly material classes (PLA, PHA, starch-based, natural fiber composites, etc.).
  - Use for grouping, clustering, and filtering.

### 2.2 Primary ML Attributes (Fixed)

These 5 core attributes are kept conceptually fixed compared to the original dataset (same semantics and roles):

- **Tensile_Strength_MPa** (float)
  - Range ≈ 6.78 – 95.31
  - Mechanical strength under tension.

- **Weight_Capacity_kg** (float)
  - Range ≈ 20.41 – 126.00
  - Maximum supported load for packaging use.

- **Biodegradability_Score** (float, 0–100)
  - Higher = degrades faster and more completely.

- **CO2_Emission_Score** (float, 0–100)
  - Lower = better climate performance.
  - Used as an inverse sustainability signal.

- **Recyclability_Percentage** (float, 0–100)
  - Share of material expected to be recyclable.

These are ideal candidates for:
- Targets (e.g., predict biodegradability from composition and process).
- Multi-objective optimization (strength vs cost vs impact).

### 2.3 Cost, Physical, and Barrier Properties

- **Thickness_Micrometers** (float)
- **Production_Cost_per_kg_INR** (float, in ₹)
- **Shelf_Life_Days** (integer)
- **Moisture_Barrier_g_m2_day** (float)
- **Oxygen_Barrier_cc_m2_day** (float)
- **Processing_Temperature_C** (float)
- **Density_g_cm3** (float)
- **Biodegradation_Time_Days** (float)
- **Water_Absorption_Percentage** (float)
- **Thermal_Stability_C** (float)
- **Environmental_Impact_Score** (float, 20–95)

These features are useful for:
- Engineering feasibility filters.
- Feature importance analysis for ML.
- Trade-off analysis (e.g., cost vs barrier performance).

### 2.4 Application & Usage Context

- **Application_Type** (categorical, 15 values)
  - India-specific packaging use cases (e.g., "Food Packaging Film (Masala/Spices)", "Tray/Clamshell (Street Food)", "Mulch Film (Agricultural)").

- **Manufacturing_Method** (categorical)
  - 9 processes (Injection Molding, Film Extrusion, Thermoforming, etc.).

- **Additives_Used** (categorical)
  - Includes Indian-context additives like "Essential Oils (Turmeric/Neem)" and "Plant Fiber Reinforcement (Jute/Coconut)".

- **Food_Product_Type** (categorical)
  - 15 Indian food/product categories (Spices, Wheat Flour, Rice, Tea/Coffee, Dairy, Seafood, etc.).

- **Barrier_Property** (categorical)
  - High/standard moisture/oxygen/gas barrier classification.

- **Storage_Temperature** (categorical)
  - Ambient (25–30°C), Refrigerated (0–4°C), Frozen (−18°C), Room Temperature (20–25°C), Cool & Dry (15–20°C).

### 2.5 Regional & Regulatory Context (India-Specific)

- **Supplier_Region_India** (categorical)
  - Values: North India, South India, West India, Central India, East India.

- **Certification** (categorical)
  - Includes BIS Certification, FSSAI Approved, Eco‑Mark India, ISI Certified, Green Label (India), plus international labels.

- **Market_State** (categorical)
  - New Product, Growth, Established, Mature.

- **Testing_Date** (date, within recent years)
  - Use for temporal split (train/validation) or drift checks.

- **GST_Applicable** (categorical, NEW)
  - Values: "Yes (18%)", "Yes (12%)", "No".

- **Indian_Standard** (categorical, NEW)
  - Values: "BIS", "ISI", "FSSAI", "Both", "None".

---

## 3. Typical ML Workflows

### 3.1 Regression – Predict Biodegradability

Target:
- `Biodegradability_Score`

Example predictors:
- Material_Type, Additives_Used, Manufacturing_Method
- Thickness_Micrometers, Production_Cost_per_kg_INR
- Environmental_Impact_Score, Supplier_Region_India

### 3.2 Recommendation Engine

Goal:
- Recommend top‑K materials for a given use case:
  - Inputs: Food_Product_Type, Storage_Temperature, Region, Target Cost Range, Minimum Strength.
  - Outputs: Ranked list of Material_ID with scores.

### 3.3 Multi-Objective Ranking

Combine:
- High Biodegradability_Score
- Low CO2_Emission_Score
- High Recyclability_Percentage
- Acceptable production cost and GST.

---

## 4. Data Preparation Tips

- Encode categorical features with:
  - One‑hot encoding for tree‑based/GNNs or
  - Target / ordinal encoding where appropriate.
- Normalize key continuous features for distance-based models.
- Consider:
  - Train/val split by Testing_Date (time-based) for robustness.
  - Per-region models (e.g., separate models for South vs North India).

---

## 5. Suggested Target & Feature Sets

- **Primary targets**:
  - `Biodegradability_Score`
  - `CO2_Emission_Score`
  - `Recyclability_Percentage`

- **Key context features**:
  - Application_Type
  - Food_Product_Type
  - Supplier_Region_India
  - Storage_Temperature
  - Certification, Indian_Standard, GST_Applicable

Use `Feature_Dictionary` sheet for precise definitions while coding.

---

## 6. Appendix: Quick Reference

### Material Types (30 total)
PLA, PHA, Starch-based Polymer, Cellulose Acetate, PCL, PBAT, PBS, Chitosan, Gelatin, Alginate, and 20+ more.

### Indian Regions (5 total)
- North: Delhi, Punjab, Haryana, Himachal Pradesh
- South: Tamil Nadu, Andhra Pradesh, Karnataka, Telangana
- West: Gujarat, Maharashtra, Goa, Rajasthan
- Central: Madhya Pradesh, Chhattisgarh, Jharkhand
- East: West Bengal, Odisha, Bihar, Assam

### Certifications (10 total)
BIS, FSSAI, Eco-Mark India, ISI, Green Label (India), ISO 14855, EN 13432, No Certification, Emerging Certification, International Standard

---

**Last Updated**: December 31, 2025
**Version**: 1.0
**Dataset Size**: 9,000 records, 30 features, 270,000 data points