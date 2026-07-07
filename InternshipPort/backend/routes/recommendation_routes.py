import os
from flask import Blueprint
from flask import request
from flask import jsonify
import pandas as pd

from database import mysql
from recommendation import recommend_internships
from collaborative_filtering import get_hybrid_recommendations

recommendation_bp = Blueprint(
    "recommendation",
    __name__
)

# Existing Content-Based Endpoint
@recommendation_bp.route(
    "/recommend",
    methods=["POST"]
)
def recommend():
    data = request.json
    user_skills = data["skills"]

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(BASE_DIR, "datasets", "internships.csv")
    internships_df = pd.read_csv(csv_path)

    recommendations = recommend_internships(
        user_skills,
        internships_df
    )

    return jsonify(
        recommendations.to_dict(
            orient="records"
        )
    )

# New Collaborative Filtering/Hybrid Endpoint (GET)
@recommendation_bp.route(
    "/collaborative/<int:user_id>",
    methods=["GET"]
)
def collaborative_recommendations(user_id):
    try:
        alpha = request.args.get("alpha", 0.5, type=float)
        cursor = mysql.connection.cursor()
        recommendations = get_hybrid_recommendations(user_id, cursor, alpha=alpha)
        cursor.close()
        return jsonify({
            "status": "success",
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Endpoint to record User Interactions (POST)
@recommendation_bp.route(
    "/interaction",
    methods=["POST"]
)
def record_interaction():
    try:
        data = request.json
        user_id = data.get("user_id")
        job_id = data.get("job_id")
        interaction_type = data.get("interaction_type") # 'view', 'bookmark', 'apply'

        if not user_id or not job_id or not interaction_type:
            return jsonify({
                "status": "error",
                "message": "Missing required fields: user_id, job_id, interaction_type"
            }), 400

        # Define rating values
        ratings_map = {
            "view": 1.0,
            "bookmark": 3.0,
            "apply": 5.0
        }
        rating = ratings_map.get(interaction_type.lower(), 1.0)

        cursor = mysql.connection.cursor()

        # Check if interaction already exists
        cursor.execute(
            "SELECT interaction_id, rating FROM user_interactions WHERE user_id = %s AND job_id = %s",
            (user_id, job_id)
        )
        existing = cursor.fetchone()

        if existing:
            # Update only if new rating is higher (e.g. view -> apply)
            existing_id, existing_rating = existing
            if rating > existing_rating:
                cursor.execute(
                    "UPDATE user_interactions SET interaction_type = %s, rating = %s WHERE interaction_id = %s",
                    (interaction_type, rating, existing_id)
                )
        else:
            # Insert new interaction
            cursor.execute(
                "INSERT INTO user_interactions (user_id, job_id, interaction_type, rating) VALUES (%s, %s, %s, %s)",
                (user_id, job_id, interaction_type, rating)
            )

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Interaction recorded successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500