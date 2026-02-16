import os
from functools import wraps

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# Reuse your existing ML pipeline and recommendation engine
from ML import main as ml_main


# ============================================================
# Flask & Database Configuration
# ============================================================

app = Flask(__name__)

# Database URL (SQLite by default; override with PostgreSQL if desired)
# Examples:
#   SQLite (default): sqlite:///ecopackai.db
#   PostgreSQL: postgresql://user:password@localhost:5432/ecopackai
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ecopackai.db")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# Security – Simple API Key
# ============================================================

API_KEY = os.getenv("ECOPACKAI_API_KEY", "change-me")  # override in prod


def error_response(code: str, message: str, status: int = 400, details=None):
    return (
        jsonify(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                },
            }
        ),
        status,
    )


def success_response(data, status: int = 200):
    return (
        jsonify(
            {
                "success": True,
                "data": data,
                "error": None,
            }
        ),
        status,
    )


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        provided = request.headers.get("X-API-KEY")
        if not provided or provided != API_KEY:
            return error_response(
                code="unauthorized",
                message="Missing or invalid API key.",
                status=401,
            )
        return fn(*args, **kwargs)

    return wrapper


# ============================================================
# Database Models
# ============================================================


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(128), nullable=False)
    packaging_format = db.Column(db.String(128), nullable=True)
    weight_kg = db.Column(db.Float, nullable=False)
    budget_per_kg = db.Column(db.Float, nullable=False)
    max_co2_kg = db.Column(db.Float, nullable=False)
    shelf_life_days = db.Column(db.Integer, nullable=False)


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )
    material_name = db.Column(db.String(255), nullable=False)
    primary_material = db.Column(db.String(255), nullable=True)
    predicted_cost = db.Column(db.Float, nullable=True)
    predicted_co2 = db.Column(db.Float, nullable=True)
    sustainability_score = db.Column(db.Float, nullable=True)
    ai_score = db.Column(db.Float, nullable=True)

    product = db.relationship(
        "Product", backref=db.backref("recommendations", lazy=True)
    )


# ============================================================
# Helper Functions
# ============================================================


def validate_json(required_fields):
    """Validate presence of required fields in JSON request body."""
    if not request.is_json:
        return None, error_response(
            "invalid_request", "Request body must be JSON.", 400
        )

    payload = request.get_json(silent=True) or {}
    missing = [f for f in required_fields if f not in payload]
    if missing:
        return None, error_response(
            "missing_fields",
            f"Missing required fields: {', '.join(missing)}",
            400,
        )
    return payload, None


def compute_environmental_score_from_row(row) -> dict:
    """
    Compute an environmental score (0–100) for a material row from the ML dataset.
    Combines sustainability and CO₂ efficiency into a single value.
    """
    # Higher sustainability is better, lower CO2 is better
    sustainability = float(row["Overall_Sustainability_Score"])

    co2_series = ml_main.df["CO2_Emission_Packaging_kgCO2e"]
    co2_max = float(co2_series.max())
    co2_value = float(row["CO2_Emission_Packaging_kgCO2e"])
    # 0 (worst) to 100 (best) CO₂ score
    co2_score = max(0.0, 100.0 * (1.0 - co2_value / (co2_max + 1e-6)))

    # Weighted combination
    environmental_score = 0.7 * sustainability + 0.3 * co2_score

    return {
        "environmental_score": round(environmental_score, 2),
        "components": {
            "sustainability_score": round(sustainability, 2),
            "co2_score": round(co2_score, 2),
        },
    }


def compute_environmental_score_for_material_name(material_name: str):
    matches = ml_main.df[ml_main.df["Material_Name"] == material_name]
    if matches.empty:
        return None
    row = matches.iloc[0]
    return compute_environmental_score_from_row(row)


# ============================================================
# API Endpoints
# ============================================================


