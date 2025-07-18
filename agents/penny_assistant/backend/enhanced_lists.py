from typing import List, Dict, Any
import os
import json
import uuid
from datetime import datetime
from config_reader import config_reader

class EnhancedLists:
    def __init__(self):
        self.firestore_configured = config_reader.is_service_configured("firestore")
        self.local_storage_file = "local_lists.json"
        
        if self.firestore_configured:
            self.initialize_firestore()
        else:
            self.initialize_local_storage()
    
    def initialize_firestore(self):
        """Initialize Firestore client."""
        try:
            from google.cloud import firestore
            project_id = config_reader.get_project_id()
            self.db = firestore.Client(project=project_id)
            self.collection = config_reader.get_service_config("firestore").get("collection", "user_lists")
            print("✅ Firestore initialized successfully")
        except Exception as e:
            print(f"⚠️  Firestore initialization failed: {e}")
            self.firestore_configured = False
            self.initialize_local_storage()
    
    def initialize_local_storage(self):
        """Initialize local storage for lists."""
        self.db = None
        self.collection = None
        # Ensure local storage file exists
        if not os.path.exists(self.local_storage_file):
            with open(self.local_storage_file, 'w') as f:
                json.dump({}, f)
        print("✅ Local storage initialized for lists")
    
    def create_list(self, user_id: str, name: str) -> str:
        """Create a new list for a user."""
        if self.firestore_configured and self.db:
            return self._create_firestore_list(user_id, name)
        else:
            return self._create_local_list(user_id, name)
    
    def _create_firestore_list(self, user_id: str, name: str) -> str:
        """Create a list in Firestore."""
        try:
            doc_ref = self.db.collection(self.collection).document()
            doc_ref.set({
                "user_id": user_id,
                "name": name,
                "items": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            return doc_ref.id
        except Exception as e:
            print(f"⚠️  Firestore list creation failed: {e}")
            return self._create_local_list(user_id, name)
    
    def _create_local_list(self, user_id: str, name: str) -> str:
        """Create a list in local storage."""
        try:
            with open(self.local_storage_file, 'r') as f:
                data = json.load(f)
            
            list_id = str(uuid.uuid4())
            data[list_id] = {
                "user_id": user_id,
                "name": name,
                "items": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            with open(self.local_storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return list_id
        except Exception as e:
            print(f"⚠️  Local list creation failed: {e}")
            return str(uuid.uuid4())
    
    def get_lists(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all lists for a user."""
        if self.firestore_configured and self.db:
            return self._get_firestore_lists(user_id)
        else:
            return self._get_local_lists(user_id)
    
    def _get_firestore_lists(self, user_id: str) -> List[Dict[str, Any]]:
        """Get lists from Firestore."""
        try:
            docs = self.db.collection(self.collection).where("user_id", "==", user_id).stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"⚠️  Firestore list retrieval failed: {e}")
            return self._get_local_lists(user_id)
    
    def _get_local_lists(self, user_id: str) -> List[Dict[str, Any]]:
        """Get lists from local storage."""
        try:
            with open(self.local_storage_file, 'r') as f:
                data = json.load(f)
            
            user_lists = []
            for list_id, list_data in data.items():
                if list_data.get("user_id") == user_id:
                    user_lists.append({"id": list_id, **list_data})
            
            return user_lists
        except Exception as e:
            print(f"⚠️  Local list retrieval failed: {e}")
            return []
    
    def update_list(self, list_id: str, items: List[str]):
        """Update items in a list."""
        if self.firestore_configured and self.db:
            return self._update_firestore_list(list_id, items)
        else:
            return self._update_local_list(list_id, items)
    
    def _update_firestore_list(self, list_id: str, items: List[str]):
        """Update list in Firestore."""
        try:
            self.db.collection(self.collection).document(list_id).update({
                "items": items,
                "updated_at": datetime.now().isoformat()
            })
            return {"status": "success", "storage": "firestore"}
        except Exception as e:
            print(f"⚠️  Firestore list update failed: {e}")
            return self._update_local_list(list_id, items)
    
    def _update_local_list(self, list_id: str, items: List[str]):
        """Update list in local storage."""
        try:
            with open(self.local_storage_file, 'r') as f:
                data = json.load(f)
            
            if list_id in data:
                data[list_id]["items"] = items
                data[list_id]["updated_at"] = datetime.now().isoformat()
                
                with open(self.local_storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return {"status": "success", "storage": "local"}
            else:
                return {"status": "error", "message": "List not found"}
        except Exception as e:
            print(f"⚠️  Local list update failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_list(self, list_id: str):
        """Delete a list by ID."""
        if self.firestore_configured and self.db:
            return self._delete_firestore_list(list_id)
        else:
            return self._delete_local_list(list_id)
    
    def _delete_firestore_list(self, list_id: str):
        """Delete list from Firestore."""
        try:
            self.db.collection(self.collection).document(list_id).delete()
            return {"status": "success", "storage": "firestore"}
        except Exception as e:
            print(f"⚠️  Firestore list deletion failed: {e}")
            return self._delete_local_list(list_id)
    
    def _delete_local_list(self, list_id: str):
        """Delete list from local storage."""
        try:
            with open(self.local_storage_file, 'r') as f:
                data = json.load(f)
            
            if list_id in data:
                del data[list_id]
                
                with open(self.local_storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return {"status": "success", "storage": "local"}
            else:
                return {"status": "error", "message": "List not found"}
        except Exception as e:
            print(f"⚠️  Local list deletion failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_list_status(self) -> Dict[str, Any]:
        """Get list service status."""
        return {
            "firestore_configured": self.firestore_configured,
            "local_storage_available": os.path.exists(self.local_storage_file),
            "storage_method": "firestore" if self.firestore_configured else "local"
        }

# Global instance
lists_service = EnhancedLists()

# Convenience functions
def create_list(user_id: str, name: str) -> str:
    return lists_service.create_list(user_id, name)

def get_lists(user_id: str) -> List[Dict[str, Any]]:
    return lists_service.get_lists(user_id)

def update_list(list_id: str, items: List[str]):
    return lists_service.update_list(list_id, items)

def delete_list(list_id: str):
    return lists_service.delete_list(list_id)

def get_list_status() -> Dict[str, Any]:
    return lists_service.get_list_status() 