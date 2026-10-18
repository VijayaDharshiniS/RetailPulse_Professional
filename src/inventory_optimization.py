
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "retailpulse_sales_features.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "inventory_recommendations.csv"


def main():
    print("Loading retail sales data...")

    df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])

    # Remove rows without a product code or valid date
    df = df.dropna(subset=["StockCode", "InvoiceDate"]).copy()

    # Keep positive-quantity sales
    df = df[df["Quantity"] > 0].copy()

    if df.empty:
        print("No valid sales records found.")
        return

    # Count product sales and estimate average monthly demand
    product_summary = (
        df.groupby("StockCode")
        .agg(
            ProductDescription=("Description", "first"),
            TotalUnitsSold=("Quantity", "sum"),
            TotalOrders=("Invoice", "nunique"),
            TotalRevenue=("Sales", "sum"),
            FirstSaleDate=("InvoiceDate", "min"),
            LastSaleDate=("InvoiceDate", "max"),
        )
        .reset_index()
    )

    # Use the dataset's overall date range for comparable estimates
    first_date = df["InvoiceDate"].min()
    last_date = df["InvoiceDate"].max()

    months_observed = max(
        (last_date.year - first_date.year) * 12
        + last_date.month - first_date.month + 1,
        1,
    )

    product_summary["AverageMonthlyUnits"] = (
        product_summary["TotalUnitsSold"] / months_observed
    )

    # Rank products by units sold
    product_summary["DemandRank"] = (
        product_summary["TotalUnitsSold"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    # Sales-based priority, not actual stock availability
    def assign_priority(row):
        if row["DemandRank"] <= 100:
            return "High Demand"
        elif row["AverageMonthlyUnits"] >= 5:
            return "Monitor Demand"
        else:
            return "Lower Demand"

    product_summary["InventoryPriority"] = (
        product_summary.apply(assign_priority, axis=1)
    )

    # Approximate one-month demand planning quantity
    product_summary["SuggestedMonthlyPlanningUnits"] = (
        product_summary["AverageMonthlyUnits"].round().astype(int)
    )

    product_summary = product_summary.sort_values(
        "TotalUnitsSold", ascending=False
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    product_summary.to_csv(OUTPUT_PATH, index=False)

    print("\nInventory analysis completed!")
    print("Products analysed:", len(product_summary))

    print("\nPriority counts:")
    print(product_summary["InventoryPriority"].value_counts())

    print("\nTop 10 products by units sold:")
    print(
        product_summary[
            [
                "StockCode",
                "ProductDescription",
                "TotalUnitsSold",
                "AverageMonthlyUnits",
                "InventoryPriority",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nSaved to:", OUTPUT_PATH)
    print(
        "\nNote: These are sales-based planning estimates. "
        "Actual stock levels and reorder quantities require "
        "inventory and supplier lead-time data."
    )


if __name__ == "__main__":
    main()
