# Penny Assistant - Troubleshooting Guide 🛠️

## Quick Start Debugging

### 🚨 **Immediate Issues**

#### **Deployment Fails**
```bash
# Check if you're authenticated
gcloud auth list

# Check if project is set
gcloud config get-value project

# Check if required APIs are enabled
gcloud services list --enabled | grep -E "(run|cloudbuild)"
```

#### **Frontend Won't Load**
```bash
# Check if frontend is deployed
gcloud run services list --filter="metadata.name=penny-assistant-frontend"

# Check frontend logs
gcloud run services logs read penny-assistant-frontend --region=us-central1
```

#### **Backend Not Responding**
```bash
# Check if backend is deployed
gcloud run services list --filter="metadata.name=penny-assistant-backend"

# Check backend logs
gcloud run services logs read penny-assistant-backend --region=us-central1

# Test backend directly
curl https://your-backend-url/healthz
```

## 🔧 **Configuration Issues**

### **Project ID Problems**

#### **Invalid Project ID Format**
**Error:** `❌ Invalid project ID format`

**Solution:**
- Project ID must be lowercase
- 6-30 characters long
- Only letters, numbers, and hyphens
- Must start with a letter
- Example: `my-project-123456`

#### **Project Not Found**
**Error:** `❌ Project not found or access denied`

**Solution:**
```bash
# List available projects
gcloud projects list

# Set correct project
gcloud config set project YOUR_PROJECT_ID

# Verify access
gcloud auth list
```

### **File Upload Issues**

#### **Credentials File Invalid**
**Error:** `❌ Invalid credentials file`

**Solution:**
1. Download fresh credentials from Google Cloud Console
2. Ensure it's a JSON file (not CSV or other format)
3. Check that it contains required fields:
   ```json
   {
     "client_id": "...",
     "client_secret": "...",
     "redirect_uris": ["..."]
   }
   ```

#### **File Upload Fails**
**Error:** `❌ Failed to save credentials file`

**Solution:**
1. Check file permissions in `config/` directory
2. Ensure file is not corrupted
3. Try uploading a smaller file first
4. Check browser console for JavaScript errors

### **Configuration Not Saving**

#### **Settings Reset After Refresh**
**Symptoms:** Configuration disappears after page refresh

**Solution:**
1. Check if `config/setup_status.json` exists
2. Verify file permissions (should be writable)
3. Check browser storage (try different browser)
4. Ensure you clicked "Save" buttons

#### **Export to Backend Fails**
**Error:** `❌ Failed to export configuration`

**Solution:**
1. Check if `../backend/` directory exists
2. Verify write permissions
3. Ensure backend service is running
4. Check file system space

## 🌐 **Network & Connectivity Issues**

### **Backend Connection Problems**

#### **Connection Timeout**
**Error:** `❌ Backend connection timeout`

**Diagnosis:**
```bash
# Test backend URL
curl -v https://your-backend-url/healthz

# Check if service is running
gcloud run services describe penny-assistant-backend --region=us-central1
```

**Solutions:**
1. Verify `BACKEND_URL` environment variable
2. Check if backend service is deployed
3. Ensure no firewall blocking connections
4. Try accessing backend URL directly in browser

#### **CORS Errors**
**Error:** `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Solution:**
1. Backend CORS is configured for all origins (`*`)
2. Check if backend is properly deployed
3. Verify backend URL is correct
4. Clear browser cache and cookies

### **Google Cloud API Issues**

#### **API Not Enabled**
**Error:** `❌ API not enabled for this project`

**Solution:**
```bash
# Enable required APIs
gcloud services enable firestore.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable vectorsearch.googleapis.com
```

#### **Authentication Failures**
**Error:** `❌ Authentication failed`

**Solution:**
1. Check service account permissions
2. Verify credentials file is correct
3. Ensure project has billing enabled
4. Check if APIs are enabled

## 📁 **File System Issues**

### **Permission Problems**

#### **Cannot Write to Config Directory**
**Error:** `❌ Cannot write to config directory`

**Solution:**
```bash
# Check permissions
ls -la config/

