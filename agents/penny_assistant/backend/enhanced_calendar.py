from typing import List, Dict, Any
import os
import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from config_reader import config_reader

class EnhancedCalendar:
    def __init__(self):
        self.calendar_configured = config_reader.is_service_configured("calendar")
        self.credentials_file = config_reader.get_service_config("calendar").get("credentials_file")
        self.service = None
        
        if self.calendar_configured and self.credentials_file:
            self.initialize_calendar_service()
    
    def initialize_calendar_service(self):
        """Initialize Google Calendar service."""
        try:
            SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
            
            creds = None
            # The file token.pickle stores the user's access and refresh tokens
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar service initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Google Calendar initialization failed: {e}")
            self.calendar_configured = False
            self.service = None
    
    def get_calendar_events(self, user_id: str = "demo-user", max_results: int = 10) -> Dict[str, Any]:
        """Get calendar events from Google Calendar or placeholder."""
        if self.calendar_configured and self.service:
            return self._get_real_calendar_events(max_results)
        else:
            return self._get_placeholder_events()
    
    def _get_real_calendar_events(self, max_results: int = 10) -> Dict[str, Any]:
        """Get real calendar events from Google Calendar."""
        try:
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return {
                    "status": "success",
                    "events": [],
                    "count": 0,
                    "source": "google_calendar"
                }
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    "id": event['id'],
                    "title": event['summary'],
                    "start": start,
                    "end": end,
                    "location": event.get('location', ''),
                    "description": event.get('description', ''),
                    "attendees": [attendee.get('email') for attendee in event.get('attendees', [])]
                })
            
            return {
                "status": "success",
                "events": formatted_events,
                "count": len(formatted_events),
                "source": "google_calendar"
            }
            
        except Exception as e:
            print(f"⚠️  Google Calendar API failed, using placeholder: {e}")
            return self._get_placeholder_events()
    
    def _get_placeholder_events(self) -> Dict[str, Any]:
        """Generate placeholder calendar events."""
        now = datetime.datetime.now()
        events = [
            {
                "id": "event_1",
                "title": "Team Meeting",
                "start": (now + datetime.timedelta(hours=1)).isoformat(),
                "end": (now + datetime.timedelta(hours=2)).isoformat(),
                "location": "Conference Room A",
                "description": "Weekly team sync meeting",
                "attendees": ["team@company.com"]
            },
            {
                "id": "event_2", 
                "title": "Project Review",
                "start": (now + datetime.timedelta(days=1, hours=10)).isoformat(),
                "end": (now + datetime.timedelta(days=1, hours=11)).isoformat(),
                "location": "Virtual",
                "description": "Quarterly project review with stakeholders",
                "attendees": ["stakeholders@company.com"]
            },
            {
                "id": "event_3",
                "title": "Lunch with Client",
                "start": (now + datetime.timedelta(days=2, hours=12)).isoformat(),
                "end": (now + datetime.timedelta(days=2, hours=13)).isoformat(),
                "location": "Downtown Restaurant",
                "description": "Client meeting over lunch",
                "attendees": ["client@company.com"]
            }
        ]
        
        return {
            "status": "success",
            "events": events,
            "count": len(events),
            "source": "placeholder"
        }
    
    def create_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event."""
        if self.calendar_configured and self.service:
            return self._create_real_calendar_event(event_data)
        else:
            return self._create_placeholder_event(event_data)
    
    def _create_real_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a real calendar event in Google Calendar."""
        try:
            event = {
                'summary': event_data.get('title', 'New Event'),
                'location': event_data.get('location', ''),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data.get('start'),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': event_data.get('end'),
                    'timeZone': 'America/New_York',
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "status": "success",
                "event_id": event['id'],
                "message": f"Event '{event['summary']}' created successfully",
                "source": "google_calendar"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create calendar event: {str(e)}",
                "source": "google_calendar"
            }
    
    def _create_placeholder_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a placeholder calendar event."""
        return {
            "status": "success",
            "event_id": f"placeholder_{datetime.datetime.now().timestamp()}",
            "message": f"Placeholder event '{event_data.get('title', 'New Event')}' created",
            "source": "placeholder"
        }
    
    def get_calendar_status(self) -> Dict[str, Any]:
        """Get calendar service status."""
        return {
            "configured": self.calendar_configured,
            "service_available": self.service is not None,
            "credentials_file": self.credentials_file
        }

# Global instance
calendar_service = EnhancedCalendar()

# Convenience functions
def get_calendar_events(user_id: str = "demo-user", max_results: int = 10) -> Dict[str, Any]:
    return calendar_service.get_calendar_events(user_id, max_results)

def create_calendar_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    return calendar_service.create_calendar_event(event_data)

def get_calendar_status() -> Dict[str, Any]:
    return calendar_service.get_calendar_status() 