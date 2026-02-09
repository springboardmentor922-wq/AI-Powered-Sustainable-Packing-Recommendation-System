# 🌍 EcoPackAI: Sustainable Packaging Optimization

**EcoPackAI** is an intelligent packing assistant that uses AI to recommend the most eco-friendly and cost-effective packaging materials for logistics.  
It balances **Cost**, **Carbon Footprint (CO₂)**, and **Durability** to help businesses make greener decisions.

---
## 📊 Logic & Methodology
The system analyzes the trade-offs between three competing factors:
1. **Financial Cost:** Minimizing overhead for packaging.
2. **Environmental Impact:** Calculating grams of $CO_2$ per unit.
3. **Structural Integrity:** Ensuring the material meets the "Fragility Threshold" of the item.



---

## 🚀 Features
- **AI Recommendation Engine:** Predicts the best packaging material based on item weight, distance, and fragility.
- **Smart Scaling:** Adjusts cost impact for local vs long-haul deliveries.
- **Interactive Dashboard:** Power BI dashboard to monitor sustainability and cost savings.
- **Real-Time Analytics:** Identifies high-emission (“dirty”) sectors and growth trends.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask  
- **AI Models:** Scikit-Learn (Random Forest, XGBoost)  
- **Frontend:** HTML, CSS, Jinja2  
- **Data Visualization:** Power BI, Plotly  
- **Storage:** CSV (file-based logging)

---

## 📁 Project Structure


├── app.py
├── templates/
│ ├── index.html
│ └── dashboard.html
├── model_cost_rf.pkl
├── model_co2_xgb.pkl
├── usage_logs.csv
├── engineered_material_data.csv
├── Dashboard2.pbix
└── README.md



---

## ⚙️ How to Run Locally

1️⃣ Clone the Repository
git clone https://github.com/springboardmentor922-wq/AI-Powered-Sustainable-Packing-Recommendation-System.git
cd AI-Powered-Sustainable-Packing-Recommendation-System

2️⃣ Install Dependencies
 pip install -r requirements.txt

3️⃣ Run the Application
 python app.py

4️⃣ Open in Browser
http://127.0.0.1:5000



