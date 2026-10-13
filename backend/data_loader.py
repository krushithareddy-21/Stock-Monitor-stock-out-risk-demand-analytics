"""Load and validate the cleaned inventory dataset."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "stock_monitor_clean_dataset_final.csv"

REQUIRED_COLUMNS = {
    "Date",
    "Store ID",
    "Product ID",
    "Category",
    "Region",
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast",
    "Price",
    "Demand Difference",
    "Stock Coverage",
    "Stock-Out Risk",
    "Reorder Recommendation",
}


def load_dataset(path: Path | str = DATASET_PATH) -> pd.DataFrame:
    """Read the cleaned CSV and check that dashboard-required columns exist."""
    dataset = pd.read_csv(path, parse_dates=["Date"])
    missing_columns = REQUIRED_COLUMNS.difference(dataset.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required columns: {missing}")

    numeric_columns = [
        "Inventory Level",
        "Units Sold",
        "Units Ordered",
        "Demand Forecast",
        "Price",
        "Demand Difference",
        "Stock Coverage",
    ]
    for column in numeric_columns:
        dataset[column] = pd.to_numeric(dataset[column], errors="coerce")

    return dataset