@app.route("/api/products", methods=["POST"])
@require_api_key
def create_product():
    """
    Product input handling.

    Request JSON:
    {
      "name": "Milk 1L",
      "category": "DAIRY",
      "packaging_format": "BOTTLE",   # optional
      "weight_kg": 1.0,
      "budget_per_kg": 400,
      "max_co2_kg": 2.5,
      "shelf_life_days": 180
    }
    """
    required = [
        "name",
        "category",
        "weight_kg",
        "budget_per_kg",
        "max_co2_kg",
        "shelf_life_days",
    ]
    payload, error = validate_json(required)
    if error:
        return error

    try:
        product = Product(
            name=payload["name"],
            category=str(payload["category"]).upper().strip(),
            packaging_format=payload.get("packaging_format"),
            weight_kg=float(payload["weight_kg"]),
            budget_per_kg=float(payload["budget_per_kg"]),
            max_co2_kg=float(payload["max_co2_kg"]),
            shelf_life_days=int(payload["shelf_life_days"]),
        )
        db.session.add(product)
        db.session.commit()
    except (ValueError, SQLAlchemyError) as exc:
        db.session.rollback()
        return error_response(
            "database_error", "Failed to save product.", 500, str(exc)
        )

    return success_response(
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "packaging_format": product.packaging_format,
            "weight_kg": product.weight_kg,
            "budget_per_kg": product.budget_per_kg,
            "max_co2_kg": product.max_co2_kg,
            "shelf_life_days": product.shelf_life_days,
        },
        status=201,
    )


@app.route("/api/recommendations", methods=["POST"])
@require_api_key
def get_recommendations():
    """
    AI material recommendation.

    Request JSON (option 1 – use an existing product):
    { "product_id": 1, "top_n": 5 }

    Request JSON (option 2 – ad-hoc product, not persisted):
    {
      "category": "DAIRY",
      "weight_kg": 1.0,
      "budget_per_kg": 400,
      "max_co2_kg": 2.5,
      "shelf_life_days": 180,
      "top_n": 5
    }
    """
    if not request.is_json:
        return error_response("invalid_request", "Request body must be JSON.", 400)

    payload = request.get_json(silent=True) or {}

    top_n = int(payload.get("top_n", 5))
    product = None

    # Option 1: Use existing product
    product_id = payload.get("product_id")
    if product_id is not None:
        product = Product.query.get(product_id)
        if not product:
            return error_response("not_found", "Product not found.", 404)

        category = product.category
        weight = product.weight_kg
        budget = product.budget_per_kg
        max_co2 = product.max_co2_kg
        shelf_life = product.shelf_life_days
    else:
        # Option 2: ad-hoc product
        required = [
            "category",
            "weight_kg",
            "budget_per_kg",
            "max_co2_kg",
            "shelf_life_days",
        ]
        missing = [f for f in required if f not in payload]
        if missing:
            return error_response(
                "missing_fields",
                f"Missing required fields: {', '.join(missing)}",
                400,
            )

        category = str(payload["category"]).upper().strip()
        weight = float(payload["weight_kg"])
        budget = float(payload["budget_per_kg"])
        max_co2 = float(payload["max_co2_kg"])
        shelf_life = int(payload["shelf_life_days"])

    # Validate category against the ML dataset
    if category not in ml_main.SUPPORTED_CATEGORIES:
        return error_response(
            "invalid_category",
            f"Category '{category}' is not supported. "
            f"Supported: {', '.join(ml_main.SUPPORTED_CATEGORIES)}",
            400,
        )

    # Run the recommendation engine from main.py
    df_recs = ml_main.recommend_sustainable_packaging(
        category=category,
        budget=budget,
        co2_limit=max_co2,
        product_weight=weight,
        shelf_life=shelf_life,
        top_n=top_n,
    )

    if df_recs.empty:
        return success_response({"recommendations": []}, status=200)

    recommendations = []
    for _, row in df_recs.iterrows():
        rec = {
            "material_name": row["Material_Name"],
            "primary_material": row["Primary_Material"],
            "predicted_cost": float(row["predicted_cost"]),
            "predicted_co2": float(row["predicted_co2"]),
            "sustainability_score": float(row["Overall_Sustainability_Score"]),
            "ai_score": float(row["ai_score"]),
        }
        recommendations.append(rec)

        # Persist only if we have a stored product
        if product:
            try:
                db_rec = Recommendation(
                    product_id=product.id,
                    material_name=rec["material_name"],
                    primary_material=rec["primary_material"],
                    predicted_cost=rec["predicted_cost"],
                    predicted_co2=rec["predicted_co2"],
                    sustainability_score=rec["sustainability_score"],
                    ai_score=rec["ai_score"],
                )
                db.session.add(db_rec)
            except SQLAlchemyError:
                db.session.rollback()
                # Don't fail whole request if one recommendation fails to save

    if product:
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

    return success_response({"recommendations": recommendations}, status=200)


