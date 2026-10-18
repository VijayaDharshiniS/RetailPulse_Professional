
from pathlib import Path
import pandas as pd

file_path = Path("data/processed/retailpulse_enriched.csv")

print("Loading enriched dataset...")
df = pd.read_csv(file_path)

print("\n1. Dataset shape")
print(df.shape)

print("\n2. Column names")
print(df.columns.tolist())

print("\n3. Duplicate rows")
print(df.duplicated().sum())

print("\n4. Missing values")
print(df.isnull().sum())

print("\n5. Invalid sales checks")
print("Zero or negative quantity:", (df["Quantity"] <= 0).sum())
print("Zero or negative price:", (df["Price"] <= 0).sum())
print("Missing invoice date:", df["InvoiceDate"].isnull().sum())

print("\n6. Sales calculation check")
expected_sales = df["Quantity"] * df["Price"]
mismatch = ~(
    (df["Sales"] - expected_sales).abs() < 0.000001
)
print("Sales calculation mismatches:", mismatch.sum())

print("\n7. Transaction type counts")
print(df["TransactionType"].value_counts())

print("\n8. Valid sale consistency")
expected_valid = (
    (~df["IsCancelled"].astype(bool))
    & (df["Quantity"] > 0)
    & (df["Price"] > 0)
    & df["InvoiceDate"].notna()
)
print(
    "IsValidSale mismatches:",
    (df["IsValidSale"].astype(bool) != expected_valid).sum()
)

print("\n9. Sample records")
print(df.head(5).to_string(index=False))

print("\nValidation completed.")
