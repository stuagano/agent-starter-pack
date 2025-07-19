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

import base64
from typing import Any, Dict, List
from urllib.parse import quote

from google.cloud import storage

# Constants for help messages - centralized to follow DRY principles
HELP_MESSAGE_MULTIMODALITY = (
    "For Gemini models to access the URIs you provide, store them in "
    "Google Cloud Storage buckets within the same project used by Gemini."
)

HELP_GCS_CHECKBOX = (
    "Enabling GCS upload will increase the app observability by avoiding"
    " forwarding and logging large byte strings within the app."
)


class Base64Handler:
    """Utility class for base64 encoding/decoding operations.
    
    Centralizes base64 operations to eliminate code duplication across
    the multimedia processing pipeline.
    """
    
    @staticmethod
    def encode_bytes(data: bytes) -> str:
        """Encode bytes to base64 string.
        
        Args:
            data: Bytes data to encode.
            
        Returns:
            Base64 encoded string.
        """
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def decode_string(data: str) -> bytes:
        """Decode base64 string to bytes.
        
        Args:
            data: Base64 string to decode.
            
        Returns:
            Decoded bytes.
        """
        return base64.b64decode(data)
    
    @staticmethod
    def create_data_url(data: bytes, mime_type: str) -> str:
        """Create a data URL from bytes and MIME type.
        
        Args:
            data: Bytes data for the URL.
            mime_type: MIME type of the data.
            
        Returns:
            Complete data URL string.
        """
        encoded_data = Base64Handler.encode_bytes(data)
        return f"data:{mime_type};base64,{encoded_data}"


