import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DB", "internship_db"),
    port=int(os.getenv("MYSQL_PORT") or "3306")
)

cursor = db.cursor()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
jobs_path = os.path.join(BASE_DIR, "datasets", "final_jobs.csv")
jobs = pd.read_csv(jobs_path)
jobs = jobs.where(pd.notnull(jobs), None)

def clean_val(v):
    if pd.isna(v):
        return None
    return v

for _, row in jobs.iterrows():

    query = """
    INSERT INTO jobs(
        company_name,
        role,
        required_skills,
        location,
        salary,
        description
    )
    VALUES(%s, %s, %s, %s, %s, %s)
    """

    values = (
        1,
        clean_val(row["role"]),
        clean_val(row["required_skills"]),
        clean_val(row["location"]),
        "Not Specified",
        clean_val(row["description_y"])
    )

    cursor.execute(query, values)

db.commit()

cursor.close()

db.close()

print("Jobs inserted successfully")