from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

from config import Config
from database import mysql

from routes.auth_routes import auth_bp
from routes.internship_routes import internship_bp
from routes.recommendation_routes import recommendation_bp
from routes.resume_routes import (
    resume_bp
)


app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*"}})

mysql.init_app(app)

@app.route("/envcheck")
def envcheck():
    return {
        "MYSQL_HOST": os.getenv("MYSQL_HOST"),
        "MYSQL_USER": os.getenv("MYSQL_USER"),
        "MYSQL_DB": os.getenv("MYSQL_DB"),
        "MYSQL_PORT": os.getenv("MYSQL_PORT"),
        "CONFIG_HOST": app.config.get("MYSQL_HOST"),
        "CONFIG_USER": app.config.get("MYSQL_USER"),
        "CONFIG_DB": app.config.get("MYSQL_DB")
    }
@app.route("/")
def home():
    return {"message": "Backend running successfully"}

app.register_blueprint(auth_bp)
app.register_blueprint(internship_bp)
app.register_blueprint(recommendation_bp, url_prefix="/recommend")
app.register_blueprint(
    resume_bp
)
if __name__ == '__main__':
    app.run(debug=True)

