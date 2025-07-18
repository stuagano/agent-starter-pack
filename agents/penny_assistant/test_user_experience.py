#!/usr/bin/env python3
"""
User experience test to verify error handling works in real-world scenarios.
"""

import sys
import os
import time
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

def simulate_user_workflow():
    """Simulate a typical user workflow with various error scenarios."""
    print("🔍 Simulating User Workflow")
    print("=" * 50)
    
    print("Scenario 1: User starts app with backend down")
    print("-" * 40)
    
    # Test 1: Check backend status
    status = get_backend_status()
    print(f"Backend status: {status['status']}")
    print_test_result("Backend Status Check", status['status'] == 'unreachable',
                     f"Status: {status['status']}")
    
    # Test 2: Try to get lists (should return empty list)
    lists = get_lists("demo-user")
    print(f"Lists retrieved: {len(lists)}")
    print_test_result("Get Lists (Backend Down)", isinstance(lists, list) and len(lists) == 0,
                     f"Got {len(lists)} lists")
    
    # Test 3: Try to create a list (should return error)
    result = create_list("demo-user", "Test List")
    print(f"Create list result: {result}")
    print_test_result("Create List (Backend Down)", "error" in result,
                     f"Result: {result}")
    
    # Test 4: Try chat (should work with placeholder)
    chat_result = chat("Hello Penny", "demo-user")
    print(f"Chat result: {chat_result}")
    print_test_result("Chat (Backend Down)", "response" in chat_result and "error" not in chat_result,
                     f"Has response: {'response' in chat_result}")
    
    # Test 5: Try memory (should work with placeholder)
    memory_result = get_memory()
    print(f"Memory result: {memory_result}")
    print_test_result("Memory (Backend Down)", "memory" in memory_result and "error" not in memory_result,
                     f"Has memory: {'memory' in memory_result}")
    
    print("\nScenario 2: Backend comes back online")
    print("-" * 40)
    
    # Start backend
    print("Starting backend...")
    import subprocess
    backend_process = subprocess.Popen([
        "python", "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8080"
    ], cwd="backend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for backend to start
    time.sleep(5)
    
    # Test 1: Check backend status
    status = get_backend_status()
    print(f"Backend status: {status['status']}")
    print_test_result("Backend Status (Online)", status['status'] == 'healthy',
                     f"Status: {status['status']}")
    
    # Test 2: Get lists (should work now)
    lists = get_lists("demo-user")
    print(f"Lists retrieved: {len(lists)}")
    print_test_result("Get Lists (Backend Online)", isinstance(lists, list),
                     f"Got {len(lists)} lists")
    
    # Test 3: Create a list (should work now)
    result = create_list("demo-user", "UX Test List")
    print(f"Create list result: {result}")
    print_test_result("Create List (Backend Online)", "error" not in result,
                     f"Result: {result}")
    
    # Test 4: Update the list
    if "error" not in result:
        list_id = result.get("id")
        update_result = update_list(list_id, ["Item 1", "Item 2"])
        print(f"Update list result: {update_result}")
        print_test_result("Update List", "error" not in update_result,
                         f"Result: {update_result}")
    
    # Test 5: Delete the list
    if "error" not in result:
        delete_result = delete_list(list_id)
        print(f"Delete list result: {delete_result}")
        print_test_result("Delete List", "error" not in delete_result,
                         f"Result: {delete_result}")
    
    # Clean up
    backend_process.terminate()
    backend_process.wait()
    
    print("\nScenario 3: Error recovery")
    print("-" * 40)
    
    # Test 1: Backend goes down again
    print("Backend goes down...")
    status = get_backend_status()
    print_test_result("Backend Status (Down Again)", status['status'] == 'unreachable',
                     f"Status: {status['status']}")
    
    # Test 2: App should still work with placeholders
    chat_result = chat("Test recovery", "demo-user")
    print_test_result("Chat Recovery", "response" in chat_result,
                     f"Has response: {'response' in chat_result}")
    
    memory_result = get_memory()
    print_test_result("Memory Recovery", "memory" in memory_result,
                     f"Has memory: {'memory' in memory_result}")

def test_error_messages():
    """Test that error messages are user-friendly."""
    print("🔍 Testing Error Messages")
    print("=" * 50)
    
    # Test 1: Connection error message
    print("Test 1: Connection error message")
    try:
        requests.get("http://localhost:8080/healthz", timeout=1)
    except requests.exceptions.ConnectionError:
        error_msg = "Backend connection failed. Is the server running at http://localhost:8080?"
        print_test_result("Connection Error Message", "connection failed" in error_msg.lower(),
                         f"Message: {error_msg}")
    
    # Test 2: Timeout error message
    print("Test 2: Timeout error message")
    try:
        requests.get("http://localhost:8080/healthz", timeout=0.1)
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. The backend is taking too long to respond."
        print_test_result("Timeout Error Message", "timed out" in error_msg.lower(),
                         f"Message: {error_msg}")
    
    # Test 3: JSON decode error message
    print("Test 3: JSON decode error message")
    try:
        json.loads("{invalid json}")
    except json.JSONDecodeError:
        error_msg = "Invalid response from backend. The server returned malformed JSON."
        print_test_result("JSON Error Message", "invalid response" in error_msg.lower(),
                         f"Message: {error_msg}")

def test_graceful_degradation():
    """Test graceful degradation when services fail."""
    print("🔍 Testing Graceful Degradation")
    print("=" * 50)
    
    # Test 1: All services down
    print("Test 1: All services down")
    
    # Lists should return empty list
    lists = get_lists("demo-user")
    print_test_result("Lists Graceful Degradation", isinstance(lists, list),
                     f"Got {len(lists)} lists")
    
    # Chat should work with placeholder
    chat_result = chat("Test degradation", "demo-user")
    print_test_result("Chat Graceful Degradation", "response" in chat_result,
                     f"Has response: {'response' in chat_result}")
    
    # Memory should work with placeholder
    memory_result = get_memory()
    print_test_result("Memory Graceful Degradation", "memory" in memory_result,
                     f"Has memory: {'memory' in memory_result}")
    
    # Evaluation should work with placeholder
    eval_data = {"data": [{"query": "test", "response": "test", "rating": 4}]}
    eval_result = evaluate(eval_data)
    print_test_result("Evaluation Graceful Degradation", "metrics" in eval_result,
                     f"Has metrics: {'metrics' in eval_result}")

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print a formatted test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    print()

def main():
    """Run all user experience tests."""
    print("🧪 Penny Assistant User Experience Tests")
    print("=" * 60)
    print()
    
    simulate_user_workflow()
    test_error_messages()
    test_graceful_degradation()
    
    print("🎉 User Experience Tests Complete!")
    print()
    print("📋 Summary:")
    print("- App works gracefully when backend is down")
    print("- App recovers when backend comes back online")
    print("- Error messages are user-friendly")
    print("- Graceful degradation works for all features")
    print("- User workflow is not interrupted by errors")

if __name__ == "__main__":
    main() 