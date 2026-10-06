import pandas as pd
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse.linalg import svds
from sentence_transformers import SentenceTransformer


# ============================================================
# SKILL STANDARDIZATION
# ============================================================

ONTOLOGY_EXPANSIONS = {
    "ML": "Machine Learning",
    "AI": "Artificial Intelligence",
    "MRKT": "Marketing",
    "SALE": "Sales",
    "ENG": "Engineering",
    "IT": "Information Technology",
    "HCPR": "Healthcare",
    "ACCT": "Accounting",
    "FIN": "Finance",
    "MGMT": "Management",
    "DSGN": "Design",
    "ART": "Art",
    "PRJM": "Project Management",
    "BD": "Business Development",
    "LGL": "Legal",
    "EDU": "Education",
    "TRNG": "Training",
    "ADM": "Administrative",
    "HR": "Human Resources",
    "CUST": "Customer Support"
}


def standardize_skills_text(skills_str):

    if not skills_str or pd.isna(skills_str):
        return ""

    cleaned_str = (
        str(skills_str)
        .replace("/", ",")
        .replace(";", ",")
    )

    tokens = []

    for token in cleaned_str.split(","):

        token = token.strip().lower()

        if not token:
            continue

        token_upper = token.upper()

        if token_upper in ONTOLOGY_EXPANSIONS:

            tokens.append(
                ONTOLOGY_EXPANSIONS[token_upper]
            )

        else:

            words = token.split()
            expanded_words = []

            for word in words:

                word_upper = word.upper()

                if word_upper in ONTOLOGY_EXPANSIONS:
                    expanded_words.append(
                        ONTOLOGY_EXPANSIONS[word_upper]
                    )
                else:
                    expanded_words.append(word)

            tokens.append(
                " ".join(expanded_words)
            )

    return ", ".join(tokens)


# ============================================================
# SBERT MODEL
# ============================================================

_sbert_model = None


def get_sbert_model():

    global _sbert_model

    if _sbert_model is None:

        _sbert_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _sbert_model


# ============================================================
# MMR DIVERSITY
# ============================================================

def select_top_k_mmr(
    scores_dict,
    similarity_matrix,
    item_index_map,
    K=10,
    lmbda=0.70
):

    if not scores_dict:
        return []

    if len(scores_dict) <= K:
        return list(
            sorted(
                scores_dict,
                key=scores_dict.get,
                reverse=True
            )
        )

    selected = []

    candidates = list(
        scores_dict.keys()
    )

    max_score = max(
        scores_dict.values()
    )

    min_score = min(
        scores_dict.values()
    )

    score_range = (
        max_score - min_score
    )

    if score_range == 0:
        score_range = 1.0

    # --------------------------------------------------------
    # Select highest relevance item first
    # --------------------------------------------------------

    first_item = max(
        scores_dict,
        key=scores_dict.get
    )

    selected.append(first_item)
    candidates.remove(first_item)

    # --------------------------------------------------------
    # MMR selection
    # --------------------------------------------------------

    while (
        len(selected) < K
        and candidates
    ):

        best_candidate = None
        best_mmr = -float("inf")

        for candidate in candidates:

            relevance = (
                scores_dict[candidate]
                - min_score
            ) / score_range

            max_similarity = 0.0

            if candidate in item_index_map:

                candidate_idx = (
                    item_index_map[candidate]
                )

                for selected_item in selected:

                    if selected_item not in item_index_map:
                        continue

                    selected_idx = (
                        item_index_map[selected_item]
                    )

                    similarity = similarity_matrix[
                        candidate_idx,
                        selected_idx
                    ]

                    max_similarity = max(
                        max_similarity,
                        similarity
                    )

            # ------------------------------------------------
            # MMR formula
            # ------------------------------------------------

            mmr_score = (
                lmbda * relevance
                -
                (1.0 - lmbda)
                * max_similarity
            )

            if mmr_score > best_mmr:

                best_mmr = mmr_score
                best_candidate = candidate

        if best_candidate is None:
            break

        selected.append(
            best_candidate
        )

        candidates.remove(
            best_candidate
        )

    return selected


