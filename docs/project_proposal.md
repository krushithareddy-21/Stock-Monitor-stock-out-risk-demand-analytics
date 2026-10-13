# Project Proposal

## 1. Project Title

**Smart Inventory Intelligence System: Stock-Out Risk & Demand Analytics**

## 2. Introduction

Retailers need to balance product availability with the cost of holding stock. A stock-out can mean a missed sale, while ordering too much can tie up money and storage space. This project uses an inventory dataset to explore demand, sales, stock levels, and the stock-out risk labels already present in the data. The proposed web dashboard makes these patterns easier to inspect by store, category, region, and date.

## 3. Problem Statement

Inventory records can be difficult to interpret when they are viewed as a large spreadsheet. Students and inventory decision-makers need a clear way to compare actual sales with forecast demand, find products with higher stock-out risk, and review the existing reorder recommendations without replacing the dataset's risk definitions.

## 4. Objectives

- Explore inventory, sales, ordering, and demand patterns in the supplied data.
- Summarize existing high-, medium-, and low-risk stock records.
- Compare demand forecasts with units sold across product categories.
- Build a browser-based dashboard with store, category, region, and date filters.
- Connect a JavaScript frontend to a Python API that reads the cleaned CSV.
- Present the analysis in a format suitable for a classroom demonstration.

## 5. Dataset Description

The project uses `stock_monitor_clean_dataset_final.csv`, a prepared CSV with approximately 73,000 observations. Its fields include Date, Store ID, Product ID, Category, Region, Inventory Level, Units Sold, Units Ordered, Demand Forecast, Price, Demand Difference, Stock Coverage, Stock-Out Risk, and Reorder Recommendation. The original `RAW_DATASET.csv` and the team's preprocessed workbook remain part of the repository and are not replaced by the dashboard.

## 6. Data Collection

The raw inventory CSV is supplied in the project repository. The existing team work also includes a cleaned and enriched CSV and a preprocessed Excel workbook. The original collection source and collection procedure should be documented by the team based on its actual work; this proposal does not assume an external source that is not recorded in the repository.

## 7. Data Cleaning

The repository contains a cleaned dataset with additional derived fields, including Demand Difference, Stock Coverage, Stock-Out Risk, and Reorder Recommendation. The existing cleaning steps should be described and verified by the team using its original workflow. The new dashboard reads this prepared file and validates required columns; it does not rewrite either CSV or the workbook.

## 8. Data Analysis

The dashboard analysis will summarize sales and units ordered over the selected records, calculate average forecast demand, and compare forecast demand with actual units sold. For stock summaries and risk counts, it will use the latest available record for each store-product pair in the selected date range. Risk groups and suggested actions come directly from the existing Stock-Out Risk and Reorder Recommendation fields.

## 9. Data Visualization

The dashboard will use Chart.js to show category sales, current inventory by category, forecast demand versus sales, stock-out risk distribution, store inventory, and store sales. The visualizations will update when filters change and use actual aggregates from the CSV API.

## 10. Proposed Interactive Dashboard

The new dashboard will provide summary cards, dropdown filters for store, category, and region, optional date filters, charts, and a risk/reorder watchlist. A Flask API will serve JSON to the browser and also serve the frontend files so the dashboard can be opened from one local address. These dashboard components are new development; they are not claimed as part of the team's earlier completed work.

## 11. Frontend Technologies

- HTML for page structure and accessible controls.
- CSS for the responsive layout and visual styling.
- JavaScript and the Fetch API for filters, API requests, and rendering.
- Chart.js for interactive charts.

## 12. Backend Technologies

- Python for analytics and application logic.
- Flask for the local web server and JSON API.
- Pandas for CSV loading, filtering, and aggregation.

## 13. Methodology

1. Keep the supplied source data unchanged and load the cleaned CSV by a path resolved relative to the project files.
2. Check that required columns are present and parse the date and numeric fields.
3. Apply optional store, category, region, and inclusive date filters to API requests.
4. Aggregate sales and order totals over the selected period.
5. Use the latest available row for each store-product pair for inventory and risk summaries, avoiding summing repeated daily stock snapshots as if they were separate stock.
6. Return JSON from Flask and render it in the browser with Chart.js and a risk table.
7. Verify the analytics and API behavior with automated tests.

## 14. Expected Results

The expected outcome is a functioning local dashboard that helps users compare sales and forecast demand, inspect current inventory summaries, and find high-risk items with the corresponding existing reorder recommendations. The project will also demonstrate a basic frontend-to-backend data flow. These are expected results of the new implementation, not claims about features that existed in the repository beforehand.

## 15. Future Scope

Future work could add replenishment simulations, alert thresholds, downloadable filtered reports, user authentication, a database for ongoing updates, forecast model evaluation, and deployment to a hosted service. Such additions would require validation with stakeholders and should not be treated as automated operational advice without further testing.
