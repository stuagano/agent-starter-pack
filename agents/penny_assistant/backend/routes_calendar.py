from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from enhanced_calendar import get_calendar_events, create_calendar_event, get_calendar_status

router = APIRouter()

@router.get("/calendar/events")
def api_get_calendar_events(user_id: str = "demo-user", max_results: int = 10):
    """Fetch upcoming calendar events for a user."""
    try:
        result = get_calendar_events(user_id, max_results)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")

@router.post("/calendar/events")
def api_create_calendar_event(event_data: Dict[str, Any]):
    """Create a new calendar event."""
    try:
        result = create_calendar_event(event_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")

@router.get("/calendar/health")
def calendar_health():
    """Health check for calendar functionality."""
    try:
        status = get_calendar_status()
        return {
            "status": "ok", 
            "service": "calendar",
            "configured": status.get("configured", False),
            "service_available": status.get("service_available", False)
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "calendar",
            "error": str(e)
        } 