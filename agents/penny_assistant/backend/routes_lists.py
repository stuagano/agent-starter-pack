from fastapi import APIRouter, HTTPException
from typing import List
from .firestore_utils import create_list, get_lists, update_list, delete_list

router = APIRouter()

@router.get("/lists")
def api_get_lists(user_id: str):
    """Get all lists for a user."""
    try:
        return get_lists(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lists")
def api_create_list(user_id: str, name: str):
    """Create a new list for a user."""
    try:
        list_id = create_list(user_id, name)
        return {"status": "created", "id": list_id, "name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/lists/{list_id}")
def api_update_list(list_id: str, items: List[str]):
    """Update items in a list."""
    try:
        update_list(list_id, items)
        return {"status": "updated", "list_id": list_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/lists/{list_id}")
def api_delete_list(list_id: str):
    """Delete a list."""
    try:
        delete_list(list_id)
        return {"status": "deleted", "list_id": list_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 