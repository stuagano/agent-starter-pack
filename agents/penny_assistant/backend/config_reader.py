import json
import os
from pathlib import Path
from typing import Dict, Any

class ConfigReader:
    def __init__(self):
        self.config_file = Path("setup_status.json")
        self.frontend_config_file = Path("../streamlit/config/setup_status.json")
        self.setup_status = self.load_setup_status()
    
    def load_setup_status(self) -> Dict[str, Any]:
        """Load setup status from backend or frontend config file."""
        # Try backend config first
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load backend config: {e}")
        
        # Try frontend config
        if self.frontend_config_file.exists():
            try:
                with open(self.frontend_config_file, "r") as f:
                    config = json.load(f)
                    # Set environment variables from frontend config
                    if config.get("project_id"):
                        os.environ["GOOGLE_CLOUD_PROJECT"] = config["project_id"]
                    return config
            except Exception as e:
                print(f"Failed to load frontend config: {e}")
        
        # Return default config
        return {
            "firestore": {"configured": False, "collection": "user_lists"},
            "calendar": {"configured": False, "credentials_file": None},
            "vertex_ai": {"configured": False, "embedding_model": "textembedding-gecko@001"},
            "vector_search": {"configured": False, "index_name": "penny-assistant-index"},
            "project_id": None,
            "region": "us-central1"
        }
    
    def get_setup_status(self) -> Dict[str, Any]:
        """Get current setup status."""
        return self.setup_status
    
    def is_service_configured(self, service_name: str) -> bool:
        """Check if a specific service is configured."""
        return self.setup_status.get(service_name, {}).get("configured", False)
    
    def get_project_id(self) -> str:
        """Get the Google Cloud project ID."""
        return self.setup_status.get("project_id") or os.environ.get("GOOGLE_CLOUD_PROJECT")
    
    def get_region(self) -> str:
        """Get the Google Cloud region."""
        return self.setup_status.get("region", "us-central1")
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        return self.setup_status.get(service_name, {})
    
    def reload_config(self):
        """Reload configuration from file."""
        self.setup_status = self.load_setup_status()

# Global instance
config_reader = ConfigReader() 