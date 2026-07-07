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
    
    has_marketing = any(k in skills_flat for k in marketing_keywords)
    has_software = any(k in skills_flat for k in software_keywords)
    
    if has_marketing:
        return "Marketing"
    elif has_software:
        return "Software"
    return "Other"

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
    
    # 4. Standardize jobs required skills
    filtered_jobs_df["standardized_skills"] = filtered_jobs_df["required_skills"].map(standardize_skills_text)
    
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
            penalties.append(1.0 if overlap > 0 else 0.0)
        else:
            penalties.append(1.0)
            
    filtered_jobs_df["match_percentage"] = similarity * np.array(penalties) * 100.0
    
    # Sort and return top 10
    recommendations = filtered_jobs_df.sort_values(
        by="match_percentage",
        ascending=False
    )
    return recommendations.head(10)
