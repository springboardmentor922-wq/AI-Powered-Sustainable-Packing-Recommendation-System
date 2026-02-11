from flask import Flask
from routes.recommendation_routes import recommendation_bp

app = Flask(__name__)

app.register_blueprint(recommendation_bp)

@app.route("/")
def home():
    return "EcoPackAI Backend Running"

if __name__ == "__main__":
    app.run(debug=True)
