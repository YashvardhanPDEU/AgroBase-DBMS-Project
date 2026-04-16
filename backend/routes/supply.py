from flask import Blueprint, jsonify
from db import query, query_one

supply_bp = Blueprint("supply", __name__, url_prefix="/api/supply")


@supply_bp.route("/distribution-load")
def distribution_load():
    """
    Total shipment weight per Distribution Center, for the bar chart.
    """
    rows = query(
        """
        SELECT dc.name AS center_name, dc.location,
               dc.capacity_units,
               COALESCE(SUM(ps.weight_tons), 0) AS total_weight_tons,
               COUNT(ps.shipment_id) AS shipment_count
        FROM Distribution_Centers dc
        LEFT JOIN Product_Shipments ps ON dc.center_id = ps.destination_id
        GROUP BY dc.center_id, dc.name, dc.location, dc.capacity_units
        ORDER BY total_weight_tons DESC
        """
    )
    return jsonify({
        "labels": [r["center_name"] for r in rows],
        "data": [float(r["total_weight_tons"]) for r in rows],
        "capacity": [r["capacity_units"] for r in rows],
        "shipment_count": [r["shipment_count"] for r in rows],
    })


@supply_bp.route("/infrastructure-status")
def infrastructure_status():
    """
    Count-based status of key infrastructure across all farms.
    """
    irrigation_count = query_one(
        "SELECT COUNT(*) AS total FROM Irrigation_Systems"
    )["total"]

    soil_sensors = query_one(
        "SELECT COUNT(DISTINCT field_id) AS total FROM Soil_Samples"
    )["total"]

    dist_centers = query_one(
        "SELECT COUNT(*) AS total FROM Distribution_Centers"
    )["total"]

    active_shipments = query_one(
        "SELECT COUNT(*) AS total FROM Product_Shipments"
    )["total"]

    return jsonify({
        "irrigation_systems": irrigation_count,
        "soil_sensors_active": soil_sensors,
        "distribution_centers": dist_centers,
        "total_shipments": active_shipments,
    })


@supply_bp.route("/recent-shipments")
def recent_shipments():
    """
    Last 10 shipments with harvest and destination details.
    """
    rows = query(
        """
        SELECT ps.shipment_id, ps.shipment_date, ps.weight_tons,
               ps.traceability_code,
               dc.name AS destination,
               h.harvest_date, h.yield_tons AS harvest_yield,
               c.crop_name
        FROM Product_Shipments ps
        JOIN Distribution_Centers dc ON ps.destination_id = dc.center_id
        JOIN Harvests h ON ps.harvest_id = h.harvest_id
        JOIN Crop_Plantings cp ON h.planting_id = cp.planting_id
        JOIN Crops c ON cp.crop_id = c.crop_id
        ORDER BY ps.shipment_date DESC
        LIMIT 10
        """
    )
    return jsonify([
        {
            "shipment_id": r["shipment_id"],
            "date": str(r["shipment_date"]),
            "weight_tons": float(r["weight_tons"]),
            "traceability": r["traceability_code"],
            "destination": r["destination"],
            "crop": r["crop_name"],
        }
        for r in rows
    ])


@supply_bp.route("/processing-plants")
def processing_plants():
    """
    All processing plants with storage facility info.
    """
    rows = query(
        """
        SELECT pp.plant_id, pp.name, pp.location,
               pp.capacity_tons_per_day, pp.certification_type,
               pp.cert_expiry_date, sf.location AS storage_location,
               sf.capacity_tons AS storage_capacity
        FROM Processing_Plants pp
        LEFT JOIN Storage_Facilities sf ON pp.facility_id = sf.facility_id
        ORDER BY pp.capacity_tons_per_day DESC
        """
    )
    return jsonify([
        {
            "plant_id": r["plant_id"],
            "name": r["name"],
            "location": r["location"],
            "capacity_per_day": r["capacity_tons_per_day"],
            "certification": r["certification_type"],
            "cert_expiry": str(r["cert_expiry_date"]),
            "storage_location": r["storage_location"],
            "storage_capacity_tons": r["storage_capacity"],
        }
        for r in rows
    ])
