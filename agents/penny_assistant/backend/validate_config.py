#!/usr/bin/env python3
"""
Validation script for Penny Assistant Cloud Run configuration.
This script checks that all requirements are met for Cloud Run deployment.
"""

import os
import sys
import ast
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {filepath} exists")
        return True
    else:
        print(f"❌ {filepath} missing")
        return False

def check_dockerfile():
    """Check Dockerfile configuration."""
    print("\n🔍 Checking Dockerfile configuration...")
    
    if not check_file_exists("Dockerfile"):
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    checks = [
        ("Uses Python 3.10+ base image", "FROM python:3.10" in content),
        ("Exposes port 8080", "EXPOSE 8080" in content),
        ("Uses startup script", "CMD [\"./start.sh\"]" in content or "start.sh" in content),
        ("Sets working directory", "WORKDIR /app" in content),
        ("Copies requirements first", "COPY requirements.txt" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

def check_startup_script():
    """Check startup script configuration."""
    print("\n🔍 Checking startup script...")
    
    if not check_file_exists("start.sh"):
        return False
    
    with open("start.sh", "r") as f:
        content = f.read()
    
    checks = [
        ("Uses PORT environment variable", "PORT=" in content),
        ("Listens on 0.0.0.0", "0.0.0.0" in content),
        ("Uses uvicorn", "uvicorn" in content),
        ("Executable shebang", content.startswith("#!/bin/bash")),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

def check_main_py():
    """Check main.py configuration."""
    print("\n🔍 Checking main.py configuration...")
    
    if not check_file_exists("main.py"):
        return False
    
    with open("main.py", "r") as f:
        content = f.read()
    
    checks = [
        ("Imports os module", "import os" in content),
        ("Has health endpoint", "/healthz" in content),
        ("Uses FastAPI", "FastAPI" in content),
        ("Includes routers", "include_router" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

def check_requirements():
    """Check requirements.txt."""
    print("\n🔍 Checking requirements.txt...")
    
    if not check_file_exists("requirements.txt"):
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "google-cloud-firestore",
        "google-cloud-aiplatform",
        "PyPDF2",
        "python-dotenv",
        "adk"
    ]
    
    all_passed = True
    for package in required_packages:
        if package in content:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} missing")
            all_passed = False
    
    return all_passed

def check_cloud_run_requirements():
    """Check Cloud Run specific requirements."""
    print("\n🔍 Checking Cloud Run requirements...")
    
    requirements = [
        ("Dockerfile exists", check_file_exists("Dockerfile")),
        ("Startup script exists", check_file_exists("start.sh")),
        ("Requirements.txt exists", check_file_exists("requirements.txt")),
        ("Main.py exists", check_file_exists("main.py")),
        ("Dockerfile configuration", check_dockerfile()),
        ("Startup script configuration", check_startup_script()),
        ("Main.py configuration", check_main_py()),
        ("Requirements.txt configuration", check_requirements()),
    ]
    
    all_passed = True
    for req_name, passed in requirements:
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """Main validation function."""
    print("🚀 Penny Assistant Cloud Run Configuration Validator")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Run all checks
    if check_cloud_run_requirements():
        print("\n🎉 All Cloud Run requirements are met!")
        print("\n📋 Next steps:")
        print("1. Test locally: ./test_container.sh")
        print("2. Deploy to Cloud Run: gcloud run deploy penny-assistant-backend --source .")
        print("3. Set environment variables in Cloud Run console")
        return True
    else:
        print("\n❌ Some requirements are not met. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 