@app.route("/api/environmental-score", methods=["POST"])
@require_api_key
def compute_environmental_score():
    """
    Environmental score computation.

    Request JSON option 1 (lookup by material in dataset):
    { "material_name": "Recycled PET Bottle" }

    Returns a 0–100 environmental score and component breakdown.
    """
    payload, error = validate_json(["material_name"])
    if error:
        return error

    material_name = str(payload["material_name"]).strip()

    matches = ml_main.df[ml_main.df["Material_Name"] == material_name]
    if matches.empty:
        return error_response(
            "not_found",
            f"Material '{material_name}' not found in ML dataset.",
            404,
        )

    row = matches.iloc[0]
    score_info = compute_environmental_score_from_row(row)

    return success_response(
        {
            "material_name": material_name,
            **score_info,
        },
        status=200,
    )


@app.route("/health", methods=["GET"])
def health_check():
    return success_response({"status": "ok"})


# ============================================================
# UI Routes (HTML/CSS/Bootstrap)
# ============================================================


@app.route("/", methods=["GET"])
def ui_index():
    return render_template(
        "index.html",
        supported_categories=ml_main.SUPPORTED_CATEGORIES,
        error_message=None,
        previous={},
    )


@app.route("/ui/recommend", methods=["POST"])
def ui_recommend():
    form = request.form

    category = str(form.get("category", "")).upper().strip()
    product_name = str(form.get("name", "")).strip() or "Product"
    packaging_format = str(form.get("packaging_format", "")).strip()

    try:
        weight_kg = float(form.get("weight_kg") or 2)
        budget_per_kg = float(form.get("budget_per_kg") or 400)
        max_co2_kg = float(form.get("max_co2_kg") or 2.5)
        shelf_life_days = int(form.get("shelf_life_days") or 180)
        top_n = int(form.get("top_n") or 5)
    except ValueError:
        return render_template(
            "index.html",
            supported_categories=ml_main.SUPPORTED_CATEGORIES,
            error_message="Please enter valid numeric values for weight, budget, CO₂ limit, shelf life, and top N.",
            previous=form,
        )

    if category not in ml_main.SUPPORTED_CATEGORIES:
        return render_template(
            "index.html",
            supported_categories=ml_main.SUPPORTED_CATEGORIES,
            error_message=f"Unsupported category '{category}'.",
            previous=form,
        )

    df_recs = ml_main.recommend_sustainable_packaging(
        category=category,
        budget=budget_per_kg,
        co2_limit=max_co2_kg,
        product_weight=weight_kg,
        shelf_life=shelf_life_days,
        top_n=top_n,
    )

    recommendations = []
    if not df_recs.empty:
        for rank, (_, row) in enumerate(df_recs.iterrows(), start=1):
            material_name = row["Material_Name"]
            env = compute_environmental_score_for_material_name(material_name)
            recommendations.append(
                {
                    "rank": rank,
                    "material_name": material_name,
                    "primary_material": row.get("Primary_Material"),
                    "predicted_cost": float(row["predicted_cost"]),
                    "predicted_co2": float(row["predicted_co2"]),
                    "sustainability_score": float(row["Overall_Sustainability_Score"]),
                    "ai_score": float(row["ai_score"]),
                    "environmental_score": (env or {}).get("environmental_score"),
                    "environmental_components": (env or {}).get("components"),
                }
            )

    product = {
        "name": product_name,
        "category": category,
        "packaging_format": packaging_format,
        "weight_kg": weight_kg,
        "budget_per_kg": budget_per_kg,
        "max_co2_kg": max_co2_kg,
        "shelf_life_days": shelf_life_days,
        "top_n": top_n,
    }

    return render_template(
        "recommendations.html",
        product=product,
        recommendations=recommendations,
    )


if __name__ == "__main__":
    # Ensure tables exist
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

