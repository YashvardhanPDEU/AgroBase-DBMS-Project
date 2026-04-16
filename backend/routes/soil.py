from flask import Blueprint, jsonify
from db import query, query_one

soil_bp = Blueprint("soil", __name__, url_prefix="/api/soil")


@soil_bp.route("/metrics")
def metrics():
    """
    KPI cards for the Soil & Water tab.
    Returns: avg health score, sample count, avg moisture proxy (ph_level), total daily water usage.
    """
    avg_health = query_one(
        "SELECT ROUND(AVG(health_score), 1) AS avg_health FROM Soil_Samples"
    )["avg_health"]

    sample_count = query_one(
        "SELECT COUNT(*) AS total FROM Soil_Samples"
    )["total"]

    # Use avg nitrogen_ppm as a proxy for moisture (scaled 0-100)
    avg_nitrogen = query_one(
        "SELECT ROUND(AVG(nitrogen_ppm), 1) AS avg_n FROM Soil_Samples"
    )["avg_n"]

    # Total water usage in gallons from all irrigation systems
    total_water = query_one(
        "SELECT COALESCE(SUM(water_usage_gallons), 0) AS total FROM Irrigation_Systems"
    )["total"]

    return jsonify({
        "avg_health_score": float(avg_health) if avg_health else 0,
        "sample_count": sample_count,
        "avg_nitrogen_ppm": float(avg_nitrogen) if avg_nitrogen else 0,
        "total_water_gallons": int(total_water),
    })


@soil_bp.route("/composition")
def composition():
    """
    Field area grouped by soil type, for the Soil Composition Breakdown pie chart.
    """
    rows = query(
        """
        SELECT soil_type, SUM(area_acres) AS total_acres
        FROM Fields
        GROUP BY soil_type
        ORDER BY total_acres DESC
        """
    )
    return jsonify({
        "labels": [r["soil_type"] for r in rows],
        "data": [int(r["total_acres"]) for r in rows],
    })


@soil_bp.route("/irrigation")
def irrigation():
    """
    Irrigation system type counts, for the Irrigation Efficiency doughnut chart.
    """
    rows = query(
        """
        SELECT type, COUNT(*) AS count, SUM(water_usage_gallons) AS total_gallons
        FROM Irrigation_Systems
        GROUP BY type
        ORDER BY count DESC
        """
    )
    return jsonify({
        "labels": [r["type"] for r in rows],
        "data": [r["count"] for r in rows],
        "water_usage": [int(r["total_gallons"]) for r in rows],
    })


@soil_bp.route("/recommendations")
def recommendations():
    """
    Latest soil sample recommendations for the Quick Actions panel.
    Returns top 3 most recent soil samples with recommendations.
    """
    rows = query(
        """
        SELECT ss.sample_id, f.field_name, fa.farm_name,
               ss.health_score, ss.ph_level, ss.nitrogen_ppm,
               ss.recommendation_text, ss.sample_date
        FROM Soil_Samples ss
        JOIN Fields f ON ss.field_id = f.field_id
        JOIN Farms fa ON f.farm_id = fa.farm_id
        ORDER BY ss.sample_date DESC
        LIMIT 3
        """
    )
    return jsonify([
        {
            "field": r["field_name"],
            "farm": r["farm_name"],
            "health_score": r["health_score"],
            "ph_level": float(r["ph_level"]),
            "nitrogen_ppm": r["nitrogen_ppm"],
            "recommendation": r["recommendation_text"],
            "sample_date": str(r["sample_date"]),
        }
        for r in rows
    ])


@soil_bp.route("/samples")
def samples():
    """
    Full list of soil samples with field and farm info.
    """
    rows = query(
        """
        SELECT ss.sample_id, f.field_name, fa.location AS farm_location,
               ss.sample_date, ss.ph_level, ss.nitrogen_ppm,
               ss.health_score, ss.recommendation_text
        FROM Soil_Samples ss
        JOIN Fields f ON ss.field_id = f.field_id
        JOIN Farms fa ON f.farm_id = fa.farm_id
        ORDER BY ss.sample_date DESC
        LIMIT 50
        """
    )
    return jsonify([
        {
            "sample_id": r["sample_id"],
            "field": r["field_name"],
            "location": r["farm_location"],
            "date": str(r["sample_date"]),
            "ph_level": float(r["ph_level"]),
            "nitrogen_ppm": r["nitrogen_ppm"],
            "health_score": r["health_score"],
            "recommendation": r["recommendation_text"],
        }
        for r in rows
    ])
