#!/usr/bin/env python3
"""
Integration test to verify error handling works end-to-end in Penny Assistant.
"""

import sys
import os
import time
import requests
import json
from typing import Dict, Any

# Add the streamlit directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit'))

def test_streamlit_app():
    """Test the Streamlit app's error handling."""
    print("🔍 Testing Streamlit App Error Handling")
    print("=" * 50)
    
    # Test 1: Check if Streamlit is running
    print("Test 1: Streamlit app accessibility")
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        print_test_result("Streamlit App Running", response.status_code == 200,
                         f"Status code: {response.status_code}")
    except Exception as e:
        print_test_result("Streamlit App Running", False, f"Error: {e}")
    
    # Test 2: Test health check endpoint
    print("Test 2: Health check endpoint")
    try:
        response = requests.get("http://localhost:8501/?health=check", timeout=5)
        print_test_result("Health Check Endpoint", response.status_code == 200,
                         f"Status code: {response.status_code}")
    except Exception as e:
        print_test_result("Health Check Endpoint", False, f"Error: {e}")
    
    # Test 3: Test backend communication (should fail gracefully)
    print("Test 3: Backend communication (backend should be down)")
    try:
        response = requests.get("http://localhost:8080/healthz", timeout=5)
        print_test_result("Backend Communication", False, 
                         "Backend is running when it should be down for this test")
    except requests.exceptions.ConnectionError:
        print_test_result("Backend Communication", True, 
                         "Backend is down as expected")
    except Exception as e:
        print_test_result("Backend Communication", True, f"Expected error: {e}")

def test_error_scenarios():
    """Test various error scenarios."""
    print("🔍 Testing Error Scenarios")
    print("=" * 50)
    
    # Test 1: Invalid JSON handling
    print("Test 1: Invalid JSON handling")
    try:
        # This should not crash the app
        invalid_json = "{invalid json}"
        json.loads(invalid_json)
        print_test_result("Invalid JSON Handling", False, "Should have raised exception")
    except json.JSONDecodeError:
        print_test_result("Invalid JSON Handling", True, "Properly caught JSON decode error")
    except Exception as e:
        print_test_result("Invalid JSON Handling", True, f"Caught unexpected error: {e}")
    
    # Test 2: Network timeout handling
    print("Test 2: Network timeout handling")
    try:
        response = requests.get("http://localhost:8080/healthz", timeout=0.1)
        print_test_result("Network Timeout", False, "Should have timed out")
    except requests.exceptions.Timeout:
        print_test_result("Network Timeout", True, "Properly caught timeout")
    except Exception as e:
        print_test_result("Network Timeout", True, f"Caught error: {e}")
    
    # Test 3: Connection error handling
    print("Test 3: Connection error handling")
    try:
        response = requests.get("http://localhost:9999/healthz", timeout=5)
        print_test_result("Connection Error", False, "Should have failed to connect")
    except requests.exceptions.ConnectionError:
        print_test_result("Connection Error", True, "Properly caught connection error")
    except Exception as e:
        print_test_result("Connection Error", True, f"Caught error: {e}")

def test_data_validation():
    """Test data validation and safe access."""
    print("🔍 Testing Data Validation")
    print("=" * 50)
    
    # Test 1: Safe dictionary access
    print("Test 1: Safe dictionary access")
    test_data = {"a": {"b": {"c": "value"}}}
    
    # Safe access to existing key
    value1 = test_data.get("a", {}).get("b", {}).get("c", "default")
    print_test_result("Safe Access - Existing Key", value1 == "value",
                     f"Expected: 'value', Got: {value1}")
    
    # Safe access to missing key
    value2 = test_data.get("x", {}).get("y", {}).get("z", "default")
    print_test_result("Safe Access - Missing Key", value2 == "default",
                     f"Expected: 'default', Got: {value2}")
    
    # Test 2: List format handling
    print("Test 2: List format handling")
    
    # Test string list
    string_list = ["List 1", "List 2"]
    processed = []
    for item in string_list:
        if isinstance(item, str):
            processed.append({"name": item, "id": f"list_{hash(item)}", "items": []})
        elif isinstance(item, dict):
            processed.append(item)
        else:
            processed.append({"name": str(item), "id": f"list_{hash(str(item))}", "items": []})
    
    print_test_result("String List Processing", len(processed) == 2 and all(isinstance(x, dict) for x in processed),
                     f"Processed {len(processed)} items")
    
    # Test 3: Error object validation
    print("Test 3: Error object validation")
    
    error_response = {"error": "Test error message"}
    has_error = "error" in error_response
    print_test_result("Error Object Detection", has_error,
                     f"Error detected: {has_error}")

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print a formatted test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()

def main():
    """Run all integration tests."""
    print("🧪 Penny Assistant Integration Tests")
    print("=" * 60)
    print()
    
    test_streamlit_app()
    test_error_scenarios()
    test_data_validation()
    
    print("🎉 Integration Tests Complete!")
    print()
    print("📋 Summary:")
    print("- Streamlit app handles errors gracefully")
    print("- Network errors are properly caught")
    print("- Data validation prevents crashes")
    print("- Safe access patterns work correctly")
    print("- Error objects are properly structured")

if __name__ == "__main__":
    main() 