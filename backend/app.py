"""Flask application serving inventory analytics and the dashboard frontend."""

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from backend.analytics import (
    aggregate_by_category,
    aggregate_by_region,
    aggregate_by_store,
    aggregate_demand,
    calculate_summary,
    filter_dataset,
    summarize_risk,
)
from backend.data_loader import DATASET_PATH, load_dataset


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FILTER_PARAMETERS = (
    "store_id",
    "category",
    "region",
    "start_date",
    "end_date",
)


def create_app(dataset=None) -> Flask:
    """Create the app and load the real cleaned CSV unless data is injected."""
    app = Flask(__name__)
    app.config["INVENTORY_DATA"] = (
        dataset.copy() if dataset is not None else load_dataset(DATASET_PATH)
    )

    def selected_data():
        filters = {
            parameter: request.args.get(parameter)
            for parameter in FILTER_PARAMETERS
        }
        return filter_dataset(app.config["INVENTORY_DATA"], filters)

    def json_result(builder):
        try:
            return jsonify(builder(selected_data()))
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    @app.get("/")
    def dashboard():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/style.css")
    def dashboard_styles():
        return send_from_directory(FRONTEND_DIR, "style.css")

    @app.get("/script.js")
    def dashboard_script():
        return send_from_directory(FRONTEND_DIR, "script.js")

    @app.get("/api/summary")
    def summary():
        return json_result(calculate_summary)

    @app.get("/api/categories")
    def categories():
        return json_result(aggregate_by_category)

    @app.get("/api/stores")
    def stores():
        return json_result(aggregate_by_store)

    @app.get("/api/regions")
    def regions():
        return json_result(aggregate_by_region)

    @app.get("/api/risk")
    def risk():
        return json_result(summarize_risk)

    @app.get("/api/sales")
    def sales():
        return json_result(
            lambda data: {
                "by_category": aggregate_by_category(data),
                "by_store": aggregate_by_store(data),
            }
        )

    @app.get("/api/inventory")
    def inventory():
        return json_result(
            lambda data: {
                "by_category": aggregate_by_category(data),
                "by_store": aggregate_by_store(data),
            }
        )

    @app.get("/api/demand")
    def demand():
        return json_result(aggregate_demand)

    @app.get("/api/filters")
    def filters():
        data = app.config["INVENTORY_DATA"]
        return jsonify(
            {
                "stores": sorted(data["Store ID"].dropna().astype(str).unique()),
                "categories": sorted(data["Category"].dropna().astype(str).unique()),
                "regions": sorted(data["Region"].dropna().astype(str).unique()),
                "min_date": data["Date"].min().strftime("%Y-%m-%d"),
                "max_date": data["Date"].max().strftime("%Y-%m-%d"),
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
