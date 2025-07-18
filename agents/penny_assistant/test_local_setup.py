#!/usr/bin/env python3
"""
Test script to verify local setup for Penny Assistant
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def print_status(message, status="INFO"):
    """Print a status message with color coding."""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
    }
    color = colors.get(status, "\033[0m")
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def test_python_installation():
    """Test Python installation."""
    print_status("Testing Python installation...")
    
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print_status(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible", "SUCCESS")
            return True
        else:
            print_status(f"❌ Python {version.major}.{version.minor}.{version.micro} is too old. Need 3.8+", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Python test failed: {e}", "ERROR")
        return False

def test_dependencies():
    """Test if required dependencies can be imported."""
    print_status("Testing dependencies...")
    
    dependencies = [
        ("streamlit", "Streamlit"),
        ("requests", "Requests"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn")
    ]
    
    all_good = True
    for module, name in dependencies:
        try:
            __import__(module)
            print_status(f"✅ {name} is available", "SUCCESS")
        except ImportError:
            print_status(f"❌ {name} is not installed", "ERROR")
            all_good = False
    
    return all_good

def test_file_structure():
    """Test if required files exist."""
    print_status("Testing file structure...")
    
    required_files = [
        "backend/main.py",
        "backend/requirements.txt",
        "streamlit/app.py",
        "streamlit/requirements.txt",
        "streamlit/utils.py"
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_status(f"✅ {file_path} exists", "SUCCESS")
        else:
            print_status(f"❌ {file_path} missing", "ERROR")
            all_good = False
    
    return all_good

def test_backend_startup():
    """Test if backend can start."""
    print_status("Testing backend startup...")
    
    try:
        # Try to import the backend
        sys.path.append('backend')
        import main
        print_status("✅ Backend imports successfully", "SUCCESS")
        
        # Test if we can create the FastAPI app
        app = main.app
        print_status("✅ FastAPI app created successfully", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"❌ Backend startup failed: {e}", "ERROR")
        return False

def test_frontend_startup():
    """Test if frontend can start."""
    print_status("Testing frontend startup...")
    
    try:
        # Try to import the frontend
        sys.path.append('streamlit')
        import app
        print_status("✅ Frontend imports successfully", "SUCCESS")
        
        # Test if we can access the backend URL
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8080")
        print_status(f"✅ Backend URL configured: {backend_url}", "SUCCESS")
        
        return True
    except Exception as e:
        print_status(f"❌ Frontend startup failed: {e}", "ERROR")
        return False

def test_network_connectivity():
    """Test network connectivity."""
    print_status("Testing network connectivity...")
    
    try:
        # Test basic internet connectivity
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print_status("✅ Internet connectivity works", "SUCCESS")
            return True
        else:
            print_status("❌ Internet connectivity failed", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Network test failed: {e}", "ERROR")
        return False

def test_ports_available():
    """Test if required ports are available."""
    print_status("Testing port availability...")
    
    import socket
    
    ports = [8080, 8501]
    all_good = True
    
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print_status(f"✅ Port {port} is available", "SUCCESS")
        except OSError:
            print_status(f"❌ Port {port} is already in use", "WARNING")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("🧪 Testing Local Setup for Penny Assistant")
    print("=" * 50)
    print()
    
    tests = [
        ("Python Installation", test_python_installation),
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Backend Startup", test_backend_startup),
        ("Frontend Startup", test_frontend_startup),
        ("Network Connectivity", test_network_connectivity),
        ("Port Availability", test_ports_available),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"❌ Test failed with exception: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_status("🎉 All tests passed! You're ready to run Penny Assistant locally.", "SUCCESS")
        print("\n🚀 Next steps:")
        print("1. Run everything: ./run_local.sh")
        print("2. Run just frontend: ./run_streamlit.sh")
        print("3. Manual setup: See LOCAL_DEVELOPMENT.md")
    else:
        print_status("⚠️ Some tests failed. Please fix the issues before running locally.", "WARNING")
        print("\n🔧 Troubleshooting:")
        print("1. Check LOCAL_DEVELOPMENT.md for setup instructions")
        print("2. Install missing dependencies")
        print("3. Free up ports if they're in use")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 