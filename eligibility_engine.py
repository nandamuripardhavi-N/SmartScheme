
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "government_schemes"
    / "indian_government_schemes.csv"
)


def split_values(value):
    """Convert semicolon-separated values into a list."""
    if pd.isna(value):
        return None

    values = [
        item.strip().lower()
        for item in str(value).split(";")
        if item.strip()
    ]

    return values if values else None


def check_scheme(scheme, profile):
    reasons = []
    unknown = []
    rejected = False

    # State check
    scheme_state = str(
        scheme["state_restricted_to_normalized"]
    ).strip().lower()

    user_state = profile["state"].strip().lower()

    if scheme_state not in ["all india", user_state]:
        rejected = True
        reasons.append("State does not match")
    elif scheme_state == "all india":
        reasons.append("Available across India")

    # Gender check
    allowed_gender = str(
        scheme["gender_restricted_to"]
    ).strip().lower()

    user_gender = profile["gender"].strip().lower()

    if allowed_gender not in ["any", user_gender]:
        rejected = True
        reasons.append("Gender does not match")

    # Age check
    min_age = scheme["min_age"]
    max_age = scheme["max_age"]

    if pd.notna(min_age):
        if profile["age"] < min_age:
            rejected = True
            reasons.append("Below minimum age")

    if pd.notna(max_age):
        if profile["age"] > max_age:
            rejected = True
            reasons.append("Above maximum age")

    if pd.isna(min_age) or pd.isna(max_age):
        unknown.append("Age conditions need verification")

    # Annual income check
    max_income = scheme["max_annual_income"]

    if pd.notna(max_income):
        if profile["annual_income"] > max_income:
            rejected = True
            reasons.append("Income exceeds the stated limit")
    else:
        unknown.append("Income limit needs verification")

    # Occupation check
    occupations = split_values(scheme["allowed_occupations"])

    if occupations is not None:
        if profile["occupation"].strip().lower() not in occupations:
            rejected = True
            reasons.append("Occupation does not match")
    else:
        unknown.append("Occupation conditions need verification")

    # Social category check
    categories = split_values(
        scheme["allowed_social_categories"]
    )

    if categories is not None:
        if profile["social_category"].strip().lower() not in categories:
            rejected = True
            reasons.append("Social category does not match")
    else:
        unknown.append("Social category conditions need verification")

    if rejected:
        status = "Not a match"
    elif unknown:
        status = "Potential match - verification required"
    else:
        status = "Potential match - conditions matched"

    return status, reasons, unknown


def main():
    if not DATA_FILE.exists():
        print("Government schemes dataset not found!")
        return

    df = pd.read_csv(DATA_FILE, low_memory=False)

    # Only records marked as verified are considered
    verified = df[
        df["eligibility_verified"].astype(str).str.lower()
        == "true"
    ].copy()

    print("Total schemes:", len(df))
    print("Verified schemes considered:", len(verified))

    # Fictional sample profile for testing only
    profile = {
        "age": 22,
        "annual_income": 300000,
        "state": "Andhra Pradesh",
        "occupation": "student",
        "social_category": "general",
        "gender": "female"
    }

    print("\nSample profile:")
    print(profile)

    results = []

    for _, scheme in verified.iterrows():
        status, reasons, unknown = check_scheme(
            scheme, profile
        )

        results.append({
            "scheme_name": scheme["scheme_name"],
            "status": status,
            "reasons": "; ".join(reasons),
            "unknown_conditions": "; ".join(unknown),
            "official_source": scheme["official_source_url"]
        })

    result_df = pd.DataFrame(results)

    output_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "eligibility_test_results.csv"
    )

    result_df.to_csv(output_file, index=False)

    print("\n========== MATCHING RESULTS ==========")
    print(result_df[
        ["scheme_name", "status", "reasons"]
    ].to_string(index=False))

    print("\nStatus summary:")
    print(result_df["status"].value_counts())

    print("\nResults saved to:", output_file)


if __name__ == "__main__":
    main()
