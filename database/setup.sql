-- Online Job Portal - Database Setup Script
-- Use this file to initialize the database for GitHub deployment

CREATE DATABASE IF NOT EXISTS jobportal3;
USE jobportal3;

-- --------------------------------------------------------
-- 1. Table: jobseeker
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `jobseeker` (
  `jobseeker_id` INT AUTO_INCREMENT PRIMARY KEY,
  `first_name` VARCHAR(100) NOT NULL,
  `last_name` VARCHAR(100),
  `phone_number` VARCHAR(20),
  `address` VARCHAR(255),
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. Table: company
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `company` (
  `company_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(200) NOT NULL,
  `location` VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 3. Table: job
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `job` (
  `job_id` INT AUTO_INCREMENT PRIMARY KEY,
  `company_id` INT NOT NULL,
  `job_title` VARCHAR(200) NOT NULL,
  `job_type` VARCHAR(100),
  `job_salary` VARCHAR(100),
  `job_description` TEXT,
  CONSTRAINT fk_job_company FOREIGN KEY (`company_id`) REFERENCES `company`(`company_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 4. Table: profile
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `profile` (
  `profile_id` INT AUTO_INCREMENT PRIMARY KEY,
  `jobseeker_id` INT NOT NULL,
  `college` VARCHAR(255),
  `department` VARCHAR(255),
  `education` TEXT,
  CONSTRAINT fk_profile_jobseeker FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker`(`jobseeker_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 5. Table: resume
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `resume` (
  `resume_id` INT AUTO_INCREMENT PRIMARY KEY,
  `jobseeker_id` INT NOT NULL,
  `filename` VARCHAR(255) NOT NULL,
  CONSTRAINT fk_resume_jobseeker FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker`(`jobseeker_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 6. Table: apply
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `apply` (
  `jobseeker_id` INT NOT NULL,
  `job_id` INT NOT NULL,
  `apply_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`jobseeker_id`, `job_id`),
  CONSTRAINT fk_apply_jobseeker FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker`(`jobseeker_id`) ON DELETE CASCADE,
  CONSTRAINT fk_apply_job FOREIGN KEY (`job_id`) REFERENCES `job`(`job_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 7. Table: interview
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `interview` (
  `interview_id` INT AUTO_INCREMENT PRIMARY KEY,
  `jobseeker_id` INT NOT NULL,
  `job_id` INT NOT NULL,
  `date` DATE,
  `time` TIME,
  CONSTRAINT fk_interview_jobseeker FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker`(`jobseeker_id`) ON DELETE CASCADE,
  CONSTRAINT fk_interview_job FOREIGN KEY (`job_id`) REFERENCES `job`(`job_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 8. Table: result
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `result` (
  `result_id` INT AUTO_INCREMENT PRIMARY KEY,
  `jobseeker_id` INT NOT NULL,
  `job_id` INT NOT NULL,
  `status` VARCHAR(100),
  CONSTRAINT fk_result_jobseeker FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker`(`jobseeker_id`) ON DELETE CASCADE,
  CONSTRAINT fk_result_job FOREIGN KEY (`job_id`) REFERENCES `job`(`job_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- SAMPLE DATA (FROM SCREENSHOTS)
-- --------------------------------------------------------
INSERT INTO company (name, location) VALUES 
('Samsung', 'Bangalore'),
('Citibank', 'Pune');

INSERT INTO job (company_id, job_title, job_type, job_salary, job_description) VALUES 
(1, 'Student Trainee', 'Software R&D', 'Rs. 50,000 per Month', 'The selected candidate(s) would be primarily working on Software R&D projects...'),
(2, 'Summer Analyst', 'Engineering Intern', 'Rs. 40,000 per Month', 'The interns would be interning for 2-3 months as part of the summer internship program...');

INSERT INTO jobseeker (first_name, last_name, email, password) VALUES 
('Rishabh', 'Agarwal', 'rishabh@mail.com', '12345');
