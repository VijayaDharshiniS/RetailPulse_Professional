
from pathlib import Path
import pandas as pd

# Locate the original Excel dataset
file_path = Path("data/raw/online_retail_II.xlsx")

if not file_path.exists():
    print("ERROR: Dataset file not found!")
    print("Check the filename and location: data/raw/")
else:
    print("Dataset found successfully!")

    # Read all sheets without changing the original file
    sheets = pd.read_excel(file_path, sheet_name=None)

    print("\nSHEETS IN THE DATASET")

    for sheet_name, df in sheets.items():
        print("\n" + "=" * 50)
        print("Sheet:", sheet_name)
        print("Rows and columns:", df.shape)

        print("\nOriginal column names:")
        print(df.columns.tolist())

        print("\nMissing values in each column:")
        print(df.isnull().sum())

        print("\nFirst 5 rows:")
        print(df.head())
