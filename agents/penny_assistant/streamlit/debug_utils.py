import streamlit as st
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

class DebugUtils:
    def __init__(self):
        self.config_file = Path("config/setup_status.json")
        self.backend_config_file = Path("../backend/setup_status.json")
    
    def render_debug_page(self):
        """Render the debugging page in Streamlit."""
        st.title("🐛 Debug & Troubleshooting")
        st.markdown("Use these tools to diagnose and fix configuration issues.")
        
        # Debug tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Configuration Check", 
            "🌐 Network Test", 
            "📁 File System", 
            "🔧 Service Test", 
            "📋 Logs & Errors"
        ])
        
        with tab1:
            self.render_config_check()
        
        with tab2:
            self.render_network_test()
        
        with tab3:
            self.render_file_system_check()
        
        with tab4:
            self.render_service_test()
        
        with tab5:
            self.render_logs_and_errors()
    
    def render_config_check(self):
        """Check configuration files and settings."""
        st.subheader("🔍 Configuration Check")
        
        # Check frontend config
        st.write("**Frontend Configuration:**")
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                st.success("✅ Frontend config file exists")
                
                # Display config summary
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Project ID:** {config.get('project_id', 'Not set')}")
                    st.write(f"**Region:** {config.get('region', 'Not set')}")
                with col2:
                    services = ['firestore', 'calendar', 'vertex_ai', 'vector_search']
                    for service in services:
                        status = "✅" if config.get(service, {}).get('configured', False) else "❌"
                        st.write(f"**{service.title()}:** {status}")
            except Exception as e:
                st.error(f"❌ Error reading frontend config: {e}")
        else:
            st.warning("⚠️ Frontend config file not found")
        
        # Check backend config
        st.write("**Backend Configuration:**")
        if self.backend_config_file.exists():
            try:
                with open(self.backend_config_file, 'r') as f:
                    backend_config = json.load(f)
                st.success("✅ Backend config file exists")
                
                # Compare configs
                if self.config_file.exists():
                    with open(self.config_file, 'r') as f:
                        frontend_config = json.load(f)
                    
                    if frontend_config == backend_config:
                        st.success("✅ Frontend and backend configs match")
                    else:
                        st.warning("⚠️ Frontend and backend configs differ")
                        if st.button("🔄 Sync Configs"):
                            self.sync_configs()
            except Exception as e:
                st.error(f"❌ Error reading backend config: {e}")
        else:
            st.warning("⚠️ Backend config file not found")
        
        # Environment variables
        st.write("**Environment Variables:**")
        env_vars = {
            'GOOGLE_CLOUD_PROJECT': os.getenv('GOOGLE_CLOUD_PROJECT'),
            'BACKEND_URL': os.getenv('BACKEND_URL'),
            'USER_ID': os.getenv('USER_ID'),
            'PORT': os.getenv('PORT')
        }
        
        for var, value in env_vars.items():
            if value:
                st.write(f"✅ **{var}:** {value}")
            else:
                st.write(f"❌ **{var}:** Not set")
    
    def render_network_test(self):
        """Test network connectivity and backend communication."""
        st.subheader("🌐 Network Test")
        
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:8080')
        
        # Test backend connectivity
        st.write(f"**Testing backend connectivity to:** {backend_url}")
        
        if st.button("🔍 Test Backend Connection"):
            try:
                import requests
                response = requests.get(f"{backend_url}/healthz", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Backend is responding")
                    st.json(response.json())
                else:
                    st.error(f"❌ Backend returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend")
            except requests.exceptions.Timeout:
                st.error("❌ Backend connection timeout")
            except Exception as e:
                st.error(f"❌ Network error: {e}")
        
        # Test specific endpoints
        st.write("**Test Specific Endpoints:**")
        endpoints = [
            ("Health Check", "/healthz"),
            ("PDF Health", "/api/v1/pdf/health"),
            ("Lists Status", "/api/v1/lists/status"),
            ("Calendar Health", "/api/v1/calendar/health")
        ]
        
        for name, endpoint in endpoints:
            if st.button(f"Test {name}"):
                try:
                    import requests
                    response = requests.get(f"{backend_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        st.success(f"✅ {name} endpoint working")
                        st.json(response.json())
                    else:
                        st.error(f"❌ {name} returned status {response.status_code}")
                except Exception as e:
                    st.error(f"❌ {name} test failed: {e}")
    
    def render_file_system_check(self):
        """Check file system and permissions."""
        st.subheader("📁 File System Check")
        
        # Check directories
        st.write("**Directory Structure:**")
        directories = [
            ("config", Path("config")),
            ("backend", Path("../backend")),
            ("backend config", Path("../backend/setup_status.json").parent)
        ]
        
        for name, path in directories:
            if path.exists():
                st.write(f"✅ **{name}:** {path.absolute()}")
            else:
                st.write(f"❌ **{name}:** Not found")
        
        # Check files
        st.write("**Configuration Files:**")
        files = [
            ("Frontend Config", self.config_file),
            ("Backend Config", self.backend_config_file),
            ("Calendar Credentials", Path("config/calendar_credentials.json"))
        ]
        
        for name, file_path in files:
            if file_path.exists():
                size = file_path.stat().st_size
                st.write(f"✅ **{name}:** {size} bytes")
            else:
                st.write(f"❌ **{name}:** Not found")
        
        # Check permissions
        st.write("**File Permissions:**")
        if st.button("🔍 Check Permissions"):
            try:
                # Check if we can read config
                if self.config_file.exists():
                    with open(self.config_file, 'r') as f:
                        f.read()
                    st.success("✅ Can read frontend config")
                
                # Check if we can write to config directory
                test_file = Path("config/test_write.tmp")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    test_file.unlink()
                    st.success("✅ Can write to config directory")
                except Exception as e:
                    st.error(f"❌ Cannot write to config directory: {e}")
                
            except Exception as e:
                st.error(f"❌ Permission check failed: {e}")
    
    def render_service_test(self):
        """Test individual services."""
        st.subheader("🔧 Service Test")
        
        # Load current config
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Test each service
        services = [
            ("Firestore", "firestore", self.test_firestore),
            ("Calendar", "calendar", self.test_calendar),
            ("Vertex AI", "vertex_ai", self.test_vertex_ai),
            ("Vector Search", "vector_search", self.test_vector_search)
        ]
        
        for service_name, service_key, test_func in services:
            st.write(f"**{service_name}:**")
            if config.get(service_key, {}).get('configured', False):
                if st.button(f"Test {service_name}"):
                    test_func(config.get(service_key, {}))
            else:
                st.info(f"ℹ️ {service_name} not configured")
    
    def render_logs_and_errors(self):
        """Display logs and common error solutions."""
        st.subheader("📋 Logs & Common Issues")
        
        # Common issues and solutions
        st.write("**Common Issues & Solutions:**")
        
        issues = [
            {
                "issue": "Backend not responding",
                "symptoms": ["Connection error", "Timeout", "404 errors"],
                "solutions": [
                    "Check if backend is deployed: `gcloud run services list`",
                    "Verify BACKEND_URL environment variable",
                    "Check backend logs: `gcloud run services logs read penny-assistant-backend`"
                ]
            },
            {
                "issue": "Configuration not saving",
                "symptoms": ["Settings reset after refresh", "Export fails"],
                "solutions": [
                    "Check file permissions in config directory",
                    "Verify config/setup_status.json is writable",
                    "Try refreshing the page and re-entering settings"
                ]
            },
            {
                "issue": "Google Cloud services not working",
                "symptoms": ["API errors", "Authentication failures", "Permission denied"],
                "solutions": [
                    "Verify Google Cloud project ID is correct",
                    "Check if APIs are enabled in Google Cloud Console",
                    "Ensure service account has proper permissions",
                    "Verify credentials files are uploaded correctly"
                ]
            },
            {
                "issue": "PDF upload fails",
                "symptoms": ["Upload timeout", "Processing errors", "Empty responses"],
                "solutions": [
                    "Check PDF file size (should be < 10MB)",
                    "Verify PDF is not corrupted",
                    "Check backend logs for processing errors",
                    "Ensure backend has sufficient memory allocated"
                ]
            }
        ]
        
        for issue in issues:
            with st.expander(f"🐛 {issue['issue']}"):
                st.write("**Symptoms:**")
                for symptom in issue['symptoms']:
                    st.write(f"• {symptom}")
                st.write("**Solutions:**")
                for solution in issue['solutions']:
                    st.write(f"• {solution}")
        
        # Debug commands
        st.write("**Debug Commands:**")
        debug_commands = [
            ("Check backend status", "gcloud run services describe penny-assistant-backend --region=us-central1"),
            ("View backend logs", "gcloud run services logs read penny-assistant-backend --region=us-central1"),
            ("Check frontend status", "gcloud run services describe penny-assistant-frontend --region=us-central1"),
            ("View frontend logs", "gcloud run services logs read penny-assistant-frontend --region=us-central1"),
            ("List all services", "gcloud run services list"),
            ("Check project", "gcloud config get-value project")
        ]
        
        for name, command in debug_commands:
            st.code(command, language="bash")
            if st.button(f"Copy {name}"):
                st.write("Command copied to clipboard!")
    
    def sync_configs(self):
        """Sync frontend and backend configurations."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Write to backend
                self.backend_config_file.parent.mkdir(exist_ok=True)
                with open(self.backend_config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                st.success("✅ Configurations synced successfully!")
            else:
                st.error("❌ Frontend config not found")
        except Exception as e:
            st.error(f"❌ Sync failed: {e}")
    
    def test_firestore(self, config):
        """Test Firestore connectivity."""
        try:
            from google.cloud import firestore
            project_id = config.get('project_id') or os.getenv('GOOGLE_CLOUD_PROJECT')
            if not project_id:
                st.error("❌ No project ID configured")
                return
            
            db = firestore.Client(project=project_id)
            # Try to access a collection
            collection = config.get('collection', 'user_lists')
            docs = db.collection(collection).limit(1).stream()
            list(docs)  # Force execution
            st.success("✅ Firestore connection successful")
        except Exception as e:
            st.error(f"❌ Firestore test failed: {e}")
    
    def test_calendar(self, config):
        """Test Google Calendar connectivity."""
        try:
            credentials_file = config.get('credentials_file')
            if not credentials_file or not Path(credentials_file).exists():
                st.error("❌ Calendar credentials file not found")
                return
            
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle
            
            SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
            
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            service = build('calendar', 'v3', credentials=creds)
            # Try to list calendars
            calendar_list = service.calendarList().list().execute()
            st.success("✅ Google Calendar connection successful")
            st.write(f"Found {len(calendar_list.get('items', []))} calendars")
        except Exception as e:
            st.error(f"❌ Calendar test failed: {e}")
    
    def test_vertex_ai(self, config):
        """Test Vertex AI connectivity."""
        try:
            from google.cloud import aiplatform
            project_id = config.get('project_id') or os.getenv('GOOGLE_CLOUD_PROJECT')
            if not project_id:
                st.error("❌ No project ID configured")
                return
            
            region = config.get('region', 'us-central1')
            aiplatform.init(project=project_id, location=region)
            
            # Try to list models
            from vertexai.language_models import TextEmbeddingModel
            model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
            st.success("✅ Vertex AI connection successful")
        except Exception as e:
            st.error(f"❌ Vertex AI test failed: {e}")
    
    def test_vector_search(self, config):
        """Test Vector Search connectivity."""
        try:
            # Vector Search test would go here
            # For now, just check if the service is configured
            index_name = config.get('index_name', 'penny-assistant-index')
            st.info(f"ℹ️ Vector Search index '{index_name}' configured")
            st.warning("⚠️ Vector Search testing not yet implemented")
        except Exception as e:
            st.error(f"❌ Vector Search test failed: {e}")

# Global instance
debug_utils = DebugUtils() 