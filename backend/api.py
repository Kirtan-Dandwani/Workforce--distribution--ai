from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
import json

from database.database import get_db, init_database
from database.models import Employee, JobRole, Skill, EmployeeSkill, JobRecommendation
from ml_models.model_trainer import ModelPredictor
from config import JOB_ROLES, SKILL_CATEGORIES, SALARY_RANGES

app = FastAPI(title="Workforce Distribution AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML predictor
try:
    predictor = ModelPredictor()
except Exception as e:
    print(f"Warning: Could not load ML models: {e}")
    predictor = None

# Pydantic models
class EmployeeCreate(BaseModel):
    name: str
    email: str
    age: int
    joining_year: int
    payment_tier: int
    experience_in_domain: int
    current_salary: float
    expected_salary: float
    education_level: str
    current_role: str
    department: str
    location: str
    performance_rating: float

class EmployeePrediction(BaseModel):
    age: int
    joining_year: int
    payment_tier: int
    experience_in_domain: int
    current_salary: float
    expected_salary: float
    education_level: str
    performance_rating: float

class SkillRating(BaseModel):
    employee_id: int
    skill_name: str
    proficiency_level: float
    years_experience: float

class JobRecommendationResponse(BaseModel):
    job_title: str
    match_score: float
    salary_estimate: float
    required_skills: List[str]
    missing_skills: List[str]
    recommendation_reason: str

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

@app.get("/")
async def root():
    return {"message": "Workforce Distribution AI API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Employee endpoints
@app.post("/employees/", response_model=dict)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return {"id": db_employee.id, "message": "Employee created successfully"}

@app.get("/employees/")
async def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of employees"""
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Get employee by ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# Prediction endpoints
@app.post("/predict/retention")
async def predict_retention(employee_data: EmployeePrediction):
    """Predict employee retention"""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    # Convert to dict and add derived features
    data = employee_data.dict()
    
    # Add education encoding
    education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    data['education_encoded'] = education_map.get(data['education_level'], 1)
    
    # Add derived features
    data['annual_growth'] = data['expected_salary'] - data['current_salary']
    data['salary_growth_rate'] = data['annual_growth'] / data['current_salary']
    data['tenure'] = 2023 - data['joining_year']
    
    try:
        result = predictor.predict_retention(data)
        return {
            "will_leave": result['will_leave'],
            "leave_probability": round(result['leave_probability'], 3),
            "stay_probability": round(result['stay_probability'], 3),
            "risk_level": "High" if result['leave_probability'] > 0.7 else "Medium" if result['leave_probability'] > 0.4 else "Low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/salary")
async def predict_salary(employee_data: EmployeePrediction):
    """Predict employee salary"""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    data = employee_data.dict()
    education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    data['education_encoded'] = education_map.get(data['education_level'], 1)
    data['annual_growth'] = data['expected_salary'] - data['current_salary']
    data['salary_growth_rate'] = data['annual_growth'] / data['current_salary']
    data['tenure'] = 2023 - data['joining_year']
    
    try:
        predicted_salary = predictor.predict_salary(data)
        growth_amount = predicted_salary - data['current_salary']
        growth_percentage = (growth_amount / data['current_salary']) * 100
        
        return {
            "predicted_salary": round(predicted_salary, 2),
            "current_salary": data['current_salary'],
            "growth_amount": round(growth_amount, 2),
            "growth_percentage": round(growth_percentage, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/role")
async def predict_role(employee_data: EmployeePrediction):
    """Predict best job role for employee"""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    data = employee_data.dict()
    education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    data['education_encoded'] = education_map.get(data['education_level'], 1)
    data['annual_growth'] = data['expected_salary'] - data['current_salary']
    data['salary_growth_rate'] = data['annual_growth'] / data['current_salary']
    data['tenure'] = 2023 - data['joining_year']
    
    try:
        result = predictor.predict_role(data)
        role_name = result['role']
        confidence = result['confidence']
        
        # Get salary range for this role
        salary_range = SALARY_RANGES.get(role_name, (50, 100))
        
        return {
            "recommended_role": role_name,
            "confidence": round(confidence, 3),
            "salary_range": {
                "min": salary_range[0] * 1000,
                "max": salary_range[1] * 1000
            },
            "confidence_level": "High" if confidence > 0.8 else "Medium" if confidence > 0.6 else "Low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/skill-rating")
async def predict_skill_rating(employee_data: EmployeePrediction):
    """Predict skill rating for employee"""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    data = employee_data.dict()
    education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    data['education_encoded'] = education_map.get(data['education_level'], 1)
    
    try:
        skill_rating = predictor.predict_skill_rating(data)
        
        # Categorize rating
        if skill_rating >= 8:
            category = "Expert"
        elif skill_rating >= 6:
            category = "Proficient"
        elif skill_rating >= 4:
            category = "Intermediate"
        else:
            category = "Beginner"
        
        return {
            "overall_skill_rating": skill_rating,
            "skill_category": category,
            "rating_scale": "1-10 scale",
            "description": f"Employee shows {category.lower()} level skills based on experience and performance"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Job recommendations
@app.get("/job-roles/")
async def get_job_roles():
    """Get all available job roles"""
    roles_data = []
    for role in JOB_ROLES:
        salary_range = SALARY_RANGES.get(role, (50, 100))
        roles_data.append({
            "title": role,
            "min_salary": salary_range[0] * 1000,
            "max_salary": salary_range[1] * 1000,
            "category": _get_role_category(role)
        })
    return roles_data

@app.post("/recommend-jobs")
async def recommend_jobs(employee_data: EmployeePrediction, top_n: int = 5):
    """Get job recommendations for employee"""
    data = employee_data.dict()
    education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    data['education_encoded'] = education_map.get(data['education_level'], 1)
    
    recommendations = []
    
    for role in JOB_ROLES:
        match_score = _calculate_match_score(data, role)
        salary_estimate = _estimate_salary_for_role(data, role)
        
        recommendations.append({
            "job_title": role,
            "match_score": match_score,
            "salary_estimate": salary_estimate,
            "required_skills": _get_required_skills(role),
            "missing_skills": _get_missing_skills(data, role),
            "recommendation_reason": _get_recommendation_reason(data, role, match_score)
        })
    
    # Sort by match score and return top N
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    return recommendations[:top_n]

@app.get("/skills/")
async def get_skills():
    """Get all available skills"""
    skills_data = []
    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            skills_data.append({
                "name": skill,
                "category": category
            })
    return skills_data

@app.get("/analytics/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get analytics data for dashboard"""
    total_employees = db.query(Employee).count()
    
    # Role distribution
    role_query = db.query(Employee.current_role).all()
    role_distribution = {}
    for role in role_query:
        role_name = role[0] if role[0] else "Unknown"
        role_distribution[role_name] = role_distribution.get(role_name, 0) + 1
    
    # Average salary by role
    salary_query = db.query(Employee.current_role, Employee.current_salary).all()
    salary_by_role = {}
    for role, salary in salary_query:
        if role and salary:
            if role not in salary_by_role:
                salary_by_role[role] = []
            salary_by_role[role].append(salary)
    
    avg_salary_by_role = {
        role: sum(salaries) / len(salaries) 
        for role, salaries in salary_by_role.items()
    }
    
    return {
        "total_employees": total_employees,
        "role_distribution": role_distribution,
        "average_salary_by_role": avg_salary_by_role,
        "available_roles": len(JOB_ROLES),
        "skill_categories": len(SKILL_CATEGORIES)
    }

# Helper functions
def _get_role_category(role: str) -> str:
    """Categorize job role"""
    if "Engineer" in role or "Developer" in role:
        return "Engineering"
    elif "Data" in role or "ML" in role:
        return "Data Science"
    elif "Manager" in role or "Lead" in role:
        return "Management"
    elif "Designer" in role:
        return "Design"
    else:
        return "Other"

def _calculate_match_score(employee_data: dict, role: str) -> float:
    """Calculate job match score based on employee data"""
    score = 0.0
    
    # Experience factor
    experience = employee_data.get('experience_in_domain', 0)
    if experience >= 5:
        score += 30
    elif experience >= 2:
        score += 20
    else:
        score += 10
    
    # Education factor
    education_bonus = {0: 5, 1: 15, 2: 25, 3: 30}  # High School to PhD
    score += education_bonus.get(employee_data.get('education_encoded', 1), 15)
    
    # Performance factor
    performance = employee_data.get('performance_rating', 5)
    score += (performance / 10) * 25
    
    # Salary expectations alignment
    current_salary = employee_data.get('current_salary', 50000)
    role_salary_range = SALARY_RANGES.get(role, (50, 100))
    role_avg_salary = (role_salary_range[0] + role_salary_range[1]) / 2 * 1000
    
    salary_alignment = 1 - abs(current_salary - role_avg_salary) / role_avg_salary
    score += max(0, salary_alignment * 20)
    
    return min(100, max(0, score))

def _estimate_salary_for_role(employee_data: dict, role: str) -> float:
    """Estimate salary for role based on employee data"""
    base_salary_range = SALARY_RANGES.get(role, (50, 100))
    base_salary = (base_salary_range[0] + base_salary_range[1]) / 2 * 1000
    
    # Adjust for experience
    experience = employee_data.get('experience_in_domain', 0)
    exp_multiplier = 1 + (experience * 0.03)
    
    # Adjust for education
    edu_multipliers = {0: 0.85, 1: 1.0, 2: 1.15, 3: 1.3}
    edu_multiplier = edu_multipliers.get(employee_data.get('education_encoded', 1), 1.0)
    
    # Adjust for performance
    performance = employee_data.get('performance_rating', 7)
    perf_multiplier = 0.8 + (performance / 10) * 0.4
    
    estimated_salary = base_salary * exp_multiplier * edu_multiplier * perf_multiplier
    return round(estimated_salary, 2)

def _get_required_skills(role: str) -> List[str]:
    """Get required skills for a role"""
    skill_mapping = {
        "Software Engineer": ["Python", "JavaScript", "SQL", "Git"],
        "Data Scientist": ["Python", "Statistics", "Machine Learning", "SQL"],
        "Product Manager": ["Project Management", "Communication", "Strategic Planning"],
        "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Linux"],
        "UI/UX Designer": ["UI Design", "Figma", "Prototyping", "User Testing"]
    }
    
    return skill_mapping.get(role, ["Communication", "Problem Solving"])

def _get_missing_skills(employee_data: dict, role: str) -> List[str]:
    """Get skills missing for a role (simplified logic)"""
    required_skills = _get_required_skills(role)
    # In a real scenario, you'd check against employee's actual skills
    # For now, return a subset as "missing"
    return required_skills[:2] if len(required_skills) > 2 else []

def _get_recommendation_reason(employee_data: dict, role: str, match_score: float) -> str:
    """Generate recommendation reason"""
    experience = employee_data.get('experience_in_domain', 0)
    performance = employee_data.get('performance_rating', 5)
    
    if match_score >= 80:
        return f"Excellent match! Your {experience} years of experience and {performance}/10 performance rating make you ideal for this role."
    elif match_score >= 60:
        return f"Good match. With {experience} years of experience, you meet most requirements for this role."
    else:
        return f"Potential growth opportunity. Consider developing skills in this area to improve your match score."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)