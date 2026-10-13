"""Tests for CSV loading, analytics calculations, and Flask JSON endpoints."""

import unittest

import pandas as pd

from backend.analytics import calculate_summary, filter_dataset, summarize_risk
from backend.app import create_app
from backend.data_loader import REQUIRED_COLUMNS, load_dataset


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()

    def test_cleaned_csv_loads_with_required_columns(self):
        self.assertGreater(len(self.dataset), 0)
        self.assertTrue(REQUIRED_COLUMNS.issubset(self.dataset.columns))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.dataset["Date"]))

    def test_summary_calculates_values_from_real_dataset(self):
        summary = calculate_summary(self.dataset)

        self.assertEqual(summary["total_products"], self.dataset["Product ID"].nunique())
        self.assertEqual(summary["total_units_sold"], self.dataset["Units Sold"].sum())
        self.assertEqual(summary["total_units_ordered"], self.dataset["Units Ordered"].sum())
        self.assertGreater(summary["total_inventory"], 0)
        self.assertGreater(summary["average_demand_forecast"], 0)
        self.assertEqual(
            summary["high_risk_products"]
            + summary["medium_risk_products"]
            + summary["low_risk_products"],
            self.dataset[["Store ID", "Product ID"]].drop_duplicates().shape[0],
        )

    def test_existing_risk_labels_are_recognized(self):
        risk = summarize_risk(self.dataset)
        counts = {item["risk"]: item["count"] for item in risk["distribution"]}

        self.assertEqual(list(counts), ["High", "Medium", "Low"])
        self.assertTrue(set(self.dataset["Stock-Out Risk"].dropna()).issubset(counts))
        self.assertTrue(risk["items"])
        self.assertIn("recommendation", risk["items"][0])

    def test_filters_support_values_and_reject_invalid_dates(self):
        selected = filter_dataset(
            self.dataset,
            {"store_id": "S001", "category": None, "region": None,
             "start_date": None, "end_date": None},
        )
        self.assertTrue((selected["Store ID"] == "S001").all())

        with self.assertRaisesRegex(ValueError, "Invalid start_date"):
            filter_dataset(
                self.dataset,
                {"store_id": None, "category": None, "region": None,
                 "start_date": "not-a-date", "end_date": None},
            )


class FlaskApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()

    def setUp(self):
        app = create_app(self.dataset)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_flask_dashboard_and_api_start(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Inventory", response.data)

    def test_api_endpoints_return_json(self):
        for endpoint in (
            "summary", "categories", "stores", "regions", "risk",
            "sales", "inventory", "demand", "filters",
        ):
            with self.subTest(endpoint=endpoint):
                response = self.client.get(f"/api/{endpoint}")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.is_json)

    def test_api_applies_filters_and_handles_invalid_dates(self):
        response = self.client.get("/api/summary?store_id=S001&category=Groceries")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertEqual(
            response.get_json()["total_products"],
            self.dataset.loc[
                (self.dataset["Store ID"] == "S001")
                & (self.dataset["Category"] == "Groceries"),
                "Product ID",
            ].nunique(),
        )

        invalid = self.client.get("/api/summary?start_date=bad-date")
        self.assertEqual(invalid.status_code, 400)
        self.assertTrue(invalid.is_json)
        self.assertIn("error", invalid.get_json())

    def test_frontend_can_request_backend_data(self):
        script = self.client.get("/script.js")
        summary = self.client.get("/api/summary")
        self.assertEqual(script.status_code, 200)
        self.assertIn(b"fetch(`/api/", script.data)
        self.assertEqual(summary.status_code, 200)
        self.assertIn("total_units_sold", summary.get_json())


if __name__ == "__main__":
    unittest.main()
