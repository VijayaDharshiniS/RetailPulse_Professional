
from pathlib import Path
import pandas as pd

# File locations
RAW_FILE = Path("data/raw/online_retail_II.xlsx")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "retailpulse_enriched.csv"

print("Loading original Excel dataset...")

# Load both sheets
sheets = pd.read_excel(RAW_FILE, sheet_name=None)

# Combine both years
df = pd.concat(sheets.values(), ignore_index=True)

print("Original dataset shape:", df.shape)

# Standardize column names
df.columns = df.columns.str.strip()

# Convert data types
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)

df["Price"] = pd.to_numeric(
    df["Price"], errors="coerce"
)

# Clean text fields without deleting transactions
df["Description"] = (
    df["Description"]
    .fillna("Unknown Product")
    .astype(str)
    .str.strip()
)

df["Country"] = df["Country"].astype(str).str.strip()

# Identify cancelled invoices
df["IsCancelled"] = (
    df["Invoice"].astype(str).str.startswith("C")
)

# Create business columns
df["Sales"] = df["Quantity"] * df["Price"]

df["InvoiceYear"] = df["InvoiceDate"].dt.year
df["InvoiceMonth"] = df["InvoiceDate"].dt.month

df["MonthName"] = df["InvoiceDate"].dt.strftime("%b")

df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()

df["IsWeekend"] = (
    df["InvoiceDate"].dt.dayofweek >= 5
)

# Create a transaction classification
df["TransactionType"] = "Sale"

df.loc[df["IsCancelled"], "TransactionType"] = "Cancellation"

df.loc[
    (~df["IsCancelled"]) & (df["Quantity"] < 0),
    "TransactionType"
] = "Return/Negative Quantity"

df.loc[
    (~df["IsCancelled"]) & (df["Price"] <= 0),
    "TransactionType"
] = "Invalid/Zero Price"

# Flag rows suitable for standard sales analysis
df["IsValidSale"] = (
    (~df["IsCancelled"])
    & (df["Quantity"] > 0)
    & (df["Price"] > 0)
    & df["InvoiceDate"].notna()
)

# Save enriched dataset; keep original records for auditability
df.to_csv(OUTPUT_FILE, index=False)

print("\nDataset preparation completed!")
print("Output file:", OUTPUT_FILE)
print("Final shape:", df.shape)

print("\nNew columns created:")
print([
    "Sales",
    "InvoiceYear",
    "InvoiceMonth",
    "MonthName",
    "DayOfWeek",
    "IsWeekend",
    "IsCancelled",
    "TransactionType",
    "IsValidSale"
])

print("\nTransaction types:")
print(df["TransactionType"].value_counts(dropna=False))

print("\nValid sale rows:", int(df["IsValidSale"].sum()))
print("Missing Customer IDs:", int(df["Customer ID"].isna().sum()))
print("Missing invoice dates:", int(df["InvoiceDate"].isna().sum()))
