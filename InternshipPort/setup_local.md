# Local Setup Guide - AI Internship Recommendation System

This guide outlines instructions to set up and run the Internship Recommendation System on a local Windows machine.

---

## 📌 Prerequisites

Ensure you have the following installed on your system:
1. **Python 3.10+**: Make sure to check the box "Add Python to PATH" during installation.
2. **Node.js (v18+)**: Includes `npm`.
3. **MySQL Server**: (e.g., MySQL Community Server or via XAMPP/WampServer).

---

## 🛠️ Database Setup (MySQL)

1. **Log in to MySQL** via Command Prompt or MySQL Workbench:
   ```bash
   mysql -u root -p
   ```

2. **Run the Initialization Script**:
   Import the schema using the provided `schema.sql` file located in the `backend/` directory:
   ```sql
   SOURCE backend/schema.sql;
   ```
   *Alternatively, copy the SQL statements in `backend/schema.sql` and run them in MySQL Workbench.*

   This will create a database named `internship_db` and all required tables: `users`, `jobs`, and `user_interactions`.

---

## 🐍 Backend Configuration & Startup

1. **Navigate to the Backend Directory**:
   ```bash
   cd backend
   ```

2. **Configure Environment Variables**:
   Copy the example environment configuration to create a `.env` file:
   ```bash
   copy .env.example .env
   ```
   Open the `.env` file and update database credentials:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=internship_db
   ```

3. **Set Up the Virtual Environment**:
   If not already active, activate the virtual environment:
   ```bash
   # From project root (InternshipPort)
   venv\Scripts\activate
   ```

4. **Install Python Packages**:
   Install all dependencies (including `spacy` model and `python-dotenv`):
   ```bash
   pip install -r requirements.txt
   ```

5. **Populate and Seed the Database**:
   Since the database is currently empty, you must import the jobs dataset and seed mock interactions:
   *Note: Ensure `backend/datasets/final_jobs.csv` is present before running `insert_jobs.py`.*
   ```bash
   # Insert Jobs Dataset
   python insert_jobs.py

   # Seed Interactions & Simulated Users
   python seed_interactions.py
   ```

6. **Start the Flask Server**:
   ```bash
   python app.py
   ```
   The backend will start running locally at: **`http://localhost:5000`**

---

## ⚛️ Frontend Setup & Startup

1. **Navigate to the Frontend Directory**:
   Open a new terminal window and type:
   ```bash
   cd jobnext
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Start Vite Development Server**:
   ```bash
   npm run dev
   ```
   The frontend will start running locally at: **`http://localhost:5173`**

---

## 🧪 Local Testing & Verification

1. **Environment Check**:
   Visit `http://localhost:5000/envcheck` to verify that Flask loaded all database settings from the `.env` file correctly.
2. **Database Verification**:
   Verify user registration and logins via the UI.
3. **Resume Parsing & NLP**:
   Upload a PDF resume. The system should automatically extract skills (using `spaCy` model) and display semantic job matches (using `Sentence-BERT`).
