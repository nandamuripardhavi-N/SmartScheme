
import pandas as pd
from pathlib import Path
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR / "data" / "processed"
    / "government_schemes"
    / "indian_government_schemes.csv"
)

CATEGORIES = [
    "education", "agriculture", "health", "housing",
    "employment", "pension", "disability",
    "women_and_child", "financial_inclusion", "other"
]


def normalize_interest(value):
    value = value.strip().lower().replace(" ", "_")

    aliases = {
        "women": "women_and_child",
        "child": "women_and_child",
        "finance": "financial_inclusion"
    }

    if value in aliases:
        return aliases[value]

    match = get_close_matches(
        value, CATEGORIES, n=1, cutoff=0.65
    )

    return match[0] if match else value

    
def normalize_category(value):
    value = value.strip().lower()

    aliases = {
        "gen": "general",
        "general": "general",
        "sc": "sc",
        "st": "st",
        "obc": "obc",
        "ews": "ews"
    }

    return aliases.get(value, value)


def normalize_occupation(value):
    value = value.strip().lower()

    aliases = {
        "student": "student",
        "farmer": "farmer",
        "daily wage": "daily_wage",
        "daily_wage": "daily_wage",
        "self employed": "self_employed",
        "self_employed": "self_employed",
        "unemployed": "unemployed",
        "salaried": "salaried"
    }

    return aliases.get(value, value)


def load_data():
    df = pd.read_csv(DATA_FILE, low_memory=False)

    text_columns = [
        "scheme_name",
        "scheme_category_clean",
        "issuing_authority",
        "benefit_summary",
        "eligibility_text_clean",
        "allowed_occupations",
        "allowed_social_categories"
    ]

    for col in text_columns:
        df[col] = df[col].fillna("").astype(str)

    df["scheme_description"] = df[text_columns].agg(
        " ".join, axis=1
    )

    return df


def split_values(value):
    if pd.isna(value) or not str(value).strip():
        return None

    return [
        x.strip().lower()
        for x in str(value).split(";")
        if x.strip()
    ]


def screen_scheme(scheme, profile):
    conflicts = []
    unknown = []

    # State
    scheme_state = str(
        scheme["state_restricted_to_normalized"]
    ).strip().lower()

    if scheme_state not in ["all india", profile["state"]]:
        conflicts.append("State restriction may not match")

    # Gender
    allowed_gender = str(
        scheme["gender_restricted_to"]
    ).strip().lower()

    if allowed_gender not in ["any", profile["gender"]]:
        conflicts.append("Gender restriction may not match")

    # Age
    if pd.notna(scheme["min_age"]):
        if profile["age"] < scheme["min_age"]:
            conflicts.append("Below recorded minimum age")
    else:
        unknown.append("Minimum age not recorded")

    if pd.notna(scheme["max_age"]):
        if profile["age"] > scheme["max_age"]:
            conflicts.append("Above recorded maximum age")
    else:
        unknown.append("Maximum age not recorded")

    # Income
    if pd.notna(scheme["max_annual_income"]):
        if profile["income"] > scheme["max_annual_income"]:
            conflicts.append("Above recorded income limit")
    else:
        unknown.append("Income limit not recorded")

    # Occupation
    occupations = split_values(scheme["allowed_occupations"])

    if occupations is None:
        unknown.append("Occupation conditions not recorded")
    elif profile["occupation"] not in occupations:
        conflicts.append("Occupation not in recorded allowed list")

    # Social category
    categories = split_values(
        scheme["allowed_social_categories"]
    )

    if categories is None:
        unknown.append("Social category conditions not recorded")
    elif profile["category"] not in categories:
        conflicts.append("Social category not in recorded allowed list")

    if conflicts:
        status = "Possible conflict - verify official rules"
    elif unknown:
        status = "Potential match - more information needed"
    else:
        status = "No recorded conflict - verify official rules"

    return status, conflicts, unknown


def main():
    print("\n========== SMARTSCHEME AI ==========")

    df = load_data()

    age = int(input("Age: "))
    income = float(input("Annual income in INR: "))
    state = input("State: ").strip().lower()
    occupation = input("Occupation: ").strip().lower()
    category = input("Social category: ").strip().lower()
    gender = input("Gender: ").strip().lower()
    interest = normalize_interest(
        input("Scheme interest: ")
    )

    profile = {
        "age": age,
        "income": income,
        "state": state,
        "occupation": occupation,
        "category": category,
        "gender": gender
    }

    print("\nSelected category:", interest)

    candidates = df[
        df["scheme_category_clean"].str.lower() == interest
    ].copy()

    if candidates.empty:
        print("No schemes found in this category.")
        return

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000
    )

    scheme_vectors = vectorizer.fit_transform(
        candidates["scheme_description"]
    )

    profile_text = (
        f"{occupation} {category} {state} "
        f"{interest.replace('_', ' ')} "
        "government scheme support benefits"
    )

    profile_vector = vectorizer.transform([profile_text])

    candidates["similarity_score"] = cosine_similarity(
        profile_vector, scheme_vectors
    ).flatten()

    candidates = candidates[
        candidates["similarity_score"] > 0
    ].copy()

    if candidates.empty:
        print("No textually relevant schemes found.")
        return

    screening_results = candidates.apply(
        lambda row: screen_scheme(row, profile),
        axis=1
    )

    candidates["screening_status"] = [
        result[0] for result in screening_results
    ]

    candidates["possible_conflicts"] = [
        "; ".join(result[1]) for result in screening_results
    ]

    candidates["unknown_conditions"] = [
        "; ".join(result[2]) for result in screening_results
    ]

    candidates["dataset_verification_flag"] = candidates[
        "eligibility_verified"
    ].apply(
        lambda value: (
            "Marked verified in dataset"
            if str(value).lower() == "true"
            else "Not verified in dataset"
        )
    )

    candidates = candidates.sort_values(
        "similarity_score", ascending=False
    ).head(10)

    output_columns = [
        "scheme_name",
        "similarity_score",
        "screening_status",
        "possible_conflicts",
        "unknown_conditions",
        "dataset_verification_flag",
        "official_source_url"
    ]

    print("\n========== SMARTSCHEME RESULTS ==========")
    print(candidates[output_columns].to_string(index=False))

    print(
        "\nIMPORTANT: These are preliminary screening results, "
        "not official eligibility decisions."
    )


if __name__ == "__main__":
    main()
