
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "government_schemes"
    / "indian_government_schemes.csv"
)

if not FILE_PATH.exists():
    print("Government schemes file not found!")
    print("Check the file inside data/processed/government_schemes/")
    raise SystemExit

df = pd.read_csv(FILE_PATH, low_memory=False)

print("\n========== SMARTSCHEME DATA EXPLORATION ==========")

print("\n1. DATASET SHAPE")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n2. VERIFICATION STATUS")
if "eligibility_verified" in df.columns:
    print(df["eligibility_verified"].value_counts(dropna=False))

print("\n3. DATA QUALITY SCORE")
if "data_quality_score" in df.columns:
    print(df["data_quality_score"].describe())

important_columns = [
    "scheme_category_clean",
    "allowed_occupations",
    "allowed_social_categories",
    "state_restricted_to_normalized",
    "gender_restricted_to"
]

print("\n4. ELIGIBILITY FIELD VALUES")

for column in important_columns:
    if column in df.columns:
        print(f"\n--- {column} ---")
        print(df[column].value_counts(dropna=False).head(10))

print("\n5. SAMPLE GOVERNMENT SCHEMES")

sample_columns = [
    "scheme_name",
    "issuing_authority",
    "eligibility_text_clean",
    "official_source_url",
    "last_verified_date",
    "eligibility_verified"
]

available_columns = [
    column for column in sample_columns
    if column in df.columns
]

print(df[available_columns].head(5).to_string(index=False))

print("\n6. MISSING ELIGIBILITY INFORMATION")

eligibility_columns = [
    "min_age",
    "max_age",
    "max_annual_income",
    "allowed_occupations",
    "allowed_social_categories",
    "state_restricted_to_normalized",
    "gender_restricted_to"
]

for column in eligibility_columns:
    if column in df.columns:
        missing = df[column].isna().sum()
        print(f"{column}: {missing} missing values")

print("\n========== EXPLORATION COMPLETED ==========")
