
from pathlib import Path
import pandas as pd

base = Path("data/processed")

sales_file = base / "retailpulse_sales_features.csv"
customer_file = base / "retailpulse_customer_features.csv"

sales = pd.read_csv(sales_file)
customers = pd.read_csv(customer_file)

print("STEP 1: Dataset sizes")
print("Sales rows:", len(sales))
print("Customer rows:", len(customers))

print("\nSTEP 2: Missing customer IDs")
print("Sales file:", sales["Customer ID"].isna().sum())
print("Customer file:", customers["Customer ID"].isna().sum())

print("\nSTEP 3: Duplicate customer IDs")
print("Duplicates:", customers["Customer ID"].duplicated().sum())

print("\nSTEP 4: OrderValue validation")
expected_order_values = sales.groupby("Invoice")["Sales"].transform("sum")
order_value_errors = (
    sales["OrderValue"] - expected_order_values
).abs() > 0.000001
print("OrderValue mismatches:", order_value_errors.sum())

print("\nSTEP 5: Customer feature checks")
print("Frequency below 1:", (customers["CustomerFrequency"] < 1).sum())
print("Negative monetary values:", (customers["CustomerMonetary"] < 0).sum())
print("Negative recency:", (customers["DaysSinceLastPurchase"] < 0).sum())
print("Negative tenure:", (customers["CustomerTenureDays"] < 0).sum())

print("\nSTEP 6: Segment counts")
print(customers["CustomerSegment"].value_counts())

print("\nSTEP 7: Final status")
checks = {
    "No duplicate customer IDs": not customers["Customer ID"].duplicated().any(),
    "No missing customer IDs in customer table": customers["Customer ID"].notna().all(),
    "All order values correct": not order_value_errors.any(),
    "No negative recency": (customers["DaysSinceLastPurchase"] >= 0).all(),
    "No negative tenure": (customers["CustomerTenureDays"] >= 0).all()
}

for name, passed in checks.items():
    print(("PASS" if passed else "CHECK"), "-", name)

print("\nValidation finished.")
