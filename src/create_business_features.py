
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/processed/retailpulse_enriched.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE, parse_dates=["InvoiceDate"])

# Use only positive, non-cancelled sales for customer analytics
sales = df.loc[
    df["IsValidSale"].astype(bool)
    & df["Customer ID"].notna()
].copy()

# Normalize customer IDs for consistent grouping
sales["Customer ID"] = sales["Customer ID"].astype(str)

# 1. Order-level feature: total valid sales per invoice
order_values = (
    sales.groupby("Invoice")["Sales"]
    .sum()
    .rename("OrderValue")
)

sales["OrderValue"] = sales["Invoice"].map(order_values)

# 2. Customer-level features
customer_features = (
    sales.groupby("Customer ID")
    .agg(
        CustomerFrequency=("Invoice", "nunique"),
        CustomerMonetary=("Sales", "sum"),
        FirstPurchaseDate=("InvoiceDate", "min"),
        LastPurchaseDate=("InvoiceDate", "max"),
        TotalItemsPurchased=("Quantity", "sum"),
        UniqueProducts=("StockCode", "nunique"),
        UniqueCountries=("Country", "nunique")
    )
    .reset_index()
)

# Reference date: one day after the latest valid observed transaction
reference_date = sales["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)

customer_features["DaysSinceLastPurchase"] = (
    reference_date - customer_features["LastPurchaseDate"].dt.normalize()
).dt.days

customer_features["CustomerTenureDays"] = (
    customer_features["LastPurchaseDate"].dt.normalize()
    - customer_features["FirstPurchaseDate"].dt.normalize()
).dt.days

# 3. Label customer segments using transparent RFM-style rules
recency = customer_features["DaysSinceLastPurchase"]
frequency = customer_features["CustomerFrequency"]
monetary = customer_features["CustomerMonetary"]

customer_features["CustomerSegment"] = "Regular Customer"

customer_features.loc[
    (recency <= 90) & (frequency >= 5),
    "CustomerSegment"
] = "Loyal Active Customer"

customer_features.loc[
    (monetary >= monetary.quantile(0.75)) & (frequency < 5),
    "CustomerSegment"
] = "High Spending Customer"

customer_features.loc[
    recency > 180,
    "CustomerSegment"
] = "At Risk Customer"

# Save transaction-level and customer-level datasets separately
sales.to_csv(
    OUTPUT_DIR / "retailpulse_sales_features.csv",
    index=False
)

customer_features.to_csv(
    OUTPUT_DIR / "retailpulse_customer_features.csv",
    index=False
)

print("Business feature creation completed!")
print("\nTransaction-level feature dataset:", sales.shape)
print("Customer-level feature dataset:", customer_features.shape)

print("\nNew transaction columns:")
print(["OrderValue"])

print("\nNew customer columns:")
print(customer_features.columns.tolist())

print("\nCustomer segment counts:")
print(customer_features["CustomerSegment"].value_counts())

print("\nSample customer records:")
print(customer_features.head().to_string(index=False))

print("\nFiles saved in data/processed/")
