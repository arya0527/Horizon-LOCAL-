-- Database Initialization Script

CREATE DATABASE IF NOT EXISTS internship_db;
USE internship_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    college VARCHAR(255) NULL,
    year VARCHAR(50) NULL,
    skills TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NULL,
    role VARCHAR(255) NOT NULL,
    required_skills TEXT NOT NULL,
    location VARCHAR(255) NULL,
    salary VARCHAR(255) DEFAULT 'Not Specified',
    description TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. User Interactions Table (for Collaborative Filtering)
CREATE TABLE IF NOT EXISTS user_interactions (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- 'view', 'bookmark', 'apply'
    rating DECIMAL(3, 1) NOT NULL,         -- 1.0, 3.0, 5.0
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
