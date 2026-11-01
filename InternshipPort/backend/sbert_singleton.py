"""
Shared SBERT model singleton.

Loaded once at app startup (when this module is first imported).
Both matcher.py and recommendation.py import from here so the model
is never downloaded or initialised twice, and there are no SSL
re-verification calls during live requests.
"""

from sentence_transformers import SentenceTransformer

# "all-MiniLM-L6-v2" is cached after first download.
# local_files_only=True is NOT set here so the first-time download
# still works; subsequent startups use the local cache automatically.
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
