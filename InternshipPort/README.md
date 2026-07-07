# 🚀 HORIZON NEXT - AI Internship Recommendation System

An AI-powered internship and job recommendation platform that analyzes resumes, extracts skills, and recommends relevant opportunities using modern NLP and Recommendation System techniques.

---

## 📌 Overview

InternshipPort is a hybrid recommendation system designed to help students discover internships and jobs that match their skills and interests.

The platform combines:

- Resume Parsing
- NLP-based Skill Extraction
- SBERT Semantic Matching
- SVD Collaborative Filtering
- MMR Re-ranking
- Category-Aware Recommendation Filtering

to provide highly relevant and personalized recommendations.

---

## ✨ Features

### Resume Analysis
- Upload resumes in PDF format
- Automatic skill extraction
- Resume-to-job semantic matching

### Recommendation Engine
- SBERT-based content recommendations
- SVD collaborative filtering
- Hybrid recommendation model
- Personalized job recommendations
- Match percentage scoring

### Recommendation Quality Improvements
- Category-aware filtering
- Maximal Marginal Relevance (MMR) re-ranking
- Improved diversity and ranking quality
- Cold-start user support

### Dashboard
- Student Dashboard
- Placement Dashboard
- Company Dashboard
- Mentor Dashboard

---

## 🏗️ System Architecture

### Cold Start Recommendation Flow

```text
Resume Upload
      ↓
Resume Parser
      ↓
Skill Extraction
      ↓
SBERT Embeddings
      ↓
Semantic Similarity Matching
      ↓
MMR Re-ranking
      ↓
Top Recommended Jobs
```

### Personalized Recommendation Flow

```text
User Interactions
(Views, Bookmarks, Applications)
              ↓
Interaction Matrix
              ↓
SVD Matrix Factorization
              ↓
Collaborative Filtering
              ↓
SBERT Semantic Matching
              ↓
Hybrid Recommendation Engine
              ↓
Personalized Recommendations
```

---

## 🛠️ Tech Stack

### Frontend
- React
- Vite
- CSS

### Backend
- Flask
- Python

### Machine Learning & NLP
- Sentence-BERT (all-MiniLM-L6-v2)
- spaCy
- Scikit-Learn
- Cosine Similarity
- SVD Matrix Factorization
- MMR Re-ranking

### Database
- MySQL

### Deployment
- Railway (Backend)
- Vercel (Frontend)

---

## 📊 Dataset

### Job Dataset
- 122,096 Job Postings

### Users
- 50 Simulated Users

### Interactions
- 1,846 Synthetic User-Job Interactions

---

## 🎯 Synthetic Interaction Generation

Since real user interaction data was unavailable, interactions were simulated using skill overlap probabilities.

### Interaction Probability Rules

| Condition | Probability |
|------------|-------------|
| Skill Overlap Exists | 65% |
| No Skill Overlap | 8% |

### Interaction Types

| Action | Rating |
|---------|---------|
| View | 1 |
| Bookmark | 3 |
| Apply | 5 |

This synthetic interaction matrix was used to train and evaluate the collaborative filtering component.

---

## 🧠 Problems Solved

### 1. Cold Start Problem

New users have no interaction history.

#### Solution
- Resume Parsing
- SBERT Semantic Matching

---

### 2. Data Sparsity

Dataset Characteristics:

```text
50 Users
1846 Interactions
122096 Jobs
```

Resulting in an extremely sparse interaction matrix.

#### Solution
- SVD Matrix Factorization

---

### 3. Recommendation Diversity

Traditional recommenders often produce repetitive results.

#### Solution
- Maximal Marginal Relevance (MMR) Re-ranking

---

## 📈 Evaluation Results

### Hybrid Recommendation Model

| Metric | Score |
|----------|----------|
| Precision@5 | 75.17% |
| Recall@5 | 72.00% |
| NDCG@5 | 65.03% |
| MAP@5 | 52.96% |
| Hit Rate@5 | 100.00% |
| Coverage | 59.50% |
| Diversity | 41.03% |

---

## 📸 Screenshots

### Home Page
<img width="959" height="539" alt="image" src="https://github.com/user-attachments/assets/f65bf951-2706-41ef-a932-cd7a11eafdb8" />


### Resume Upload & Skill Extraction
<img width="959" height="539" alt="image" src="https://github.com/user-attachments/assets/5c723ee9-e5a8-472e-95c1-ec934b843c08" />
<img width="959" height="539" alt="image" src="https://github.com/user-attachments/assets/c5e23844-b3ed-47a4-8008-57cc5debb4a9" />


### Recommendation Dashboard
<img width="956" height="538" alt="image" src="https://github.com/user-attachments/assets/223ca92b-04c1-40c2-90ab-3f1d1cbf4b96" />


### Metrics Analysis
<img width="959" height="503" alt="image" src="https://github.com/user-attachments/assets/e6c90aea-882f-4f5e-979e-f6b881251835" />



---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/arya0527/InternshipPort.git
cd InternshipPort
```

---

### Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

Backend runs on:(Railway)

```text
https://internshipport-production.up.railway.app/
```

---

### Frontend Setup:(Vercel)

```bash
cd jobnext

npm install

npm run dev
```

Frontend runs on:

```text
https://internship-port.vercel.app/
```

---

## 🔮 Future Enhancements

- Real User Interaction Data
- Live Job APIs
- BERT Fine-Tuning
- Reinforcement Learning Based Recommendations
- User Feedback Learning Loop
- Real-Time Recommendation Updates
- Explainable AI Recommendations

---

## 👨‍💻 Author

### Arya Bhat

BE CSE (Artificial Intelligence & Machine Learning)

Passionate about:
- Artificial Intelligence
- Recommendation Systems
- Data Science
- Formula 1 Analytics
- Machine Learning Engineering

---

## ⭐ Project Highlights

- Processed **122K+ job postings**
- Implemented **SBERT semantic matching**
- Used **SVD matrix factorization** to handle sparse interactions
- Solved the **cold-start problem**
- Improved recommendation diversity using **MMR re-ranking**
- Achieved **75.17% Precision@5** and **72.00% Recall@5**
- Built a complete **full-stack AI recommendation platform**

If you found this project interesting, consider giving it a ⭐ on GitHub.
