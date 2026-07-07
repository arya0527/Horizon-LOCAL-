import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse.linalg import svds
from sentence_transformers import SentenceTransformer

# Skill Standardization Ontology Mapper
ONTOLOGY_EXPANSIONS = {
    "ML": "Machine Learning", "AI": "Artificial Intelligence",
    "MRKT": "Marketing", "SALE": "Sales", "ENG": "Engineering",
    "IT": "Information Technology", "HCPR": "Healthcare",
    "ACCT": "Accounting", "FIN": "Finance", "MGMT": "Management",
    "DSGN": "Design", "ART": "Art", "PRJM": "Project Management",
    "BD": "Business Development", "LGL": "Legal", "EDU": "Education",
    "TRNG": "Training", "ADM": "Administrative", "HR": "Human Resources",
    "CUST": "Customer Support"
}

def standardize_skills_text(skills_str):
    if not skills_str or pd.isna(skills_str):
        return ""
    
    cleaned_str = str(skills_str).replace("/", ",").replace(";", ",")
    tokens = []
    for token in cleaned_str.split(","):
        token = token.strip().lower()
        if not token:
            continue
        
        token_upper = token.upper()
        if token_upper in ONTOLOGY_EXPANSIONS:
            tokens.append(ONTOLOGY_EXPANSIONS[token_upper])
        else:
            words = token.split()
            expanded_words = []
            for w in words:
                w_upper = w.upper()
                if w_upper in ONTOLOGY_EXPANSIONS:
                    expanded_words.append(ONTOLOGY_EXPANSIONS[w_upper])
                else:
                    expanded_words.append(w)
            tokens.append(" ".join(expanded_words))
            
    return ", ".join(tokens)

def map_user_skills_to_codes(user_skills):
    if not user_skills:
        return ""
    
    if isinstance(user_skills, str):
        skills = [s.strip().lower() for s in user_skills.split(",")]
    else:
        skills = [s.strip().lower() for s in user_skills]
        
    mapped_codes = set()
    valid_codes = {
        "IT", "ENG", "PRJM", "SALE", "BD", "MRKT", "FIN", "ACCT", 
        "HCPR", "RSCH", "DSGN", "ART", "MGMT", "LGL", "EDU", "TRNG", "ADM"
    }
    
    for skill in skills:
        if skill in ONTOLOGY_EXPANSIONS:
            mapped_codes.add(skill.upper())
        elif skill.upper() in valid_codes:
            mapped_codes.add(skill.upper())
                    
    return ", ".join(mapped_codes) if mapped_codes else user_skills

_sbert_model = None

def get_sbert_model():
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _sbert_model

def select_top_k_mmr(scores_dict, job_job_sim, job_idx_map, K=5, lmbda=0.5):
    """
    Selects top-K items using Maximal Marginal Relevance (MMR)
    to balance relevance and diversity.
    """
    if len(scores_dict) <= K:
        return list(scores_dict.keys())
        
    selected = []
    candidates = list(scores_dict.keys())
    
    max_score = max(scores_dict.values())
    min_score = min(scores_dict.values())
    score_range = max_score - min_score if max_score > min_score else 1.0
    
    # Start with the highest-scoring candidate
    first_item = max(scores_dict, key=scores_dict.get)
    selected.append(first_item)
    candidates.remove(first_item)
    
    while len(selected) < K and candidates:
        best_mmr = -9999.0
        best_candidate = None
        
        for cand in candidates:
            # Normalize relevance to [0.0, 1.0]
            rel = (scores_dict[cand] - min_score) / score_range
            
            # Max similarity to already selected items
            max_sim = -1.0
            for sel in selected:
                if cand in job_idx_map and sel in job_idx_map:
                    sim = job_job_sim[job_idx_map[cand], job_idx_map[sel]]
                    if sim > max_sim:
                        max_sim = sim
            if max_sim == -1.0:
                max_sim = 0.0
                
            # MMR formula
            mmr_score = lmbda * rel - (1.0 - lmbda) * max_sim
            if mmr_score > best_mmr:
                best_mmr = mmr_score
                best_candidate = cand
                
        if best_candidate is not None:
            selected.append(best_candidate)
            candidates.remove(best_candidate)
        else:
            break
            
    return selected

