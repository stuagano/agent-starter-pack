# Local Development Guide 🏠

## Overview

This guide will help you run Penny Assistant locally for development and testing. You can run both the backend and frontend together, or just the frontend if you have a backend running elsewhere.

## 🚀 Quick Start

### **Option 1: Run Everything Locally (Recommended)**
```bash
# From the penny_assistant directory
./run_local.sh
```

This will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Start the backend server (FastAPI)
- ✅ Start the Streamlit frontend
- ✅ Open the app at http://localhost:8501

### **Option 2: Run Just the Frontend**
```bash
# From the penny_assistant directory
./run_streamlit.sh
```

This will:
- ✅ Create a virtual environment
- ✅ Install frontend dependencies
- ✅ Start just the Streamlit frontend
- ✅ Connect to backend at http://localhost:8080 (or your specified BACKEND_URL)

### **Option 3: Manual Setup**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend && pip install -r requirements.txt && cd ..
cd streamlit && pip install -r requirements.txt && cd ..

# Start backend (in one terminal)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Start frontend (in another terminal)
cd streamlit
streamlit run app.py
```

## 📋 Prerequisites

### **Required Software**
- ✅ **Python 3.8+** - Check with `python3 --version`
- ✅ **pip** - Python package installer
- ✅ **curl** - For health checks (usually pre-installed)

### **Optional Software**
- 🔧 **Google Cloud CLI** - For cloud services (if using Vector Search, Firestore, etc.)
- 🔧 **Docker** - For containerized development

## 🏗️ Project Structure

```
penny_assistant/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── requirements.txt    # Backend dependencies
│   └── ...
├── streamlit/              # Streamlit frontend
│   ├── app.py              # Main Streamlit app
│   ├── requirements.txt    # Frontend dependencies
│   └── ...
├── run_local.sh            # Run everything locally
├── run_streamlit.sh        # Run just frontend
└── ...
```

## ⚙️ Configuration

### **Environment Variables**

You can set these environment variables to customize the local setup:

```bash
# Backend URL (default: http://localhost:8080)
export BACKEND_URL="http://localhost:8080"

# User ID (default: demo-user)
export USER_ID="your-user-id"

# Streamlit port (default: 8501)
export STREAMLIT_SERVER_PORT=8501

# Google Cloud project (for cloud services)
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### **Configuration Files**

The app uses configuration files for service settings:

- **Backend**: `backend/setup_status.json`
- **Frontend**: `streamlit/config/setup_status.json`

These are automatically created by the setup scripts.

## 🔧 Development Workflow

### **1. Start Development Environment**
```bash
./run_local.sh
```

### **2. Make Changes**
- Edit files in `backend/` for API changes
- Edit files in `streamlit/` for UI changes
- Both services have auto-reload enabled

### **3. Test Changes**
- Backend: http://localhost:8080/docs (API docs)
- Frontend: http://localhost:8501 (main app)
- Health check: http://localhost:8080/healthz

### **4. Stop Services**
- Press `Ctrl+C` in the terminal running the script
- Both services will be stopped automatically

## 🧪 Testing Features

### **Local Testing Checklist**

#### **✅ Basic Functionality**
- [ ] Frontend loads at http://localhost:8501
- [ ] Backend responds at http://localhost:8080/healthz
- [ ] Navigation works between pages
- [ ] Configuration page loads

#### **✅ PDF Upload & RAG**
- [ ] Upload a PDF file
- [ ] Verify chunks are created
- [ ] Ask questions about the PDF
- [ ] Check storage method display

#### **✅ Lists Management**
- [ ] Create a new list
- [ ] Add items to list
- [ ] Delete items from list
- [ ] Delete entire list

#### **✅ Configuration**
- [ ] Set project ID
- [ ] Configure services
- [ ] Export configuration
- [ ] Verify service status

#### **✅ Debug Tools**
- [ ] Access debug page
- [ ] Run configuration checks
- [ ] Test network connectivity
- [ ] Check file system access

