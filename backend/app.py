from flask import Flask, jsonify
from services.model_loader import load_models

app = Flask(__name__)

# Load ML models once at startup
cost_model, co2_model = load_models()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "running",
        "service": "EcoPackAI Backend",
        "models_loaded": True
    })

if __name__ == "__main__":
    app.run(debug=True)