# ============================================================
# FETCH USER PROFILE
# ============================================================

def get_user_profile(
    user_id,
    cursor
):

    cursor.execute(
        """
        SELECT
            skills
        FROM users
        WHERE user_id = %s
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if not row:
        return ""

    return row[0] or ""


# ============================================================
# SBERT CONTENT-BASED RECOMMENDATION
# ============================================================

def get_content_based_ratings(
    user_id,
    job_ids,
    cursor,
    desired_role="",
    score_components=None
):

    if not job_ids:
        return {}

    # --------------------------------------------------------
    # Get user skills
    # --------------------------------------------------------

    user_skills = get_user_profile(
        user_id,
        cursor
    )

    if not user_skills:

        return {
            job_id: 1.0
            for job_id in job_ids
        }

    # --------------------------------------------------------
    # Fetch complete job information
    #
    # IMPORTANT:
    # Previously you were only fetching required_skills.
    # Now we use:
    # role + skills + description
    # --------------------------------------------------------

    placeholders = ", ".join(
        ["%s"] * len(job_ids)
    )

    query = f"""
        SELECT
            job_id,
            role,
            required_skills,
            description
        FROM jobs
        WHERE job_id IN ({placeholders})
    """

    cursor.execute(
        query,
        tuple(job_ids)
    )

    jobs = cursor.fetchall()

    if not jobs:
        return {
            job_id: 1.0
            for job_id in job_ids
        }

    jobs_df = pd.DataFrame(
        jobs,
        columns=[
            "job_id",
            "role",
            "required_skills",
            "description"
        ]
    )

    # --------------------------------------------------------
    # Clean data
    # --------------------------------------------------------

    jobs_df["role"] = (
        jobs_df["role"]
        .fillna("")
        .astype(str)
    )

    jobs_df["required_skills"] = (
        jobs_df["required_skills"]
        .fillna("")
        .astype(str)
    )

    jobs_df["description"] = (
        jobs_df["description"]
        .fillna("")
        .astype(str)
    )

    # --------------------------------------------------------
    # Build job text
    #
    # ROLE is repeated deliberately so that role relevance
    # has stronger semantic influence.
    # --------------------------------------------------------

    jobs_df["job_text"] = (
        "Role: "
        + jobs_df["role"]
        + ". Role: "
        + jobs_df["role"]
        + ". Required skills: "
        + jobs_df["required_skills"]
        + ". Description: "
        + jobs_df["description"]
    )

    # --------------------------------------------------------
    # Build user profile
    # --------------------------------------------------------

    user_text = (
        "Candidate skills: "
        + standardize_skills_text(
            user_skills
        )
    )

    # --------------------------------------------------------
    # SBERT embeddings
    # --------------------------------------------------------

    model = get_sbert_model()

    user_embedding = model.encode(
        [user_text],
        normalize_embeddings=True
    )

    job_embeddings = model.encode(
        jobs_df["job_text"].tolist(),
        normalize_embeddings=True
    )

    # --------------------------------------------------------
    # Overall semantic similarity
    # --------------------------------------------------------

    semantic_similarity = cosine_similarity(
        user_embedding,
        job_embeddings
    ).flatten()

    # --------------------------------------------------------
    # Additional ROLE similarity
    #
    # This makes recommendations more role-specific.
    # --------------------------------------------------------

    user_role_text = desired_role.strip() or user_skills

    role_documents = (
        jobs_df["role"].tolist()
    )

    role_embeddings = model.encode(
        role_documents,
        normalize_embeddings=True
    )

    # Since the database currently stores skills rather than
    # a separate desired_role field, use the semantic profile
    # against the job roles as a supporting signal.
    user_role_embedding = model.encode(
        [user_role_text],
        normalize_embeddings=True
    )

    role_similarity = cosine_similarity(
        user_role_embedding,
        role_embeddings
    ).flatten()

    description_embeddings = model.encode(
        jobs_df["description"].tolist(),
        normalize_embeddings=True
    )

    description_similarity = cosine_similarity(
        user_embedding,
        description_embeddings
    ).flatten()

    # --------------------------------------------------------
    # Skill-specific similarity
    # --------------------------------------------------------

    skill_documents = [
        standardize_skills_text(
            skills
        )
        for skills in jobs_df[
            "required_skills"
        ]
    ]

    skill_embeddings = model.encode(
        skill_documents,
        normalize_embeddings=True
    )

    user_skill_embedding = model.encode(
        [
            standardize_skills_text(
                user_skills
            )
        ],
        normalize_embeddings=True
    )

    skill_similarity = cosine_similarity(
        user_skill_embedding,
        skill_embeddings
    ).flatten()

    # --------------------------------------------------------
    # FINAL CONTENT SCORE
    #
    # 45% overall semantic
    # 35% skills
    # 20% role
    # --------------------------------------------------------

    if desired_role.strip():
        final_similarity = (
            0.40 * role_similarity
            +
            0.35 * skill_similarity
            +
            0.15 * description_similarity
        )
    else:
        final_similarity = (
            0.45 * semantic_similarity
            +
            0.35 * skill_similarity
            +
            0.20 * role_similarity
        )

    # --------------------------------------------------------
    # Category overlap bonus
    # --------------------------------------------------------

    user_skill_set = set(
        standardize_skills_text(
            user_skills
        ).lower().split(",")
    )

    overlap_bonus = []

    for _, row in jobs_df.iterrows():

        job_skill_set = set(
            standardize_skills_text(
                row["required_skills"]
            ).lower().split(",")
        )

        user_skill_set_clean = {
            skill.strip()
            for skill in user_skill_set
            if skill.strip()
        }

        job_skill_set_clean = {
            skill.strip()
            for skill in job_skill_set
            if skill.strip()
        }

        overlap = len(
            user_skill_set_clean
            &
            job_skill_set_clean
        )

        if overlap >= 3:
            bonus = 1.10

        elif overlap == 2:
            bonus = 1.05

        elif overlap == 1:
            bonus = 1.02

        else:
            bonus = 0.95

        overlap_bonus.append(
            bonus
        )

    final_similarity = (
        final_similarity
        * np.array(overlap_bonus)
    )

    if score_components is not None:
        for index, job_id in enumerate(jobs_df["job_id"]):
            score_components[job_id] = {
                "role": float(role_similarity[index]),
                "skill": float(skill_similarity[index]),
                "content": float(description_similarity[index]),
            }

    return dict(
        zip(
            jobs_df["job_id"],
            final_similarity
        )
    )


# ============================================================
# HYBRID RECOMMENDATION
# ============================================================

def get_hybrid_recommendations(
    user_id,
    cursor,
    top_n=10,
    alpha=0.5,
    desired_role=""
):

    # --------------------------------------------------------
    # IMPORTANT:
    # Removed LIMIT 200.
    #
    # Previously the recommender only considered 200 jobs.
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            job_id,
            role,
            required_skills,
            description
        FROM jobs
        WHERE required_skills IS NOT NULL
        """
    )

    candidate_jobs_raw = cursor.fetchall()

    if not candidate_jobs_raw:
        return []

    candidate_jobs = [
        row[0]
        for row in candidate_jobs_raw
    ]

    candidate_job_data = {
        row[0]: {
            "role": row[1] or "",
            "required_skills": row[2] or "",
            "description": row[3] or ""
        }
        for row in candidate_jobs_raw
    }

    # --------------------------------------------------------
    # Get interactions
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            user_id,
            job_id,
            rating
        FROM user_interactions
        """
    )

    interactions = cursor.fetchall()

    # --------------------------------------------------------
    # Cold start
    # --------------------------------------------------------

    if not interactions:

        return get_fallback_recommendations(
            user_id,
            cursor,
            top_n,
            desired_role
        )

    df = pd.DataFrame(
        interactions,
        columns=[
            "user_id",
            "job_id",
            "rating"
        ]
    )

    if user_id not in df[
        "user_id"
    ].values:

        return get_fallback_recommendations(
            user_id,
            cursor,
            top_n,
            desired_role
        )

    # --------------------------------------------------------
    # Create user-job matrix
    # --------------------------------------------------------

    pivot_matrix = (
        df
        .pivot_table(
            index="user_id",
            columns="job_id",
            values="rating"
        )
        .fillna(0)
    )

    if user_id not in pivot_matrix.index:

        return get_fallback_recommendations(
            user_id,
            cursor,
            top_n,
            desired_role
        )

    # --------------------------------------------------------
    # Collaborative filtering
    # --------------------------------------------------------

    R = pivot_matrix.values

    user_ratings_mean = np.mean(
        R,
        axis=1
    )

    R_demeaned = (
        R
        -
        user_ratings_mean.reshape(
            -1,
            1
        )
    )

    k = min(
        15,
        min(
            R_demeaned.shape
        ) - 1
    )

    if k >= 1:

        U, sigma, Vt = svds(
            R_demeaned,
            k=k
        )

        sigma = np.diag(
            sigma
        )

        all_predicted_ratings = (
            np.dot(
                np.dot(
                    U,
                    sigma
                ),
                Vt
            )
            +
            user_ratings_mean.reshape(
                -1,
                1
            )
        )

        predictions_df = pd.DataFrame(
            all_predicted_ratings,
            columns=pivot_matrix.columns,
            index=pivot_matrix.index
        )

    else:

        predictions_df = (
            pivot_matrix.copy()
        )

    # --------------------------------------------------------
    # Find jobs user hasn't rated
    # --------------------------------------------------------

    user_ratings = (
        pivot_matrix.loc[user_id]
    )

    rated_items = (
        user_ratings[
            user_ratings > 0
        ]
        .index
        .tolist()
    )

    unrated_items = [
        job_id
        for job_id in candidate_jobs
        if job_id not in rated_items
    ]

    if not unrated_items:

        return get_popular_recommendations(
            cursor,
            top_n
        )

    # --------------------------------------------------------
    # Collaborative filtering scores
    # --------------------------------------------------------

    cf_scores = {}

    for job_id in unrated_items:

        if job_id in predictions_df.columns:

            cf_scores[job_id] = (
                predictions_df.loc[
                    user_id,
                    job_id
                ]
            )

        else:

            cf_scores[job_id] = 0.0

    # --------------------------------------------------------
    # SBERT content scores
    # --------------------------------------------------------

    content_components = {}
    content_scores = (
        get_content_based_ratings(
            user_id,
            unrated_items,
            cursor,
            desired_role,
            content_components
        )
    )

    # --------------------------------------------------------
    # Normalize CF scores
    # --------------------------------------------------------

    keys = list(
        cf_scores.keys()
    )

    cf_array = np.array(
        [
            cf_scores[key]
            for key in keys
        ]
    ).reshape(
        -1,
        1
    )

    content_array = np.array(
        [
            content_scores.get(
                key,
                0.0
            )
            for key in keys
        ]
    ).reshape(
        -1,
        1
    )

    scaler_cf = MinMaxScaler()

    scaler_content = MinMaxScaler()

    if (
        len(keys) > 1
        and np.max(cf_array)
        > np.min(cf_array)
    ):

        norm_cf = (
            scaler_cf
            .fit_transform(
                cf_array
            )
            .flatten()
        )

    else:

        norm_cf = (
            cf_array.flatten()
            / 5.0
        )

    if (
        len(keys) > 1
        and np.max(content_array)
        > np.min(content_array)
    ):

        norm_content = (
            scaler_content
            .fit_transform(
                content_array
            )
            .flatten()
        )

    else:

        norm_content = (
            content_array.flatten()
        )

    # --------------------------------------------------------
    # HYBRID SCORE
    # --------------------------------------------------------

    hybrid_scores = {}

    if desired_role.strip():
        role_values = np.array([
            content_components[key]["role"] for key in keys
        ]).reshape(-1, 1)
        skill_values = np.array([
            content_components[key]["skill"] for key in keys
        ]).reshape(-1, 1)
        description_values = np.array([
            content_components[key]["content"] for key in keys
        ]).reshape(-1, 1)

        def normalize(values):
            if len(keys) > 1 and np.max(values) > np.min(values):
                return MinMaxScaler().fit_transform(values).flatten()
            return values.flatten()

        norm_role = normalize(role_values)
        norm_skill = normalize(skill_values)
        norm_description = normalize(description_values)

        for idx, job_id in enumerate(keys):
            hybrid_scores[job_id] = (
                0.40 * norm_role[idx]
                + 0.35 * norm_skill[idx]
                + 0.15 * norm_description[idx]
                + 0.10 * norm_cf[idx]
            )
    else:
        for idx, job_id in enumerate(keys):
            cf_value = norm_cf[idx]
            content_value = norm_content[idx]
            hybrid_scores[job_id] = (
                alpha * cf_value + (1.0 - alpha) * content_value
                if cf_scores[job_id] > 0
                else content_value
            )

    top_before_mmr = sorted(
        hybrid_scores,
        key=hybrid_scores.get,
        reverse=True
    )[:top_n]
    print(
        "[RECOMMENDATION DEBUG]",
        {"user_id": user_id, "desired_role": desired_role,
         "candidate_jobs": len(unrated_items),
         "top_roles_before_mmr": [candidate_job_data[job_id]["role"] for job_id in top_before_mmr]}
    )

    # --------------------------------------------------------
    # JOB EMBEDDINGS FOR DIVERSITY
    # --------------------------------------------------------

    model = get_sbert_model()

    job_texts = []

    for job_id in unrated_items:

        job = candidate_job_data[
            job_id
        ]

        job_text = (
            "Role: "
            + str(job["role"])
            + ". Required skills: "
            + str(job["required_skills"])
            + ". Description: "
            + str(job["description"])
        )

        job_texts.append(
            job_text
        )

    job_embeddings = model.encode(
        job_texts,
        normalize_embeddings=True
    )

    job_job_similarity = cosine_similarity(
        job_embeddings
    )

    job_index_map = {
        job_id: idx
        for idx, job_id in enumerate(
            unrated_items
        )
    }

    # --------------------------------------------------------
    # MMR
    #
    # lambda = 0.70 means:
    # more relevance, but still some diversity.
    # --------------------------------------------------------

    top_items = select_top_k_mmr(
        hybrid_scores,
        job_job_similarity,
        job_index_map,
        K=min(
            top_n,
            len(unrated_items)
        ),
        lmbda=0.70
    )

    print(
        "[RECOMMENDATION DEBUG]",
        {"user_id": user_id,
         "top_roles_after_mmr": [candidate_job_data[job_id]["role"] for job_id in top_items],
         "scores": [{"role": content_components.get(job_id, {}).get("role"),
                     "skill_content": content_components.get(job_id, {}).get("skill"),
                     "collaborative": cf_scores.get(job_id),
                     "final": hybrid_scores.get(job_id)} for job_id in top_items]}
    )

    if not top_items:

        return get_fallback_recommendations(
            user_id,
            cursor,
            top_n,
            desired_role
        )

    # --------------------------------------------------------
    # Fetch final job details
    # --------------------------------------------------------

    placeholders = ", ".join(
        ["%s"] * len(top_items)
    )

    query = f"""
        SELECT
            job_id,
            company_name,
            role,
            required_skills,
            location,
            salary,
            description
        FROM jobs
        WHERE job_id IN ({placeholders})
    """

    cursor.execute(
        query,
        tuple(top_items)
    )

    jobs = cursor.fetchall()

    jobs_df = pd.DataFrame(
        jobs,
        columns=[
            "job_id",
            "company_name",
            "role",
            "required_skills",
            "location",
            "salary",
            "description"
        ]
    )

    # --------------------------------------------------------
    # Match percentage
    # --------------------------------------------------------

    score_dict = {
        job_id: hybrid_scores[
            job_id
        ]
        for job_id in top_items
    }

    jobs_df["match_percentage"] = jobs_df["job_id"].map(
        lambda job_id: min(98.0, max(30.0, round((score_dict.get(job_id, 0.0) * 240.0) + 15.0, 2)))
        if score_dict.get(job_id, 0.0) > 0 else 0.0
    )

    # --------------------------------------------------------
    # Preserve recommendation order
    # --------------------------------------------------------

    jobs_df["rank"] = (
        jobs_df["job_id"]
        .map(
            lambda job_id:
                top_items.index(
                    job_id
                )
        )
    )

    jobs_df = (
        jobs_df
        .sort_values(
            by="rank"
        )
        .drop(
            columns=["rank"]
        )
    )

    return jobs_df.to_dict(
        orient="records"
    )


# ============================================================
# COLLABORATIVE RECOMMENDATIONS
# ============================================================

def get_collaborative_recommendations(
    user_id,
    cursor,
    top_n=10,
    alpha=0.5,
    desired_role=""
):

    return get_hybrid_recommendations(
        user_id,
        cursor,
        top_n,
        alpha=alpha,
        desired_role=desired_role
    )


# ============================================================
# FALLBACK CONTENT-BASED RECOMMENDATIONS
# ============================================================

def get_fallback_recommendations(
    user_id,
    cursor,
    top_n=10,
    desired_role=""
):

    # --------------------------------------------------------
    # Get user skills
    # --------------------------------------------------------

    user_skills = get_user_profile(
        user_id,
        cursor
    )

    if not user_skills:

        return get_popular_recommendations(
            cursor,
            top_n
        )

    # --------------------------------------------------------
    # IMPORTANT:
    # Removed LIMIT 200.
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            job_id,
            company_name,
            role,
            required_skills,
            location,
            salary,
            description
        FROM jobs
        WHERE required_skills IS NOT NULL
        """
    )

    jobs = cursor.fetchall()

    if not jobs:
        return []

    jobs_df = pd.DataFrame(
        jobs,
        columns=[
            "job_id",
            "company_name",
            "role",
            "required_skills",
            "location",
            "salary",
            "description"
        ]
    )

    # --------------------------------------------------------
    # Build job text
    # --------------------------------------------------------

    jobs_df["role"] = (
        jobs_df["role"]
        .fillna("")
        .astype(str)
    )

    jobs_df["required_skills"] = (
        jobs_df["required_skills"]
        .fillna("")
        .astype(str)
    )

    jobs_df["description"] = (
        jobs_df["description"]
        .fillna("")
        .astype(str)
    )

    jobs_df["job_text"] = (
        "Role: "
        + jobs_df["role"]
        + ". Required skills: "
        + jobs_df["required_skills"]
        + ". Description: "
        + jobs_df["description"]
    )

    # --------------------------------------------------------
    # User embedding
    # --------------------------------------------------------

    model = get_sbert_model()

    user_text = (
        "Candidate skills: "
        + standardize_skills_text(
            user_skills
        )
    )

    user_embedding = model.encode(
        [user_text],
        normalize_embeddings=True
    )

    # --------------------------------------------------------
    # Job embeddings
    # --------------------------------------------------------

    job_embeddings = model.encode(
        jobs_df["job_text"].tolist(),
        normalize_embeddings=True
    )

    similarity = cosine_similarity(
        user_embedding,
        job_embeddings
    ).flatten()

    role_embeddings = model.encode(
        jobs_df["role"].tolist(),
        normalize_embeddings=True
    )
    role_similarity = cosine_similarity(
        model.encode([desired_role], normalize_embeddings=True),
        role_embeddings
    ).flatten() if desired_role.strip() else None

    description_embeddings = model.encode(
        jobs_df["description"].tolist(),
        normalize_embeddings=True
    )
    description_similarity = cosine_similarity(
        user_embedding,
        description_embeddings
    ).flatten()

    jobs_df[
        "content_score"
    ] = similarity

    # --------------------------------------------------------
    # Skill overlap
    # --------------------------------------------------------

    user_skill_set = {
        skill.strip().lower()
        for skill in standardize_skills_text(
            user_skills
        ).split(",")
        if skill.strip()
    }

    overlap_bonus = []

    for _, row in jobs_df.iterrows():

        job_skill_set = {
            skill.strip().lower()
            for skill in standardize_skills_text(
                row["required_skills"]
            ).split(",")
            if skill.strip()
        }

        overlap = len(
            user_skill_set
            &
            job_skill_set
        )

        if overlap >= 3:
            bonus = 1.10

        elif overlap == 2:
            bonus = 1.05

        elif overlap == 1:
            bonus = 1.02

        else:
            bonus = 0.95

        overlap_bonus.append(
            bonus
        )

    if desired_role.strip():
        jobs_df["content_score"] = (
            0.40 * role_similarity
            + 0.35 * similarity
            + 0.15 * description_similarity
        )
    jobs_df["content_score"] = (
        jobs_df["content_score"]
        * np.array(overlap_bonus)
    )

    # --------------------------------------------------------
    # MMR diversity
    # --------------------------------------------------------

    job_job_similarity = cosine_similarity(
        job_embeddings
    )

    job_index_map = {
        job_id: idx
        for idx, job_id in enumerate(
            jobs_df["job_id"]
        )
    }

    content_scores = dict(
        zip(
            jobs_df["job_id"],
            jobs_df["content_score"]
        )
    )

    top_items = select_top_k_mmr(
        content_scores,
        job_job_similarity,
        job_index_map,
        K=min(
            top_n,
            len(jobs_df)
        ),
        lmbda=0.70
    )

    if not top_items:
        return []

    # --------------------------------------------------------
    # Match percentage
    # --------------------------------------------------------

    jobs_df["match_percentage"] = jobs_df["job_id"].map(
        lambda job_id: min(98.0, max(30.0, round((content_scores.get(job_id, 0.0) * 240.0) + 15.0, 2)))
        if content_scores.get(job_id, 0.0) > 0 else 0.0
    )

    # --------------------------------------------------------
    # Preserve MMR order
    # --------------------------------------------------------

    jobs_df["rank"] = (
        jobs_df["job_id"]
        .map(
            lambda job_id:
                top_items.index(
                    job_id
                )
        )
    )

    return (
        jobs_df[
            jobs_df["job_id"].isin(
                top_items
            )
        ]
        .sort_values(
            by="rank"
        )
        .drop(
            columns=["rank"]
        )
        .to_dict(
            orient="records"
        )
    )


