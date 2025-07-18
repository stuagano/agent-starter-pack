# Penny Assistant 🤖

Penny is a personal digital assistant agent that helps you:
- **📄 Read and answer questions** about your uploaded PDF documents using Retrieval-Augmented Generation (RAG)
- **📝 Create and manage personal lists** (to-dos, shopping, etc.)
- **📅 Read your calendar events** (Google Calendar integration)
- **💬 Chat with AI** for general assistance and questions
- **🧠 Memory and evaluation** for personalized experiences
- **📝 Provide structured feedback** using Gherkin syntax for testing and improvement

## 🚀 Key Features

### **Core Functionality**
- **PDF Processing**: Upload PDFs and ask questions about their content
- **List Management**: Create, update, and manage personal lists
- **Calendar Integration**: View and manage Google Calendar events
- **AI Chat**: Natural language conversations with Penny
- **Memory System**: Personalized experiences and preferences
- **Evaluation Tools**: Assess and improve AI responses

### **Advanced Features**
- **🔧 Progressive Enhancement**: Works with placeholders, upgrades to real cloud services
- **🐛 Comprehensive Debugging**: Built-in troubleshooting and diagnostic tools
- **📝 Gherkin Feedback Interface**: Structured feedback using natural language
- **⚙️ Web-based Configuration**: Easy setup through the Streamlit interface
- **☁️ Cloud Run Ready**: Fully containerized for Google Cloud deployment

## 🏗️ Architecture

### **Frontend (Streamlit)**
- Interactive web interface
- Configuration management
- Debugging tools
- Gherkin feedback system

### **Backend (FastAPI)**
- RESTful API endpoints
- PDF processing and RAG
- List and calendar management
- Progressive enhancement with fallbacks

### **Cloud Services**
- **Firestore**: List storage
- **Google Calendar API**: Calendar integration
- **Vertex AI**: AI model inference
- **Vector Search**: PDF embeddings storage

## 🛠️ Quick Start

### **Local Development**
```bash
# Start backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Start frontend (in another terminal)
cd streamlit
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### **Cloud Deployment**
```bash
# Deploy both services
./deploy_simple.sh
```

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT_READY.md)** - Complete deployment instructions
- **[Frontend Configuration](FRONTEND_CONFIGURATION.md)** - Setup and configuration
- **[Debug Features](DEBUG_FEATURES.md)** - Troubleshooting and diagnostics
- **[Gherkin Feedback Guide](GHERKIN_FEEDBACK_GUIDE.md)** - Using the feedback interface
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## 🎯 Testing with Gherkin Feedback

The Gherkin Feedback Interface allows you to provide structured, natural language feedback during testing:

```gherkin
Feature: PDF Upload and Processing
Scenario: User uploads a PDF and asks questions
  Given I am on the PDF Upload page
  And I have a valid PDF file
  When I upload the PDF file
  And I wait for processing to complete
  And I ask "What is the main topic?"
  Then I should see a relevant answer
  And the answer should reference the PDF content
  But I should not see placeholder text
```

### **Benefits**
- ✅ **Structured feedback** in natural language
- ✅ **Clear test scenarios** with Given/When/Then format
- ✅ **Easy tracking** of issues and feature requests
- ✅ **Export capabilities** for analysis and reporting

## 🔧 Configuration

### **Progressive Enhancement**
Penny works out of the box with placeholder implementations and can be progressively enhanced with real cloud services:

1. **Start with placeholders** - All features work immediately
2. **Configure cloud services** - Through the web interface
3. **Export configuration** - To backend for production use
4. **Test and validate** - Using built-in debugging tools

### **Service Status**
The interface shows real-time status of configured services:
- 📝 **Firestore** - List storage
- 📅 **Calendar** - Google Calendar integration
- 🤖 **Vertex AI** - AI model inference
- 🔍 **Vector Search** - PDF embeddings

## 🐛 Debugging and Troubleshooting

### **Built-in Debug Tools**
- **Configuration Check** - Verify settings and environment
- **Network Test** - Test backend connectivity
- **File System Check** - Verify permissions and paths
- **Service Test** - Test individual cloud services
- **Logs & Errors** - Common issues and solutions

### **Health Checks**
- Frontend: `/?health=check`
- Backend: `/healthz`

## 📊 Feedback and Improvement

### **Gherkin Feedback System**
- **Structured input** using Gherkin syntax
- **Category classification** (Bug, Feature, Usability, etc.)
- **Priority levels** (Low, Medium, High, Critical)
- **Status tracking** (New, In Progress, Resolved, Won't Fix)
- **Export capabilities** (JSON and summary formats)

### **Feedback Categories**
- 🐛 **Bug Reports** - Issues and problems
- 💡 **Feature Requests** - New functionality
- 🎨 **Usability Issues** - Interface improvements
- ⚡ **Performance** - Speed and resource usage
- 📚 **Documentation** - Help and guides

## 🚀 Deployment

### **Cloud Run Ready**
- **Containerized** with Docker
- **Health checks** for monitoring
- **Environment variables** for configuration
- **CI/CD pipeline** with Cloud Build

### **Local Testing**
- **Container testing** scripts included
- **Import validation** for dependencies
- **Configuration validation** for settings
- **Network connectivity** testing

## 🤝 Contributing

1. **Test the application** using the Gherkin feedback interface
2. **Report issues** with structured feedback
3. **Suggest improvements** through feature requests
4. **Document findings** for future development

## 📄 License

This project is part of the agent-starter-pack and follows the same licensing terms.

---

**Penny Assistant** - Your personal digital assistant with structured feedback for continuous improvement! 🎯 