# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ruff: noqa: E722
import subprocess
from typing import Dict, Any

import google.auth
from google.api_core.client_options import ClientOptions
from google.api_core.gapic_v1.client_info import ClientInfo
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    PredictionServiceClient,
)
from google.cloud.aiplatform_v1beta1.types.prediction_service import (
    CountTokensRequest,
)

from src.cli.utils.version import PACKAGE_NAME, get_current_version


class GCPManager:
    """Centralized GCP operations and credential management.
    
    This class encapsulates GCP-related operations including credential verification,
    client configuration, and Vertex AI connectivity checks, implementing DRY principles
    for common GCP patterns.
    """
    
    def __init__(self, project_id: str | None = None, location: str = "us-central1"):
        """Initialize GCP manager with optional project and location.
        
        Args:
            project_id: GCP project ID. If None, will be detected from credentials.
            location: GCP region/location for services.
        """
        self.project_id = project_id
        self.location = location
        self._credentials = None
        self._client_info = None
    
    def get_user_agent(self) -> str:
        """Returns custom user agent header string."""
        version = get_current_version()
        return f"{version}-{PACKAGE_NAME}/{version}-{PACKAGE_NAME}"
    
    def get_client_info(self) -> ClientInfo:
        """Returns ClientInfo with custom user agent.
        
        Uses caching to avoid recreating the same ClientInfo object.
        """
        if self._client_info is None:
            user_agent = self.get_user_agent()
            self._client_info = ClientInfo(
                client_library_version=user_agent, 
                user_agent=user_agent
            )
        return self._client_info
    
    def get_credentials(self) -> tuple[Any, str | None]:
        """Get and cache GCP credentials and project ID.
        
        Returns:
            Tuple of (credentials, project_id)
        """
        if self._credentials is None:
            credentials, project = google.auth.default()
            self._credentials = credentials
            if self.project_id is None:
                self.project_id = project
        return self._credentials, self.project_id
    
    def create_dummy_request(self, project_id: str | None = None) -> CountTokensRequest:
        """Creates a simple test request for Gemini.
        
        Args:
            project_id: Override project ID for the request.
        """
        project = project_id or self.project_id
        if not project:
            raise ValueError("Project ID must be provided or configured")
            
        return CountTokensRequest(
            contents=[{"role": "user", "parts": [{"text": "Hi"}]}],
            endpoint=f"projects/{project}/locations/global/publishers/google/models/gemini-2.0-flash",
        )
    
    def verify_vertex_connection(self, project_id: str | None = None, location: str | None = None) -> None:
        """Verifies Vertex AI connection with a test Gemini request.
        
        Args:
            project_id: Override project ID for verification.
            location: Override location for verification.
        """
        project = project_id or self.project_id
        loc = location or self.location
        
        credentials, _ = self.get_credentials()
        
        client = PredictionServiceClient(
            credentials=credentials,
            client_options=ClientOptions(
                api_endpoint=f"{loc}-aiplatform.googleapis.com"
            ),
            client_info=self.get_client_info(),
            transport=initializer.global_config._api_transport,
        )
        
        request = self.create_dummy_request(project)
        client.count_tokens(request=request)
    
    def _get_account_from_credentials(self, credentials: Any) -> str | None:
        """Extract account email from credentials using multiple methods.
        
        Args:
            credentials: GCP credentials object.
            
        Returns:
            Account email string or None if not found.
        """
        # Method 1: Try _account attribute
        if hasattr(credentials, "_account"):
            return credentials._account

        # Method 2: Try service_account_email
        if hasattr(credentials, "service_account_email"):
            return credentials.service_account_email

        # Method 3: Try getting from token info if available
        if hasattr(credentials, "id_token"):
            try:
                import jwt
                decoded = jwt.decode(
                    credentials.id_token, options={"verify_signature": False}
                )
                return decoded.get("email")
            except:
                pass
        
        return None
    
    def _get_account_from_gcloud(self) -> str | None:
        """Get account from gcloud config as fallback method.
        
        Returns:
            Account email string or None if not available.
        """
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "account"],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() if result.stdout.strip() else None
        except:
            return None
    
    def verify_credentials(self) -> Dict[str, Any]:
        """Verify GCP credentials and return current project and account.
        
        Returns:
            Dictionary containing project and account information.
            
        Raises:
            Exception: If credential verification fails.
        """
        try:
            credentials, project = self.get_credentials()
            
            # Try multiple methods to get account email
            account = (
                self._get_account_from_credentials(credentials) or
                self._get_account_from_gcloud() or
                "Unknown account"
            )
            
            return {"project": project, "account": account}
            
        except Exception as e:
            raise Exception(f"Failed to verify GCP credentials: {e!s}") from e


# Global instance for backward compatibility
_default_manager = GCPManager()

# Convenience functions that delegate to the default manager
def get_user_agent() -> str:
    """Returns custom user agent header string using the default manager."""
    return _default_manager.get_user_agent()

def get_client_info() -> ClientInfo:
    """Returns ClientInfo with custom user agent using the default manager."""
    return _default_manager.get_client_info()

def get_dummy_request(project_id: str) -> CountTokensRequest:
    """Creates a simple test request for Gemini using the default manager."""
    return _default_manager.create_dummy_request(project_id)

def verify_vertex_connection(project_id: str, location: str = "us-central1") -> None:
    """Verifies Vertex AI connection using the default manager."""
    _default_manager.verify_vertex_connection(project_id, location)

def verify_credentials() -> Dict[str, Any]:
    """Verify GCP credentials using the default manager."""
    return _default_manager.verify_credentials()