# Fix permissions
chmod 755 config/
chmod 644 config/setup_status.json
```

#### **Cannot Read Configuration**
**Error:** `❌ Error reading frontend config`

**Solution:**
1. Check if config file exists
2. Verify file permissions
3. Check file format (should be valid JSON)
4. Try recreating config file

### **Missing Files**

#### **Configuration File Not Found**
**Error:** `⚠️ Frontend config file not found`

**Solution:**
1. Navigate to Configuration page
2. Enter project settings
3. Save configuration
4. Check if `config/setup_status.json` is created

#### **Credentials File Missing**
**Error:** `❌ Calendar credentials file not found`

**Solution:**
1. Go to Configuration page
2. Enable Calendar service
3. Upload OAuth2 credentials file
4. Save settings

## 🔧 **Service-Specific Issues**

### **Firestore Issues**

#### **Database Not Created**
**Error:** `❌ Firestore test failed: Database not found`

**Solution:**
1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Click "Create Database"
3. Choose "Start in test mode"
4. Select location (us-central1 recommended)

#### **Permission Denied**
**Error:** `❌ Firestore test failed: Permission denied`

**Solution:**
1. Check service account has Firestore permissions
2. Verify project has billing enabled
3. Ensure Firestore API is enabled
4. Check collection name is valid

### **Calendar Issues**

#### **OAuth2 Flow Fails**
**Error:** `❌ Calendar test failed: OAuth2 flow failed`

**Solution:**
1. Verify credentials file is valid
2. Check redirect URIs include your frontend URL
3. Ensure Calendar API is enabled
4. Try re-authenticating

#### **No Calendars Found**
**Error:** `Found 0 calendars`

**Solution:**
1. Check if user has calendars
2. Verify OAuth2 scope includes calendar access
3. Try accessing Google Calendar directly
4. Check if calendar is shared with service account

### **Vertex AI Issues**

#### **API Not Enabled**
**Error:** `❌ Vertex AI test failed: API not enabled`

**Solution:**
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

#### **Model Not Available**
**Error:** `❌ Vertex AI test failed: Model not found`

**Solution:**
1. Check if embedding model name is correct
2. Verify model is available in your region
3. Ensure project has billing enabled
4. Check service account permissions

### **Vector Search Issues**

#### **Index Not Found**
**Error:** `❌ Vector Search test failed: Index not found`

**Solution:**
1. Create Vector Search index in Google Cloud Console
2. Verify index name matches configuration
3. Check index dimensions (should be 768)
4. Ensure Vector Search API is enabled

## 🐛 **Common Error Messages**

### **"Backend not responding"**
**Quick Fix:**
1. Check if backend is deployed
2. Verify `BACKEND_URL` environment variable
3. Test backend health endpoint
4. Check backend logs

### **"Configuration not saving"**
**Quick Fix:**
1. Check file permissions
2. Verify config directory exists
3. Try refreshing page
4. Check browser console for errors

### **"Google Cloud services not working"**
**Quick Fix:**
1. Verify project ID is correct
2. Check if APIs are enabled
3. Ensure billing is enabled
4. Verify service account permissions

### **"PDF upload fails"**
**Quick Fix:**
1. Check PDF file size (< 10MB)
2. Verify PDF is not corrupted
3. Check backend logs
4. Ensure backend has sufficient memory

## 🔍 **Debug Commands**

### **Service Status**
```bash
# List all services
gcloud run services list

# Check specific service
gcloud run services describe penny-assistant-backend --region=us-central1
```

### **View Logs**
```bash
# Backend logs
gcloud run services logs read penny-assistant-backend --region=us-central1

# Frontend logs
gcloud run services logs read penny-assistant-frontend --region=us-central1

# Follow logs in real-time
gcloud run services logs tail penny-assistant-backend --region=us-central1
```

### **Check Configuration**
```bash
# Check project
gcloud config get-value project

# Check authentication
gcloud auth list

# Check APIs
gcloud services list --enabled
```

### **Test Connectivity**
```bash
# Test backend health
curl https://your-backend-url/healthz

# Test specific endpoints
curl https://your-backend-url/api/v1/pdf/health
curl https://your-backend-url/api/v1/lists/status
curl https://your-backend-url/api/v1/calendar/health
```

## 📞 **Getting Help**

### **Debug Page**
Use the **Debug** page in the Streamlit interface for:
- Configuration checks
- Network tests
- Service tests
- Common issue solutions

### **Logs**
Check Cloud Run logs for detailed error information:
```bash
gcloud run services logs read penny-assistant-backend --region=us-central1 --limit=50
```

### **Common Solutions**
1. **Restart services** - Sometimes a simple restart fixes issues
2. **Check permissions** - Ensure service accounts have proper access
3. **Verify configuration** - Double-check all settings
4. **Clear cache** - Clear browser cache and cookies
5. **Try different browser** - Some issues are browser-specific

### **Still Stuck?**
1. Check the Debug page in the web interface
2. Review Cloud Run logs for error details
3. Verify all prerequisites are met
4. Try the simple deployment script again
5. Check Google Cloud Console for service status

## 🎯 **Prevention Tips**

### **Before Deployment**
1. ✅ Verify Google Cloud project is set
2. ✅ Ensure you're authenticated
3. ✅ Check billing is enabled
4. ✅ Verify required APIs are enabled

### **During Configuration**
1. ✅ Use valid project ID format
2. ✅ Upload correct credentials files
3. ✅ Save settings after each change
4. ✅ Export configuration to backend

### **After Setup**
1. ✅ Test each service individually
2. ✅ Verify configuration is saved
3. ✅ Check service status in sidebar
4. ✅ Monitor logs for any issues

Remember: **Placeholder implementations always work**, so if something fails, you can still use the application while debugging the issue! 🎉 