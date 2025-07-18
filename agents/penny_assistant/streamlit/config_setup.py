import streamlit as st
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class StreamlitConfigSetup:
    def __init__(self):
        self.config_file = Path("config/setup_status.json")
        self.config_file.parent.mkdir(exist_ok=True)
        self.setup_status = self.load_setup_status()
    
    def load_setup_status(self) -> Dict[str, Any]:
        """Load setup status from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Failed to load config: {e}")
        
        return {
            "firestore": {"configured": False, "collection": "user_lists"},
            "calendar": {"configured": False, "credentials_file": None},
            "vertex_ai": {"configured": False, "embedding_model": "textembedding-gecko@001"},
            "vector_search": {"configured": False, "index_name": "penny-assistant-index"},
            "project_id": None,
            "region": "us-central1"
        }
    
    def save_setup_status(self):
        """Save setup status to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.setup_status, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save config: {e}")
            return False
    
    def validate_project_id(self, project_id: str) -> bool:
        """Validate Google Cloud project ID format."""
        if not project_id:
            return False
        
        # Basic validation: should be lowercase, alphanumeric, hyphens
        import re
        pattern = r'^[a-z][a-z0-9-]{5,29}$'
        return bool(re.match(pattern, project_id))
    
    def validate_credentials_file(self, uploaded_file) -> bool:
        """Validate uploaded credentials file."""
        if not uploaded_file:
            return False
        
        try:
            # Try to parse as JSON
            content = uploaded_file.getvalue().decode('utf-8')
            json.loads(content)
            
            # Check for required fields
            data = json.loads(content)
            required_fields = ['client_id', 'client_secret', 'redirect_uris']
            return all(field in data for field in required_fields)
        except Exception:
            return False
    
    def render_config_page(self):
        """Render the configuration setup page in Streamlit."""
        st.title("🔧 Penny Assistant Configuration")
        st.markdown("Configure your Google Cloud services for Penny Assistant.")
        
        # Show current status
        self.render_current_status()
        
        # Project Configuration
        st.header("📋 Project Configuration")
        project_id = st.text_input(
            "Google Cloud Project ID",
            value=self.setup_status.get("project_id", ""),
            help="Your Google Cloud project ID (e.g., my-project-123456)"
        )
        
        # Validate project ID
        if project_id and not self.validate_project_id(project_id):
            st.error("❌ Invalid project ID format. Should be lowercase, 6-30 characters, alphanumeric with hyphens.")
        
        region = st.selectbox(
            "Google Cloud Region",
            ["us-central1", "us-east1", "us-west1", "europe-west1", "asia-northeast1"],
            index=0 if self.setup_status.get("region") == "us-central1" else 0
        )
        
        if st.button("💾 Save Project Settings"):
            if not project_id:
                st.error("❌ Project ID is required")
            elif not self.validate_project_id(project_id):
                st.error("❌ Invalid project ID format")
            else:
                self.setup_status["project_id"] = project_id
                self.setup_status["region"] = region
                if self.save_setup_status():
                    st.success("✅ Project settings saved!")
                    st.rerun()
        
        st.divider()
        
        # Firestore Configuration
        st.header("📝 Firestore Setup")
        st.markdown("Firestore is used for storing user lists and preferences.")
        
        firestore_configured = st.checkbox(
            "Enable Firestore",
            value=self.setup_status["firestore"]["configured"],
            help="Check this if you want to use Google Cloud Firestore for data storage"
        )
        
        if firestore_configured:
            collection_name = st.text_input(
                "Collection Name",
                value=self.setup_status["firestore"]["collection"],
                help="Name of the Firestore collection for user lists"
            )
            
            # Validate collection name
            if collection_name and not collection_name.replace('_', '').replace('-', '').isalnum():
                st.error("❌ Collection name should be alphanumeric with underscores or hyphens only.")
            
            st.info("""
            **To enable Firestore:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Select your project
            3. Navigate to Firestore Database
            4. Click 'Create Database'
            5. Choose 'Start in test mode' (for development)
            6. Select a location (us-central1 recommended)
            """)
        
        if st.button("💾 Save Firestore Settings"):
            if firestore_configured and not collection_name:
                st.error("❌ Collection name is required when Firestore is enabled")
            elif firestore_configured and collection_name and not collection_name.replace('_', '').replace('-', '').isalnum():
                st.error("❌ Invalid collection name format")
            else:
                self.setup_status["firestore"]["configured"] = firestore_configured
                if firestore_configured:
                    self.setup_status["firestore"]["collection"] = collection_name
                if self.save_setup_status():
                    st.success("✅ Firestore settings saved!")
                    st.rerun()
        
        st.divider()
        
        # Calendar Configuration
        st.header("📅 Google Calendar Setup")
        st.markdown("Google Calendar integration for viewing and managing events.")
        
        calendar_configured = st.checkbox(
            "Enable Google Calendar",
            value=self.setup_status["calendar"]["configured"],
            help="Check this if you want to integrate with Google Calendar"
        )
        
        if calendar_configured:
            st.info("""
            **To enable Google Calendar:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Select your project
            3. Navigate to APIs & Services > Library
            4. Search for 'Google Calendar API'
            5. Click 'Enable'
            6. Go to APIs & Services > Credentials
            7. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'
            8. Choose 'Web application'
            9. Add authorized redirect URIs:
               - http://localhost:8501
               - https://your-frontend-url (after deployment)
            10. Download the JSON credentials file
            """)
            
            credentials_file = st.file_uploader(
                "Upload OAuth2 Credentials JSON",
                type=['json'],
                help="Upload the OAuth2 credentials JSON file from Google Cloud Console"
            )
            
            if credentials_file:
                # Validate credentials file
                if self.validate_credentials_file(credentials_file):
                    st.success("✅ Credentials file is valid")
                    
                    # Save the uploaded file
                    creds_path = Path("config/calendar_credentials.json")
                    creds_path.parent.mkdir(exist_ok=True)
                    with open(creds_path, "wb") as f:
                        f.write(credentials_file.getvalue())
                    self.setup_status["calendar"]["credentials_file"] = str(creds_path)
                else:
                    st.error("❌ Invalid credentials file. Please upload a valid OAuth2 credentials JSON file.")
        
        if st.button("💾 Save Calendar Settings"):
            if calendar_configured and not credentials_file:
                st.error("❌ Credentials file is required when Calendar is enabled")
            else:
                self.setup_status["calendar"]["configured"] = calendar_configured
                if self.save_setup_status():
                    st.success("✅ Calendar settings saved!")
                    st.rerun()
        
        st.divider()
        
        # Vertex AI Configuration
        st.header("🤖 Vertex AI Setup")
        st.markdown("Vertex AI is used for text embeddings and AI model inference.")
        
        vertex_configured = st.checkbox(
            "Enable Vertex AI",
            value=self.setup_status["vertex_ai"]["configured"],
            help="Check this if you want to use Vertex AI for embeddings"
        )
        
        if vertex_configured:
            embedding_model = st.selectbox(
                "Embedding Model",
                ["textembedding-gecko@001", "textembedding-gecko@003"],
                index=0 if self.setup_status["vertex_ai"]["embedding_model"] == "textembedding-gecko@001" else 1
            )
            
            st.info("""
            **To enable Vertex AI:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Select your project
            3. Navigate to Vertex AI
            4. Click 'Enable Vertex AI API'
            5. Wait for the API to be enabled
            """)
        
        if st.button("💾 Save Vertex AI Settings"):
            self.setup_status["vertex_ai"]["configured"] = vertex_configured
            if vertex_configured:
                self.setup_status["vertex_ai"]["embedding_model"] = embedding_model
            if self.save_setup_status():
                st.success("✅ Vertex AI settings saved!")
                st.rerun()
        
        st.divider()
        
        # Vector Search Configuration
        st.header("🔍 Vector Search Setup")
        st.markdown("Vector Search is used for storing and searching PDF embeddings.")
        
        vector_configured = st.checkbox(
            "Enable Vector Search",
            value=self.setup_status["vector_search"]["configured"],
            help="Check this if you want to use Vector Search for PDF embeddings"
        )
        
        if vector_configured:
            index_name = st.text_input(
                "Index Name",
                value=self.setup_status["vector_search"]["index_name"],
                help="Name of the Vector Search index"
            )
            
            # Validate index name
            if index_name and not index_name.replace('-', '').replace('_', '').isalnum():
                st.error("❌ Index name should be alphanumeric with hyphens or underscores only.")
            
            st.info("""
            **To enable Vector Search:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Select your project
            3. Navigate to Vector Search
            4. Click 'Enable Vector Search API'
            5. Create an index:
               - Click 'Create Index'
               - Name: penny-assistant-index
               - Dimensions: 768
               - Distance measure: COSINE
               - Algorithm: TREE_AH
            """)
        
        if st.button("💾 Save Vector Search Settings"):
            if vector_configured and not index_name:
                st.error("❌ Index name is required when Vector Search is enabled")
            elif vector_configured and index_name and not index_name.replace('-', '').replace('_', '').isalnum():
                st.error("❌ Invalid index name format")
            else:
                self.setup_status["vector_search"]["configured"] = vector_configured
                if vector_configured:
                    self.setup_status["vector_search"]["index_name"] = index_name
                if self.save_setup_status():
                    st.success("✅ Vector Search settings saved!")
                    st.rerun()
        
        st.divider()
        
        # Configuration Summary
        st.header("📊 Configuration Summary")
        self.render_config_summary()
        
        # Export Configuration
        st.header("📤 Export Configuration")
        if st.button("📋 Export Config to Backend"):
            if self.export_to_backend():
                st.success("✅ Configuration exported to backend!")
                st.info("🔄 Backend will automatically reload configuration on next request.")
            else:
                st.error("❌ Failed to export configuration")
    
    def render_current_status(self):
        """Render current configuration status."""
        st.subheader("📊 Current Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Project ID:** {self.setup_status.get('project_id', 'Not set')}")
            st.write(f"**Region:** {self.setup_status.get('region', 'Not set')}")
        
        with col2:
            services = [
                ("Firestore", self.setup_status["firestore"]["configured"]),
                ("Calendar", self.setup_status["calendar"]["configured"]),
                ("Vertex AI", self.setup_status["vertex_ai"]["configured"]),
                ("Vector Search", self.setup_status["vector_search"]["configured"])
            ]
            
            for service, configured in services:
                status_icon = "✅" if configured else "❌"
                st.write(f"**{service}:** {status_icon}")
        
        # Overall status
        configured_count = sum(1 for _, configured in services if configured)
        total_services = len(services)
        
        if configured_count == 0:
            st.warning("⚠️ No services configured. Penny Assistant will use placeholder implementations.")
        elif configured_count < total_services:
            st.info(f"ℹ️ {configured_count}/{total_services} services configured. Some features will use placeholders.")
        else:
            st.success(f"🎉 All {total_services} services configured! Full functionality available.")
        
        st.divider()
    
    def render_config_summary(self):
        """Render a summary of the current configuration."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Settings")
            st.write(f"**Project ID:** {self.setup_status.get('project_id', 'Not set')}")
            st.write(f"**Region:** {self.setup_status.get('region', 'Not set')}")
        
        with col2:
            st.subheader("Service Status")
            services = [
                ("Firestore", self.setup_status["firestore"]["configured"]),
                ("Calendar", self.setup_status["calendar"]["configured"]),
                ("Vertex AI", self.setup_status["vertex_ai"]["configured"]),
                ("Vector Search", self.setup_status["vector_search"]["configured"])
            ]
            
            for service, configured in services:
                status = "✅ Configured" if configured else "❌ Not configured"
                st.write(f"**{service}:** {status}")
        
        # Overall status
        configured_count = sum(1 for service in services if service[1])
        total_services = len(services)
        
        if configured_count == 0:
            st.warning("⚠️ No services configured. Penny Assistant will use placeholder implementations.")
        elif configured_count < total_services:
            st.info(f"ℹ️ {configured_count}/{total_services} services configured. Some features will use placeholders.")
        else:
            st.success(f"🎉 All {total_services} services configured! Full functionality available.")
    
    def export_to_backend(self) -> bool:
        """Export configuration to backend directory."""
        try:
            backend_config_file = Path("../backend/setup_status.json")
            backend_config_file.parent.mkdir(exist_ok=True)
            
            with open(backend_config_file, "w") as f:
                json.dump(self.setup_status, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Export failed: {e}")
            return False
    
    def get_setup_status(self) -> Dict[str, Any]:
        """Get current setup status."""
        return self.setup_status
    
    def is_fully_configured(self) -> bool:
        """Check if all services are configured."""
        return all(
            self.setup_status[service]["configured"] 
            for service in ["firestore", "calendar", "vertex_ai", "vector_search"]
        )

# Global instance
config_setup = StreamlitConfigSetup() 