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

# Category shortcodes that should not appear in missing_skills output.
# Sourced from the same ontology used in recommendation.py / collaborative_filtering.py.
_RAW_CODES = {
    "eng", "it", "prjm", "mrkt", "sale", "bd", "dsgn", "art",
    "hcpr", "othr", "mnfc", "acct", "fin", "mgmt", "rsch", "lgl",
    "edu", "trng", "adm", "ml", "ai"
}


def _build_results(records, extracted_skills):
    """
    Convert a list of job dicts (from either match_jobs or
    get_collaborative_recommendations) into the standard
    /upload_resume response format.

    Works with both DataFrame rows (via iterrows) and plain dicts.
    """
    results = []

    for rec in records:

        req_skills_raw = str(rec.get("required_skills", "")).lower()
        req_skills_list = [
            s.strip()
            for s in req_skills_raw.split(",")
            if s.strip()
        ]

        missing_skills = [
            skill.title()
            for skill in req_skills_list
            if skill not in extracted_skills
            and skill not in _RAW_CODES
        ]

        results.append({
            "job_id":           int(rec["job_id"]),
            "company_name":     rec["company_name"],
            "role":             rec["role"],
            "location":         rec["location"],
            "salary":           rec["salary"],
            "match_percentage": round(float(rec["match_percentage"]), 2),
            "required_skills":  rec["required_skills"],
            "matched_skills":   extracted_skills,
            "missing_skills":   missing_skills,
        })

    return results


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

    try:
        resume_text = extract_resume_text(file_path)
    except Exception as e:
        print("Failed to read resume PDF:", e)
        return jsonify({
            "error": "Could not read the PDF. The file may be corrupted or incomplete. Please try uploading again."
        }), 400

    # EXTRACT SKILLS

    extracted_skills = extract_skills(resume_text)

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

    # GET RECOMMENDATIONS
    #
    # Always use match_jobs() here for a fast, immediate response.
    # The full recommendation engine (SBERT over all jobs + SVD collaborative
    # filtering) runs on the dashboard via GET /collaborative/<user_id>.
    # Skills saved above ensure that endpoint benefits from this upload.

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT job_id, company_name, role, required_skills,
               location, description, salary
        FROM jobs
        WHERE required_skills IS NOT NULL
        LIMIT 300
    """)
    jobs = cursor.fetchall()
    cursor.close()

    jobs_df = pd.DataFrame(jobs, columns=[
        "job_id", "company_name", "role", "required_skills",
        "location", "description", "salary"
    ])

    matched_df = match_jobs(extracted_skills, jobs_df)

    results = _build_results(
        [row.to_dict() for _, row in matched_df.iterrows()],
        extracted_skills
    )

    return jsonify({
        "extracted_skills":  extracted_skills,
        "recommendations":   results
    })

