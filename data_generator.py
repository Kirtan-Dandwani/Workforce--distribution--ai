import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from config import JOB_ROLES, SKILL_CATEGORIES, SALARY_RANGES
import os

def generate_employee_data(n_employees=1000):
    """Generate synthetic employee data for training"""
    
    np.random.seed(42)
    random.seed(42)
    
    employees = []
    
    # Flatten skills from all categories
    all_skills = []
    for category, skills in SKILL_CATEGORIES.items():
        all_skills.extend(skills)
    
    for i in range(n_employees):
        # Basic demographics
        age = np.random.normal(32, 8)
        age = max(22, min(60, int(age)))
        
        joining_year = np.random.randint(2015, 2024)
        experience = max(0, age - 22 - (2023 - joining_year))
        experience = min(experience, 25)
        
        # Role and department
        role = random.choice(JOB_ROLES)
        department = random.choice(["Engineering", "Data Science", "Product", "Design", "Operations"])
        
        # Education
        education_level = random.choices(
            ["High School", "Bachelors", "Masters", "PhD"],
            weights=[10, 50, 30, 10]
        )[0]
        
        # Salary based on role, experience, and education
        base_salary_min, base_salary_max = SALARY_RANGES[role]
        
        # Adjust for experience
        exp_multiplier = 1 + (experience * 0.05)
        
        # Adjust for education
        edu_multipliers = {"High School": 0.8, "Bachelors": 1.0, "Masters": 1.2, "PhD": 1.4}
        edu_multiplier = edu_multipliers[education_level]
        
        current_salary = np.random.uniform(
            base_salary_min * exp_multiplier * edu_multiplier,
            base_salary_max * exp_multiplier * edu_multiplier
        ) * 1000
        
        # Expected salary (usually 5-15% increase)
        salary_growth_rate = np.random.uniform(0.05, 0.15)
        expected_salary = current_salary * (1 + salary_growth_rate)
        
        # Payment tier based on salary
        if current_salary < 60000:
            payment_tier = 1
        elif current_salary < 100000:
            payment_tier = 2
        else:
            payment_tier = 3
        
        # Performance rating (affects retention)
        performance_rating = np.random.normal(7.5, 1.5)
        performance_rating = max(1, min(10, performance_rating))
        
        # Will leave prediction (based on multiple factors)
        leave_probability = 0.2  # Base probability
        
        # Factors that increase leave probability
        if performance_rating < 6:
            leave_probability += 0.3
        if salary_growth_rate < 0.08:
            leave_probability += 0.2
        if experience > 8 and payment_tier == 1:
            leave_probability += 0.25
        if age > 45:
            leave_probability += 0.15
        
        # Factors that decrease leave probability
        if performance_rating > 8:
            leave_probability -= 0.2
        if salary_growth_rate > 0.12:
            leave_probability -= 0.15
        if payment_tier == 3:
            leave_probability -= 0.1
        
        will_leave = random.random() < max(0.05, min(0.8, leave_probability))
        
        # Skills (random selection based on role)
        role_relevant_skills = []
        if "Engineer" in role or "Developer" in role:
            role_relevant_skills.extend(SKILL_CATEGORIES["Technical"][:8])
        if "Data" in role or "ML" in role:
            role_relevant_skills.extend(SKILL_CATEGORIES["Analytical"])
        if "Manager" in role or "Lead" in role:
            role_relevant_skills.extend(SKILL_CATEGORIES["Management"])
        if "Designer" in role:
            role_relevant_skills.extend(SKILL_CATEGORIES["Design"])
        
        # Add some random skills
        role_relevant_skills.extend(random.sample(all_skills, 3))
        role_relevant_skills = list(set(role_relevant_skills))
        
        employee = {
            "id": i + 1,
            "name": f"Employee_{i+1}",
            "email": f"employee{i+1}@company.com",
            "age": age,
            "joining_year": joining_year,
            "payment_tier": payment_tier,
            "experience_in_domain": experience,
            "current_salary": round(current_salary, 2),
            "expected_salary": round(expected_salary, 2),
            "education_level": education_level,
            "current_role": role,
            "department": department,
            "location": random.choice(["New York", "San Francisco", "Austin", "Seattle", "Remote"]),
            "performance_rating": round(performance_rating, 2),
            "will_leave": will_leave,
            "skills": ",".join(random.sample(role_relevant_skills, min(len(role_relevant_skills), 8)))
        }
        
        employees.append(employee)
    
    return pd.DataFrame(employees)

def generate_skills_data():
    """Generate skills master data"""
    skills_data = []
    skill_id = 1
    
    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            # Weight based on category
            category_weights = {
                "Technical": np.random.uniform(1.2, 1.8),
                "Analytical": np.random.uniform(1.3, 1.9),
                "Management": np.random.uniform(1.0, 1.5),
                "Design": np.random.uniform(1.1, 1.6)
            }
            
            skills_data.append({
                "id": skill_id,
                "name": skill,
                "category": category,
                "description": f"Proficiency in {skill}",
                "weight": round(category_weights[category], 2)
            })
            skill_id += 1
    
    return pd.DataFrame(skills_data)

def generate_job_roles_data():
    """Generate job roles data"""
    roles_data = []
    
    for i, role in enumerate(JOB_ROLES):
        min_sal, max_sal = SALARY_RANGES[role]
        
        # Required skills based on role
        required_skills = []
        preferred_skills = []
        
        if "Engineer" in role or "Developer" in role:
            required_skills = ["Python", "JavaScript", "SQL"]
            preferred_skills = ["React", "Node.js", "Docker"]
        elif "Data" in role:
            required_skills = ["Python", "SQL", "Machine Learning", "Statistics"]
            preferred_skills = ["Deep Learning", "Tableau", "AWS"]
        elif "Manager" in role:
            required_skills = ["Project Management", "Team Leadership", "Communication"]
            preferred_skills = ["Agile", "Strategic Planning"]
        elif "Designer" in role:
            required_skills = ["UI Design", "Figma", "Prototyping"]
            preferred_skills = ["UX Research", "User Testing"]
        
        roles_data.append({
            "id": i + 1,
            "title": role,
            "description": f"Role description for {role}",
            "department": random.choice(["Engineering", "Data Science", "Product", "Design", "Operations"]),
            "min_salary": min_sal * 1000,
            "max_salary": max_sal * 1000,
            "min_experience": random.randint(0, 5),
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "is_active": True
        })
    
    return pd.DataFrame(roles_data)

if __name__ == "__main__":
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Generate datasets
    print("Generating employee data...")
    employees_df = generate_employee_data(1000)
    employees_df.to_csv("data/employees.csv", index=False)
    
    print("Generating skills data...")
    skills_df = generate_skills_data()
    skills_df.to_csv("data/skills.csv", index=False)
    
    print("Generating job roles data...")
    roles_df = generate_job_roles_data()
    roles_df.to_csv("data/job_roles.csv", index=False)
    
    # Create training data for ML models
    print("Creating training data...")
    training_data = employees_df.copy()
    
    # Add derived features
    training_data["annual_growth"] = training_data["expected_salary"] - training_data["current_salary"]
    training_data["salary_growth_rate"] = training_data["annual_growth"] / training_data["current_salary"]
    training_data["tenure"] = 2023 - training_data["joining_year"]
    
    # Education encoding
    education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    training_data["education_encoded"] = training_data["education_level"].map(education_map)
    
    training_data.to_csv("data/training_data.csv", index=False)
    
    print("Data generation completed!")
    print(f"Generated {len(employees_df)} employee records")
    print(f"Generated {len(skills_df)} skills")
    print(f"Generated {len(roles_df)} job roles")