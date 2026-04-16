# 🌱 AgroBase — Agricultural Management Dashboard

A full-stack agricultural management system with a **Python Flask** backend connected to a **TiDB Cloud** (MySQL-compatible) database, and a live dashboard frontend.

## Project Structure

```
├── Frontend/
│   └── AgroBase_FullWidth_CommandCenter.html   # Dashboard UI
├── backend/
│   ├── app.py              # Flask API entry point
│   ├── config.py           # DB config
│   ├── db.py               # MySQL connection helper
│   ├── import_sql.py       # One-time DB import script
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Credentials template
│   └── routes/
│       ├── overview.py     # /api/overview/*
│       ├── crops.py        # /api/crops/*
│       ├── soil.py         # /api/soil/*
│       └── supply.py       # /api/supply/*
└── dbms_project.sql        # Full database schema + seed data
```

## Features

- **Overview Tab** — Total farms, fields, managed acres, active harvests; farm distribution by state; planting variety analysis
- **Crops & Yield Tab** — Avg yield, growth days, profit estimates; monthly yield trend chart
- **Soil & Water Tab** — Soil health score, composition breakdown, irrigation type distribution, live recommendations
- **Supply Chain Tab** — Distribution center load, infrastructure status, shipment tracking

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Chart.js |
| Backend | Python 3, Flask, Flask-CORS |
| Database | TiDB Cloud (MySQL-compatible) |
| DB Driver | mysql-connector-python |

## Setup

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure database
```bash
cp .env.example .env
# Edit .env with your TiDB Cloud credentials
```

### 3. Import database (first time only)
```bash
cd backend
python import_sql.py
```

### 4. Start the server
```bash
python app.py
# API running at http://localhost:5000
```

### 5. Open the dashboard
Open `Frontend/AgroBase_FullWidth_CommandCenter.html` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/overview/metrics` | KPI summary |
| GET | `/api/overview/farms-by-state` | Farm distribution chart data |
| GET | `/api/overview/crop-distribution` | Crop variety chart data |
| GET | `/api/crops/metrics` | Crop KPIs |
| GET | `/api/crops/performance` | Monthly yield trend |
| GET | `/api/crops/recent-yields` | Top crops by profit |
| GET | `/api/soil/metrics` | Soil health KPIs |
| GET | `/api/soil/composition` | Soil type breakdown |
| GET | `/api/soil/irrigation` | Irrigation type distribution |
| GET | `/api/soil/recommendations` | Latest soil recommendations |
| GET | `/api/supply/distribution-load` | Shipment weight per center |
| GET | `/api/supply/infrastructure-status` | System counts |
| GET | `/api/supply/recent-shipments` | Last 10 shipments |

## Database Schema

15 tables: `Farms`, `Fields`, `Crops`, `Crop_Plantings`, `Livestock`, `Weather_Readings`, `Soil_Samples`, `Irrigation_Systems`, `Pesticide_Applications`, `Harvests`, `Storage_Facilities`, `Processing_Plants`, `Distribution_Centers`, `Retail_Outlets`, `Product_Shipments`
