
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "government_schemes"
    / "indian_government_schemes.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml_recommendations.csv"
)


def load_schemes():
    if not DATA_FILE.exists():
        raise FileNotFoundError("Government schemes dataset not found!")

    df = pd.read_csv(DATA_FILE, low_memory=False)

    # Use descriptive fields, not inferred eligibility fields.
    text_columns = [
        "scheme_name",
        "scheme_category_clean",
        "issuing_authority",
        "benefit_summary",
        "eligibility_text_clean",
        "allowed_occupations",
        "allowed_social_categories"
    ]

    for column in text_columns:
        if column not in df.columns:
            df[column] = ""

        df[column] = df[column].fillna("").astype(str)

    df["scheme_description"] = (
        df[text_columns].agg(" ".join, axis=1)
    )

    return df


def get_user_profile():
    print("\n========== SMARTSCHEME PROFILE ==========")

    age = input("Enter age: ").strip()
    occupation = input("Enter occupation (student/farmer/etc.): ").strip()
    state = input("Enter state: ").strip()
    category = input("Enter social category (SC/ST/OBC/EWS/General): ").strip()
    gender = input("Enter gender: ").strip()
    interest = input(
        "What kind of government support do you need? "
        "(education/agriculture/health/housing/employment): "
    ).strip()

    profile_text = (
        f"Age {age}. "
        f"Occupation {occupation}. "
        f"State {state}. "
        f"Social category {category}. "
        f"Gender {gender}. "
        f"Interested in {interest} schemes."
    )

    return profile_text


def recommend_schemes(df, profile_text, top_n=10):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000
    )

    scheme_vectors = vectorizer.fit_transform(
        df["scheme_description"]
    )

    profile_vector = vectorizer.transform([profile_text])

    similarity_scores = cosine_similarity(
        profile_vector,
        scheme_vectors
    ).flatten()

    results = df.copy()
    results["similarity_score"] = similarity_scores

    results = results.sort_values(
        by="similarity_score",
        ascending=False
    )

    results = results[
        results["similarity_score"] > 0
    ].head(top_n).copy()

    results["verification_status"] = results[
        "eligibility_verified"
    ].apply(
        lambda value: (
            "Dataset marked verified - check official rules"
            if str(value).lower() == "true"
            else "Unverified - official verification required"
        )
    )

    return results


def main():
    print("\n========== SMARTSCHEME ML RECOMMENDER ==========")

    df = load_schemes()

    print("Total schemes loaded:", len(df))

    profile_text = get_user_profile()

    recommendations = recommend_schemes(
        df,
        profile_text,
        top_n=10
    )

    if recommendations.empty:
        print("\nNo relevant schemes found.")
        return

    display_columns = [
        "scheme_name",
        "scheme_category_clean",
        "similarity_score",
        "verification_status",
        "official_source_url"
    ]

    display_columns = [
        col for col in display_columns
        if col in recommendations.columns
    ]

    print("\n========== TOP RECOMMENDATIONS ==========")

    print(
        recommendations[display_columns].to_string(index=False)
    )


    print("\nRecommendations saved to:")
    print(OUTPUT_FILE)

    print(
        "\nNote: Similarity scores measure text relevance, "
        "not eligibility."
    )


if __name__ == "__main__":
    main()
