from google.cloud import firestore
from typing import List, Dict
import os

COLLECTION = "user_lists"

def get_firestore_client():
    """Get a Firestore client using GOOGLE_APPLICATION_CREDENTIALS."""
    try:
        return firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    except Exception as e:
        raise RuntimeError(f"Failed to create Firestore client: {e}")

def create_list(user_id: str, name: str) -> str:
    """Create a new list for a user. Returns list ID."""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set({"user_id": user_id, "name": name, "items": []})
    return doc_ref.id

def get_lists(user_id: str) -> List[Dict]:
    """Get all lists for a user."""
    db = get_firestore_client()
    docs = db.collection(COLLECTION).where("user_id", "==", user_id).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

def update_list(list_id: str, items: List[str]):
    """Update items in a list."""
    db = get_firestore_client()
    db.collection(COLLECTION).document(list_id).update({"items": items})

def delete_list(list_id: str):
    """Delete a list by ID."""
    db = get_firestore_client()
    db.collection(COLLECTION).document(list_id).delete() 