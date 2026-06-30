# Fleet Ops Console

A Fleet Operations dashboard for monitoring autonomous robots at Punggol Digital District.

## Quick Start

### Prerequisites
- Python 3.9+ (the only requirement — the frontend is a dependency-free static page)

### Installation & Running

**1. Install backend dependencies** (from `backend/` directory):
```powershell
cd backend
py -m pip install -r requirements.txt
```

**2. Start the backend** (from `backend/` directory):
```powershell
py app.py
```
API runs on `http://localhost:5000`

**3. In a new terminal, serve the dashboard** (from the repo root):
```powershell
py -m http.server 3000
```
Open `http://localhost:3000` in your browser.

> The dashboard (`index.html`) is plain HTML/JS and calls the Flask API directly, so no
> Node.js / npm toolchain is required to run it.

## Project Structure

```
├── index.html                 # The dashboard (static, no build step)
├── backend/
│   ├── app.py                 # Flask server & API endpoints
│   ├── data_processor.py      # CSV parsing, cleaning & metric calculation
│   └── requirements.txt
├── data/                       # CSV data files
├── summary.json                # Machine-readable results
├── DECISIONS.md                # Assumptions, definitions, trade-offs
├── RND_MEMO.md                 # Proposed next capability
├── WALKTHROUGH.md              # Written walkthrough
├── starter/                    # Provided templates
└── README.md
```

## Features

- **Fleet Overview**: Real-time robot status and key metrics
- **Per-Robot Drill-down**: Detailed metrics for individual robots
- **Data Quality Panel**: Anomalies detected and metric definitions
- **Key Metrics**:
  - Robot availability/uptime
  - QR scan conversion rate
  - Vending revenue
  - Navigation events & faults

## Data Quality

The application automatically detects and reports data quality issues. See the "Data Quality Panel" on the dashboard for:
- Zone name inconsistencies
- Missing fields
- Data anomalies

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/dashboard` - Complete dashboard data
- `GET /api/robot/:robotId` - Robot-specific details

## Notes

- The backend reads CSV files from the `data/` directory
- No database is required; data is processed in-memory on startup
- The frontend communicates with the backend via the proxy (configured in frontend/package.json)