def get_content_based_ratings(user_id, job_ids, cursor):
    """
    SBERT content mapping with Category Overlap Filters.
    """
    if not job_ids:
        return {}

    cursor.execute("SELECT skills FROM users WHERE user_id = %s", (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row or not user_row[0]:
        return {jid: 1.0 for jid in job_ids}
        
    raw_skills = user_row[0]
    
    # 1. Map user skills to category codes
    user_codes = set(map_user_skills_to_codes(raw_skills).split(", "))
    standardized_user_skills = standardize_skills_text(raw_skills)

    # Fetch jobs
    placeholders = ", ".join(["%s"] * len(job_ids))
    query = f"SELECT job_id, required_skills FROM jobs WHERE job_id IN ({placeholders})"
    cursor.execute(query, tuple(job_ids))
    jobs = cursor.fetchall()
    
    if not jobs:
        return {jid: 1.0 for jid in job_ids}
        
    jobs_df = pd.DataFrame(jobs, columns=["job_id", "required_skills"])
    jobs_df["standardized_skills"] = jobs_df["required_skills"].map(standardize_skills_text)
    
    # Compute similarity embeddings
    model = get_sbert_model()
    user_emb = model.encode([standardized_user_skills])
    job_embs = model.encode(jobs_df["standardized_skills"].fillna("").tolist())
    similarity = cosine_similarity(user_emb, job_embs).flatten()
    
    # 2. Apply Category Overlap Filter: penalize zero overlap jobs by 90%
    penalties = []
    for idx, row in jobs_df.iterrows():
        req_skills = row["required_skills"]
        job_codes = set(map_user_skills_to_codes(req_skills).split(", "))
        overlap = len(user_codes & job_codes)
        penalties.append(1.0 if overlap > 0 else 0.1)
        
    jobs_df["similarity"] = similarity * np.array(penalties)
    jobs_df["content_rating"] = 1.0 + 4.0 * jobs_df["similarity"]
    
    return dict(zip(jobs_df["job_id"], jobs_df["content_rating"]))

def get_hybrid_recommendations(user_id, cursor, top_n=10, alpha=0.5):
    """
    Optimized SVD + SBERT hybrid model with Category Overlap Filters and MMR re-ranking.
    """
    cursor.execute("SELECT user_id, job_id, rating FROM user_interactions")
    interactions = cursor.fetchall()
    
    cursor.execute("SELECT job_id, required_skills FROM jobs WHERE required_skills IS NOT NULL LIMIT 600")
    candidate_jobs_raw = cursor.fetchall()
    candidate_jobs = [row[0] for row in candidate_jobs_raw]
    candidate_skills_dict = {row[0]: row[1] for row in candidate_jobs_raw}

    if not candidate_jobs:
        return []

    if not interactions:
        return get_fallback_recommendations(user_id, cursor, top_n)

    df = pd.DataFrame(interactions, columns=["user_id", "job_id", "rating"])
    df["rating"] = df["rating"].astype(float)
    
    if user_id not in df["user_id"].values:
        return get_fallback_recommendations(user_id, cursor, top_n)

    pivot_matrix = df.pivot_table(index="user_id", columns="job_id", values="rating").fillna(0)

    if user_id not in pivot_matrix.index:
        return get_fallback_recommendations(user_id, cursor, top_n)

    # SVD rating prediction
    R = pivot_matrix.values
    user_ratings_mean = np.mean(R, axis=1)
    R_demeaned = R - user_ratings_mean.reshape(-1, 1)
    k = min(15, min(R_demeaned.shape) - 1)
    
    if k >= 1:
        U, sigma, Vt = svds(R_demeaned, k=k)
        sigma = np.diag(sigma)
        all_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
        predictions_df = pd.DataFrame(all_predicted_ratings, columns=pivot_matrix.columns, index=pivot_matrix.index)
    else:
        predictions_df = pivot_matrix.copy()

    user_ratings = pivot_matrix.loc[user_id]
    rated_items = user_ratings[user_ratings > 0].index.tolist()
    unrated_items = [jid for jid in candidate_jobs if jid not in rated_items]

    if not unrated_items:
        return get_popular_recommendations(cursor, top_n)

    cf_scores = {}
    for jid in unrated_items:
        cf_scores[jid] = predictions_df.loc[user_id, jid] if jid in predictions_df.columns else 0.0

    content_scores = get_content_based_ratings(user_id, unrated_items, cursor)

    # Normalize
    scaler = MinMaxScaler()
    keys = list(cf_scores.keys())
    cf_array = np.array([cf_scores[k] for k in keys]).reshape(-1, 1)
    content_array = np.array([content_scores.get(k, 1.0) for k in keys]).reshape(-1, 1)

    norm_cf = scaler.fit_transform(cf_array).flatten() if (len(keys) > 1 and np.max(cf_array) > np.min(cf_array)) else cf_array.flatten() / 5.0
    norm_content = scaler.fit_transform(content_array).flatten() if (len(keys) > 1 and np.max(content_array) > np.min(content_array)) else content_array.flatten() / 5.0

    # Hybrid scores dict
    hybrid_scores = {}
    for idx, jid in enumerate(keys):
        cf_val = norm_cf[idx]
        content_val = norm_content[idx]
        hybrid_scores[jid] = alpha * cf_val + (1.0 - alpha) * content_val if cf_scores[jid] > 0.0 else content_val

    # MMR Re-ranking for Diversity
    model = get_sbert_model()
    job_skills_list = [standardize_skills_text(candidate_skills_dict[jid]) for jid in unrated_items]
    job_embs = model.encode(job_skills_list)
    job_job_sim = cosine_similarity(job_embs, job_embs)
    job_idx_map = {jid: idx for idx, jid in enumerate(unrated_items)}
    
    # Run MMR to select top items
    top_items = select_top_k_mmr(hybrid_scores, job_job_sim, job_idx_map, K=min(top_n, len(unrated_items)), lmbda=0.5)

    if not top_items:
        return get_fallback_recommendations(user_id, cursor, top_n)

    # Fetch top jobs details
    placeholders = ", ".join(["%s"] * len(top_items))
    query = f"SELECT job_id, company_name, role, required_skills, location, salary, description FROM jobs WHERE job_id IN ({placeholders})"
    cursor.execute(query, tuple(top_items))
    jobs = cursor.fetchall()

    jobs_df = pd.DataFrame(jobs, columns=["job_id", "company_name", "role", "required_skills", "location", "salary", "description"])
    
    # Calculate match percentage
    scores_dict = {jid: hybrid_scores[jid] for jid in top_items}
    jobs_df["match_percentage"] = jobs_df["job_id"].map(lambda x: min(100.0, round(scores_dict.get(x, 0.0) * 100, 2)))
    
    # Keep the MMR order
    jobs_df["rank"] = jobs_df["job_id"].map(lambda x: top_items.index(x))
    return jobs_df.sort_values(by="rank").drop(columns=["rank"]).to_dict(orient="records")

def get_collaborative_recommendations(user_id, cursor, top_n=10):
    return get_hybrid_recommendations(user_id, cursor, top_n, alpha=0.5)

def get_fallback_recommendations(user_id, cursor, top_n=10):
    """
    SBERT Content-Based fallback with MMR re-ranking.
    """
    cursor.execute("SELECT skills FROM users WHERE user_id = %s", (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row or not user_row[0]:
        return get_popular_recommendations(cursor, top_n)

    user_skills = user_row[0]
    
    # Fetch candidate jobs
    cursor.execute("SELECT job_id, company_name, role, required_skills, location, salary, description FROM jobs WHERE required_skills IS NOT NULL LIMIT 600")
    jobs = cursor.fetchall()
    
    if not jobs:
        return []

    columns = ["job_id", "company_name", "role", "required_skills", "location", "salary", "description"]
    jobs_df = pd.DataFrame(jobs, columns=columns)
    
    # Mapped user codes
    user_codes = set(map_user_skills_to_codes(user_skills).split(", "))
    
    # Pre-compute SBERT similarities
    model = get_sbert_model()
    user_emb = model.encode([standardize_skills_text(user_skills)])
    job_skills_list = [standardize_skills_text(skills) for skills in jobs_df["required_skills"]]
    job_embs = model.encode(job_skills_list)
    similarity = cosine_similarity(user_emb, job_embs).flatten()
    
    # Apply category overlap filter
    penalties = []
    for idx, row in jobs_df.iterrows():
        req_skills = row["required_skills"]
        job_codes = set(map_user_skills_to_codes(req_skills).split(", "))
        overlap = len(user_codes & job_codes)
        penalties.append(1.0 if overlap > 0 else 0.1)
        
    jobs_df["similarity"] = similarity * np.array(penalties)
    content_scores = dict(zip(jobs_df["job_id"], jobs_df["similarity"]))
    
    # Compute job-job similarity matrix
    job_job_sim = cosine_similarity(job_embs, job_embs)
    job_idx_map = {jid: idx for idx, jid in enumerate(jobs_df["job_id"])}
    
    # MMR to select top jobs
    top_items = select_top_k_mmr(content_scores, job_job_sim, job_idx_map, K=min(top_n, len(jobs_df)), lmbda=0.5)
    
    jobs_df = jobs_df[jobs_df["job_id"].isin(top_items)].copy()
    jobs_df["match_percentage"] = jobs_df["job_id"].map(lambda x: min(100.0, round(content_scores[x] * 100, 2)))
    jobs_df["rank"] = jobs_df["job_id"].map(lambda x: top_items.index(x))
    
    return jobs_df.sort_values(by="rank").drop(columns=["rank"]).to_dict(orient="records")

def get_popular_recommendations(cursor, top_n=10):
    query = """
    SELECT j.job_id, j.company_name, j.role, j.required_skills, j.location, j.salary, j.description,
           COALESCE(AVG(ui.rating), 0) as avg_rating, COUNT(ui.interaction_id) as interaction_count
    FROM jobs j
    LEFT JOIN user_interactions ui ON j.job_id = ui.job_id
    GROUP BY j.job_id
    ORDER BY interaction_count DESC, avg_rating DESC
    LIMIT %s
    """
    cursor.execute(query, (top_n,))
    jobs = cursor.fetchall()
    
    columns = ["job_id", "company_name", "role", "required_skills", "location", "salary", "description", "avg_rating", "interaction_count"]
    jobs_df = pd.DataFrame(jobs, columns=columns)
    
    max_count = jobs_df["interaction_count"].max() if not jobs_df.empty else 1
    if max_count == 0:
        max_count = 1
    jobs_df["match_percentage"] = jobs_df["interaction_count"].map(lambda x: min(95.0, round((x / max_count) * 45.0 + 50.0, 2)))
    
    return jobs_df[["job_id", "company_name", "role", "required_skills", "location", "salary", "description", "match_percentage"]].to_dict(orient="records")
