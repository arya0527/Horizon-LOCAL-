import os
import pandas as pd

postings = pd.read_csv(
    r"C:\Users\Arya\Downloads\archive (8)\postings.csv"
)

companies = pd.read_csv(
    r"C:\Users\Arya\Downloads\archive (8)\companies\companies.csv"
)

skills = pd.read_csv(
    r"C:\Users\Arya\Downloads\archive (8)\jobs\job_skills.csv"
)

postings = postings[
    [
        "job_id",
        "company_id",
        "title",
        "description",
        "location"
    ]
]

skills_grouped = skills.groupby(
    "job_id"
)["skill_abr"].apply(
    lambda x: ", ".join(x)
).reset_index()

jobs = postings.merge(
    skills_grouped,
    on="job_id",
    how="left"
)

jobs = jobs.merge(
    companies,
    on="company_id",
    how="left"
)

jobs.rename(columns={
    "title": "role",
    "name": "company_name",
    "skill_abr": "required_skills"
}, inplace=True)

jobs = jobs.dropna(
    subset=[
        "role",
        "required_skills"
    ]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(BASE_DIR, "datasets", "final_jobs.csv")
jobs.to_csv(
    output_path,
    index=False
)
