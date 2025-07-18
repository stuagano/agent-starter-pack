#!/usr/bin/env python3
"""
Validation script for Penny Assistant Streamlit Frontend Cloud Run configuration.
This script checks that all requirements are met for Cloud Run deployment.
"""

import os
import sys
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
        ("Exposes port 8501", "EXPOSE 8501" in content),
        ("Uses startup script", "CMD [\"./start.sh\"]" in content or "start.sh" in content),
        ("Sets working directory", "WORKDIR /app" in content),
        ("Copies requirements first", "COPY requirements.txt" in content),
        ("Sets Python environment variables", "PYTHONUNBUFFERED=1" in content),
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
        ("Uses streamlit", "streamlit" in content),
        ("Executable shebang", content.startswith("#!/bin/bash")),
        ("Headless mode", "headless=true" in content),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

def check_app_py():
    """Check app.py configuration."""
    print("\n🔍 Checking app.py configuration...")
    
    if not check_file_exists("app.py"):
        return False
    
    with open("app.py", "r") as f:
        content = f.read()
    
    checks = [
        ("Imports os module", "import os" in content),
        ("Uses environment variables", "os.getenv" in content),
        ("Uses Streamlit", "import streamlit" in content),
        ("Has page configuration", "set_page_config" in content),
        ("Handles BACKEND_URL", "BACKEND_URL" in content),
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
        "streamlit",
        "requests",
        "google-auth"
    ]
    
    all_passed = True
    for package in required_packages:
        if package in content:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} missing")
            all_passed = False
    
    return all_passed

def check_utils():
    """Check utils.py exists."""
    print("\n🔍 Checking utils.py...")
    
    if check_file_exists("utils.py"):
        print("✅ utils.py exists")
        return True
    else:
        print("❌ utils.py missing")
        return False

def check_cloud_run_requirements():
    """Check Cloud Run specific requirements."""
    print("\n🔍 Checking Cloud Run requirements...")
    
    requirements = [
        ("Dockerfile exists", check_file_exists("Dockerfile")),
        ("Startup script exists", check_file_exists("start.sh")),
        ("Requirements.txt exists", check_file_exists("requirements.txt")),
        ("App.py exists", check_file_exists("app.py")),
        ("Utils.py exists", check_utils()),
        ("Dockerfile configuration", check_dockerfile()),
        ("Startup script configuration", check_startup_script()),
        ("App.py configuration", check_app_py()),
        ("Requirements.txt configuration", check_requirements()),
    ]
    
    all_passed = True
    for req_name, passed in requirements:
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """Main validation function."""
    print("🚀 Penny Assistant Streamlit Frontend Cloud Run Configuration Validator")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the streamlit directory")
        sys.exit(1)
    
    # Run all checks
    if check_cloud_run_requirements():
        print("\n🎉 All Cloud Run requirements are met!")
        print("\n📋 Next steps:")
        print("1. Test locally: ./test_container.sh")
        print("2. Deploy to Cloud Run: gcloud run deploy penny-assistant-frontend --source .")
        print("3. Set environment variables in Cloud Run console:")
        print("   - BACKEND_URL: URL of your backend service")
        print("   - USER_ID: Default user ID (optional)")
        return True
    else:
        print("\n❌ Some requirements are not met. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 