import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import joblib
import os
from config import MODEL_PATHS

class WorkforceMLTrainer:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.imputer = SimpleImputer(strategy='median')
        
    def load_data(self):
        """Load training data"""
        print("Loading training data...")
        self.df = pd.read_csv("data/training_data.csv")
        self.skills_df = pd.read_csv("data/skills.csv")
        self.roles_df = pd.read_csv("data/job_roles.csv")
        
        print(f"Loaded {len(self.df)} employee records")
        return self.df
    
    def prepare_features(self, df):
        """Prepare features for ML models"""
        
        # Select numerical features
        feature_cols = [
            'age', 'joining_year', 'payment_tier', 'experience_in_domain',
            'current_salary', 'expected_salary', 'education_encoded',
            'performance_rating', 'annual_growth', 'salary_growth_rate', 'tenure'
        ]
        
        X = df[feature_cols].copy()
        
        # Handle missing values
        X = pd.DataFrame(self.imputer.fit_transform(X), columns=feature_cols)
        
        return X
    
    def train_retention_model(self):
        """Train employee retention prediction model"""
        print("Training retention model...")
        
        X = self.prepare_features(self.df)
        y = self.df['will_leave'].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Retention model accuracy: {accuracy:.3f}")
        
        self.models['retention'] = model
        return model
    
    def train_salary_model(self):
        """Train salary prediction model"""
        print("Training salary prediction model...")
        
        X = self.prepare_features(self.df)
        y = self.df['expected_salary']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Gradient Boosting model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=6)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        print(f"Salary model RMSE: {rmse:.2f}")
        
        self.models['salary'] = model
        return model
    
    def train_role_classification_model(self):
        """Train job role classification model"""
        print("Training role classification model...")
        
        X = self.prepare_features(self.df)
        
        # Encode job roles
        role_encoder = LabelEncoder()
        y = role_encoder.fit_transform(self.df['current_role'])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Role classification accuracy: {accuracy:.3f}")
        
        self.models['role'] = model
        self.encoders['role'] = role_encoder
        return model, role_encoder
    
    def train_skill_rating_model(self):
        """Train skill rating prediction model"""
        print("Training skill rating model...")
        
        # Generate synthetic skill ratings based on employee data
        skill_ratings = []
        
        for idx, employee in self.df.iterrows():
            # Simulate skill ratings based on role, experience, and performance
            base_rating = min(10, max(1, employee['performance_rating'] + np.random.normal(0, 1)))
            
            # Experience bonus
            exp_bonus = min(2, employee['experience_in_domain'] * 0.2)
            
            # Education bonus
            edu_bonus = employee['education_encoded'] * 0.3
            
            final_rating = min(10, max(1, base_rating + exp_bonus + edu_bonus))
            
            skill_ratings.append({
                'employee_id': idx,
                'age': employee['age'],
                'experience_in_domain': employee['experience_in_domain'],
                'education_encoded': employee['education_encoded'],
                'performance_rating': employee['performance_rating'],
                'current_salary': employee['current_salary'],
                'payment_tier': employee['payment_tier'],
                'skill_rating': final_rating
            })
        
        skill_df = pd.DataFrame(skill_ratings)
        
        feature_cols = ['age', 'experience_in_domain', 'education_encoded', 
                       'performance_rating', 'current_salary', 'payment_tier']
        
        X = skill_df[feature_cols]
        y = skill_df['skill_rating']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest Regressor
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        print(f"Skill rating model RMSE: {rmse:.3f}")
        
        self.models['skill_rating'] = model
        return model
    
    def save_models(self):
        """Save all trained models"""
        print("Saving models...")
        
        # Create models directory
        os.makedirs("models", exist_ok=True)
        
        # Save individual models
        for model_name, model in self.models.items():
            model_path = MODEL_PATHS[model_name]
            joblib.dump(model, model_path)
            print(f"Saved {model_name} model to {model_path}")
        
        # Save encoders and scalers
        joblib.dump(self.encoders, MODEL_PATHS['encoders'])
        joblib.dump(self.imputer, "models/imputer.pkl")
        
        print("All models saved successfully!")
    
    def train_all_models(self):
        """Train all ML models"""
        print("Starting ML model training...")
        
        # Load data
        self.load_data()
        
        # Train models
        self.train_retention_model()
        self.train_salary_model()
        self.train_role_classification_model()
        self.train_skill_rating_model()
        
        # Save models
        self.save_models()
        
        print("Model training completed successfully!")

class ModelPredictor:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.imputer = None
        self.load_models()
    
    def load_models(self):
        """Load trained models"""
        try:
            self.models['retention'] = joblib.load(MODEL_PATHS['retention'])
            self.models['salary'] = joblib.load(MODEL_PATHS['salary'])
            self.models['role'] = joblib.load(MODEL_PATHS['role'])
            self.models['skill_rating'] = joblib.load(MODEL_PATHS['skill_rating'])
            
            self.encoders = joblib.load(MODEL_PATHS['encoders'])
            self.imputer = joblib.load("models/imputer.pkl")
            
            print("Models loaded successfully!")
        except FileNotFoundError as e:
            print(f"Model files not found: {e}")
            print("Please run training first!")
    
    def predict_retention(self, employee_data):
        """Predict if employee will leave"""
        X = self._prepare_input(employee_data)
        prediction = self.models['retention'].predict(X)[0]
        probability = self.models['retention'].predict_proba(X)[0]
        
        return {
            'will_leave': bool(prediction),
            'leave_probability': probability[1],
            'stay_probability': probability[0]
        }
    
    def predict_salary(self, employee_data):
        """Predict next year salary"""
        X = self._prepare_input(employee_data)
        prediction = self.models['salary'].predict(X)[0]
        return round(prediction, 2)
    
    def predict_role(self, employee_data):
        """Predict best job role"""
        X = self._prepare_input(employee_data)
        prediction = self.models['role'].predict(X)[0]
        role_name = self.encoders['role'].inverse_transform([prediction])[0]
        probability = self.models['role'].predict_proba(X)[0].max()
        
        return {
            'role': role_name,
            'confidence': probability
        }
    
    def predict_skill_rating(self, employee_data):
        """Predict skill rating"""
        feature_cols = ['age', 'experience_in_domain', 'education_encoded', 
                       'performance_rating', 'current_salary', 'payment_tier']
        
        X = pd.DataFrame([employee_data])[feature_cols]
        prediction = self.models['skill_rating'].predict(X)[0]
        
        return min(10, max(1, round(prediction, 1)))
    
    def _prepare_input(self, employee_data):
        """Prepare input data for prediction"""
        feature_cols = [
            'age', 'joining_year', 'payment_tier', 'experience_in_domain',
            'current_salary', 'expected_salary', 'education_encoded',
            'performance_rating', 'annual_growth', 'salary_growth_rate', 'tenure'
        ]
        
        df = pd.DataFrame([employee_data])
        
        # Calculate derived features
        if 'annual_growth' not in df.columns:
            df['annual_growth'] = df['expected_salary'] - df['current_salary']
        if 'salary_growth_rate' not in df.columns:
            df['salary_growth_rate'] = df['annual_growth'] / df['current_salary']
        if 'tenure' not in df.columns:
            df['tenure'] = 2023 - df['joining_year']
        
        X = df[feature_cols]
        X = pd.DataFrame(self.imputer.transform(X), columns=feature_cols)
        
        return X

if __name__ == "__main__":
    trainer = WorkforceMLTrainer()
    trainer.train_all_models()