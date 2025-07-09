from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    age = Column(Integer)
    joining_year = Column(Integer)
    payment_tier = Column(Integer)
    experience_in_domain = Column(Integer)
    current_salary = Column(Float)
    expected_salary = Column(Float)
    education_level = Column(String(50))
    current_role = Column(String(100))
    department = Column(String(100))
    location = Column(String(100))
    performance_rating = Column(Float)
    will_leave = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = relationship("EmployeeSkill", back_populates="employee")
    assessments = relationship("SkillAssessment", back_populates="employee")

class JobRole(Base):
    __tablename__ = "job_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    department = Column(String(100))
    min_salary = Column(Float)
    max_salary = Column(Float)
    min_experience = Column(Integer)
    required_skills = Column(JSON)  # List of skill IDs
    preferred_skills = Column(JSON)  # List of skill IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))  # Technical, Analytical, Management, Design
    description = Column(Text)
    weight = Column(Float, default=1.0)  # Importance weight for scoring
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_skills = relationship("EmployeeSkill", back_populates="skill")
    assessments = relationship("SkillAssessment", back_populates="skill")

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    proficiency_level = Column(Float)  # 1-10 scale
    years_experience = Column(Float)
    self_rating = Column(Float)  # 1-10 scale
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

class SkillAssessment(Base):
    __tablename__ = "skill_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    assessment_type = Column(String(50))  # "technical_test", "peer_review", "manager_review"
    score = Column(Float)  # 1-10 scale
    assessor_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    notes = Column(Text)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="assessments", foreign_keys=[employee_id])
    skill = relationship("Skill", back_populates="assessments")

class JobRecommendation(Base):
    __tablename__ = "job_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    job_role_id = Column(Integer, ForeignKey("job_roles.id"))
    match_score = Column(Float)  # 0-100 percentage
    skill_gap_analysis = Column(JSON)  # Missing skills and their importance
    salary_estimate = Column(Float)
    recommendation_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)