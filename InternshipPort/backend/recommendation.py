import pandas as pd

from sklearn.feature_extraction.text import (
    TfidfVectorizer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

def recommend_internships(
    user_skills,
    internships_df
):

    internships_df["combined"] = (
        internships_df["skills"]
    )

    documents = internships_df[
        "combined"
    ].tolist()

    documents.append(user_skills)

    tfidf = TfidfVectorizer()

    matrix = tfidf.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        matrix[-1],
        matrix[:-1]
    )

    internships_df["match_score"] = (
        similarity.flatten() * 100
    )

    recommendations = (
        internships_df.sort_values(
            by="match_score",
            ascending=False
        )
    )

    return recommendations.head(5)