# ============================================================
# POPULAR RECOMMENDATIONS
# ============================================================

def get_popular_recommendations(
    cursor,
    top_n=10
):

    query = """
        SELECT
            j.job_id,
            j.company_name,
            j.role,
            j.required_skills,
            j.location,
            j.salary,
            j.description,

            COALESCE(
                AVG(ui.rating),
                0
            ) AS avg_rating,

            COUNT(
                ui.interaction_id
            ) AS interaction_count

        FROM jobs j

        LEFT JOIN user_interactions ui
            ON j.job_id = ui.job_id

        GROUP BY j.job_id

        ORDER BY
            interaction_count DESC,
            avg_rating DESC

        LIMIT %s
    """

    cursor.execute(
        query,
        (top_n,)
    )

    jobs = cursor.fetchall()

    if not jobs:
        return []

    columns = [
        "job_id",
        "company_name",
        "role",
        "required_skills",
        "location",
        "salary",
        "description",
        "avg_rating",
        "interaction_count"
    ]

    jobs_df = pd.DataFrame(
        jobs,
        columns=columns
    )

    max_count = (
        jobs_df[
            "interaction_count"
        ].max()
        if not jobs_df.empty
        else 1
    )

    if max_count == 0:
        max_count = 1

    jobs_df[
        "match_percentage"
    ] = jobs_df[
        "interaction_count"
    ].map(
        lambda count:
            min(
                95.0,
                round(
                    (
                        count
                        /
                        max_count
                    )
                    * 45.0
                    + 50.0,
                    2
                )
            )
    )

    return jobs_df[
        [
            "job_id",
            "company_name",
            "role",
            "required_skills",
            "location",
            "salary",
            "description",
            "match_percentage"
        ]
    ].to_dict(
        orient="records"
    )