class GCSManager:
    """Google Cloud Storage operations manager.
    
    Centralizes GCS operations to eliminate duplication and provide
    consistent error handling and URI management.
    """
    
    def __init__(self, storage_client: storage.Client | None = None):
        """Initialize GCS manager with optional client.
        
        Args:
            storage_client: Optional GCS client. If None, creates default client.
        """
        self.storage_client = storage_client or storage.Client()
    
    def get_blob_mime_type(self, gcs_uri: str) -> str | None:
        """Fetches the MIME type (content type) of a Google Cloud Storage blob.

        Args:
            gcs_uri: The GCS URI of the blob in the format "gs://bucket-name/object-name".

        Returns:
            The MIME type of the blob (e.g., "image/jpeg", "text/plain") if found,
            or None if the blob does not exist or an error occurs.
        """
        try:
            bucket_name, object_name = gcs_uri.replace("gs://", "").split("/", 1)
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.reload()
            return blob.content_type
        except Exception as e:
            print(f"Error retrieving MIME type for {gcs_uri}: {e}")
            return None
    
    def upload_bytes(
        self,
        bucket_name: str,
        blob_name: str,
        file_bytes: bytes,
        content_type: str | None = None,
    ) -> str:
        """Uploads a bytes object to Google Cloud Storage and returns the GCS URI.

        Args:
            bucket_name: The name of the GCS bucket.
            blob_name: The desired name for the uploaded file in GCS.
            file_bytes: The file's content as a bytes object.
            content_type: The MIME type of the file (e.g., "image/png").
                If not provided, GCS will try to infer it.

        Returns:
            The GCS URI (gs://bucket_name/blob_name) of the uploaded file.

        Raises:
            GoogleCloudError: If there's an issue with the GCS operation.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data=file_bytes, content_type=content_type)
        return f"gs://{bucket_name}/{blob_name}"
    
    @staticmethod
    def uri_to_https_url(gs_uri: str) -> str:
        """Converts a GS URI to an HTTPS URL without authentication.

        Args:
            gs_uri: The GS URI in the format gs://<bucket>/<object>.

        Returns:
            The corresponding HTTPS URL.
            
        Raises:
            ValueError: If the GS URI format is invalid.
        """
        if not gs_uri.startswith("gs://"):
            raise ValueError("Invalid GS URI format")

        gs_uri_clean = gs_uri[5:]
        bucket_name, object_name = gs_uri_clean.split("/", 1)
        object_name = quote(object_name)

        return f"https://storage.mtls.cloud.google.com/{bucket_name}/{object_name}"


class MediaContentProcessor:
    """Processes multimedia content for chat applications.
    
    Handles content formatting, file processing, and integration
    with storage systems while maintaining DRY principles.
    """
    
    def __init__(self, gcs_manager: GCSManager | None = None):
        """Initialize media processor with optional GCS manager.
        
        Args:
            gcs_manager: Optional GCS manager. If None, creates default instance.
        """
        self.gcs_manager = gcs_manager or GCSManager()
        self.base64_handler = Base64Handler()
    
    def format_content(self, content: str | List[Dict[str, Any]]) -> str:
        """Formats content as a string, handling both text and multimedia inputs.
        
        Args:
            content: Content to format (string or list of content parts).
            
        Returns:
            Formatted markdown string representation.
        """
        if isinstance(content, str):
            return content
            
        if len(content) == 1 and content[0]["type"] == "text":
            return content[0]["text"]
        
        markdown_parts = ["Media:\n"]
        text_content = ""
        
        for part in content:
            if part["type"] == "text":
                text_content = part["text"]
            elif part["type"] == "image_url":
                image_url = part["image_url"]["url"]
                image_markdown = f'<img src="{image_url}" width="100">'
                markdown_parts.append(f"- {image_markdown}\n")
            elif part["type"] == "media":
                if "data" in part:
                    markdown_parts.append(f"- Local media: {part['file_name']}\n")
                elif "file_uri" in part:
                    if "image" in part["mime_type"]:
                        image_url = self.gcs_manager.uri_to_https_url(part["file_uri"])
                        image_markdown = f'<img src="{image_url}" width="100">'
                        markdown_parts.append(f"- {image_markdown}\n")
                    else:
                        media_url = self.gcs_manager.uri_to_https_url(part["file_uri"])
                        markdown_parts.append(
                            f"- Remote media: [{part['file_uri']}]({media_url})\n"
                        )
        
        return "".join(markdown_parts) + f"\n{text_content}"
    
    def create_local_content_part(self, uploaded_file: Any) -> Dict[str, Any]:
        """Create content part from local uploaded file.
        
        Args:
            uploaded_file: Uploaded file object with read(), type, and name attributes.
            
        Returns:
            Content part dictionary for local file.
        """
        file_bytes = uploaded_file.read()
        
        if "image" in uploaded_file.type:
            return {
                "type": "image_url",
                "image_url": {
                    "url": self.base64_handler.create_data_url(file_bytes, uploaded_file.type)
                },
                "file_name": uploaded_file.name,
            }
        else:
            return {
                "type": "media",
                "data": self.base64_handler.encode_bytes(file_bytes),
                "file_name": uploaded_file.name,
                "mime_type": uploaded_file.type,
            }
    
    def create_gcs_content_part(self, uri: str) -> Dict[str, Any]:
        """Create content part from GCS URI.
        
        Args:
            uri: GCS URI string.
            
        Returns:
            Content part dictionary for GCS file.
        """
        return {
            "type": "media",
            "file_uri": uri,
            "mime_type": self.gcs_manager.get_blob_mime_type(uri),
        }
    
    def get_parts_from_files(
        self, 
        upload_gcs_checkbox: bool, 
        uploaded_files: List[Any], 
        gcs_uris: str
    ) -> List[Dict[str, Any]]:
        """Processes uploaded files and GCS URIs to create a list of content parts.
        
        Args:
            upload_gcs_checkbox: Whether to upload to GCS.
            uploaded_files: List of uploaded file objects.
            gcs_uris: Comma-separated string of GCS URIs.
            
        Returns:
            List of content part dictionaries.
        """
        parts = []
        
        # Process local files if not uploading to GCS
        if not upload_gcs_checkbox:
            for uploaded_file in uploaded_files:
                parts.append(self.create_local_content_part(uploaded_file))
        
        # Process GCS URIs
        if gcs_uris:
            for uri in gcs_uris.split(","):
                uri = uri.strip()
                if uri:
                    parts.append(self.create_gcs_content_part(uri))
        
        return parts
    
    def upload_files_to_gcs(self, st: Any, bucket_name: str, files_to_upload: List[Any]) -> None:
        """Upload multiple files to Google Cloud Storage and store URIs in session state.
        
        Args:
            st: Streamlit module instance.
            bucket_name: Target GCS bucket name.
            files_to_upload: List of files to upload.
        """
        bucket_name = bucket_name.replace("gs://", "")
        uploaded_uris = []
        
        for file in files_to_upload:
            if file:
                file_bytes = file.read()
                gcs_uri = self.gcs_manager.upload_bytes(
                    bucket_name=bucket_name,
                    blob_name=file.name,
                    file_bytes=file_bytes,
                    content_type=file.type,
                )
                uploaded_uris.append(gcs_uri)
        
        st.session_state.uploader_key += 1
        st.session_state["gcs_uris_to_be_sent"] = ",".join(uploaded_uris)


# Global instances for backward compatibility - use lazy initialization
_default_gcs_manager = None
_default_processor = None

def _get_default_gcs_manager():
    """Get the default GCS manager with lazy initialization."""
    global _default_gcs_manager
    if _default_gcs_manager is None:
        _default_gcs_manager = GCSManager()
    return _default_gcs_manager

def _get_default_processor():
    """Get the default processor with lazy initialization."""
    global _default_processor
    if _default_processor is None:
        _default_processor = MediaContentProcessor(_get_default_gcs_manager())
    return _default_processor

# Convenience functions that delegate to the default instances
def format_content(content: str | List[Dict[str, Any]]) -> str:
    """Formats content as a string, handling both text and multimedia inputs."""
    return _get_default_processor().format_content(content)

def get_gcs_blob_mime_type(gcs_uri: str) -> str | None:
    """Fetches the MIME type of a Google Cloud Storage blob."""
    return _get_default_gcs_manager().get_blob_mime_type(gcs_uri)

def get_parts_from_files(
    upload_gcs_checkbox: bool, uploaded_files: List[Any], gcs_uris: str
) -> List[Dict[str, Any]]:
    """Processes uploaded files and GCS URIs to create a list of content parts."""
    return _get_default_processor().get_parts_from_files(upload_gcs_checkbox, uploaded_files, gcs_uris)

def upload_bytes_to_gcs(
    bucket_name: str,
    blob_name: str,
    file_bytes: bytes,
    content_type: str | None = None,
) -> str:
    """Uploads a bytes object to Google Cloud Storage and returns the GCS URI."""
    return _get_default_gcs_manager().upload_bytes(bucket_name, blob_name, file_bytes, content_type)

def gs_uri_to_https_url(gs_uri: str) -> str:
    """Converts a GS URI to an HTTPS URL without authentication."""
    return GCSManager.uri_to_https_url(gs_uri)

def upload_files_to_gcs(st: Any, bucket_name: str, files_to_upload: List[Any]) -> None:
    """Upload multiple files to Google Cloud Storage and store URIs in session state."""
    _get_default_processor().upload_files_to_gcs(st, bucket_name, files_to_upload)
