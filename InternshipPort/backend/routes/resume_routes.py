from flask import Blueprint
from flask import request
from flask import jsonify

import os
import pandas as pd

from database import mysql

from resume_parser import (
    extract_resume_text,
    extract_skills
)

from matcher import match_jobs


resume_bp = Blueprint(
    "resume",
    __name__
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@resume_bp.route(
    "/upload_resume",
    methods=["POST"]
)
def upload_resume():

    if "resume" not in request.files:

        return jsonify({
            "error": "Resume file missing"
        }), 400

    file = request.files["resume"]

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)

    # EXTRACT TEXT

    resume_text = extract_resume_text(
        file_path
    )

    # EXTRACT SKILLS

    extracted_skills = extract_skills(
        resume_text
    )

    # UPDATE USER SKILLS IN MYSQL IF USER_ID IS PASSED
    user_id = request.form.get("user_id")
    if user_id and extracted_skills:
        try:
            update_cursor = mysql.connection.cursor()
            update_cursor.execute(
                "UPDATE users SET skills = %s WHERE user_id = %s",
                (", ".join(extracted_skills), user_id)
            )
            mysql.connection.commit()
            update_cursor.close()
        except Exception as e:
            print("Failed to update user skills in DB:", e)

    # FETCH JOBS FROM MYSQL

    cursor = mysql.connection.cursor()

    query = """
    SELECT job_id, company_name, role, required_skills, location, description, salary
    FROM jobs
    LIMIT 200
    """
    cursor.execute(query)
    jobs = cursor.fetchall()

    columns = [
        "job_id",
        "company_name",
        "role",
        "required_skills",
        "location",
        "description",
        "salary"
    ]

    jobs_df = pd.DataFrame(
        jobs,
        columns=columns
    )

    cursor.close()

    # MATCH JOBS

    recommendations = match_jobs(
        extracted_skills,
        jobs_df
    )

    results = []
    raw_codes = {"eng", "it", "prjm", "mrkt", "sale", "bd", "dsgn", "art", "hcpr", "othr", "mnfc", "acct", "fin", "mgmt", "rsch", "lgl", "edu", "trng", "adm", "ml", "ai"}

    for _, row in recommendations.iterrows():

        req_skills_raw = str(row["required_skills"]).lower()
        req_skills_list = [s.strip() for s in req_skills_raw.split(",") if s.strip()]

        missing_skills = []
        for skill in req_skills_list:
            if skill not in extracted_skills and skill not in raw_codes:
                missing_skills.append(skill.title())

        results.append({

            "job_id":
            int(row["job_id"]),

            "company_name":
            row["company_name"],

            "role":
            row["role"],

            "location":
            row["location"],

            "salary":
            row["salary"],

            "match_percentage":
            round(
                float(
                    row["match_percentage"]
                ),
                2
            ),

            "required_skills":
            row["required_skills"],

            "matched_skills":
            extracted_skills,

            "missing_skills":
            missing_skills
        })

    return jsonify({

        "extracted_skills":
        extracted_skills,

        "recommendations":
        results
    })

