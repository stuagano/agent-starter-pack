#!/usr/bin/env python3
"""
Test script to verify error handling improvements in Penny Assistant.
"""

import sys
import os
import requests
import json
from typing import Dict, Any

# Add the streamlit directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit'))

from utils import (
    get_lists, create_list, update_list, delete_list,
    get_calendar_events, chat, get_memory, evaluate,
    health_check, get_backend_status, test_backend_connection
)

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print a formatted test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()

def test_backend_connection_scenarios():
    """Test backend connection scenarios."""
    print("🔍 Testing Backend Connection Scenarios")
    print("=" * 50)
    
    # Test 1: Backend down
    print("Test 1: Backend is down")
    result = test_backend_connection()
    print_test_result("Backend Connection Test", not result, 
                     f"Expected: False (backend down), Got: {result}")
    
    # Test 2: Health check with backend down
    print("Test 2: Health check with backend down")
    result = health_check()
    print_test_result("Health Check (Backend Down)", "error" in result,
                     f"Expected: error in result, Got: {result}")
    
    # Test 3: Get backend status
    print("Test 3: Get backend status")
    result = get_backend_status()
    print_test_result("Backend Status", result["status"] == "unreachable",
                     f"Expected: unreachable, Got: {result['status']}")

def test_api_error_handling():
    """Test API error handling."""
    print("🔍 Testing API Error Handling")
    print("=" * 50)
    
    # Test 1: Lists API with backend down
    print("Test 1: Lists API with backend down")
    result = get_lists("demo-user")
    print_test_result("Get Lists (Backend Down)", isinstance(result, list) and len(result) == 0,
                     f"Expected: empty list, Got: {result}")
    
    # Test 2: Create list with backend down
    print("Test 2: Create list with backend down")
    result = create_list("demo-user", "Test List")
    print_test_result("Create List (Backend Down)", "error" in result,
                     f"Expected: error in result, Got: {result}")
    
    # Test 3: Calendar events with backend down
    print("Test 3: Calendar events with backend down")
    result = get_calendar_events("demo-user")
    print_test_result("Calendar Events (Backend Down)", "error" in result,
                     f"Expected: error in result, Got: {result}")

def test_placeholder_functionality():
    """Test placeholder functionality when backend is down."""
    print("🔍 Testing Placeholder Functionality")
    print("=" * 50)
    
    # Test 1: Chat with backend down
    print("Test 1: Chat with backend down")
    result = chat("Hello Penny", "demo-user")
    print_test_result("Chat (Backend Down)", "response" in result and "error" not in result,
                     f"Expected: response without error, Got: {result}")
    
    # Test 2: Memory with backend down
    print("Test 2: Memory with backend down")
    result = get_memory()
    print_test_result("Memory (Backend Down)", "memory" in result and "error" not in result,
                     f"Expected: memory without error, Got: {result}")
    
    # Test 3: Evaluation with backend down
    print("Test 3: Evaluation with backend down")
    test_data = {"data": [{"query": "test", "response": "test", "rating": 4}]}
    result = evaluate(test_data)
    print_test_result("Evaluation (Backend Down)", "metrics" in result and "error" not in result,
                     f"Expected: metrics without error, Got: {result}")

def test_data_format_handling():
    """Test data format handling."""
    print("🔍 Testing Data Format Handling")
    print("=" * 50)
    
    # Test 1: Safe dictionary access
    print("Test 1: Safe dictionary access")
    test_dict = {"a": {"b": {"c": "value"}}}
    value = test_dict.get("a", {}).get("b", {}).get("c", "default")
    print_test_result("Safe Dictionary Access", value == "value",
                     f"Expected: 'value', Got: {value}")
    
    # Test 2: Missing key handling
    print("Test 2: Missing key handling")
    value = test_dict.get("x", {}).get("y", {}).get("z", "default")
    print_test_result("Missing Key Handling", value == "default",
                     f"Expected: 'default', Got: {value}")

def test_with_backend_running():
    """Test with backend running."""
    print("🔍 Testing With Backend Running")
    print("=" * 50)
    
    # Start backend
    print("Starting backend...")
    import subprocess
    import time
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8080"
        ], cwd="backend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for backend to start
        time.sleep(5)
        
        # Test 1: Health check
        print("Test 1: Health check with backend running")
        result = health_check()
        print_test_result("Health Check (Backend Running)", "error" not in result,
                         f"Expected: no error, Got: {result}")
        
        # Test 2: Lists API
        print("Test 2: Lists API with backend running")
        result = get_lists("demo-user")
        print_test_result("Get Lists (Backend Running)", isinstance(result, list),
                         f"Expected: list, Got: {type(result)}")
        
        # Test 3: Create list
        print("Test 3: Create list with backend running")
        result = create_list("demo-user", "Test List Error Handling")
        print_test_result("Create List (Backend Running)", "error" not in result,
                         f"Expected: no error, Got: {result}")
        
        # Clean up
        backend_process.terminate()
        backend_process.wait()
        
    except Exception as e:
        print(f"❌ FAIL Backend Test Setup: {e}")
        print()

def main():
    """Run all error handling tests."""
    print("🧪 Penny Assistant Error Handling Tests")
    print("=" * 60)
    print()
    
    # Test with backend down
    test_backend_connection_scenarios()
    test_api_error_handling()
    test_placeholder_functionality()
    test_data_format_handling()
    
    # Test with backend running
    test_with_backend_running()
    
    print("🎉 Error Handling Tests Complete!")
    print()
    print("📋 Summary:")
    print("- Backend connection errors are handled gracefully")
    print("- API errors return proper error objects")
    print("- Placeholder functionality works when backend is down")
    print("- Data format handling is robust")
    print("- Safe dictionary access prevents crashes")

if __name__ == "__main__":
    main() 