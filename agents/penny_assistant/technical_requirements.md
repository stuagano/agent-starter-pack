# Technical Requirements: Penny Assistant

## Overview
Penny is a personal digital assistant agent that enables users to:
- Upload PDF documents and ask questions about their content (RAG)
- Create, update, and manage personal lists
- Read calendar events from Google Calendar

## Functional Requirements

### 1. PDF Ingestion & RAG
- Users can upload PDF documents via a web UI or API endpoint.
- PDFs are parsed and chunked into text segments.
- Text segments are embedded and stored in a vector database (e.g., Vertex AI Vector Search on Google Cloud).
- User queries are answered using retrieval-augmented generation (RAG) over the uploaded PDFs.
- Support for multiple users and document isolation.
- All storage and compute should use Google Cloud services where possible.

### 2. List Management
- Users can create, update, delete, and retrieve named lists (e.g., to-dos, shopping).
- Lists are stored per user in a Google Cloud database (e.g., Firestore).
- API endpoints for list CRUD operations.

### 3. Calendar Integration
- Penny can read and summarize upcoming events from the user's Google Calendar.
- OAuth2 authentication for Google Calendar access.
- API endpoint to fetch and display calendar events.

### 4. User Interface
- Streamlit app deployed on Google Cloud Run for PDF upload, list management, and chat with Penny.
- Authentication for user isolation.
- The Streamlit app should be publicly accessible (with authentication) and serve as the main user interface.

### 5. Startup Script & Project Setup
- Provide an interactive startup script that:
  - Guides the user through Google Cloud project selection/creation
  - Checks for required APIs and permissions (Vertex AI, Firestore, Cloud Run, Google Calendar API, etc.)
  - Sets up service accounts and credentials
  - Confirms all prerequisites are met before deployment

### 6. CI/CD
- Set up CI/CD so that pushing to GitHub automatically deploys/updates the agent and Streamlit app on Cloud Run.
- Use Google Cloud Build and GitHub Actions for automation.

## Non-Functional Requirements
- Modular, extensible codebase (easy to add new skills).
- Secure handling of user data and authentication tokens.
- Scalable backend (stateless, supports multiple users).
- Logging and error handling for all endpoints.
- Unit and integration tests for all major features.

## Technology Stack
- Python 3.10+
- JAX, NumPy (for ML components)
- FastAPI or Flask (for API endpoints)
- Vertex AI Vector Search (for RAG)
- Google Calendar API
- Firestore (for lists)
- Streamlit (frontend)
- Cloud Run (deployment)
- Google Cloud Build, GitHub Actions (CI/CD)

## Extensibility
- Skills can be added as new modules (e.g., reminders, email integration).
- RAG pipeline supports additional document types (e.g., DOCX, TXT).

## Security & Privacy
- User authentication and authorization for all endpoints.
- Secure storage of OAuth tokens and user data.
- Data isolation between users.
- Use Google Cloud IAM for access control. 