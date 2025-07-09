import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime
import time

from config import JOB_ROLES, SKILL_CATEGORIES, SALARY_RANGES
from ml_models.model_trainer import ModelPredictor
from database.database import init_database

# Page configuration
st.set_page_config(
    page_title="Workforce Distribution AI",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .prediction-result {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .recommendation-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize ML models
@st.cache_resource
def load_models():
    try:
        return ModelPredictor()
    except Exception as e:
        st.warning(f"ML models not available: {e}")
        return None

def main():
    st.markdown('<h1 class="main-header">👥 Workforce Distribution AI</h1>', unsafe_allow_html=True)
    
    # Initialize database and models
    if 'initialized' not in st.session_state:
        with st.spinner("Initializing system..."):
            init_database()
            st.session_state.initialized = True
    
    predictor = load_models()
    
    # Sidebar navigation
    st.sidebar.title("🔍 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "👤 Employee Assessment", "💼 Job Recommendations", 
         "📊 Analytics", "⚙️ Model Training", "🎯 Skill Rating"]
    )
    
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "👤 Employee Assessment":
        employee_assessment_page(predictor)
    elif page == "💼 Job Recommendations":
        job_recommendations_page(predictor)
    elif page == "📊 Analytics":
        analytics_page()
    elif page == "⚙️ Model Training":
        model_training_page()
    elif page == "🎯 Skill Rating":
        skill_rating_page(predictor)

def dashboard_page():
    st.header("📈 Workforce Overview Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Available Roles</h3>
            <h2>{}</h2>
        </div>
        """.format(len(JOB_ROLES)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Skill Categories</h3>
            <h2>{}</h2>
        </div>
        """.format(len(SKILL_CATEGORIES)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Skills</h3>
            <h2>{}</h2>
        </div>
        """.format(sum(len(skills) for skills in SKILL_CATEGORIES.values())), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>System Status</h3>
            <h2>🟢 Active</h2>
        </div>
        """.format(sum(len(skills) for skills in SKILL_CATEGORIES.values())), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Salary ranges visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Salary Ranges by Role")
        roles_df = pd.DataFrame([
            {"Role": role, "Min Salary": ranges[0]*1000, "Max Salary": ranges[1]*1000}
            for role, ranges in SALARY_RANGES.items()
        ])
        
        fig = px.bar(roles_df, x="Role", y=["Min Salary", "Max Salary"],
                    title="Salary Ranges by Job Role",
                    barmode="group")
        fig.update_layout(xaxis_tickangle=45)


        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Skills by Category")
        skills_count = {category: len(skills) for category, skills in SKILL_CATEGORIES.items()}
        
        fig = px.pie(values=list(skills_count.values()), 
                    names=list(skills_count.keys()),
                    title="Distribution of Skills by Category")
        st.plotly_chart(fig, use_container_width=True)

def employee_assessment_page(predictor):
    st.header("👤 Employee Assessment & Predictions")
    
    if predictor is None:
        st.error("⚠️ ML models are not available. Please run model training first.")
        return
    
    st.markdown("### Enter Employee Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider("Age", 18, 65, 30)
        joining_year = st.selectbox("Joining Year", list(range(2015, 2025)), index=5)
        payment_tier = st.selectbox("Payment Tier", [1, 2, 3], index=1)
        experience = st.slider("Experience in Domain (years)", 0, 25, 3)
        performance_rating = st.slider("Performance Rating", 1.0, 10.0, 7.5, 0.1)
    
    with col2:
        current_salary = st.number_input("Current Salary ($)", value=70000, step=1000)
        expected_salary = st.number_input("Expected Salary ($)", value=75000, step=1000)
        education = st.selectbox("Education Level", 
                                ["High School", "Bachelors", "Masters", "PhD"], 
                                index=1)
    
    if st.button("🔮 Generate Predictions", type="primary"):
        employee_data = {
            "age": age,
            "joining_year": joining_year,
            "payment_tier": payment_tier,
            "experience_in_domain": experience,
            "current_salary": current_salary,
            "expected_salary": expected_salary,
            "education_level": education,
            "performance_rating": performance_rating
        }
        
        # Add derived features
        education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
        employee_data['education_encoded'] = education_map[education]
        employee_data['annual_growth'] = expected_salary - current_salary
        employee_data['salary_growth_rate'] = employee_data['annual_growth'] / current_salary
        employee_data['tenure'] = 2023 - joining_year
        
        with st.spinner("Generating predictions..."):
            # Retention prediction
            try:
                retention_result = predictor.predict_retention(employee_data)
                
                st.markdown("### 🎯 Prediction Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    retention_color = "🔴" if retention_result['will_leave'] else "🟢"
                    retention_text = "Will Leave" if retention_result['will_leave'] else "Will Stay"
                    
                    st.markdown(f"""
                    <div class="prediction-result">
                        <h4>{retention_color} Employee Retention</h4>
                        <h3>{retention_text}</h3>
                        <p>Leave Probability: {retention_result['leave_probability']:.1%}</p>
                        <p>Stay Probability: {retention_result['stay_probability']:.1%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    predicted_salary = predictor.predict_salary(employee_data)
                    growth = predicted_salary - current_salary
                    growth_pct = (growth / current_salary) * 100
                    
                    st.markdown(f"""
                    <div class="prediction-result">
                        <h4>💰 Salary Prediction</h4>
                        <h3>${predicted_salary:,.0f}</h3>
                        <p>Growth: ${growth:,.0f} ({growth_pct:.1f}%)</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    role_result = predictor.predict_role(employee_data)
                    confidence_color = "🟢" if role_result['confidence'] > 0.8 else "🟡" if role_result['confidence'] > 0.6 else "🔴"
                    
                    st.markdown(f"""
                    <div class="prediction-result">
                        <h4>🎭 Best Role Match</h4>
                        <h3>{role_result['role']}</h3>
                        <p>{confidence_color} Confidence: {role_result['confidence']:.1%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Skill rating
                skill_rating = predictor.predict_skill_rating(employee_data)
                
                if skill_rating >= 8:
                    skill_level = "Expert 🎓"
                    skill_color = "#28a745"
                elif skill_rating >= 6:
                    skill_level = "Proficient 💪"
                    skill_color = "#007bff"
                elif skill_rating >= 4:
                    skill_level = "Intermediate 📈"
                    skill_color = "#ffc107"
                else:
                    skill_level = "Beginner 🌱"
                    skill_color = "#6c757d"
                
                st.markdown(f"""
                <div class="prediction-result" style="text-align: center;">
                    <h4>🎯 Overall Skill Rating</h4>
                    <h2 style="color: {skill_color};">{skill_rating:.1f}/10</h2>
                    <h3>{skill_level}</h3>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Prediction error: {e}")

def job_recommendations_page(predictor):
    st.header("💼 Job Role Recommendations")
    
    st.markdown("### Employee Profile for Job Matching")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider("Age", 18, 65, 30, key="job_age")
        joining_year = st.selectbox("Joining Year", list(range(2015, 2025)), index=5, key="job_joining")
        experience = st.slider("Experience (years)", 0, 25, 3, key="job_exp")
        current_salary = st.number_input("Current Salary ($)", value=70000, step=1000, key="job_salary")
    
    with col2:
        expected_salary = st.number_input("Expected Salary ($)", value=75000, step=1000, key="job_expected")
        education = st.selectbox("Education", ["High School", "Bachelors", "Masters", "PhD"], index=1, key="job_edu")
        payment_tier = st.selectbox("Payment Tier", [1, 2, 3], index=1, key="job_tier")
        performance_rating = st.slider("Performance Rating", 1.0, 10.0, 7.5, 0.1, key="job_perf")
    
    if st.button("🔍 Get Job Recommendations", type="primary"):
        employee_data = {
            "age": age,
            "joining_year": joining_year,
            "payment_tier": payment_tier,
            "experience_in_domain": experience,
            "current_salary": current_salary,
            "expected_salary": expected_salary,
            "education_level": education,
            "performance_rating": performance_rating
        }
        
        st.markdown("### 🎯 Top Job Recommendations")
        
        recommendations = []
        education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
        employee_data['education_encoded'] = education_map[education]
        
        for role in JOB_ROLES:
            match_score = calculate_match_score(employee_data, role)
            salary_estimate = estimate_salary_for_role(employee_data, role)
            
            recommendations.append({
                "Role": role,
                "Match Score": match_score,
                "Estimated Salary": salary_estimate,
                "Salary Range": f"${SALARY_RANGES[role][0]}k - ${SALARY_RANGES[role][1]}k"
            })
        
        recommendations.sort(key=lambda x: x['Match Score'], reverse=True)
        
        # Display top 5 recommendations
        for i, rec in enumerate(recommendations[:5]):
            match_color = "#28a745" if rec['Match Score'] >= 80 else "#007bff" if rec['Match Score'] >= 60 else "#ffc107"
            
            st.markdown(f"""
            <div class="recommendation-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>#{i+1} {rec['Role']}</h4>
                        <p><strong>Estimated Salary:</strong> ${rec['Estimated Salary']:,.0f}</p>
                        <p><strong>Market Range:</strong> {rec['Salary Range']}</p>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="color: {match_color}; margin: 0;">{rec['Match Score']:.0f}%</h3>
                        <p style="margin: 0;">Match Score</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualization
        rec_df = pd.DataFrame(recommendations[:10])
        fig = px.bar(rec_df, x="Match Score", y="Role", orientation='h',
                    title="Job Role Match Scores",
                    color="Match Score",
                    color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)

def analytics_page():
    st.header("📊 Workforce Analytics")
    
    # Generate sample data for visualization
    np.random.seed(42)
    
    # Role distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Role Distribution")
        role_counts = {role: np.random.randint(5, 50) for role in JOB_ROLES}
        
        fig = px.pie(values=list(role_counts.values()), 
                    names=list(role_counts.keys()),
                    title="Current Workforce Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Salary Analysis")
        salary_data = []
        for role in JOB_ROLES[:8]:  # Top 8 roles for clarity
            min_sal, max_sal = SALARY_RANGES[role]
            avg_sal = (min_sal + max_sal) / 2 * 1000
            salary_data.append({"Role": role, "Average Salary": avg_sal})
        
        salary_df = pd.DataFrame(salary_data)
        fig = px.bar(salary_df, x="Role", y="Average Salary",
                    title="Average Salary by Role")
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Skill demand analysis
    st.subheader("Skill Demand Analysis")
    
    skill_demand = {}
    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            skill_demand[skill] = np.random.randint(10, 100)
    
    # Top 15 skills
    top_skills = dict(sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:15])
    
    fig = px.bar(x=list(top_skills.values()), y=list(top_skills.keys()),
                orientation='h', title="Top Skills in Demand")
    st.plotly_chart(fig, use_container_width=True)

def model_training_page():
    st.header("⚙️ ML Model Training & Management")
    
    st.markdown("""
    ### Model Training Pipeline
    Train machine learning models for workforce predictions including:
    - 🎯 Employee Retention Prediction
    - 💰 Salary Prediction
    - 🎭 Role Classification
    - ⭐ Skill Rating Prediction
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Training Data", type="secondary"):
            with st.spinner("Generating synthetic training data..."):
                import subprocess
                result = subprocess.run(["python", "data_generator.py"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Training data generated successfully!")
                    st.code(result.stdout)
                else:
                    st.error("❌ Error generating data:")
                    st.code(result.stderr)
    
    with col2:
        if st.button("🤖 Train ML Models", type="primary"):
            with st.spinner("Training machine learning models..."):
                import subprocess
                result = subprocess.run(["python", "-m", "ml_models.model_trainer"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✅ Models trained successfully!")
                    st.code(result.stdout)
                    st.balloons()
                else:
                    st.error("❌ Error training models:")
                    st.code(result.stderr)
    
    # Model status
    st.markdown("### 📈 Model Status")
    import os
    
    models_status = []
    model_files = [
        ("Retention Model", "models/retention_model.pkl"),
        ("Salary Model", "models/salary_model.pkl"),
        ("Role Classifier", "models/role_model.pkl"),
        ("Skill Rating", "models/skill_rating_model.pkl"),
        ("Encoders", "models/encoders.pkl"),
        ("Data Imputer", "models/imputer.pkl")
    ]
    
    for name, path in model_files:
        status = "✅ Available" if os.path.exists(path) else "❌ Missing"
        size = f"{os.path.getsize(path) / 1024:.1f} KB" if os.path.exists(path) else "N/A"
        models_status.append({"Model": name, "Status": status, "Size": size})
    
    st.dataframe(pd.DataFrame(models_status), use_container_width=True)

def skill_rating_page(predictor):
    st.header("🎯 Employee Skill Rating System")
    
    st.markdown("""
    ### Skill Assessment Tool
    Evaluate employee skills across different categories and get detailed ratings.
    """)
    
    if predictor is None:
        st.error("⚠️ ML models are not available. Please train models first.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Employee Information")
        age = st.slider("Age", 18, 65, 30, key="skill_age")
        experience = st.slider("Years of Experience", 0, 25, 5, key="skill_exp")
        education = st.selectbox("Education", ["High School", "Bachelors", "Masters", "PhD"], 
                                index=1, key="skill_edu")
        performance = st.slider("Performance Rating", 1.0, 10.0, 7.5, 0.1, key="skill_perf")
        current_salary = st.number_input("Current Salary ($)", value=70000, step=1000, key="skill_sal")
        payment_tier = st.selectbox("Payment Tier", [1, 2, 3], index=1, key="skill_tier")
    
    with col2:
        st.subheader("Skill Categories")
        selected_categories = st.multiselect(
            "Select skill categories to assess:",
            list(SKILL_CATEGORIES.keys()),
            default=["Technical", "Analytical"]
        )
    
    if st.button("📊 Generate Skill Assessment", type="primary"):
        education_map = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
        
        employee_data = {
            "age": age,
            "experience_in_domain": experience,
            "education_encoded": education_map[education],
            "performance_rating": performance,
            "current_salary": current_salary,
            "payment_tier": payment_tier
        }
        
        overall_rating = predictor.predict_skill_rating(employee_data)
        
        st.markdown("### 📈 Skill Assessment Results")
        
        # Overall rating
        rating_color = "#28a745" if overall_rating >= 8 else "#007bff" if overall_rating >= 6 else "#ffc107" if overall_rating >= 4 else "#dc3545"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 1rem; margin: 1rem 0;">
            <h2>Overall Skill Rating</h2>
            <h1 style="color: {rating_color}; font-size: 4rem; margin: 0;">{overall_rating:.1f}/10</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Category-wise ratings
        st.markdown("### 🔍 Category-wise Skill Breakdown")
        
        category_ratings = {}
        for category in selected_categories:
            # Simulate category-specific rating based on overall rating
            category_modifier = np.random.normal(0, 0.5)
            cat_rating = max(1, min(10, overall_rating + category_modifier))
            category_ratings[category] = cat_rating
        
        cols = st.columns(len(selected_categories))
        for i, (category, rating) in enumerate(category_ratings.items()):
            with cols[i]:
                rating_color = "#28a745" if rating >= 8 else "#007bff" if rating >= 6 else "#ffc107" if rating >= 4 else "#dc3545"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background-color: #f8f9fa; border-radius: 0.5rem;">
                    <h4>{category}</h4>
                    <h2 style="color: {rating_color}; margin: 0;">{rating:.1f}/10</h2>
                </div>
                """, unsafe_allow_html=True)
        
        # Skills radar chart
        if len(selected_categories) > 2:
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(category_ratings.values()),
                theta=list(category_ratings.keys()),
                fill='toself',
                name='Skill Ratings'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Skill Category Radar Chart"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.markdown("### 💡 Development Recommendations")
        
        for category, rating in category_ratings.items():
            skills_in_category = SKILL_CATEGORIES[category]
            
            if rating < 6:
                st.warning(f"**{category}**: Focus on developing fundamental skills. Consider training in: {', '.join(skills_in_category[:3])}")
            elif rating < 8:
                st.info(f"**{category}**: Good foundation! Consider advanced training in: {', '.join(skills_in_category[3:6])}")
            else:
                st.success(f"**{category}**: Excellent skills! Consider mentoring others and staying current with: {', '.join(skills_in_category[-3:])}")

# Helper functions
def calculate_match_score(employee_data, role):
    """Calculate job match score"""
    score = 0.0
    
    experience = employee_data.get('experience_in_domain', 0)
    if experience >= 5:
        score += 30
    elif experience >= 2:
        score += 20
    else:
        score += 10
    
    education_bonus = {0: 5, 1: 15, 2: 25, 3: 30}
    score += education_bonus.get(employee_data.get('education_encoded', 1), 15)
    
    performance = employee_data.get('performance_rating', 5)
    score += (performance / 10) * 25
    
    current_salary = employee_data.get('current_salary', 50000)
    role_salary_range = SALARY_RANGES.get(role, (50, 100))
    role_avg_salary = (role_salary_range[0] + role_salary_range[1]) / 2 * 1000
    
    salary_alignment = 1 - abs(current_salary - role_avg_salary) / role_avg_salary
    score += max(0, salary_alignment * 20)
    
    return min(100, max(0, score))

def estimate_salary_for_role(employee_data, role):
    """Estimate salary for role"""
    base_salary_range = SALARY_RANGES.get(role, (50, 100))
    base_salary = (base_salary_range[0] + base_salary_range[1]) / 2 * 1000
    
    experience = employee_data.get('experience_in_domain', 0)
    exp_multiplier = 1 + (experience * 0.03)
    
    edu_multipliers = {0: 0.85, 1: 1.0, 2: 1.15, 3: 1.3}
    edu_multiplier = edu_multipliers.get(employee_data.get('education_encoded', 1), 1.0)
    
    performance = employee_data.get('performance_rating', 7)
    perf_multiplier = 0.8 + (performance / 10) * 0.4
    
    estimated_salary = base_salary * exp_multiplier * edu_multiplier * perf_multiplier
    return estimated_salary

if __name__ == "__main__":
    main()
