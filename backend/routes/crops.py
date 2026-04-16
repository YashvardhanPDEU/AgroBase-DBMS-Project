from flask import Blueprint, jsonify
from db import query, query_one

crops_bp = Blueprint("crops", __name__, url_prefix="/api/crops")


@crops_bp.route("/metrics")
def metrics():
    """
    KPI cards for the Crops & Yield tab.
    Returns: distinct crop varieties, avg predicted yield, avg growth days, max profit estimate.
    """
    varieties = query_one("SELECT COUNT(DISTINCT crop_name) AS total FROM Crops")["total"]

    avg_yield = query_one(
        "SELECT ROUND(AVG(predicted_yield_tons), 1) AS avg_yield FROM Crop_Plantings"
    )["avg_yield"]

    avg_growth = query_one(
        "SELECT ROUND(AVG(growth_days)) AS avg_growth FROM Crops"
    )["avg_growth"]

    max_profit = query_one(
        "SELECT MAX(profit_estimate) AS max_profit FROM Crops"
    )["max_profit"]

    return jsonify({
        "varieties": varieties,
        "avg_yield_tons": float(avg_yield) if avg_yield else 0,
        "avg_growth_days": int(avg_growth) if avg_growth else 0,
        "max_profit": float(max_profit) if max_profit else 0,
    })


@crops_bp.route("/performance")
def performance():
    """
    Monthly total predicted yield grouped by harvest month, for the Crop Performance line chart.
    Returns last 6 months of data.
    """
    rows = query(
        """
        SELECT
            DATE_FORMAT(expected_harvest_date, '%b %Y') AS month_label,
            DATE_FORMAT(expected_harvest_date, '%Y-%m') AS month_key,
            ROUND(SUM(predicted_yield_tons), 1) AS total_yield
        FROM Crop_Plantings
        WHERE expected_harvest_date IS NOT NULL
        GROUP BY month_key, month_label
        ORDER BY month_key DESC
        LIMIT 6
        """
    )
    # Reverse so chart shows oldest → newest
    rows = list(reversed(rows))
    return jsonify({
        "labels": [r["month_label"] for r in rows],
        "data": [float(r["total_yield"]) for r in rows],
    })


@crops_bp.route("/recent-yields")
def recent_yields():
    """
    Top 4 crops by highest profit estimate, shown in the right panel table.
    """
    rows = query(
        """
        SELECT
            CONCAT(crop_name, ' (Variety ', crop_id, ')') AS label,
            profit_estimate
        FROM Crops
        ORDER BY profit_estimate DESC
        LIMIT 4
        """
    )
    return jsonify([
        {"label": r["label"], "profit": float(r["profit_estimate"])}
        for r in rows
    ])


@crops_bp.route("/list")
def crop_list():
    """
    Full list of all crops with details.
    """
    rows = query(
        """
        SELECT crop_id, crop_name, growth_days, season,
               predicted_price_per_ton, profit_estimate
        FROM Crops
        ORDER BY crop_name
        """
    )
    return jsonify([
        {
            "crop_id": r["crop_id"],
            "crop_name": r["crop_name"],
            "growth_days": r["growth_days"],
            "season": r["season"],
            "predicted_price_per_ton": float(r["predicted_price_per_ton"]),
            "profit_estimate": float(r["profit_estimate"]),
        }
        for r in rows
    ])
