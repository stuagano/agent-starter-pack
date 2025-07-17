import os
import requests
from typing import List

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


def get_lists(user_id: str):
    """Fetch all lists for a user from the backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/lists", params={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return []

def create_list(user_id: str, name: str):
    """Create a new list for a user."""
    try:
        resp = requests.post(f"{BACKEND_URL}/lists", params={"user_id": user_id, "name": name})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def update_list(list_id: str, items: List[str]):
    """Update items in a list."""
    try:
        resp = requests.put(f"{BACKEND_URL}/lists/{list_id}", json={"items": items})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def delete_list(list_id: str):
    """Delete a list by ID."""
    try:
        resp = requests.delete(f"{BACKEND_URL}/lists/{list_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)} 