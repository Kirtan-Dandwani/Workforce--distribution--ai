#!/usr/bin/env python3
"""
Workforce Distribution AI - Setup Script
Complete system initialization including data generation, model training, and database setup
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_step(step_num, total_steps, description):
    """Print formatted step information"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}/{total_steps}: {description}")
    print(f"{'='*60}")

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
        if result.stdout.strip():
            print("Output:", result.stdout.strip())
    else:
        print(f"❌ {description} failed!")
        print("Error:", result.stderr.strip())
        return False
    
    return True

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print_step(1, 6, "Installing Dependencies")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install --break-system-packages -r requirements.txt",
        "Installing Python dependencies"
    )

def create_directories():
    """Create necessary directories"""
    print_step(2, 6, "Creating Directory Structure")
    
    directories = [
        "data",
        "models", 
        "database",
        "ml_models",
        "backend",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def generate_training_data():
    """Generate synthetic training data"""
    print_step(3, 6, "Generating Training Data")
    
    return run_command(
        f"{sys.executable} data_generator.py",
        "Generating synthetic employee and job data"
    )

def initialize_database():
    """Initialize the database"""
    print_step(4, 6, "Initializing Database")
    
    try:
        from database.database import init_database
        init_database()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def train_ml_models():
    """Train machine learning models"""
    print_step(5, 6, "Training ML Models")
    
    return run_command(
        f"{sys.executable} -m ml_models.model_trainer",
        "Training machine learning models"
    )

def verify_setup():
    """Verify that all components are working"""
    print_step(6, 6, "Verifying Setup")
    
    # Check if model files exist
    model_files = [
        "models/retention_model.pkl",
        "models/salary_model.pkl",
        "models/role_model.pkl",
        "models/skill_rating_model.pkl",
        "models/encoders.pkl",
        "models/imputer.pkl"
    ]
    
    missing_files = []
    for file_path in model_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing model files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    # Check data files
    data_files = [
        "data/employees.csv",
        "data/skills.csv",
        "data/job_roles.csv",
        "data/training_data.csv"
    ]
    
    missing_data = []
    for file_path in data_files:
        if not os.path.exists(file_path):
            missing_data.append(file_path)
    
    if missing_data:
        print("❌ Missing data files:")
        for file_path in missing_data:
            print(f"  - {file_path}")
        return False
    
    print("✅ All components verified successfully!")
    return True

def main():
    """Main setup function"""
    print("🚀 Workforce Distribution AI - System Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    start_time = time.time()
    
    # Setup steps
    steps = [
        install_dependencies,
        create_directories,
        generate_training_data,
        initialize_database,
        train_ml_models,
        verify_setup
    ]
    
    # Execute setup steps
    for step_func in steps:
        try:
            if not step_func():
                print(f"\n❌ Setup failed at step: {step_func.__name__}")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n⚠️ Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error in {step_func.__name__}: {e}")
            sys.exit(1)
    
    # Setup completed
    end_time = time.time()
    setup_duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"⏱️  Total setup time: {setup_duration:.1f} seconds")
    print("\n📋 Next Steps:")
    print("1. Start the Streamlit app:")
    print("   streamlit run streamlit_app.py")
    print("\n2. Or start the FastAPI backend:")
    print("   python backend/api.py")
    print("\n3. Access the web interface:")
    print("   Streamlit: http://localhost:8501")
    print("   FastAPI: http://localhost:8000")

if __name__ == "__main__":
    main()