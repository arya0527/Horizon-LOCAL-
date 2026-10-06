import re
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from collaborative_filtering import standardize_skills_text, map_user_skills_to_codes

_sbert_model = None

def get_sbert_model():
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _sbert_model

def classify_resume_domain(resume_skills):
    """
    Classifies the resume into Marketing or Software domain based on keyword matching.
    """
    marketing_keywords = {
        "marketing", "market", "brand", "growth", "sales", "sale", 
        "business development", "bd", "social media", "seo", 
        "influencer", "positioning", "advertising", "pr"
    }
    software_keywords = {
        "software", "developer", "it", "ai", "ml", "machine learning", 
        "data science", "python", "java", "node", "react", "typescript", 
        "mongodb", "devops", "aws", "docker", "ci/cd", "coding", 
        "backend", "frontend", "programming", "c++", "c#", "dotnet", "springboot"
    }
    
    # Check lowercased flat skills text
    skills_flat = " ".join(resume_skills).lower()
    
    has_marketing = any(re.search(rf"\b{re.escape(k)}\b", skills_flat) for k in marketing_keywords)
    has_software = any(re.search(rf"\b{re.escape(k)}\b", skills_flat) for k in software_keywords)
    
    if has_marketing and not has_software:
        return "Marketing"
    elif has_software and not has_marketing:
        return "Software"
    elif has_marketing and has_software:
        m_count = sum(1 for k in marketing_keywords if re.search(rf"\b{re.escape(k)}\b", skills_flat))
        s_count = sum(1 for k in software_keywords if re.search(rf"\b{re.escape(k)}\b", skills_flat))
        return "Marketing" if m_count > s_count else "Software"
    return "Other"

def build_job_text(row):
    role = str(row.get("role", "") or "").strip()
    req_skills = standardize_skills_text(str(row.get("required_skills", "") or ""))
    desc = str(row.get("description", "") or "").strip()
    
    parts = []
    if role:
        parts.append(f"Role: {role}")
    if req_skills:
        parts.append(f"Required Skills: {req_skills}")
    if desc:
        parts.append(f"Description: {desc[:300]}")
    return ". ".join(parts)

def match_jobs(resume_skills, jobs_df):
    model = get_sbert_model()
    
    # 1. Classify resume domain
    domain = classify_resume_domain(resume_skills)
    
    # 2. Filter candidates based on domain classifier
    filtered_jobs_df = jobs_df.copy()
    if domain == "Marketing":
        allowed_codes = {"MRKT", "SALE", "BD"}
        keep_indices = []
        for idx, row in jobs_df.iterrows():
            job_codes = set(map_user_skills_to_codes(row["required_skills"]).split(", "))
            if job_codes & allowed_codes:
                keep_indices.append(idx)
        if keep_indices:
            filtered_jobs_df = jobs_df.loc[keep_indices].copy()
            
    elif domain == "Software":
        allowed_codes = {"IT", "ENG", "PRJM"}
        keep_indices = []
        for idx, row in jobs_df.iterrows():
            job_codes = set(map_user_skills_to_codes(row["required_skills"]).split(", "))
            if job_codes & allowed_codes:
                keep_indices.append(idx)
        if keep_indices:
            filtered_jobs_df = jobs_df.loc[keep_indices].copy()
            
    if filtered_jobs_df.empty:
        filtered_jobs_df = jobs_df.copy()

    # 3. Standardize resume skills text
    resume_text = ", ".join(resume_skills)
    std_resume = standardize_skills_text(resume_text)
    user_codes = set(map_user_skills_to_codes(resume_text).split(", "))
    
    # 4. Standardize jobs text using role, required skills, and description
    filtered_jobs_df["standardized_skills"] = filtered_jobs_df.apply(build_job_text, axis=1)
    
    # 5. Compute SBERT similarity
    user_emb = model.encode([std_resume])
    job_embs = model.encode(filtered_jobs_df["standardized_skills"].fillna("").tolist())
    similarity = cosine_similarity(user_emb, job_embs).flatten()
    
    # 6. Apply Category Overlap Filter
    penalties = []
    for idx, row in filtered_jobs_df.iterrows():
        req_skills = row["required_skills"]
        job_codes = set(map_user_skills_to_codes(req_skills).split(", "))
        
        user_codes_clean = {c for c in user_codes if c}
        job_codes_clean = {c for c in job_codes if c}
        
        if user_codes_clean and job_codes_clean:
            overlap = len(user_codes_clean & job_codes_clean)
            penalties.append(1.0 if overlap > 0 else 0.1)
        else:
            penalties.append(1.0)
            
    raw_scores = similarity * np.array(penalties)
    filtered_jobs_df["match_percentage"] = [
        min(98.0, max(30.0, round((s * 240.0) + 15.0, 2))) if s > 0 else 0.0
        for s in raw_scores
    ]
    
    # Sort and return top 10
    recommendations = filtered_jobs_df.sort_values(
        by="match_percentage",
        ascending=False
    )
    return recommendations.head(10)

