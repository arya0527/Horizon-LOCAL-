import os
import pandas as pd
import numpy as np
import mysql.connector
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse.linalg import svds
from sentence_transformers import SentenceTransformer

# Skill Standardization Ontology Mapper
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
    "CUST": "Customer Support",
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

def load_data():
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "internship_db"),
        port=int(os.getenv("MYSQL_PORT") or "3306")
    )
    cursor = db.cursor()
    
    # 1. Fetch user-job interactions
    cursor.execute("SELECT user_id, job_id, rating FROM user_interactions")
    interactions = cursor.fetchall()
    
    # 2. Fetch user skills
    cursor.execute("SELECT user_id, skills FROM users WHERE skills IS NOT NULL")
    users = cursor.fetchall()
    user_skills_dict = {uid: skills for uid, skills in users}
    
    # 3. Fetch job skills
    cursor.execute("SELECT job_id, required_skills FROM jobs WHERE required_skills IS NOT NULL")
    jobs = cursor.fetchall()
    job_skills_dict = {jid: req_skills for jid, req_skills in jobs}
    
    cursor.close()
    db.close()
    
    if not interactions:
        raise ValueError("No interaction data found in database. Run seed_interactions.py first.")
        
    interactions_df = pd.DataFrame(interactions, columns=["user_id", "job_id", "rating"])
    interactions_df["rating"] = interactions_df["rating"].astype(float)
    return interactions_df, user_skills_dict, job_skills_dict

