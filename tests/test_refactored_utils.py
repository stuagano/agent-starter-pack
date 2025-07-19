"""
Comprehensive test suite for refactored utility classes.

This module tests the DRY-compliant, class-based refactoring of utility functions
to ensure functionality is preserved while improving code organization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import yaml
import base64

# Import the refactored classes
from src.cli.utils.logging import CLILogger, handle_cli_error, print_info
from src.cli.utils.gcp import GCPManager, get_user_agent, verify_credentials
from src.frontends.streamlit.frontend.utils.chat_utils import (
    ChatProcessor, clean_text, sanitize_messages
)
from src.frontends.streamlit.frontend.utils.multimodal_utils import (
    Base64Handler, GCSManager, MediaContentProcessor, 
    format_content, get_gcs_blob_mime_type
)


class TestCLILogger:
    """Test suite for CLILogger class."""
    
    def test_cli_logger_initialization(self):
        """Test CLILogger initialization with and without console."""
        # Test with default console
        logger = CLILogger()
        assert logger.console is not None
        
        # Test with custom console
        mock_console = Mock()
        logger = CLILogger(console=mock_console)
        assert logger.console == mock_console
    
    def test_print_methods(self):
        """Test all print methods use correct styling."""
        mock_console = Mock()
        logger = CLILogger(console=mock_console)
        
        logger.print_info("test info")
        mock_console.print.assert_called_with("test info", style="bold blue")
        
        logger.print_success("test success")
        mock_console.print.assert_called_with("test success", style="bold green")
        
        logger.print_warning("test warning")
        mock_console.print.assert_called_with("test warning", style="bold yellow")
        
        logger.print_error("test error")
        mock_console.print.assert_called_with("test error", style="bold red")
    
    def test_handle_cli_error_decorator(self):
        """Test error handling decorator functionality."""
        mock_console = Mock()
        logger = CLILogger(console=mock_console)
        
        @logger.handle_cli_error
        def test_function():
            return "success"
        
        @logger.handle_cli_error
        def failing_function():
            raise ValueError("test error")
        
        # Test successful execution
        result = test_function()
        assert result == "success"
        
        # Test error handling
        with pytest.raises(SystemExit) as exc_info:
            failing_function()
        assert exc_info.value.code == 1
        mock_console.print.assert_called_with("Error: test error", style="bold red")
    
    def test_backward_compatibility_functions(self):
        """Test that standalone functions delegate to default logger."""
        with patch('src.cli.utils.logging._default_logger') as mock_logger:
            handle_cli_error(lambda: None)
            mock_logger.handle_cli_error.assert_called_once()
            
            print_info("test")
            mock_logger.print_info.assert_called_with("test", "bold blue")


class TestGCPManager:
    """Test suite for GCPManager class."""
    
    def test_gcp_manager_initialization(self):
        """Test GCPManager initialization."""
        manager = GCPManager()
        assert manager.project_id is None
        assert manager.location == "us-central1"
        assert manager._credentials is None
        assert manager._client_info is None
        
        manager = GCPManager(project_id="test-project", location="us-west1")
        assert manager.project_id == "test-project"
        assert manager.location == "us-west1"
    
    @patch('src.cli.utils.gcp.get_current_version')
    @patch('src.cli.utils.gcp.PACKAGE_NAME', 'test-package')
    def test_get_user_agent(self, mock_version):
        """Test user agent generation."""
        mock_version.return_value = "1.0.0"
        manager = GCPManager()
        user_agent = manager.get_user_agent()
        assert user_agent == "1.0.0-test-package/1.0.0-test-package"
    
    def test_get_client_info_caching(self):
        """Test ClientInfo caching behavior."""
        manager = GCPManager()
        
        with patch.object(manager, 'get_user_agent', return_value="test-agent"):
            client_info1 = manager.get_client_info()
            client_info2 = manager.get_client_info()
            
            # Should return the same cached instance
            assert client_info1 is client_info2
    
    @patch('google.auth.default')
    def test_get_credentials_caching(self, mock_auth):
        """Test credentials caching behavior."""
        mock_creds = Mock()
        mock_auth.return_value = (mock_creds, "test-project")
        
        manager = GCPManager()
        creds1, project1 = manager.get_credentials()
        creds2, project2 = manager.get_credentials()
        
        # Should only call google.auth.default once due to caching
        assert mock_auth.call_count == 1
        assert creds1 is creds2
        assert project1 == project2 == "test-project"
    
    def test_create_dummy_request(self):
        """Test dummy request creation."""
        manager = GCPManager(project_id="test-project")
        request = manager.create_dummy_request()
        
        assert request.contents[0]["role"] == "user"
        assert request.contents[0]["parts"][0]["text"] == "Hi"
        assert "test-project" in request.endpoint
    
    def test_account_extraction_methods(self):
        """Test different methods of extracting account information."""
        manager = GCPManager()
        
        # Test _account attribute
        mock_creds = Mock()
        mock_creds._account = "test@example.com"
        result = manager._get_account_from_credentials(mock_creds)
        assert result == "test@example.com"
        
        # Test service_account_email
        mock_creds = Mock()
        del mock_creds._account  # Remove _account attribute
        mock_creds.service_account_email = "service@example.com"
        result = manager._get_account_from_credentials(mock_creds)
        assert result == "service@example.com"
    
    def test_backward_compatibility_functions(self):
        """Test that standalone functions delegate to default manager."""
        with patch('src.cli.utils.gcp._default_manager') as mock_manager:
            get_user_agent()
            mock_manager.get_user_agent.assert_called_once()
            
            verify_credentials()
            mock_manager.verify_credentials.assert_called_once()


class TestChatProcessor:
    """Test suite for ChatProcessor class."""
    
    def test_chat_processor_initialization(self):
        """Test ChatProcessor initialization."""
        processor = ChatProcessor()
        assert ".saved_chats" in processor.saved_chat_path
        
        custom_path = "/tmp/custom_chats"
        processor = ChatProcessor(saved_chat_path=custom_path)
        assert processor.saved_chat_path == custom_path
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        processor = ChatProcessor()
        
        # Test empty text
        assert processor.clean_text("") == ""
        assert processor.clean_text(None) is None
        
        # Test newline removal
        assert processor.clean_text("\nhello\n") == "hello"
        assert processor.clean_text("\nhello") == "hello"
        assert processor.clean_text("hello\n") == "hello"
        assert processor.clean_text("hello") == "hello"
    
    def test_sanitize_message_content(self):
        """Test message content sanitization."""
        processor = ChatProcessor()
        
        # Test string content
        result = processor.sanitize_message_content("\ntest content\n")
        assert result == "test content"
        
        # Test list content
        content = [
            {"type": "text", "text": "\ntest text\n"},
            {"type": "image", "url": "test.jpg"}
        ]
        result = processor.sanitize_message_content(content)
        assert result[0]["text"] == "test text"
        assert result[1]["url"] == "test.jpg"  # Non-text parts unchanged
    
    def test_sanitize_messages(self):
        """Test messages sanitization."""
        processor = ChatProcessor()
        
        messages = [
            {"content": "\nHello\n", "role": "user"},
            {"content": [{"type": "text", "text": "\nWorld\n"}], "role": "assistant"}
        ]
        
        result = processor.sanitize_messages(messages)
        assert result[0]["content"] == "Hello"
        assert result[1]["content"][0]["text"] == "World"
    
    def test_save_chat_session(self):
        """Test chat session saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = ChatProcessor(saved_chat_path=temp_dir)
            
            session_data = {
                "messages": [{"content": "\ntest\n", "role": "user"}],
                "metadata": {"test": True}
            }
            
            filepath = processor.save_chat_session(session_data, "test_session")
            
            # Verify file was created
            assert os.path.exists(filepath)
            
            # Verify content
            with open(filepath, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert len(saved_data) == 1
            assert saved_data[0]["messages"][0]["content"] == "test"
            assert saved_data[0]["metadata"]["test"] is True
    
    def test_backward_compatibility_functions(self):
        """Test that standalone functions delegate to processor."""
        with patch('src.frontends.streamlit.frontend.utils.chat_utils.ChatProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            
            clean_text("test")
            mock_processor.clean_text.assert_called_with("test")
            
            sanitize_messages([])
            mock_processor.sanitize_messages.assert_called_with([])


class TestBase64Handler:
    """Test suite for Base64Handler class."""
    
    def test_encode_decode_roundtrip(self):
        """Test base64 encoding and decoding roundtrip."""
        test_data = b"Hello, World!"
        
        # Encode to base64
        encoded = Base64Handler.encode_bytes(test_data)
        assert isinstance(encoded, str)
        
        # Decode back to bytes
        decoded = Base64Handler.decode_string(encoded)
        assert decoded == test_data
    
    def test_create_data_url(self):
        """Test data URL creation."""
        test_data = b"test data"
        mime_type = "text/plain"
        
        data_url = Base64Handler.create_data_url(test_data, mime_type)
        
        assert data_url.startswith("data:text/plain;base64,")
        
        # Extract and verify base64 part
        base64_part = data_url.split(",")[1]
        decoded = base64.b64decode(base64_part)
        assert decoded == test_data


class TestGCSManager:
    """Test suite for GCSManager class."""
    
    def test_gcs_manager_initialization(self):
        """Test GCSManager initialization."""
        with patch('google.cloud.storage.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Test with default client
            manager = GCSManager()
            assert manager.storage_client == mock_client
            
            # Test with custom client
            custom_client = Mock()
            manager = GCSManager(storage_client=custom_client)
            assert manager.storage_client == custom_client
    
    def test_uri_to_https_url(self):
        """Test GS URI to HTTPS URL conversion."""
        gs_uri = "gs://test-bucket/path/to/file.jpg"
        expected_url = "https://storage.mtls.cloud.google.com/test-bucket/path%2Fto%2Ffile.jpg"
        
        result = GCSManager.uri_to_https_url(gs_uri)
        assert result == expected_url
        
        # Test invalid URI
        with pytest.raises(ValueError, match="Invalid GS URI format"):
            GCSManager.uri_to_https_url("invalid://uri")
    
    @patch('google.cloud.storage.Client')
    def test_get_blob_mime_type(self, mock_client_class):
        """Test blob MIME type retrieval."""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_client_class.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.content_type = "image/jpeg"
        
        manager = GCSManager()
        result = manager.get_blob_mime_type("gs://test-bucket/test-file.jpg")
        
        assert result == "image/jpeg"
        mock_client.bucket.assert_called_with("test-bucket")
        mock_bucket.blob.assert_called_with("test-file.jpg")
        mock_blob.reload.assert_called_once()


class TestMediaContentProcessor:
    """Test suite for MediaContentProcessor class."""
    
    def test_media_processor_initialization(self):
        """Test MediaContentProcessor initialization."""
        processor = MediaContentProcessor()
        assert isinstance(processor.gcs_manager, GCSManager)
        assert isinstance(processor.base64_handler, Base64Handler)
        
        # Test with custom GCS manager
        custom_gcs = Mock()
        processor = MediaContentProcessor(gcs_manager=custom_gcs)
        assert processor.gcs_manager == custom_gcs
    
    def test_format_content_string(self):
        """Test content formatting with string input."""
        processor = MediaContentProcessor()
        
        result = processor.format_content("Simple text content")
        assert result == "Simple text content"
    
    def test_format_content_single_text(self):
        """Test content formatting with single text part."""
        processor = MediaContentProcessor()
        
        content = [{"type": "text", "text": "Single text part"}]
        result = processor.format_content(content)
        assert result == "Single text part"
    
    def test_format_content_multimodal(self):
        """Test content formatting with multimodal content."""
        processor = MediaContentProcessor()
        
        content = [
            {"type": "text", "text": "Text content"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,test"}},
            {"type": "media", "data": "test", "file_name": "test.pdf"},
        ]
        
        result = processor.format_content(content)
        
        assert "Media:" in result
        assert "Text content" in result
        assert 'img src="data:image/png;base64,test"' in result
        assert "Local media: test.pdf" in result
    
    def test_create_local_content_part_image(self):
        """Test local content part creation for images."""
        processor = MediaContentProcessor()
        
        mock_file = Mock()
        mock_file.read.return_value = b"fake image data"
        mock_file.type = "image/png"
        mock_file.name = "test.png"
        
        result = processor.create_local_content_part(mock_file)
        
        assert result["type"] == "image_url"
        assert result["file_name"] == "test.png"
        assert result["image_url"]["url"].startswith("data:image/png;base64,")
    
    def test_create_local_content_part_non_image(self):
        """Test local content part creation for non-images."""
        processor = MediaContentProcessor()
        
        mock_file = Mock()
        mock_file.read.return_value = b"fake file data"
        mock_file.type = "application/pdf"
        mock_file.name = "test.pdf"
        
        result = processor.create_local_content_part(mock_file)
        
        assert result["type"] == "media"
        assert result["file_name"] == "test.pdf"
        assert result["mime_type"] == "application/pdf"
        assert "data" in result
    
    def test_get_parts_from_files(self):
        """Test processing files and GCS URIs into content parts."""
        processor = MediaContentProcessor()
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.read.return_value = b"test data"
        mock_file.type = "text/plain"
        mock_file.name = "test.txt"
        
        # Test local file processing
        parts = processor.get_parts_from_files(
            upload_gcs_checkbox=False,
            uploaded_files=[mock_file],
            gcs_uris=""
        )
        
        assert len(parts) == 1
        assert parts[0]["type"] == "media"
        assert parts[0]["file_name"] == "test.txt"
        
        # Test GCS URI processing
        with patch.object(processor.gcs_manager, 'get_blob_mime_type', return_value="image/jpeg"):
            parts = processor.get_parts_from_files(
                upload_gcs_checkbox=True,
                uploaded_files=[],
                gcs_uris="gs://bucket/file1.jpg, gs://bucket/file2.jpg"
            )
            
            assert len(parts) == 2
            assert all(part["type"] == "media" for part in parts)
            assert parts[0]["file_uri"] == "gs://bucket/file1.jpg"
            assert parts[1]["file_uri"] == "gs://bucket/file2.jpg"
    
    def test_backward_compatibility_functions(self):
        """Test that standalone functions delegate to default processor."""
        with patch('src.frontends.streamlit.frontend.utils.multimodal_utils._get_default_processor') as mock_processor:
            mock_processor.return_value = Mock()
            format_content("test")
            mock_processor.return_value.format_content.assert_called_with("test")
        
        with patch('src.frontends.streamlit.frontend.utils.multimodal_utils._get_default_gcs_manager') as mock_gcs:
            mock_gcs.return_value = Mock()
            get_gcs_blob_mime_type("gs://test/file")
            mock_gcs.return_value.get_blob_mime_type.assert_called_with("gs://test/file")


class TestIntegration:
    """Integration tests for refactored classes working together."""
    
    def test_cli_logger_with_gcp_manager(self):
        """Test CLI logger working with GCP manager for error handling."""
        logger = CLILogger()
        manager = GCPManager()
        
        @logger.handle_cli_error
        def test_gcp_operation():
            # This would normally fail without proper credentials
            return manager.get_user_agent()
        
        # Should work for user agent (doesn't require credentials)
        result = test_gcp_operation()
        assert isinstance(result, str)
    
    def test_chat_processor_with_media_processor(self):
        """Test chat processor working with media processor."""
        chat_processor = ChatProcessor()
        media_processor = MediaContentProcessor()
        
        # Create multimodal message content
        content = [
            {"type": "text", "text": "\nProcessed text\n"},
            {"type": "media", "file_name": "test.pdf", "data": "base64data"}
        ]
        
        # Sanitize the content
        sanitized = chat_processor.sanitize_message_content(content)
        
        # Format for display
        formatted = media_processor.format_content(sanitized)
        
        assert "Processed text" in formatted
        assert "Local media: test.pdf" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])