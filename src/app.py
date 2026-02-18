from flask import Flask, jsonify
from flask_cors import CORS
from routes.recommendation_routes import recommendation_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(recommendation_bp)

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "EcoPackAI Backend"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })

if __name__ == "__main__":
    app.run(debug=True)

