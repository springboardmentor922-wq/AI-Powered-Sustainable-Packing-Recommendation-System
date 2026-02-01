USE ecopackdb;

-- USERS
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255),
    failed_attempts INT DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RECOMMENDATION HISTORY
CREATE TABLE IF NOT EXISTS recommendation_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    product_category VARCHAR(100),
    weight_kg FLOAT,
    fragility INT,
    shipping_mode VARCHAR(50),
    distance_km FLOAT,
    moisture_sensitive BOOLEAN,
    length_cm FLOAT,
    width_cm FLOAT,
    height_cm FLOAT,
    k_value INT,

    recommendation JSON,

    FOREIGN KEY (email) REFERENCES users(email)
);

-- FEATURES 
CREATE TABLE feature_dataset (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_item VARCHAR(100),
    weight_kg FLOAT,
    volumetric_weight_kg FLOAT,
    fragility INT,
    moisture_sens BOOLEAN,
    shipping_mode VARCHAR(50),
    distance_km FLOAT,
    packaging_used VARCHAR(100),
    cost_usd FLOAT,
    co2_emission_kg_item FLOAT,
    material_id INT,
    material_name VARCHAR(100),
    category_material VARCHAR(50),
    density_kg_m3 FLOAT,
    tensile_strength_mpa FLOAT,
    cost_per_kg FLOAT,
    co2_emission_kg_material FLOAT,
    biodegradable VARCHAR(10),
    co2_impact_index FLOAT,
    cost_efficiency_index FLOAT,
    environmental_impact_score FLOAT,
    material_suitability_score FLOAT,
    sustainability_score FLOAT,
    sustainability_rating VARCHAR(5),
    item_volume_m3 FLOAT
);