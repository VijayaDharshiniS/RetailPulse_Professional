
from pathlib import Path
import pandas as pd

input_file = Path("data/processed/retailpulse_enriched.csv")
output_file = Path("outputs/duplicate_review.csv")

df = pd.read_csv(input_file)

# Create output folder if needed
output_file.parent.mkdir(parents=True, exist_ok=True)

# Find rows that are exact duplicates across all columns
duplicate_mask = df.duplicated(keep=False)
duplicates = df.loc[duplicate_mask].copy()

print("Total dataset rows:", len(df))
print("Rows belonging to duplicate groups:", len(duplicates))
print(
    "Extra repeated rows if keeping one copy per group:",
    int(df.duplicated().sum())
)

print("\nFirst 10 duplicate records:")
print(duplicates.head(10).to_string(index=False))

print("\nDuplicate rows grouped by invoice:")
print(
    duplicates.groupby("Invoice").size()
    .sort_values(ascending=False)
    .head(10)
)

# Save a review file; do not delete anything from the main dataset
duplicates.to_csv(output_file, index=False)

print("\nDuplicate review saved to:", output_file)
print("Original enriched dataset remains unchanged.")
