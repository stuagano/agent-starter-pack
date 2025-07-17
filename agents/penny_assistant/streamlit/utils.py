import os
import requests
from typing import List

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

# PDF Upload
def pdf_upload(file, user_id: str):
    """Upload a PDF file to the backend."""
    try:
        files = {"file": (file.name, file, file.type)}
        resp = requests.post(f"{BACKEND_URL}/pdf/upload", files=files, params={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# RAG Query
def rag_query(query: str, user_id: str):
    """Query the RAG endpoint."""
    try:
        resp = requests.post(f"{BACKEND_URL}/rag/query", json={"query": query, "user_id": user_id})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# Lists CRUD
def get_lists(user_id: str):
    try:
        resp = requests.get(f"{BACKEND_URL}/lists", params={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return []

def create_list(user_id: str, name: str):
    try:
        resp = requests.post(f"{BACKEND_URL}/lists", params={"user_id": user_id, "name": name})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def update_list(list_id: str, items: List[str]):
    try:
        resp = requests.put(f"{BACKEND_URL}/lists/{list_id}", json={"items": items})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def delete_list(list_id: str):
    try:
        resp = requests.delete(f"{BACKEND_URL}/lists/{list_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# Calendar
def get_calendar_events(user_id: str):
    try:
        resp = requests.get(f"{BACKEND_URL}/calendar/events", params={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# Chat
def chat(message: str, user_id: str):
    try:
        resp = requests.post(f"{BACKEND_URL}/chat", json={"message": message, "user_id": user_id})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# Memory
def get_memory():
    try:
        resp = requests.get(f"{BACKEND_URL}/memory")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# Evaluation
def evaluate(data):
    try:
        resp = requests.post(f"{BACKEND_URL}/evaluate", json=data)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)} 