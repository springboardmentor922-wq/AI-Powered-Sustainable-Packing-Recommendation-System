import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to MySQL
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

df = pd.read_csv("../data/processed/final_ecopack_dataset_fe.csv")
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(
        """
        INSERT INTO feature_dataset (
            category_item, weight_kg, volumetric_weight_kg,
            fragility, moisture_sens, shipping_mode,
            distance_km, packaging_used, cost_usd,
            co2_emission_kg_item, material_id, material_name,
            category_material, density_kg_m3, tensile_strength_mpa,
            cost_per_kg, co2_emission_kg_material, biodegradable,
            co2_impact_index, cost_efficiency_index, environmental_impact_score,
            material_suitability_score, sustainability_score, sustainability_rating,
            item_volume_m3
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            row["Category_item"],
            row["Weight_kg"],
            row["Volumetric_Weight_kg"],
            row["Fragility"],
            row["Moisture_Sens"],
            row["Shipping_Mode"],
            row["Distance_km"],
            row["Packaging_Used"],
            row["Cost_USD"],
            row["CO2_Emission_kg_item"],
            row["Material_ID"],
            row["Material_Name"],
            row["Category_material"],
            row["Density_kg_m3"],
            row["Tensile_Strength_MPa"],
            row["Cost_per_kg"],
            row["CO2_Emission_kg_material"],
            row["Biodegradable"],
            row["co2_impact_index"],
            row["cost_efficiency_index"],
            row["environmental_impact_score"],
            row["material_suitability_score"],
            row["sustainability_score"],
            row["sustainability_rating"],
            row["Item_Volume_m3"]
        )
    )

conn.commit()
cursor.close()
conn.close()

print("✅ Feature dataset seeded successfully")