import os
import mysql.connector
import random
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

def seed_database():
    print("Connecting to the database...")
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "internship_db"),
        port=int(os.getenv("MYSQL_PORT") or "3306")
    )
    cursor = db.cursor()

    # Clear previous simulated data
    print("Clearing old simulated users and interactions...")
    cursor.execute("DELETE FROM user_interactions")
    cursor.execute("DELETE FROM users WHERE email LIKE 'simulated_user_%@example.com'")
    db.commit()

    # Define skill groups
    skill_groups = [
        ["IT", "ENG", "PRJM"],       # Tech/Engineering
        ["SALE", "BD", "MRKT"],      # Business/Sales
        ["FIN", "ACCT"],             # Finance
        ["HCPR", "RSCH"],            # Healthcare/Research
        ["DSGN", "ART", "IT"]        # Design/Creative
    ]

    bcrypt_pwd_hash = "$2b$12$R9h/lIPzMRgIm6dBf3gGge1v9UOp6B3C0NqV4B4F2U2f1K.n6sSdq" # hash for password123

    # 1. Insert 50 simulated users
    user_ids = []
    print("Inserting 50 simulated users...")
    for i in range(1, 51):
        group_idx = i % len(skill_groups)
        skills = ", ".join(skill_groups[group_idx])
        full_name = f"Simulated User {i}"
        email = f"simulated_user_{i}@example.com"
        college = "Simulated University"
        year = f"{(i % 4) + 1}rd Year" if (i % 4) == 2 else f"{(i % 4) + 1}th Year" if (i % 4) == 3 else f"{(i % 4) + 1}st Year" if (i % 4) == 0 else f"{(i % 4) + 1}nd Year"

        query = """
        INSERT INTO users (full_name, email, password, college, year, skills)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (full_name, email, bcrypt_pwd_hash, college, year, skills))
        user_ids.append(cursor.lastrowid)

    db.commit()
    print(f"Successfully inserted {len(user_ids)} users.")

    # 2. Fetch a subset of 200 jobs
    print("Fetching 200 jobs for simulation...")
    cursor.execute("SELECT job_id, required_skills FROM jobs WHERE required_skills IS NOT NULL LIMIT 200")
    jobs = cursor.fetchall()
    if not jobs:
        print("Error: No jobs found in the database. Run insert_jobs.py first.")
        return

    print(f"Found {len(jobs)} jobs to simulate interactions with.")

    # 3. Generate interactions
    # Each user group prefers jobs that have skills overlapping with their profile
    interaction_count = 0
    print("Generating simulated user interactions...")
    for idx, user_id in enumerate(user_ids):
        user_num = idx + 1
        group_idx = user_num % len(skill_groups)
        user_skills = skill_groups[group_idx]

        for job_id, req_skills in jobs:
            req_skills_list = [s.strip() for s in req_skills.split(",")]
            # Check overlap
            overlap = any(s in user_skills for s in req_skills_list)

            # Assign probability of interaction based on overlap
            prob = 0.65 if overlap else 0.08

            if random.random() < prob:
                # Decide interaction type and corresponding rating
                rand_val = random.random()
                if rand_val < 0.5:
                    interaction_type = "view"
                    rating = 1.0
                elif rand_val < 0.8:
                    interaction_type = "bookmark"
                    rating = 3.0
                else:
                    interaction_type = "apply"
                    rating = 5.0

                query = """
                INSERT INTO user_interactions (user_id, job_id, interaction_type, rating)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user_id, job_id, interaction_type, rating))
                interaction_count += 1

    db.commit()
    print(f"Seeded {interaction_count} interactions successfully.")

    # Close connections
    cursor.close()
    db.close()
    print("Database seeding finished successfully!")

if __name__ == "__main__":
    seed_database()
