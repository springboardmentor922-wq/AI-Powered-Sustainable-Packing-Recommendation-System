from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import traceback

from EcoPackAI import ai_material_ranking
from flask import render_template
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DISTANCE_MAP = {
    "Local": 50,
    "Regional": 300,
    "Long": 1000,
    "National": 1000,
    "International": 5000
}

FRAGILITY_MAP = {
    "Low": 0.3,
    "Medium": 0.6,
    "High": 0.9
}


@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        print("✅ Incoming request:", data)

        
        required = ["product_name", "category", "weight", "distance", "fragility"]
        missing = [k for k in required if k not in data]

        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing fields: {missing}"
            }), 400

        
        product_features = {
            "Weight_kg": float(data["weight"]),
            "Distance_km": DISTANCE_MAP.get(data["distance"], 100),
            "Fragility": FRAGILITY_MAP.get(data["fragility"], 0.5),
            "Moisture_Sens": data.get("moisture", "Low"),
            "Shipping_Mode": data.get("shipping_mode", "Road"),
            "Product_Category": data["category"]
        }

        print("✅ Model input:", product_features)

        
        recommendations = ai_material_ranking(product_features)

        print("✅ AI output columns:", recommendations.columns.tolist())
        print(recommendations.head())

        return jsonify({
            "status": "success",
            "product": data["product_name"],
            "recommendations": recommendations.to_dict(orient="records")
        }), 200

    except Exception as e:
        print("❌ BACKEND ERROR:")
        traceback.print_exc()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    try:
        df = pd.read_csv("cleaned_and_merged_eco_data.csv")

        df["Cost_Base"] = df["Cost_USD"] * 1.15
        df["Cost_Saved"] = df["Cost_Base"] - df["Cost_USD"]

        labels = df["Material_Name"].head(10).tolist()
        co2_saved = (df["CO2_Emission_kg_x"] * 0.25).head(10).tolist()
        cost_saved = df["Cost_Saved"].head(10).tolist()

        durability = df["Tensile_Strength_MPa"].head(10).tolist()

        biodegradable_count = df["Biodegradable"].value_counts().reindex(["Yes", "No"], fill_value=0).tolist()

        eco_scores = df["Material_Suitability_Score"].head(10).tolist()

        return jsonify({
            "labels": labels,
            "co2_saved": co2_saved,
            "cost_saved": cost_saved,
            "durability": durability,
            "bio_stats": biodegradable_count,
            "eco_scores": eco_scores
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "EcoPackAI backend running"}), 200






@app.route("/api/dashboard/export/excel", methods=["GET"])
def export_excel():
    try:
        import os

        df = pd.read_csv("cleaned_and_merged_eco_data.csv")

        
        export_dir = os.path.abspath("exports")
        os.makedirs(export_dir, exist_ok=True)

        
        file_path = os.path.join(export_dir, "EcoPackAI_Report.xlsx")

        
        df.to_excel(file_path, index=False)

        
        if not os.path.isfile(file_path):
            return jsonify({"status": "error", "message": "Excel file not found after saving."}), 500

        
        return send_file(
            file_path,
            as_attachment=True,
            download_name="EcoPackAI_Report.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/api/dashboard/export/pdf", methods=["GET"])
def export_pdf():
    try:
        import os
        df = pd.read_csv("cleaned_and_merged_eco_data.csv")

        
        export_dir = os.path.abspath("exports")
        os.makedirs(export_dir, exist_ok=True)

        file_path = os.path.join(export_dir, "EcoPackAI_Professional_Report.pdf")

        
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        margin = 50
        y = height - margin

        
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#182848"))
        c.drawString(margin, y, "EcoPackAI Sustainability Report")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        c.drawString(margin, y - 18, "Environmental Impact • Cost Analytics • Material Insights")

        y -= 35
        c.setStrokeColor(colors.HexColor("#4b6cb7"))
        c.line(margin, y, width - margin, y)
        y -= 30

        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Key Performance Indicators")
        y -= 20

        avg_co2 = round(df["CO2_Emission_kg_x"].mean(), 2)
        avg_cost = round(df["Cost_USD"].mean(), 2)
        avg_strength = round(df["Tensile_Strength_MPa"].mean(), 2)
        avg_bio = round(df["Biodegradable_Binary"].mean() * 100, 2)

        kp_items = [
            ("Avg CO₂ Emission (kg)", avg_co2),
            ("Avg Cost (USD)", avg_cost),
            ("Avg Durability (MPa)", avg_strength),
            ("Avg Biodegradable (%)", avg_bio),
        ]

        c.setFont("Helvetica", 11)
        for title, val in kp_items:
            c.drawString(margin, y, f"{title}:   {val}")
            y -= 18

        y -= 15

        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Material Impact Summary")
        y -= 20

        headers = ["Material", "Cost", "CO₂ (kg)", "Strength"]
        col_x = [margin, margin + 180, margin + 260, margin + 340]

        c.setFillColor(colors.HexColor("#4b6cb7"))
        c.roundRect(margin, y - 5, width - 2 * margin, 22, 5, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)

        for i, h in enumerate(headers):
            c.drawString(col_x[i], y, h)

        y -= 28
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)

        
        for _, row in df.head(20).iterrows():

            if y < 80:
                c.showPage()
                y = height - margin

                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(margin, y, "Material Impact Summary (continued)")
                y -= 20

                c.setFillColor(colors.HexColor("#4b6cb7"))
                c.roundRect(margin, y - 5, width - 2 * margin, 22, 5, fill=1)
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 11)
                for i, h in enumerate(headers):
                    c.drawString(col_x[i], y, h)

                y -= 28
                c.setFont("Helvetica", 10)
                c.setFillColor(colors.black)

            
            c.drawString(col_x[0], y, str(row["Material_Name"])[:25])
            c.drawString(col_x[1], y, str(round(row["Cost_USD"], 2)))
            c.drawString(col_x[2], y, str(round(row["CO2_Emission_kg_x"], 2)))
            c.drawString(col_x[3], y, str(round(row["Tensile_Strength_MPa"], 2)))

            y -= 18

        
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.gray)
        c.drawString(margin, 40, "Generated by EcoPackAI")
        c.drawRightString(width - margin, 40, datetime.now().strftime("%d %b %Y • %I:%M %p"))

        c.save()

        
        return send_file(
            file_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="EcoPackAI_Professional_Report.pdf"
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)