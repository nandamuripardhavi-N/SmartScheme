
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

df = pd.read_csv(FILE_PATH, low_memory=False)

verified = df[
    df["eligibility_verified"].astype(str).str.lower()
    == "true"
].copy()

columns = [
    "scheme_name",
    "min_age",
    "max_age",
    "max_annual_income",
    "allowed_occupations",
    "allowed_social_categories",
    "state_restricted_to_normalized",
    "gender_restricted_to",
    "eligibility_text_clean",
    "official_source_url",
    "last_verified_date"
]

columns = [col for col in columns if col in verified.columns]

print("\n========== VERIFIED SCHEME AUDIT ==========")
print("Total verified schemes:", len(verified))

for _, row in verified[columns].iterrows():
    print("\n----------------------------------------")

    for column in columns:
        print(f"{column}: {row[column]}")

print("\n========== AUDIT COMPLETED ==========")
