# Task List: Penny Assistant

## 1. Project Setup
- [ ] Clone agentic_rag as penny_assistant
- [ ] Update README and documentation
- [ ] Set up initial tests
- [ ] Create interactive startup script for Google Cloud project setup and validation
- [ ] Ensure all required Google Cloud APIs are enabled (Vertex AI, Firestore, Cloud Run, Google Calendar API, etc.)
- [ ] Set up service accounts and credentials

## 2. PDF Ingestion & RAG
- [ ] Implement PDF upload endpoint (Streamlit + backend)
- [ ] Parse and chunk PDF documents
- [ ] Embed text and store in Vertex AI Vector Search
- [ ] Implement RAG query endpoint
- [ ] User isolation for documents
- [ ] Tests for PDF ingestion and RAG

## 3. List Management
- [ ] Design list data model (per user, Firestore)
- [ ] Implement CRUD API for lists
- [ ] Integrate with Firestore backend
- [ ] Tests for list management

## 4. Calendar Integration
- [ ] Set up Google Calendar API credentials
- [ ] Implement OAuth2 flow for users
- [ ] Fetch and display calendar events
- [ ] Tests for calendar integration

## 5. User Interface (Streamlit)
- [ ] Build Streamlit app for PDF upload, lists, and chat
- [ ] User authentication in UI
- [ ] Deploy Streamlit app on Cloud Run (public, with authentication)

## 6. CI/CD
- [ ] Set up GitHub repository for Penny
- [ ] Configure Google Cloud Build for CI/CD
- [ ] Set up GitHub Actions for integration with Cloud Build
- [ ] Automate deployment of backend and Streamlit app to Cloud Run on push

## 7. General
- [ ] Logging and error handling
- [ ] Modularize code for extensibility
- [ ] Add unit and integration tests
- [ ] Documentation and usage examples 