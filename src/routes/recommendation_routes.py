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

    # =========================
    # REQUIRED FIELDS
    # =========================

    required_fields = [
        "distance",
        "packaging_type",
        "category",
        "weight",
        "volumetric_weight",
        "fragility",
        "moisture",
        "shipping_mode"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"Missing required field: {field}"
            }), 400

    # =========================
    # EXTRACT VALUES
    # =========================

    distance = data["distance"]
    packaging_type = data["packaging_type"]
    category = data["category"]
    weight = data["weight"]
    volumetric_weight = data["volumetric_weight"]
    fragility = data["fragility"]
    moisture = data["moisture"]
    shipping_mode = data["shipping_mode"]

    # =========================
    # BASIC VALIDATION
    # =========================

    if not isinstance(distance, (int, float)):
        return jsonify({
            "status": "error",
            "message": "Distance must be a number"
        }), 400

    if not isinstance(weight, (int, float)):
        return jsonify({
            "status": "error",
            "message": "Weight must be a number"
        }), 400

    if not isinstance(volumetric_weight, (int, float)):
        return jsonify({
            "status": "error",
            "message": "Volumetric weight must be a number"
        }), 400

    if not isinstance(fragility, (int, float)):
        return jsonify({
            "status": "error",
            "message": "Fragility must be numeric"
        }), 400

    if not isinstance(moisture, (int, float)):
        return jsonify({
            "status": "error",
            "message": "Moisture must be numeric"
        }), 400

    if not isinstance(packaging_type, str):
        return jsonify({
            "status": "error",
            "message": "Packaging type must be a string"
        }), 400

    if not isinstance(category, str):
        return jsonify({
            "status": "error",
            "message": "Category must be a string"
        }), 400

    if not isinstance(shipping_mode, str):
        return jsonify({
            "status": "error",
            "message": "Shipping mode must be a string"
        }), 400

    # =========================
    # CALL RECOMMENDATION ENGINE
    # =========================

    try:
        results = get_recommendations(
            distance,
            packaging_type,
            category,
            weight,
            volumetric_weight,
            fragility,
            moisture,
            shipping_mode
        )

        return jsonify({
            "status": "success",
            "input": data,
            "recommendations": results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
