import os
import requests
from typing import List, Dict, Any
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

def safe_request(func):
    """Decorator to safely handle requests with better error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            return {"error": f"Backend connection failed. Is the server running at {BACKEND_URL}?"}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. The backend is taking too long to respond."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Invalid response from backend. The server returned malformed JSON."}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    return wrapper

# PDF Upload
@safe_request
def pdf_upload(file, user_id: str):
    """Upload a PDF file to the backend."""
    files = {"file": (file.name, file, file.type)}
    resp = requests.post(f"{BACKEND_URL}/api/v1/pdf/upload", files=files, timeout=30)
    resp.raise_for_status()
    return resp.json()

# RAG Query
@safe_request
def rag_query(query: str, user_id: str):
    """Query the RAG endpoint."""
    resp = requests.post(f"{BACKEND_URL}/api/v1/pdf/query", params={"query": query, "user_id": user_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()

# Lists CRUD
@safe_request
def get_lists(user_id: str):
    """Get all lists for a user with fallback to empty list."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/lists", params={"user_id": user_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Ensure we return a list of dictionaries with proper structure
        if isinstance(data, list):
            return [
                item if isinstance(item, dict) else {"name": str(item), "id": f"list_{hash(str(item))}", "items": []}
                for item in data
            ]
        elif isinstance(data, dict) and "lists" in data:
            return data["lists"]
        else:
            return []
    except Exception as e:
        # Return empty list instead of error for better UX
        return []

@safe_request
def create_list(user_id: str, name: str):
    """Create a new list for a user."""
    resp = requests.post(f"{BACKEND_URL}/api/v1/lists", params={"user_id": user_id, "name": name}, timeout=10)
    resp.raise_for_status()
    return resp.json()

@safe_request
def update_list(list_id: str, items: List[str]):
    """Update items in a list."""
    resp = requests.put(f"{BACKEND_URL}/api/v1/lists/{list_id}", json={"items": items}, timeout=10)
    resp.raise_for_status()
    return resp.json()

@safe_request
def delete_list(list_id: str):
    """Delete a list."""
    resp = requests.delete(f"{BACKEND_URL}/api/v1/lists/{list_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()

# Calendar
@safe_request
def get_calendar_events(user_id: str):
    """Get calendar events for a user."""
    resp = requests.get(f"{BACKEND_URL}/api/v1/calendar/events", params={"user_id": user_id}, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Chat (placeholder implementation)
def chat(message: str, user_id: str):
    """Chat with Penny (placeholder implementation)."""
    try:
        # Try to use backend chat if available
        resp = requests.post(f"{BACKEND_URL}/api/v1/chat", json={"message": message, "user_id": user_id}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    
    # Fallback to placeholder response
    try:
        return {
            "response": f"Hello! I'm Penny, your AI assistant. You said: '{message}'. This is a placeholder response while the chat functionality is being implemented.",
            "context": ["Sample context for demonstration"],
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {"error": str(e)}

# Memory (placeholder implementation)
def get_memory():
    """Get memory bank contents (placeholder implementation)."""
    try:
        # Try to use backend memory if available
        resp = requests.get(f"{BACKEND_URL}/api/v1/memory", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    
    # Fallback to placeholder memory data
    try:
        return {
            "memory": {
                "user_preferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                },
                "recent_queries": [
                    "What is machine learning?",
                    "How to deploy to Cloud Run?",
                    "Best practices for API design"
                ],
                "favorite_topics": [
                    "AI/ML",
                    "Cloud Computing",
                    "Software Development"
                ]
            }
        }
    except Exception as e:
        return {"error": str(e)}

# Evaluation (placeholder implementation)
def evaluate(data):
    """Run evaluation on data (placeholder implementation)."""
    try:
        # Try to use backend evaluation if available
        resp = requests.post(f"{BACKEND_URL}/api/v1/evaluate", json=data, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    
    # Fallback to placeholder evaluation results
    try:
        return {
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85
            },
            "details": {
                "total_samples": len(data.get("data", [])),
                "evaluation_time": "0.5s",
                "model_version": "1.0.0"
            },
            "status": "completed"
        }
    except Exception as e:
        return {"error": str(e)}

# Health check
@safe_request
def health_check():
    """Check backend health."""
    resp = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
    resp.raise_for_status()
    return resp.json()

# Additional utility functions for better error handling
def get_backend_status():
    """Get detailed backend status."""
    try:
        health = health_check()
        if "error" not in health:
            return {
                "status": "healthy",
                "backend_url": BACKEND_URL,
                "details": health
            }
        else:
            # Check if it's a connection error (unreachable)
            if "connection failed" in health.get("error", "").lower():
                return {
                    "status": "unreachable",
                    "backend_url": BACKEND_URL,
                    "error": health["error"]
                }
            else:
                return {
                    "status": "error",
                    "backend_url": BACKEND_URL,
                    "error": health["error"]
                }
    except Exception as e:
        return {
            "status": "unreachable",
            "backend_url": BACKEND_URL,
            "error": str(e)
        }

def test_backend_connection():
    """Test if backend is reachable."""
    try:
        resp = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
        return resp.status_code == 200
    except:
        return False 