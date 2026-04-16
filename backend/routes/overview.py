from flask import Blueprint, jsonify
from db import query, query_one

overview_bp = Blueprint("overview", __name__, url_prefix="/api/overview")


@overview_bp.route("/metrics")
def metrics():
    """
    Summary KPIs for the Overview dashboard card row.
    Returns: total farms, total fields, total managed acres, active harvests count.
    """
    total_farms = query_one("SELECT COUNT(*) AS total FROM Farms")["total"]
    total_fields = query_one("SELECT COUNT(*) AS total FROM Fields")["total"]
    managed_acres = query_one("SELECT COALESCE(SUM(area_acres), 0) AS total FROM Fields")["total"]

    # Active harvests = plantings whose expected_harvest_date >= today
    active_harvests = query_one(
        "SELECT COUNT(*) AS total FROM Crop_Plantings WHERE expected_harvest_date >= CURDATE()"
    )["total"]

    return jsonify({
        "total_farms": total_farms,
        "total_fields": total_fields,
        "managed_acres": int(managed_acres),
        "active_harvests": active_harvests,
    })


@overview_bp.route("/farms-by-state")
def farms_by_state():
    """
    Farm count grouped by state, for the Regional Farm Distribution bar chart.
    Returns top 8 states sorted by farm count desc.
    """
    rows = query(
        """
        SELECT location AS state, COUNT(*) AS count
        FROM Farms
        GROUP BY location
        ORDER BY count DESC
        LIMIT 8
        """
    )
    return jsonify({
        "labels": [r["state"] for r in rows],
        "data": [r["count"] for r in rows],
    })


@overview_bp.route("/crop-distribution")
def crop_distribution():
    """
    Number of plantings per crop type, for the Planting Variety Analysis doughnut chart.
    """
    rows = query(
        """
        SELECT c.crop_name, COUNT(cp.planting_id) AS count
        FROM Crops c
        LEFT JOIN Crop_Plantings cp ON c.crop_id = cp.crop_id
        GROUP BY c.crop_name
        ORDER BY count DESC
        """
    )
    return jsonify({
        "labels": [r["crop_name"] for r in rows],
        "data": [r["count"] for r in rows],
    })
