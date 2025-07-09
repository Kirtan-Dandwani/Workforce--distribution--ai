import os
from pathlib import Path

# Database Configuration
DATABASE_URL = "sqlite:///./workforce_ai.db"
DATABASE_PATH = Path("workforce_ai.db")

# Model Paths
MODEL_DIR = Path("models")
MODEL_PATHS = {
    "retention": MODEL_DIR / "retention_model.pkl",
    "salary": MODEL_DIR / "salary_model.pkl", 
    "role": MODEL_DIR / "role_model.pkl",
    "skill_rating": MODEL_DIR / "skill_rating_model.pkl",
    "encoders": MODEL_DIR / "encoders.pkl",
    "scalers": MODEL_DIR / "scalers.pkl"
}

# Data Paths
DATA_DIR = Path("data")
DATA_PATHS = {
    "employees": DATA_DIR / "employees.csv",
    "job_roles": DATA_DIR / "job_roles.csv",
    "skills": DATA_DIR / "skills.csv",
    "training": DATA_DIR / "training_data.csv"
}

# Job Roles and Skills Configuration
JOB_ROLES = [
    "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer",
    "UI/UX Designer", "QA Engineer", "Business Analyst", "Technical Lead",
    "System Administrator", "Frontend Developer", "Backend Developer",
    "Machine Learning Engineer", "Cybersecurity Analyst", "Database Administrator"
]

SKILL_CATEGORIES = {
    "Technical": ["Python", "JavaScript", "Java", "C++", "SQL", "MongoDB", "React", "Angular", "Node.js", "Docker", "Kubernetes", "AWS", "Azure", "GCP"],
    "Analytical": ["Data Analysis", "Statistics", "Machine Learning", "Deep Learning", "Business Intelligence", "Excel", "Tableau", "Power BI"],
    "Management": ["Project Management", "Team Leadership", "Agile", "Scrum", "Communication", "Strategic Planning"],
    "Design": ["UI Design", "UX Research", "Figma", "Adobe Creative Suite", "Prototyping", "User Testing"]
}

# Salary Ranges by Role (in thousands)
SALARY_RANGES = {
    "Software Engineer": (50, 120),
    "Data Scientist": (70, 150),
    "Product Manager": (80, 160),
    "DevOps Engineer": (60, 130),
    "UI/UX Designer": (45, 100),
    "QA Engineer": (40, 90),
    "Business Analyst": (50, 110),
    "Technical Lead": (90, 180),
    "System Administrator": (45, 95),
    "Frontend Developer": (45, 105),
    "Backend Developer": (55, 125),
    "Machine Learning Engineer": (80, 170),
    "Cybersecurity Analyst": (65, 140),
    "Database Administrator": (55, 115)
}