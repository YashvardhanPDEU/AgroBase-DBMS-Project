"""
AgroBase Backend — Flask REST API
Connects to MySQL Agro database and serves dashboard data.

Start server:  python app.py
API base URL:  http://localhost:5000
"""

from flask import Flask, jsonify
from flask_cors import CORS

from routes.overview import overview_bp
from routes.crops import crops_bp
from routes.soil import soil_bp
from routes.supply import supply_bp

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend HTML file

# ── Register Blueprint routes ────────────────────────────────────────────────
app.register_blueprint(overview_bp)
app.register_blueprint(crops_bp)
app.register_blueprint(soil_bp)
app.register_blueprint(supply_bp)


# ── Health check ─────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    """Simple health-check endpoint to confirm the server is running."""
    return jsonify({"status": "ok", "message": "AgroBase API is running"})


# ── API overview / index ──────────────────────────────────────────────────────
@app.route("/api")
def api_index():
    """Lists all available endpoints."""
    endpoints = {
        "overview": {
            "GET /api/overview/metrics":          "KPI cards (farms, fields, acres, harvests)",
            "GET /api/overview/farms-by-state":   "Farm count grouped by state (bar chart)",
            "GET /api/overview/crop-distribution":"Planting count per crop type (donut chart)",
        },
        "crops": {
            "GET /api/crops/metrics":      "KPI cards (varieties, avg yield, growth, profit)",
            "GET /api/crops/performance":  "Monthly yield trend (line chart)",
            "GET /api/crops/recent-yields":"Top 4 crops by profit (right-panel table)",
            "GET /api/crops/list":         "Full crop list",
        },
        "soil": {
            "GET /api/soil/metrics":         "KPI cards (health, samples, nitrogen, water)",
            "GET /api/soil/composition":     "Soil type breakdown (pie chart)",
            "GET /api/soil/irrigation":      "Irrigation type distribution (donut chart)",
            "GET /api/soil/recommendations": "Latest soil recommendations",
            "GET /api/soil/samples":         "Full soil samples list",
        },
        "supply": {
            "GET /api/supply/distribution-load":    "Weight per distribution center (bar chart)",
            "GET /api/supply/infrastructure-status":"Counts of systems/sensors/centers",
            "GET /api/supply/recent-shipments":     "Last 10 shipments",
            "GET /api/supply/processing-plants":    "All processing plants",
        },
    }
    return jsonify({"api": "AgroBase", "version": "1.0", "endpoints": endpoints})


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "detail": str(e)}), 500


if __name__ == "__main__":
    print("=" * 55)
    print("  AgroBase API  --  http://localhost:5000")
    print("  Endpoints:       http://localhost:5000/api")
    print("=" * 55)
    app.run(debug=True, port=5000)
