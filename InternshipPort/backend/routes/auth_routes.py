from flask import Blueprint
from flask import request
from flask import jsonify

from database import mysql

import bcrypt


auth_bp = Blueprint(
    "auth",
    __name__
)


# REGISTER

@auth_bp.route(
    "/register",
    methods=["POST"]
)
def register():

    try:

        data = request.json

        name = data["name"]
        email = data["email"]
        password = data["password"]
        college = data["college"]
        year = data["year"]

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor = mysql.connection.cursor()

        # CHECK IF USER EXISTS

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()

            return jsonify({
                "message": "Email already registered"
            }), 400

        query = """
        INSERT INTO users(
            full_name,
            email,
            password,
            college,
            year
        )
        VALUES(%s,%s,%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                name,
                email,
                hashed_password.decode("utf-8"),
                college,
                year
            )
        )

        mysql.connection.commit()

        cursor.close()

        return jsonify({
            "message": "User registered successfully"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# LOGIN

@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    try:

        data = request.json

        email = data["email"]
        password = data["password"]

        cursor = mysql.connection.cursor()

        query = """
        SELECT *
        FROM users
        WHERE email=%s
        """

        cursor.execute(
            query,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        if not user:

            return jsonify({
                "message": "User not found"
            }), 404

        stored_password = user[3]

        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password.encode("utf-8")
        ):

            return jsonify({

                "message":
                "Login successful",

                "user": {

                    "user_id":
                    user[0],

                    "name":
                    user[1],

                    "email":
                    user[2],

                    "college":
                    user[4],

                    "year":
                    user[5]
                }
            })

        return jsonify({
            "message": "Invalid credentials"
        }), 401

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

