
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "retailpulse_sales_features.csv"
)

OUTPUT_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "retailpulse_rfm_analysis.csv"
)


def main():
    print("Loading sales dataset...")

    df = pd.read_csv(DATA_PATH, parse_dates=["InvoiceDate"])

    print("Dataset shape:", df.shape)

    # Remove rows without customer IDs or dates
    df = df.dropna(subset=["Customer ID", "InvoiceDate"]).copy()

    # One row per customer order for frequency calculation
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df = df.dropna(subset=["InvoiceDate"])

    # Use the latest available transaction date + 1 day as the
    # analysis reference date, avoiding an arbitrary current date.
    reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    print("Reference date:", reference_date.date())

    # Calculate RFM metrics
    rfm = (
        df.groupby("Customer ID")
        .agg(
            Recency=("InvoiceDate", lambda dates:
                     (reference_date - dates.max()).days),
            Frequency=("Invoice", "nunique"),
            Monetary=("Sales", "sum"),
        )
        .reset_index()
    )

    # Five-level scores: higher is better for all three dimensions.
    # Lower recency days means a more recent purchase.
    rfm["R_Score"] = pd.qcut(
        rfm["Recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1],
    ).astype(int)

    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5],
    ).astype(int)

    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(str)
        + rfm["F_Score"].astype(str)
        + rfm["M_Score"].astype(str)
    )

    # Simple, transparent segment rules based on RFM scores.
    def assign_segment(row):
        if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
            return "Champions"
        elif row["R_Score"] >= 3 and row["F_Score"] >= 3:
            return "Loyal Customers"
        elif row["R_Score"] >= 4:
            return "Recent Customers"
        elif row["R_Score"] <= 2 and row["F_Score"] >= 3:
            return "At Risk"
        else:
            return "Needs Attention"

    rfm["RFM_Segment"] = rfm.apply(assign_segment, axis=1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_csv(OUTPUT_PATH, index=False)

    print("\nRFM analysis completed!")
    print("Customers analysed:", len(rfm))
    print("\nSegment counts:")
    print(rfm["RFM_Segment"].value_counts())
    print("\nSaved to:", OUTPUT_PATH)
    print("\nSample records:")
    print(rfm.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
