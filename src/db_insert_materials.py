import pandas as pd
import psycopg2

# =========================
# DATABASE CONNECTION
# =========================

conn = psycopg2.connect(
    host="localhost",
    database="Ecopackai_db",
    user="postgres",
    password="boorgir"   # Replace if you used different password
)

cur = conn.cursor()

# =========================
# LOAD PROCESSED DATA
# =========================

df = pd.read_excel("data/materials_processed.xlsx")

# =========================
# INSERT INTO DATABASE
# =========================

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO materials (
            material_name,
            category,
            strength,
            weight_capacity,
            biodegradability_score,
            co2_emission_score,
            recyclability_percent,
            co2_impact_index,
            cost_efficiency_index,
            material_suitability_score
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row.get("Material_Name"),
        row.get("Category"),
        row.get("Tensile_Strength_MPa"),
        row.get("Density_kg_m3"),
        row.get("Biodegradable"),
        row.get("CO2_Emission_kg"),
        row.get("Recyclability_percent", 0),
        row.get("CO2_Impact_Index"),
        row.get("Cost_Efficiency_Index"),
        row.get("Material_Suitability_Score")
    ))

conn.commit()
cur.close()
conn.close()

print("Materials inserted successfully into PostgreSQL.")
