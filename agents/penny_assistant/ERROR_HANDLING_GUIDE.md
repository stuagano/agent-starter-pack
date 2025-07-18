# Error Handling Guide 🛠️

## Overview

This guide helps you understand and resolve common errors in Penny Assistant. The application now includes comprehensive error handling to provide clear feedback and graceful fallbacks.

## 🚨 Common Error Types

### **1. Backend Connection Errors**

#### **"Backend connection failed"**
**What it means**: The frontend can't connect to the backend server.

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:8080/healthz

# Start backend if not running
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Or use the automated script
./run_local.sh
```

#### **"Request timed out"**
**What it means**: The backend is taking too long to respond.

**Solutions**:
- Check if the backend is under heavy load
- Restart the backend server
- Check for infinite loops or blocking operations

### **2. Configuration Errors**

#### **"Configuration error"**
**What it means**: There's an issue with the setup configuration.

**Solutions**:
1. Go to the **Configuration** page
2. Check that all required fields are filled
3. Verify your Google Cloud project ID
4. Export configuration to backend

#### **"Service not configured"**
**What it means**: A cloud service (Firestore, Calendar, etc.) isn't set up.

**Solutions**:
- Use placeholder mode (works without cloud services)
- Set up the service in the Configuration page
- Follow the setup guides for each service

### **3. Data Format Errors**

#### **"Invalid response from backend"**
**What it means**: The backend returned malformed data.

**Solutions**:
- Check backend logs for errors
- Restart the backend server
- Verify the backend is running the correct version

#### **"Error processing list"**
**What it means**: There's an issue with list data format.

**Solutions**:
- The app now handles both string and dictionary formats
- Check if your backend is returning the expected format
- Try creating a new list to test

### **4. File Upload Errors**

#### **"Upload failed"**
**What it means**: PDF upload didn't work.

**Solutions**:
- Check file size (should be under 10MB)
- Ensure it's a valid PDF file
- Check backend storage configuration
- Verify backend is running

## 🔧 Debug Tools

### **Built-in Debug Page**
1. Go to the **Debug** page in the sidebar
2. Run the configuration checks
3. Test network connectivity
4. Check file system access
5. Test service connections

### **Health Check**
The footer shows backend status:
- ✅ **Backend OK** - Everything is working
- ❌ **Backend Error** - There's an issue
- ❌ **Backend Unreachable** - Can't connect

### **Service Status**
The sidebar shows which services are configured:
- ✅ **Configured** - Service is ready
- ❌ **Not Configured** - Using placeholder

## 🚀 Error Recovery

### **Automatic Fallbacks**
The app includes automatic fallbacks for:
- **Backend unavailable**: Uses placeholder data
- **Service errors**: Shows helpful error messages
- **Data format issues**: Handles multiple formats
- **Network timeouts**: Retries with shorter timeouts

### **Graceful Degradation**
- **PDF Upload**: Works with local storage if cloud storage fails
- **Lists**: Works with local storage if Firestore fails
- **Chat**: Shows placeholder responses if AI service fails
- **Calendar**: Shows sample data if Google Calendar fails

## 📋 Troubleshooting Checklist

### **Before Starting**
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Ports 8080 and 8501 available

### **Backend Issues**
- [ ] Backend server is running
- [ ] Health check passes: `curl http://localhost:8080/healthz`
- [ ] No firewall blocking connections
- [ ] Correct BACKEND_URL environment variable

### **Frontend Issues**
- [ ] Streamlit is running
- [ ] Browser can access http://localhost:8501
- [ ] No JavaScript errors in browser console
- [ ] Session state is working

### **Configuration Issues**
- [ ] Configuration files exist
- [ ] Project ID is set correctly
- [ ] Service accounts have proper permissions
- [ ] APIs are enabled in Google Cloud

## 🛠️ Manual Debugging

### **Check Backend Logs**
```bash
# If running manually
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Look for error messages in the terminal
```

### **Check Frontend Logs**
```bash
# If running manually
cd streamlit
streamlit run app.py

# Look for error messages in the terminal
```

### **Test API Endpoints**
```bash
# Health check
curl http://localhost:8080/healthz

# PDF health
curl http://localhost:8080/api/v1/pdf/health

# Lists endpoint
curl http://localhost:8080/api/v1/lists?user_id=demo-user
```

### **Check Environment Variables**
```bash
# Check current environment
echo $BACKEND_URL
echo $USER_ID
echo $GOOGLE_CLOUD_PROJECT

# Set if needed
export BACKEND_URL="http://localhost:8080"
export USER_ID="demo-user"
```

## 🔄 Recovery Procedures

### **Complete Reset**
```bash
# Stop all services
pkill -f "uvicorn"
pkill -f "streamlit"

# Clear any cached data
rm -rf ~/.streamlit/
rm -f backend/pdf_embeddings.json

# Restart with clean state
./run_local.sh
```

### **Configuration Reset**
```bash
# Remove configuration files
rm -f backend/setup_status.json
rm -f streamlit/config/setup_status.json

# Restart and reconfigure
./run_local.sh
```

### **Database Reset**
```bash
# Clear local storage
rm -f backend/pdf_embeddings.json
rm -f streamlit/data/*.json

# Restart services
./run_local.sh
```

## 📞 Getting Help

### **Self-Service Debugging**
1. **Use the Debug page** - Built-in diagnostic tools
2. **Check the logs** - Look for error messages
3. **Test connectivity** - Verify network connections
4. **Reset configuration** - Start with clean state

### **Common Solutions**
- **Restart services**: `./run_local.sh`
- **Clear cache**: Remove temporary files
- **Check permissions**: Verify file and network access
- **Update dependencies**: `pip install -r requirements.txt`

### **When to Seek Help**
- Errors persist after following this guide
- Backend won't start despite correct setup
- Configuration issues that can't be resolved
- Performance problems affecting usability

## 🎯 Prevention Tips

### **Best Practices**
1. **Use virtual environments** - Isolate dependencies
2. **Check logs regularly** - Monitor for issues
3. **Test incrementally** - Verify each component
4. **Backup configuration** - Save working setups
5. **Use version control** - Track changes

### **Monitoring**
- Watch the service status in the sidebar
- Monitor the backend status in the footer
- Check the debug page periodically
- Review logs for warnings

---

**Happy Debugging! 🐛**

With these tools and procedures, you should be able to resolve most issues and get Penny Assistant running smoothly. 