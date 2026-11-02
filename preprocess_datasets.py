
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

quality_reports = []


# ==========================================
# 2. DATA TYPE CONFIGURATION
# ==========================================

NUMERIC_COLUMNS = {
    "government_schemes": [
        "min_age", "max_age", "max_annual_income",
        "min_age_inferred", "max_age_inferred",
        "income_inferred", "benefit_value_numeric",
        "data_quality_score"
    ],

    "agriculture": [
        "Area", "Production", "Yield"
    ],

    "education": [
        "lat", "lng", "fees_ug_inr",
        "placement_avg_lpa", "rating", "nirf_rank"
    ]
}


# ==========================================
# 3. CLEAN DATA
# ==========================================

def clean_dataframe(df, category, filename):

    original_rows = len(df)

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Remove unnecessary spaces from text columns
    for column in df.select_dtypes(include=["object", "str"]).columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        df[column] = df[column].replace("", pd.NA)

    # Convert configured numeric columns
    for column in NUMERIC_COLUMNS.get(category, []):

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Remove exact duplicate records
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Missing values after cleaning
    missing_count = int(df.isna().sum().sum())

    # Store quality information
    quality_reports.append({
        "Dataset": category,
        "File": filename,
        "Original Rows": original_rows,
        "Cleaned Rows": len(df),
        "Duplicates Removed": duplicate_count,
        "Missing Values": missing_count,
        "Columns": len(df.columns)
    })

    print(f"\nProcessed: {filename}")
    print("Original rows:", original_rows)
    print("Cleaned rows:", len(df))
    print("Duplicates removed:", duplicate_count)
    print("Missing values preserved:", missing_count)

    return df


# ==========================================
# 4. PROCESS ALL DATASETS
# ==========================================

def process_datasets():

    if not RAW_DIR.exists():
        print("Raw dataset folder not found!")
        return

    for category_folder in RAW_DIR.iterdir():

        if not category_folder.is_dir():
            continue

        category = category_folder.name

        output_folder = PROCESSED_DIR / category
        output_folder.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 55)
        print("DATASET:", category.upper())
        print("=" * 55)

        for file_path in category_folder.rglob("*.csv"):

            try:

                df = pd.read_csv(
                    file_path,
                    encoding="utf-8-sig",
                    low_memory=False
                )

                cleaned_df = clean_dataframe(
                    df,
                    category,
                    file_path.name
                )

                output_file = output_folder / file_path.name

                cleaned_df.to_csv(
                    output_file,
                    index=False,
                    encoding="utf-8-sig"
                )

                print("Saved:", output_file)

            except Exception as error:

                print(
                    f"Error processing {file_path.name}: {error}"
                )


# ==========================================
# 5. GENERATE QUALITY REPORT
# ==========================================

def generate_quality_report():

    if not quality_reports:
        print("No quality report generated.")
        return

    report = pd.DataFrame(quality_reports)

    report_path = (
        PROCESSED_DIR / "data_quality_report.csv"
    )

    report.to_csv(
        report_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nQuality report saved:", report_path)


# ==========================================
# 6. MAIN FUNCTION
# ==========================================

def main():

    print("\nSMARTSCHEME AI")
    print("DATA CLEANING AND PREPROCESSING")
    print("=" * 55)

    process_datasets()

    generate_quality_report()

    print("\n" + "=" * 55)
    print("PREPROCESSING COMPLETED!")
    print("=" * 55)


if __name__ == "__main__":
    main()