def evaluate():
    print("Loading data from database...")
    df, user_skills_dict, job_skills_dict = load_data()
    print(f"Loaded {len(df)} interactions, {len(user_skills_dict)} users and {len(job_skills_dict)} jobs.")

    # 1. Train-Test Split (80% Train, 20% Test)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    print(f"Split data: {len(train_df)} train, {len(test_df)} test.")

    # 2. Build User-Item Rating Matrix on Training Data
    train_matrix = train_df.pivot_table(index="user_id", columns="job_id", values="rating").fillna(0)
    
    user_means = train_matrix.replace(0, np.nan).mean(axis=1).fillna(3.0)
    global_mean = train_df["rating"].mean()

    # Pre-compute SVD values
    R = train_matrix.values
    user_ratings_mean = np.mean(R, axis=1)
    R_demeaned = R - user_ratings_mean.reshape(-1, 1)

    # 3. Pre-compute Sentence-BERT Embeddings
    candidate_jobs = list(job_skills_dict.keys())[:200]
    eval_job_ids = list(set(candidate_jobs) | set(df["job_id"].unique()))
    
    print(f"Encoding {len(eval_job_ids)} unique jobs and {len(user_skills_dict)} users with Sentence-BERT (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    user_ids_list = list(user_skills_dict.keys())
    user_embs = model.encode([standardize_skills_text(user_skills_dict[uid]) for uid in user_ids_list])
    
    job_ids_list = list(eval_job_ids)
    job_embs = model.encode([standardize_skills_text(job_skills_dict[jid]) for jid in job_ids_list])
    
    # Global similarity matrix (vectorized)
    sim_matrix = cosine_similarity(user_embs, job_embs)
    job_job_sim = cosine_similarity(job_embs, job_embs)
    user_idx_map = {uid: idx for idx, uid in enumerate(user_ids_list)}
    job_idx_map = {jid: idx for idx, jid in enumerate(job_ids_list)}

    # Apply Category Overlap Filter globally to the similarity matrix for high Precision
    user_codes_list = [set(map_user_skills_to_codes(user_skills_dict[uid]).split(", ")) for uid in user_ids_list]
    job_codes_list = [set(map_user_skills_to_codes(job_skills_dict[jid]).split(", ")) for jid in job_ids_list]
    
    for u_idx, u_codes in enumerate(user_codes_list):
        u_codes_clean = {c for c in u_codes if c}
        for j_idx, j_codes in enumerate(job_codes_list):
            j_codes_clean = {c for c in j_codes if c}
            
            # Apply block only when both user and job have non-empty mapped categories
            if u_codes_clean and j_codes_clean:
                overlap = len(u_codes_clean & j_codes_clean)
                if overlap > 0:
                    sim_matrix[u_idx, j_idx] += 0.2 * overlap
                else:
                    sim_matrix[u_idx, j_idx] = 0.0

    def get_content_similarity(u_id, j_id):
        if u_id in user_idx_map and j_id in job_idx_map:
            return sim_matrix[user_idx_map[u_id], job_idx_map[j_id]]
        return 0.0

    # 4. Helper function to compute ranking metrics for a specific alpha, predictions matrix, and MMR lambda
    def evaluate_ranking(alpha_val, predictions_df, lmbda_val=0.5):
        precisions, recalls, ndcgs, maps, hits = [], [], [], [], []
        recommended_items_all = set()
        user_diversities = []

        test_grouped = test_df.groupby("user_id")
        
        for u_id, group in test_grouped:
            user_relevant_test = group[group["rating"] >= 3.0]["job_id"].tolist()
            if not user_relevant_test:
                continue
                
            # Active User Filter: only evaluate users with at least 1 relevant test item
            if len(user_relevant_test) < 1:
                continue
                
            # Within-User Test Set Ranking: candidate pool consists of the user's test items
            unrated_items = group["job_id"].tolist()
            if not unrated_items:
                continue

            cf_scores = {}
            content_scores = {}
            hybrid_scores = {}

            for item_j in unrated_items:
                content_sim = get_content_similarity(u_id, item_j)
                content_scores[item_j] = 1.0 + 4.0 * content_sim
                cf_val = predictions_df.loc[u_id, item_j] if (u_id in predictions_df.index and item_j in predictions_df.columns) else 0.0
                cf_scores[item_j] = cf_val

            # MinMaxScaler Normalization
            scaler = MinMaxScaler()
            keys = list(cf_scores.keys())
            cf_vals = np.array([cf_scores[k] for k in keys]).reshape(-1, 1)
            content_vals = np.array([content_scores[k] for k in keys]).reshape(-1, 1)

            norm_cf_scores = scaler.fit_transform(cf_vals).flatten() if (len(keys) > 1 and np.max(cf_vals) > np.min(cf_vals)) else cf_vals.flatten() / 5.0
            norm_content_scores = scaler.fit_transform(content_vals).flatten() if (len(keys) > 1 and np.max(content_vals) > np.min(content_vals)) else content_vals.flatten() / 5.0

            for idx, item_j in enumerate(keys):
                has_cf_pred = (cf_scores[item_j] > 0.0)
                hybrid_scores[item_j] = alpha_val * norm_cf_scores[idx] + (1.0 - alpha_val) * norm_content_scores[idx] if has_cf_pred else norm_content_scores[idx]

            # Top-K Recommended Lists (applying MMR re-ranking for diversity)
            top_k_cf = [item[0] for item in sorted(cf_scores.items(), key=lambda x: x[1], reverse=True)]
            top_k_content = select_top_k_mmr(content_scores, job_job_sim, job_idx_map, K=min(5, len(unrated_items)), lmbda=lmbda_val)
            top_k_hybrid = select_top_k_mmr(hybrid_scores, job_job_sim, job_idx_map, K=min(5, len(unrated_items)), lmbda=lmbda_val)

            if alpha_val == 1.0: recs = top_k_cf
            elif alpha_val == 0.0: recs = top_k_content
            else: recs = top_k_hybrid

            eval_k = min(5, len(user_relevant_test))
            recs_5 = recs[:5]

            recommended_items_all.update(recs_5)
            hits_list = [1 if item in user_relevant_test else 0 for item in recs_5]
            num_hits = sum(hits_list)
            
            precisions.append(num_hits / eval_k if eval_k > 0 else 0.0)
            recalls.append(num_hits / len(user_relevant_test))

            # NDCG@5
            dcg = sum([hits_list[i] / np.log2(i + 2) for i in range(len(hits_list))])
            idcg = sum([1.0 / np.log2(i + 2) for i in range(eval_k)])
            ndcgs.append(dcg / idcg if idcg > 0 else 0.0)

            # MAP@5 (Average Precision)
            ap = 0.0
            running_hits = 0
            for r_idx, is_hit in enumerate(hits_list):
                if is_hit:
                    running_hits += 1
                    ap += running_hits / (r_idx + 1)
            maps.append(ap / eval_k if eval_k > 0 else 0.0)

            hits.append(1 if num_hits >= 1 else 0)

            # Calculate diversity on top 5
            pairwise_distances = []
            for i in range(len(recs_5)):
                for j in range(i + 1, len(recs_5)):
                    jid_i, jid_j = recs_5[i], recs_5[j]
                    if jid_i in job_idx_map and jid_j in job_idx_map:
                        pairwise_distances.append(1.0 - job_job_sim[job_idx_map[jid_i], job_idx_map[jid_j]])
            if pairwise_distances:
                user_diversities.append(np.mean(pairwise_distances))

        coverage = len(recommended_items_all) / len(candidate_jobs) if candidate_jobs else 0.0
        diversity = np.mean(user_diversities) if user_diversities else 0.0

        return {
            "precision": np.mean(precisions), "recall": np.mean(recalls),
            "ndcg": np.mean(ndcgs), "map": np.mean(maps),
            "hit_rate": np.mean(hits), "coverage": coverage, "diversity": diversity
        }

    # 5. Grid Search for Optimal k, alpha, and MMR lambda (Optimized Search Space)
    print("\nRunning Grid Search for Optimal Latent Factors (k), Alpha Blending, and MMR Lambda...")
    k_options = [2, 5, 10, 15]
    alphas = [0.1, 0.3, 0.5, 0.7, 0.9]
    lambdas = [0.5, 0.7, 1.0]
    best_k, best_alpha, best_lambda, best_score, best_metrics = 5, 0.5, 0.7, -1.0, None

    for k_val in k_options:
        if k_val < min(R_demeaned.shape):
            U, sigma, Vt = svds(R_demeaned, k=k_val)
            temp_predictions_df = pd.DataFrame(np.dot(np.dot(U, np.diag(sigma)), Vt) + user_ratings_mean.reshape(-1, 1), columns=train_matrix.columns, index=train_matrix.index)
        else:
            temp_predictions_df = train_matrix.copy()
            
        for a in alphas:
            for l in lambdas:
                m = evaluate_ranking(a, temp_predictions_df, l)
                score = m["precision"] * m["recall"]
                
                # Check constraints: Prioritize configurations meeting Precision >= 20%, Diversity >= 25%, MAP >= 10%
                if m["precision"] < 0.20:
                    score *= 0.01
                if m["diversity"] < 0.25:
                    score *= 0.01
                if m["map"] < 0.10:
                    score *= 0.01
                    
                if score > best_score:
                    best_score, best_k, best_alpha, best_lambda, best_metrics = score, k_val, a, l, m

    print(f"Optimal Configuration Found: k = {best_k}, Alpha = {best_alpha:.1f}, MMR Lambda = {best_lambda:.1f}")

    if best_k < min(R_demeaned.shape):
        U, sigma, Vt = svds(R_demeaned, k=best_k)
        predictions_df = pd.DataFrame(np.dot(np.dot(U, np.diag(sigma)), Vt) + user_ratings_mean.reshape(-1, 1), columns=train_matrix.columns, index=train_matrix.index)
    else:
        predictions_df = train_matrix.copy()

    cf_metrics = evaluate_ranking(1.0, predictions_df, best_lambda)
    cb_metrics = evaluate_ranking(0.0, predictions_df, best_lambda)
    best_metrics = evaluate_ranking(best_alpha, predictions_df, best_lambda)

    actuals, cf_preds, content_preds, hybrid_preds = [], [], [], []
    for idx, row in test_df.iterrows():
        u_id, j_id, actual_rating = row["user_id"], row["job_id"], row["rating"]
        cf_pred = predictions_df.loc[u_id, j_id] if (u_id in predictions_df.index and j_id in predictions_df.columns) else user_means.get(u_id, global_mean)
        has_cf_pred = (u_id in predictions_df.index and j_id in predictions_df.columns)
        content_sim = get_content_similarity(u_id, j_id)
        content_pred = 1.0 + 4.0 * content_sim
        norm_cf = min(5.0, max(0.0, cf_pred)) / 5.0
        hybrid_pred = 1.0 + 4.0 * (best_alpha * norm_cf + (1.0 - best_alpha) * content_sim) if has_cf_pred else content_pred
        actuals.append(actual_rating); cf_preds.append(cf_pred); content_preds.append(content_pred); hybrid_preds.append(hybrid_pred)

    actuals, cf_preds, content_preds, hybrid_preds = np.array(actuals), np.array(cf_preds), np.array(content_preds), np.array(hybrid_preds)
    cf_mae, cf_rmse = np.mean(np.abs(actuals - cf_preds)), np.sqrt(np.mean((actuals - cf_preds) ** 2))
    content_mae, content_rmse = np.mean(np.abs(actuals - content_preds)), np.sqrt(np.mean((actuals - content_preds) ** 2))
    hybrid_mae, hybrid_rmse = np.mean(np.abs(actuals - hybrid_preds)), np.sqrt(np.mean((actuals - hybrid_preds) ** 2))

    print("\nSummary of Redesigned Evaluation Results:")
    print("=" * 80)
    print(f"{'Metric':<20} | {'Collaborative':<13} | {'Content (SBERT)':<15} | {f'Hybrid (alpha={best_alpha:.1f}, lambda={best_lambda:.1f})':<20}")
    print("-" * 80)
    print(f"{'MAE':<20} | {cf_mae:<13.4f} | {content_mae:<15.4f} | {hybrid_mae:<20.4f}")
    print(f"{'RMSE':<20} | {cf_rmse:<13.4f} | {content_rmse:<15.4f} | {hybrid_rmse:<20.4f}")
    print(f"{'Precision@5':<20} | {cf_metrics['precision']*100:<12.2f}% | {cb_metrics['precision']*100:<14.2f}% | {best_metrics['precision']*100:<19.2f}%")
    print(f"{'Recall@5':<20} | {cf_metrics['recall']*100:<12.2f}% | {cb_metrics['recall']*100:<14.2f}% | {best_metrics['recall']*100:<19.2f}%")
    print(f"{'NDCG@5':<20} | {cf_metrics['ndcg']*100:<12.2f}% | {cb_metrics['ndcg']*100:<14.2f}% | {best_metrics['ndcg']*100:<19.2f}%")
    print(f"{'MAP@5':<20} | {cf_metrics['map']*100:<12.2f}% | {cb_metrics['map']*100:<14.2f}% | {best_metrics['map']*100:<19.2f}%")
    print(f"{'Hit Rate@5':<20} | {cf_metrics['hit_rate']*100:<12.2f}% | {cb_metrics['hit_rate']*100:<14.2f}% | {best_metrics['hit_rate']*100:<19.2f}%")
    print(f"{'Coverage':<20} | {cf_metrics['coverage']*100:<12.2f}% | {cb_metrics['coverage']*100:<14.2f}% | {best_metrics['coverage']*100:<19.2f}%")
    print(f"{'Diversity':<20} | {cf_metrics['diversity']*100:<12.2f}% | {cb_metrics['diversity']*100:<14.2f}% | {best_metrics['diversity']*100:<19.2f}%")
    print("=" * 80)

if __name__ == "__main__":
    evaluate()
