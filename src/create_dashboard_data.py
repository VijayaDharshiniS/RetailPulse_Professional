
from pathlib import Path

import pandas as pd

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR = PROJECT_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load prepared datasets
sales = pd.read_csv(
    DATA_DIR / "retailpulse_sales_features.csv",
    parse_dates=["InvoiceDate"],
)

customers = pd.read_csv(
    DATA_DIR / "retailpulse_customer_features.csv",
    parse_dates=["FirstPurchaseDate", "LastPurchaseDate"],
)

print("Datasets loaded successfully!")
print(f"Sales rows: {len(sales):,}")
print(f"Customers: {len(customers):,}")

# 1. Monthly sales summary
sales["YearMonth"] = sales["InvoiceDate"].dt.to_period("M").astype(str)

monthly_sales = (
    sales.groupby("YearMonth", as_index=False)
    .agg(
        TotalSales=("Sales", "sum"),
        TotalOrders=("Invoice", "nunique"),
        TotalQuantity=("Quantity", "sum"),
        UniqueCustomers=("Customer ID", "nunique"),
    )
)

monthly_sales.to_csv(
    OUTPUT_DIR / "monthly_sales_summary.csv", index=False
)

# 2. Country-wise sales summary
country_sales = (
    sales.groupby("Country", as_index=False)
    .agg(
        TotalSales=("Sales", "sum"),
        TotalOrders=("Invoice", "nunique"),
        TotalQuantity=("Quantity", "sum"),
        UniqueCustomers=("Customer ID", "nunique"),
    )
    .sort_values("TotalSales", ascending=False)
)

country_sales.to_csv(
    OUTPUT_DIR / "country_sales_summary.csv", index=False
)

# 3. Top products by sales
product_sales = (
    sales.groupby(["StockCode", "Description"], as_index=False)
    .agg(
        TotalSales=("Sales", "sum"),
        TotalQuantity=("Quantity", "sum"),
        TotalOrders=("Invoice", "nunique"),
    )
    .sort_values("TotalSales", ascending=False)
)

product_sales.to_csv(
    OUTPUT_DIR / "product_sales_summary.csv", index=False
)

# 4. Customer segment summary
segment_summary = (
    customers.groupby("CustomerSegment", as_index=False)
    .agg(
        TotalCustomers=("Customer ID", "nunique"),
        TotalRevenue=("CustomerMonetary", "sum"),
        AverageOrders=("CustomerFrequency", "mean"),
        AverageCustomerValue=("CustomerMonetary", "mean"),
    )
    .sort_values("TotalCustomers", ascending=False)
)

segment_summary.to_csv(
    OUTPUT_DIR / "customer_segment_summary.csv", index=False
)

# 5. Overall KPI summary
kpi_summary = pd.DataFrame(
    [
        {
            "TotalSales": sales["Sales"].sum(),
            "TotalOrders": sales["Invoice"].nunique(),
            "TotalCustomers": sales["Customer ID"].nunique(),
            "TotalQuantity": sales["Quantity"].sum(),
            "TotalProducts": sales["StockCode"].nunique(),
            "TotalCountries": sales["Country"].nunique(),
            "AverageOrderValue": sales.groupby("Invoice")["Sales"].sum().mean(),
        }
    ]
)

kpi_summary.to_csv(
    OUTPUT_DIR / "overall_kpi_summary.csv", index=False
)

# Show completion details
print("\nDashboard datasets created successfully!")

print("\nFiles created:")
print("1. monthly_sales_summary.csv")
print("2. country_sales_summary.csv")
print("3. product_sales_summary.csv")
print("4. customer_segment_summary.csv")
print("5. overall_kpi_summary.csv")

print("\nTop 5 countries by sales:")
print(country_sales.head().to_string(index=False))

print("\nCustomer segments:")
print(segment_summary.to_string(index=False))

print("\nAll output files are saved in the outputs folder.")
