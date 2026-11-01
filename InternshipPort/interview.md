# Interview Notes: Recent Recommendation and Resume Changes

This guide covers the current changes to resume matching and SBERT model
initialization in Horizon Next.

## 60-second project explanation

The resume upload endpoint extracts skills from a PDF and immediately matches
them against a bounded set of jobs using SBERT. Job text combines the role,
standardized required skills, and a short description excerpt. The matcher also
uses a domain classification and skill-category overlap to influence ranking.
Separately, both the resume matcher and the recommendation engine now use one
shared SBERT model instance per Python process. If a user ID is supplied, the
extracted skills are saved so the dashboard's collaborative recommendation
endpoint can use the updated profile.

## What changed

- **Shared model lifecycle —** [backend/sbert_singleton.py](./backend/sbert_singleton.py)
  creates the `all-MiniLM-L6-v2` model once when first imported. Both
  [backend/matcher.py](./backend/matcher.py) and
  [backend/recommendation.py](./backend/recommendation.py) import that instance
  instead of independently constructing a model.
- **Resume upload matching —** [backend/routes/resume_routes.py](./backend/routes/resume_routes.py)
  selects up to 300 jobs with non-null required skills, invokes the content
  matcher, and returns the top 10 results with extracted, matched, and missing
  skills. Category shortcodes are omitted from the missing-skills list.
- **PDF errors —** a PDF parsing failure now returns an explicit client error
  response rather than continuing as if parsing succeeded.
- **Recommendation split —** resume upload returns immediate content-based
  matches; the dashboard's `/collaborative/<user_id>` endpoint remains the
  separate path for the full collaborative recommendation flow.

## Interview questions and suggested answers

### Why share the Sentence Transformer instead of creating it in each module?

Creating the model in a shared module avoids duplicate initialization within a
Python process. Both features call `get_sbert_model()` and receive the same
imported instance. This is process-local: separate worker processes each load
their own instance, and startup still requires the model to be available in the
local cache or downloadable.

### How does resume-to-job matching work?

The resume skills are standardized and encoded. For each candidate job, the
matcher builds text from its role, required skills, and up to 300 characters of
description, then encodes that text and computes cosine similarity. A domain
classifier narrows candidates when it identifies a marketing or software
profile. Category-code overlap then affects the similarity score before the
results are sorted and limited to ten.

### Why does the API query at most 300 jobs?

It bounds the candidate set that must be encoded and scored during an upload
request, while excluding records without required skills. This is a practical
latency trade-off, not a guarantee that the globally best job in the complete
dataset is included. A scalable next step would be database-backed filtering
and/or precomputed job embeddings.

### What does the upload endpoint return, and what happens on a PDF error?

On success it returns extracted skills and recommendation records containing
job metadata, a match percentage, required skills, matched skills, and missing
skills. A parsing failure returns HTTP 400 with a readable error message.
When a user ID and extracted skills are present, those skills are also saved
for the dashboard recommendation flow.

### How would you test this behavior?

Test a successful upload with a valid PDF and verify response fields and the
top-10 limit; test an unreadable PDF and verify the 400 response; verify that
the database query excludes null required skills and respects its 300-row
limit; and mock the encoder to check that matcher and recommendation code use
the shared model. Tests should avoid downloading the model or requiring a live
database.

## Trade-offs to discuss honestly

- The 300-job candidate limit bounds request-time work but can exclude relevant
  jobs outside the queried set.
- The model is shared within a process, not across multiple server workers.
- The match percentage is a transformed similarity score for product display;
  it should not be described as a calibrated probability that a candidate will
  be hired.
- Domain classification and category overlap are heuristic ranking signals,
  not a substitute for measuring recommendation quality on representative
  held-out data.
