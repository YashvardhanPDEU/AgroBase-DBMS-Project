from flask import Blueprint, jsonify, request
from db import query, query_one, execute

overview_bp = Blueprint("overview", __name__, url_prefix="/api/overview")


@overview_bp.route("/farms", methods=["POST"])
def add_farm():
    """
    Add a new farm from the website form.
    Body JSON: { farm_name, location, owner, size_acres, carbon_footprint_tons }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["farm_name", "location", "owner", "size_acres"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Auto-increment the farm_id
    row = query_one("SELECT COALESCE(MAX(farm_id), 0) + 1 AS next_id FROM Farms")
    next_id = row["next_id"]

    execute(
        """INSERT INTO Farms (farm_id, farm_name, location, owner, size_acres, carbon_footprint_tons)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (next_id, data["farm_name"], data["location"], data["owner"],
         int(data["size_acres"]), float(data.get("carbon_footprint_tons", 0)))
    )
    return jsonify({"success": True, "farm_id": next_id, "message": f"Farm '{data['farm_name']}' added successfully!"}), 201


@overview_bp.route("/farms/list", methods=["GET"])
def list_farms():
    """Return all farms for the management table."""
    rows = query("SELECT farm_id, farm_name, location, owner, size_acres, carbon_footprint_tons FROM Farms ORDER BY farm_id")
    return jsonify(rows)


@overview_bp.route("/farms/<int:farm_id>", methods=["DELETE"])
def delete_farm(farm_id):
    """Delete a farm by ID."""
    row = query_one("SELECT farm_id FROM Farms WHERE farm_id = %s", (farm_id,))
    if not row:
        return jsonify({"error": "Farm not found"}), 404
    execute("DELETE FROM Farms WHERE farm_id = %s", (farm_id,))
    return jsonify({"success": True, "message": f"Farm #{farm_id} deleted."})



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
