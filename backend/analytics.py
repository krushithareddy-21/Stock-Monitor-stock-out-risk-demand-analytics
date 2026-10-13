"""Filtering and aggregation functions used by the dashboard API."""

import pandas as pd


RISK_LEVELS = ["High", "Medium", "Low"]
ITEM_KEY = ["Store ID", "Product ID"]


def filter_dataset(
    dataset: pd.DataFrame, filters: dict[str, str | None]
) -> pd.DataFrame:
    """Apply optional store, category, region, and inclusive date filters."""
    result = dataset
    column_filters = {
        "store_id": "Store ID",
        "category": "Category",
        "region": "Region",
    }
    for parameter, column in column_filters.items():
        value = filters.get(parameter)
        if value:
            result = result[result[column].astype(str) == value]

    for parameter, operator in (("start_date", ">="), ("end_date", "<=")):
        value = filters.get(parameter)
        if value:
            try:
                date_value = pd.Timestamp(value)
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid {parameter}: use YYYY-MM-DD.") from error
            if pd.isna(date_value):
                raise ValueError(f"Invalid {parameter}: use YYYY-MM-DD.")
            if operator == ">=":
                result = result[result["Date"] >= date_value]
            else:
                result = result[result["Date"] <= date_value]

    return result


def latest_item_snapshot(dataset: pd.DataFrame) -> pd.DataFrame:
    """Return the latest observation for each store and product in the selection."""
    if dataset.empty:
        return dataset.copy()
    return (
        dataset.sort_values("Date")
        .drop_duplicates(ITEM_KEY, keep="last")
        .copy()
    )


def calculate_summary(dataset: pd.DataFrame) -> dict[str, int | float]:
    """Summarize sales and demand over the selection and stock from latest items."""
    snapshot = latest_item_snapshot(dataset)
    risk_counts = snapshot["Stock-Out Risk"].value_counts()
    return {
        "total_products": int(dataset["Product ID"].nunique()),
        "total_units_sold": int(dataset["Units Sold"].sum()),
        "total_inventory": int(snapshot["Inventory Level"].sum()),
        "total_units_ordered": int(dataset["Units Ordered"].sum()),
        "average_demand_forecast": round(
            float(dataset["Demand Forecast"].mean()), 2
        )
        if not dataset.empty
        else 0,
        "high_risk_products": int(risk_counts.get("High", 0)),
        "medium_risk_products": int(risk_counts.get("Medium", 0)),
        "low_risk_products": int(risk_counts.get("Low", 0)),
    }


def aggregate_by_category(dataset: pd.DataFrame) -> list[dict[str, object]]:
    """Aggregate sales and latest stock levels by product category."""
    sales = dataset.groupby("Category", as_index=False).agg(
        units_sold=("Units Sold", "sum")
    )
    inventory = latest_item_snapshot(dataset).groupby("Category", as_index=False).agg(
        inventory_level=("Inventory Level", "sum")
    )
    result = sales.merge(inventory, on="Category", how="outer").fillna(0)
    return result.sort_values("Category").to_dict(orient="records")


def aggregate_by_store(dataset: pd.DataFrame) -> list[dict[str, object]]:
    """Aggregate sales and latest stock levels by store."""
    sales = dataset.groupby("Store ID", as_index=False).agg(
        units_sold=("Units Sold", "sum")
    )
    inventory = latest_item_snapshot(dataset).groupby("Store ID", as_index=False).agg(
        inventory_level=("Inventory Level", "sum")
    )
    result = sales.merge(inventory, on="Store ID", how="outer").fillna(0)
    return result.sort_values("Store ID").to_dict(orient="records")


def aggregate_by_region(dataset: pd.DataFrame) -> list[dict[str, object]]:
    """Aggregate sales and latest stock levels by region."""
    sales = dataset.groupby("Region", as_index=False).agg(
        units_sold=("Units Sold", "sum")
    )
    inventory = latest_item_snapshot(dataset).groupby("Region", as_index=False).agg(
        inventory_level=("Inventory Level", "sum")
    )
    result = sales.merge(inventory, on="Region", how="outer").fillna(0)
    return result.sort_values("Region").to_dict(orient="records")


def aggregate_demand(dataset: pd.DataFrame) -> list[dict[str, object]]:
    """Compare forecast demand and actual sales by category."""
    result = dataset.groupby("Category", as_index=False).agg(
        demand_forecast=("Demand Forecast", "sum"),
        units_sold=("Units Sold", "sum"),
    )
    return result.sort_values("Category").to_dict(orient="records")


def summarize_risk(dataset: pd.DataFrame) -> dict[str, object]:
    """Return risk counts and the highest-priority current store-product items."""
    snapshot = latest_item_snapshot(dataset)
    counts = snapshot["Stock-Out Risk"].value_counts()
    distribution = [
        {"risk": level, "count": int(counts.get(level, 0))}
        for level in RISK_LEVELS
    ]
    items = snapshot.copy()
    items["_risk_order"] = items["Stock-Out Risk"].map(
        {"High": 0, "Medium": 1, "Low": 2}
    ).fillna(3)
    items = items.sort_values(
        ["_risk_order", "Inventory Level", "Product ID"]
    ).head(50)
    columns = {
        "Date": "date",
        "Store ID": "store_id",
        "Product ID": "product_id",
        "Category": "category",
        "Region": "region",
        "Inventory Level": "inventory_level",
        "Demand Forecast": "demand_forecast",
        "Stock Coverage": "stock_coverage",
        "Stock-Out Risk": "risk",
        "Reorder Recommendation": "recommendation",
    }
    items = items[list(columns)].rename(columns=columns)
    items["date"] = items["date"].dt.strftime("%Y-%m-%d")
    items = items.astype(object).where(pd.notna(items), None)
    return {
        "distribution": distribution,
        "items": items.to_dict(orient="records"),
    }
