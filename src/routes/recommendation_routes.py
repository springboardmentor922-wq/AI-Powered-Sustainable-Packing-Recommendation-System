from flask import Blueprint, request, jsonify
from recommendation_engine import get_recommendations

recommendation_bp = Blueprint("recommendation", __name__)

@recommendation_bp.route("/recommend", methods=["POST"])
def recommend():

    data = request.json

    distance = data.get("distance")
    packaging_type = data.get("packaging_type")

    if distance is None or packaging_type is None:
        return jsonify({"error": "Missing required fields"}), 400

    results = get_recommendations(distance, packaging_type)

    return jsonify({
        "input": {
            "distance": distance,
            "packaging_type": packaging_type
        },
        "recommendations": results
    })
