import os
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "internship_db")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT") or "3306")