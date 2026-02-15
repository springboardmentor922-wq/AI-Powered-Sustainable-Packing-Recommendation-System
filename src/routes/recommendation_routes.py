from flask import Blueprint, request, jsonify
from recommendation_engine import get_recommendations

recommendation_bp = Blueprint("recommendation", __name__)

@recommendation_bp.route("/recommend", methods=["POST"])
def recommend():

    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400

    data = request.get_json()

    distance = data.get("distance")
    packaging_type = data.get("packaging_type")

    # Validation
    if distance is None or packaging_type is None:
        return jsonify({
            "status": "error",
            "message": "Missing required fields: distance and packaging_type"
        }), 400

    if not isinstance(distance, (int, float)):
        return jsonify({
            "status": "error",
            "message": "Distance must be a number"
        }), 400

    if not isinstance(packaging_type, str):
        return jsonify({
            "status": "error",
            "message": "Packaging type must be a string"
        }), 400

    try:
        results = get_recommendations(distance, packaging_type)

        return jsonify({
            "status": "success",
            "input": {
                "distance": distance,
                "packaging_type": packaging_type
            },
            "recommendations": results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
