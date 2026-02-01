"""
Recommender Wrapper
- Calls the ML recommendation engine
- Saves results to MySQL recommendation_history
"""

import sys
from pathlib import Path
import json
import logging

# Add ml directory to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from db import get_db

logger = logging.getLogger(__name__)

# Import ML engine
try:
    from ml.notebooks.recommendation_engine import (
        generate_recommendations,
        materials_df,
        co2_model,
        cost_model,
        FEATURES_COST,
        FEATURES_CO2
    )
    ML_AVAILABLE = True
    logger.info("✅ ML engine loaded")
except Exception as e:
    ML_AVAILABLE = False
    logger.warning(f"⚠️ ML engine not available: {e}")

def get_recommendations(shipment, top_k=5, sort_by="Sustainability"):
    """
    Generate recommendations using ML engine
    
    Args:
        shipment: dict with shipment details
        top_k: number of recommendations
        sort_by: sorting criterion (Sustainability, Pred_CO2, Pred_Cost)
    
    Returns:
        list of dicts with recommendations
    """
    if not ML_AVAILABLE:
        raise Exception("ML engine not available")
    
    try:
        # Call ML engine
        df = generate_recommendations(
            materials_df=materials_df,
            co2_model=co2_model,
            cost_model=cost_model,
            shipment_inputs=shipment,
            features_cost=FEATURES_COST,
            features_co2=FEATURES_CO2,
            top_k=top_k,
            sort_by=sort_by
        )
        
        # Convert to list of dicts
        recommendations = df[[
            "Material_Name",
            "Pred_Cost",
            "Pred_CO2",
            "Biodegradable",
            "Tensile_Strength_MPa",
            "Sustainability"
        ]].to_dict("records")
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations (sorted by {sort_by})")
        return recommendations
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise

def save_recommendation(email, session_id, shipment, k_value, sort_by, recommendations):
    """
    Save recommendation to MySQL history
    
    Args:
        email: user email
        session_id: session identifier
        shipment: dict with shipment details
        k_value: number of recommendations requested
        sort_by: sorting criterion
        recommendations: list of recommendation dicts
    """
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO recommendation_history (
                    email, session_id,
                    product_category, weight_kg, fragility, shipping_mode,
                    distance_km, moisture_sensitive,
                    length_cm, width_cm, height_cm,
                    k_value, sort_by, recommendations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                email, session_id,
                shipment.get("Category_item"),
                shipment.get("Weight_kg"),
                shipment.get("Fragility"),
                shipment.get("Shipping_Mode"),
                shipment.get("Distance_km"),
                shipment.get("Moisture_Sens"),
                shipment.get("Length_cm"),
                shipment.get("Width_cm"),
                shipment.get("Height_cm"),
                k_value,
                sort_by,
                json.dumps(recommendations)
            ))
        logger.info(f"✅ Saved recommendation to history for {email}")
        return True
    except Exception as e:
        logger.error(f"Save recommendation error: {e}")
        return False
    finally:
        db.close()

def get_user_history(email, limit=10):
    """Get user's recommendation history"""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, session_id, created_at, product_category, 
                       weight_kg, distance_km, k_value, sort_by
                FROM recommendation_history
                WHERE email = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (email, limit))
            history = cur.fetchall()
        return history
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return []
    finally:
        db.close()