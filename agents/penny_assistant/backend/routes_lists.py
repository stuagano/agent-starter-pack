from fastapi import APIRouter, HTTPException
from typing import List
from enhanced_lists import create_list, get_lists, update_list, delete_list, get_list_status

router = APIRouter()

@router.get("/lists")
def api_get_lists(user_id: str):
    """Get all lists for a user."""
    try:
        lists = get_lists(user_id)
        status = get_list_status()
        return {
            "lists": lists,
            "status": status,
            "count": len(lists)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lists")
def api_create_list(user_id: str, name: str):
    """Create a new list for a user."""
    try:
        list_id = create_list(user_id, name)
        status = get_list_status()
        return {
            "status": "created", 
            "id": list_id, 
            "name": name,
            "storage_method": status.get("storage_method", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/lists/{list_id}")
def api_update_list(list_id: str, items: List[str]):
    """Update items in a list."""
    try:
        result = update_list(list_id, items)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result.get("message", "List not found"))
        return {
            "status": "updated", 
            "list_id": list_id,
            "storage_method": result.get("storage", "unknown")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/lists/{list_id}")
def api_delete_list(list_id: str):
    """Delete a list."""
    try:
        result = delete_list(list_id)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result.get("message", "List not found"))
        return {
            "status": "deleted", 
            "list_id": list_id,
            "storage_method": result.get("storage", "unknown")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lists/status")
def api_get_list_status():
    """Get list service status."""
    try:
        return get_list_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 