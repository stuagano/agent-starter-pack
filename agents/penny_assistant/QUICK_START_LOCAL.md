# Quick Start: Run Penny Assistant Locally 🚀

## The Simple Way

### **Option 1: One-Command Setup (Recommended)**
```bash
# From the penny_assistant directory
./run_local.sh
```

This will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Start the backend server
- ✅ Start the Streamlit frontend
- ✅ Open the app at http://localhost:8501

### **Option 2: Just the Frontend**
```bash
# From the penny_assistant directory
./run_streamlit.sh
```

This will:
- ✅ Create a virtual environment
- ✅ Install frontend dependencies
- ✅ Start just the Streamlit frontend
- ✅ Connect to backend at http://localhost:8080

## The Manual Way

### **Step 1: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **Step 2: Install Dependencies**
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd streamlit
pip install -r requirements.txt
cd ..
```

### **Step 3: Start Backend (Terminal 1)**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### **Step 4: Start Frontend (Terminal 2)**
```bash
cd streamlit
streamlit run app.py
```

## 🎯 What You'll See

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/healthz

## 🔧 Troubleshooting

### **"Module not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
pip install -r streamlit/requirements.txt
```

### **"Port already in use"**
```bash
# Check what's using the port
lsof -i :8080  # Backend
lsof -i :8501  # Frontend

# Kill the process
kill -9 <PID>
```

### **"Backend connection failed"**
```bash
# Check if backend is running
curl http://localhost:8080/healthz

# Start backend manually
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## 📋 Features Available Locally

### **✅ Working Features**
- 📄 PDF Upload & Processing
- 🔍 RAG Query System
- 📝 Lists Management
- ⚙️ Configuration Setup
- 🐛 Debug Tools
- 💬 Feedback System
- 📊 Service Status

### **⚠️ Placeholder Features**
- 📅 Calendar (shows sample data)
- 💬 Chat (shows placeholder responses)
- 🧠 Memory (shows sample data)
- 📈 Evaluation (shows sample metrics)

## 🚀 Next Steps

1. **Test the app**: Upload a PDF and ask questions
2. **Configure services**: Use the Configuration page to set up cloud services
3. **Set up Vector Search**: Follow `VECTOR_SEARCH_SETUP.md` for real AI features
4. **Deploy to production**: Use `deploy_simple.sh` when ready

## 📚 More Information

- **Full Guide**: `LOCAL_DEVELOPMENT.md`
- **Vector Search Setup**: `VECTOR_SEARCH_SETUP.md`
- **Deployment**: `DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: Check the Debug page in the app

---

**Happy Local Development! 🏠**

The Streamlit interface is now ready to run locally with full functionality for development and testing. 