#### **✅ Feedback System**
- [ ] Submit Gherkin feedback
- [ ] View feedback history
- [ ] Export feedback data

## 🔍 Troubleshooting

### **Common Issues**

#### **"Port already in use"**
```bash
# Check what's using the port
lsof -i :8080  # Backend port
lsof -i :8501  # Frontend port

# Kill the process
kill -9 <PID>
```

#### **"Module not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
pip install -r streamlit/requirements.txt
```

#### **"Backend connection failed"**
```bash
# Check if backend is running
curl http://localhost:8080/healthz

# Start backend manually
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

#### **"Streamlit not starting"**
```bash
# Check Streamlit installation
pip show streamlit

# Try running directly
cd streamlit
python -m streamlit run app.py
```

### **Debug Commands**

#### **Check Service Status**
```bash
# Backend health
curl http://localhost:8080/healthz

# Frontend health
curl "http://localhost:8501/?health=check"
```

#### **Check Logs**
```bash
# Backend logs (if running in terminal)
# Look for uvicorn output

# Frontend logs (if running in terminal)
# Look for streamlit output
```

#### **Check Dependencies**
```bash
# List installed packages
pip list

# Check specific package
pip show streamlit
pip show fastapi
```

## 🚀 Advanced Development

### **Running with Cloud Services**

If you want to use real cloud services locally:

1. **Set up Google Cloud credentials**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   ```

2. **Configure services**:
   ```bash
   # Set up Vector Search
   ./setup_vector_search.sh
   
   # Or configure manually in the web interface
   ```

3. **Run with cloud services**:
   ```bash
   ./run_local.sh
   ```

### **Development with Docker**

If you prefer Docker:

```bash
# Build and run backend
cd backend
docker build -t penny-backend .
docker run -p 8080:8080 penny-backend

# Build and run frontend
cd streamlit
docker build -t penny-frontend .
docker run -p 8501:8501 penny-frontend
```

### **Hot Reloading**

Both services support hot reloading:

- **Backend**: Uses `uvicorn --reload` - changes to Python files will restart the server
- **Frontend**: Streamlit automatically reloads when you save changes

### **Environment-Specific Configuration**

You can create environment-specific configuration files:

```bash
# Development
cp streamlit/config/setup_status.json streamlit/config/setup_status.dev.json

# Production
cp streamlit/config/setup_status.json streamlit/config/setup_status.prod.json
```

## 📊 Monitoring

### **Health Checks**
- **Backend**: http://localhost:8080/healthz
- **Frontend**: http://localhost:8501/?health=check

### **API Documentation**
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### **Streamlit Debug**
- **Debug Info**: Add `st.write(st.session_state)` to see session data
- **Performance**: Use Streamlit's built-in profiler

## 🔄 Development Tips

### **Best Practices**
1. **Use virtual environment** - Always activate `venv` before development
2. **Check logs** - Monitor both backend and frontend logs
3. **Test incrementally** - Test each feature as you develop
4. **Use debug tools** - Leverage the built-in debug page
5. **Version control** - Commit changes regularly

### **Performance Tips**
1. **Use `--reload`** - For development, not production
2. **Monitor memory** - Check for memory leaks
3. **Optimize imports** - Only import what you need
4. **Use caching** - Streamlit's `@st.cache_data` for expensive operations

### **Debugging Tips**
1. **Use print statements** - Simple but effective
2. **Check network tab** - Browser dev tools for API calls
3. **Use debug page** - Built-in debugging tools
4. **Check environment** - Verify all variables are set

## 🎯 Next Steps

After getting local development working:

1. **Set up cloud services** - Follow `VECTOR_SEARCH_SETUP.md`
2. **Deploy to production** - Use `deploy_simple.sh`
3. **Add features** - Extend the application
4. **Write tests** - Add unit and integration tests
5. **Monitor performance** - Set up logging and monitoring

---

**Happy Local Development! 🏠**

With these tools, you can develop and test Penny Assistant locally with full control over the environment and easy debugging capabilities. 