def recommend_internships(
    user_skills,
    internships_df,
    top_n=10
):
    """
    Compatibility wrapper for recommendation_routes.py.

    Uses the improved SBERT recommendation logic.
    """

    # Make a copy
    df = internships_df.copy()

    # Check required columns
    if "skills" not in df.columns:
        raise ValueError(
            "Internship dataset must contain a 'skills' column"
        )

    # Make sure optional columns exist
    if "role" not in df.columns:
        df["role"] = ""

    if "description" not in df.columns:
        df["description"] = ""

    # Fill missing values
    df["skills"] = (
        df["skills"]
        .fillna("")
        .astype(str)
    )

    df["role"] = (
        df["role"]
        .fillna("")
        .astype(str)
    )

    df["description"] = (
        df["description"]
        .fillna("")
        .astype(str)
    )

    # ----------------------------------------------------
    # Build job text
    # ----------------------------------------------------

    df["job_text"] = (
        "Role: "
        + df["role"]
        + ". Required skills: "
        + df["skills"]
        + ". Description: "
        + df["description"]
    )

    # ----------------------------------------------------
    # User text
    # ----------------------------------------------------

    user_text = (
        "Candidate skills: "
        + str(user_skills)
    )

    # ----------------------------------------------------
    # SBERT
    # ----------------------------------------------------

    model = get_sbert_model()

    user_embedding = model.encode(
        [user_text],
        normalize_embeddings=True
    )

    job_embeddings = model.encode(
        df["job_text"].tolist(),
        normalize_embeddings=True
    )

    # ----------------------------------------------------
    # Overall semantic similarity
    # ----------------------------------------------------

    semantic_scores = cosine_similarity(
        user_embedding,
        job_embeddings
    ).flatten()

    # ----------------------------------------------------
    # Skill similarity
    # ----------------------------------------------------

    skill_embeddings = model.encode(
        df["skills"].tolist(),
        normalize_embeddings=True
    )

    skill_scores = cosine_similarity(
        user_embedding,
        skill_embeddings
    ).flatten()

    # ----------------------------------------------------
    # Role similarity
    # ----------------------------------------------------

    role_embeddings = model.encode(
        df["role"].tolist(),
        normalize_embeddings=True
    )

    role_scores = cosine_similarity(
        user_embedding,
        role_embeddings
    ).flatten()

    # ----------------------------------------------------
    # Final score
    # ----------------------------------------------------

    df["semantic_score"] = semantic_scores
    df["skill_score"] = skill_scores
    df["role_score"] = role_scores

    df["match_score"] = (
        0.45 * df["semantic_score"]
        +
        0.35 * df["skill_score"]
        +
        0.20 * df["role_score"]
    )

    # ----------------------------------------------------
    # Sort
    # ----------------------------------------------------

    df = df.sort_values(
        by="match_score",
        ascending=False
    ).reset_index(drop=True)

    # ----------------------------------------------------
    # MMR diversity
    # ----------------------------------------------------

    job_similarity = cosine_similarity(
        job_embeddings
    )

    job_index_map = {
        idx: idx
        for idx in df.index
    }

    score_dict = {
        idx: df.loc[idx, "match_score"]
        for idx in df.index
    }

    selected_indices = select_top_k_mmr(
        score_dict,
        job_similarity,
        job_index_map,
        K=min(
            top_n,
            len(df)
        ),
        lmbda=0.70
    )

    recommendations = (
        df.loc[selected_indices]
        .copy()
    )

    recommendations[
        "match_percentage"
    ] = (
        recommendations["match_score"]
        * 100
    ).round(2)

    return recommendations