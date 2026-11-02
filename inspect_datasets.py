
import pandas as pd
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

def inspect_csv(file_path):

    print("\n" + "-" * 60)
    print("FILE:", file_path.name)
    print("-" * 60)

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig", low_memory=False)

        print("Total Rows:", len(df))
        print("Total Columns:", len(df.columns))

        print("\nColumn Names:")
        print(list(df.columns))

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:", df.duplicated().sum())

        print("\nFirst 5 Records:")
        print(df.head())

    except Exception as error:
        print("Could not inspect file:", error)


def inspect_excel(file_path):

    print("\n" + "-" * 60)
    print("EXCEL FILE:", file_path.name)
    print("-" * 60)

    try:
        sheets = pd.read_excel(file_path, sheet_name=None)

        for sheet_name, df in sheets.items():

            print("\nSheet:", sheet_name)
            print("Rows:", len(df))
            print("Columns:", len(df.columns))
            print("Column Names:", list(df.columns))
            print("Missing Values:")
            print(df.isnull().sum())
            print("Duplicate Rows:", df.duplicated().sum())
            print("\nFirst 5 Records:")
            print(df.head())

    except Exception as error:
        print("Could not inspect Excel file:", error)


def main():

    print("=" * 60)
    print("SMARTSCHEME AI - DATASET INSPECTION")
    print("=" * 60)

    if not RAW_DIR.exists():
        print("Dataset folder not found!")
        return

    file_count = 0

    for folder in RAW_DIR.iterdir():

        if not folder.is_dir():
            continue

        print("\n\nDATASET CATEGORY:", folder.name.upper())

        for file_path in folder.rglob("*"):

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() == ".csv":
                inspect_csv(file_path)
                file_count += 1

            elif file_path.suffix.lower() in [".xlsx", ".xls"]:
                inspect_excel(file_path)
                file_count += 1

    print("\n" + "=" * 60)
    print("INSPECTION COMPLETED")
    print("Total files inspected:", file_count)
    print("=" * 60)


if __name__ == "__main__":
    main()
