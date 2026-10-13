# Smart Inventory Intelligence System

**Stock-Out Risk & Demand Analytics**

## Problem Statement

Large inventory tables are difficult to scan for product availability, sales patterns, and potential stock-outs. This project organizes the team's inventory data into an interactive dashboard so users can compare actual sales with forecast demand, inspect stock levels, and find the risk labels and reorder recommendations already present in the cleaned data.

## Objectives

- Summarize products, sales, inventory, orders, demand, and stock-out risk.
- Explore results by store, category, region, and date.
- Compare forecast demand with units sold.
- Demonstrate a complete HTML/CSS/JavaScript frontend connected to a Flask/Pandas backend.
- Preserve the team's raw, cleaned, and preprocessed files as supplied.

## Dataset

The dashboard reads `stock_monitor_clean_dataset_final.csv` from the repository root. It contains approximately 73,000 observations and includes date, store, product, category, region, inventory level, units sold, units ordered, demand forecast, price, demand difference, stock coverage, stock-out risk, and reorder recommendation.

`RAW_DATASET.csv` and `Stock_Monitor_Preprocessed.xlsx` are existing team files. The application does not modify or regenerate them. Sales and orders are summed over the selected records; inventory and risk summaries use the latest available record per store-product pair in the selected period.

## Technologies

- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Backend:** Python, Flask, Pandas
- **Testing:** Python `unittest` and Flask's test client

## Existing Team Work

The repository already contains a raw CSV, a cleaned/enriched CSV, and a preprocessed Excel workbook. Those are existing project assets. The interactive dashboard, Flask API, proposal, and tests in this project structure are new development around the cleaned CSV. The previously tracked `data_analysis.ipynb` is deleted in the existing working tree and is intentionally not restored or changed.

## Dashboard Features

- Summary cards for unique products, units sold, latest inventory, units ordered, average forecast demand, and high-risk items.
- Filters for store, category, region, and date range.
- Charts for category sales, latest category inventory, demand forecast versus sales, stock-out risk, store inventory, and store sales.
- A risk and reorder watchlist sourced from the existing `Stock-Out Risk` and `Reorder Recommendation` fields.
- Responsive layout for laptop and smaller screens.

## Project Structure

```text
DAV_LAB/
├── RAW_DATASET.csv
├── stock_monitor_clean_dataset_final.csv
├── Stock_Monitor_Preprocessed.xlsx
├── backend/
│   ├── app.py
│   ├── analytics.py
│   └── data_loader.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── docs/
│   └── project_proposal.md
├── tests/
│   └── test_analytics.py
├── requirements.txt
└── README.md
```

## Installation

From the repository root, create and activate a virtual environment in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, run the app using `.venv\Scripts\python.exe` instead.

## Run the Backend and Dashboard

From the repository root:

```powershell
python -m flask --app backend.app run --debug
```

Open **http://127.0.0.1:5000/** in a browser. Flask serves the HTML, CSS, and JavaScript along with the API, so the frontend and backend use the same local origin. The charts use Chart.js from its CDN, which requires an internet connection when loading the page.

To run tests:

```powershell
python -m unittest discover -s tests -v
```

## API

All endpoints return JSON. Optional filters can be added to the summary, aggregation, sales, inventory, risk, and demand endpoints:

```text
?store_id=S001&category=Groceries&region=North&start_date=2022-01-01&end_date=2022-12-31
```

| Endpoint | Response |
|---|---|
| `GET /api/summary` | Selected-period sales/orders, average demand, unique products, and latest per-item inventory/risk counts. |
| `GET /api/categories` | Sales and latest inventory aggregated by category. |
| `GET /api/stores` | Sales and latest inventory aggregated by store. |
| `GET /api/regions` | Sales and latest inventory aggregated by region. |
| `GET /api/risk` | Latest risk distribution and up to 50 prioritized store-product rows with reorder recommendations. |
| `GET /api/sales` | Category and store sales aggregates. |
| `GET /api/inventory` | Category and store latest inventory aggregates. |
| `GET /api/demand` | Forecast demand and units sold by category over the selected period. |
| `GET /api/filters` | Available store/category/region choices and the dataset's date range. |

An invalid date returns HTTP 400 with a JSON `error` message. Unknown store, category, or region values return an empty selection rather than crashing.

## Team Contributions

Fill in this section with the actual names and work completed by each team member. Do not assign contributions without confirming them with the team.

| Team member | Contribution |
|---|---|
| Member 1 | To be completed by the team |
| Member 2 | To be completed by the team |
| Member 3 | To be completed by the team |

## Future Scope

Potential extensions include filtered report downloads, reorder simulations, forecast accuracy evaluation, inventory alerts, database-backed data updates, authentication, and hosted deployment. Any operational recommendations should be evaluated before use.
