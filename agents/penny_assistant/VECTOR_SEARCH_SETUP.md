# Vertex AI Vector Search Setup Guide 🔍

## Overview

This guide will help you set up Vertex AI Vector Search for Penny Assistant, enabling real vector-based document search and retrieval instead of placeholder implementations.

## 🎯 Prerequisites

### **Google Cloud Project Setup**
1. **Enable Billing** - Vector Search requires billing to be enabled
2. **Enable APIs** - The following APIs must be enabled:
   - Vertex AI API
   - Vector Search API
   - Cloud Storage API

### **Required Permissions**
Your service account needs these roles:
- `roles/aiplatform.user`
- `roles/aiplatform.developer`
- `roles/storage.objectViewer`

## 🚀 Quick Setup

### **Step 1: Enable Required APIs**
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Vector Search API
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com
```

### **Step 2: Create Vector Search Index**
```bash
# Set your project and region
PROJECT_ID="your-project-id"
REGION="us-central1"

# Create Vector Search index
gcloud ai vector-search indexes create \
  --display-name="penny-assistant-index" \
  --description="Index for Penny Assistant PDF embeddings" \
  --region=$REGION \
  --project=$PROJECT_ID \
  --embedding-dimension=768 \
  --distance-measure-type="COSINE_DISTANCE"
```

### **Step 3: Deploy the Index**
```bash
# Get the index ID
INDEX_ID=$(gcloud ai vector-search indexes list --region=$REGION --project=$PROJECT_ID --format="value(name)" | grep penny-assistant-index)

# Deploy the index
gcloud ai vector-search indexes deploy \
  --index=$INDEX_ID \
  --region=$REGION \
  --project=$PROJECT_ID
```

### **Step 4: Configure Penny Assistant**
1. **Open the Penny Assistant web interface**
2. **Go to Configuration page**
3. **Set up Vertex AI**:
   - Project ID: `your-project-id`
   - Region: `us-central1`
   - Embedding Model: `textembedding-gecko@001`
4. **Set up Vector Search**:
   - Index Name: `penny-assistant-index`
   - Enable Vector Search: ✅
5. **Export configuration to backend**

## 📋 Detailed Setup Instructions

### **1. Project Configuration**

#### **Check Current Project**
```bash
gcloud config get-value project
```

#### **Set Project (if needed)**
```bash
gcloud config set project YOUR_PROJECT_ID
```

#### **Verify Billing**
```bash
gcloud billing projects describe YOUR_PROJECT_ID --format="value(billingEnabled)"
```

### **2. API Enablement**

#### **Enable All Required APIs**
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Vector Search API (part of Vertex AI)
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable IAM API
gcloud services enable iam.googleapis.com
```

#### **Verify APIs are Enabled**
```bash
gcloud services list --enabled --filter="name:aiplatform.googleapis.com"
```

### **3. Service Account Setup**

#### **Create Service Account (if needed)**
```bash
# Create service account
gcloud iam service-accounts create penny-assistant-sa \
  --display-name="Penny Assistant Service Account"

# Get service account email
SA_EMAIL="penny-assistant-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.developer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectViewer"
```

#### **Create and Download Key**
```bash
# Create key file
gcloud iam service-accounts keys create penny-assistant-key.json \
  --iam-account=$SA_EMAIL

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="penny-assistant-key.json"
```

### **4. Vector Search Index Creation**

#### **Create Index Configuration**
Create a file `index_config.json`:
```json
{
  "displayName": "penny-assistant-index",
  "description": "Vector search index for Penny Assistant PDF embeddings",
  "metadataSchemaUri": "gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_metadata/1.0.0.yaml",
  "contentsDeltaUri": "gs://YOUR_BUCKET/vector_search/",
  "config": {
    "dimensions": 768,
    "approximateNeighborsCount": 150,
    "distanceMeasureType": "COSINE_DISTANCE",
    "algorithm_config": {
      "treeAhConfig": {
        "leafNodeEmbeddingCount": 500,
        "leafNodesToSearchPercent": 10
      }
    }
  }
}
```

#### **Create the Index**
```bash
# Create index
gcloud ai vector-search indexes create \
  --metadata-file=index_config.json \
  --region=$REGION \
  --project=$PROJECT_ID
```

#### **Deploy the Index**
```bash
# Get index ID
INDEX_ID=$(gcloud ai vector-search indexes list \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(name)" | grep penny-assistant-index)

# Deploy index
gcloud ai vector-search indexes deploy \
  --index=$INDEX_ID \
  --region=$REGION \
  --project=$PROJECT_ID
```

### **5. Penny Assistant Configuration**

#### **Web Interface Configuration**
1. **Open Penny Assistant**: Navigate to your deployed frontend URL
2. **Go to Configuration**: Click the "Configuration" tab
3. **Set Project Settings**:
   - Project ID: `your-project-id`
   - Region: `us-central1`
4. **Configure Vertex AI**:
   - ✅ Enable Vertex AI
   - Embedding Model: `textembedding-gecko@001`
5. **Configure Vector Search**:
   - ✅ Enable Vector Search
   - Index Name: `penny-assistant-index`
6. **Export Configuration**: Click "Export to Backend"

#### **Manual Configuration (Alternative)**
If you prefer to configure manually, update the configuration files:

**Backend Configuration** (`backend/setup_status.json`):
```json
{
  "firestore": {"configured": false, "collection": "user_lists"},
  "calendar": {"configured": false, "credentials_file": null},
  "vertex_ai": {
    "configured": true,
    "embedding_model": "textembedding-gecko@001"
  },
  "vector_search": {
    "configured": true,
    "index_name": "penny-assistant-index"
  },
  "project_id": "your-project-id",
  "region": "us-central1"
}
```

**Frontend Configuration** (`streamlit/config/setup_status.json`):
```json
{
  "firestore": {"configured": false, "collection": "user_lists"},
  "calendar": {"configured": false, "credentials_file": null},
  "vertex_ai": {
    "configured": true,
    "embedding_model": "textembedding-gecko@001"
  },
  "vector_search": {
    "configured": true,
    "index_name": "penny-assistant-index"
  },
  "project_id": "your-project-id",
  "region": "us-central1"
}
```

### **6. Redeploy Services**

#### **Redeploy with New Configuration**
```bash
# Redeploy backend
cd backend
gcloud run deploy penny-assistant-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=your-project-id"

# Redeploy frontend
cd ../streamlit
gcloud run deploy penny-assistant-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "BACKEND_URL=https://penny-assistant-backend-xxx-uc.a.run.app"
```

## 🧪 Testing Vector Search

### **1. Upload a PDF**
1. Go to the "PDF Upload" page
2. Upload a PDF document
3. Verify the storage method shows: `Vertex AI Vector Search (penny-assistant-index)`

### **2. Ask Questions**
1. Go to the "PDF Upload" page
2. Ask a question about your uploaded PDF
3. Verify the method shows: `vector_search`

### **3. Check Logs**
```bash
# Check backend logs
gcloud run services logs read penny-assistant-backend --region=us-central1

# Check for Vector Search operations
gcloud run services logs read penny-assistant-backend --region=us-central1 | grep "Vector Search"
```

## 🔧 Troubleshooting

### **Common Issues**

#### **"Vector Search not configured"**
- ✅ Check that Vector Search is enabled in configuration
- ✅ Verify the index name is correct
- ✅ Ensure the index is deployed

#### **"Authentication failed"**
- ✅ Verify service account has correct permissions
- ✅ Check that credentials are properly set
- ✅ Ensure GOOGLE_APPLICATION_CREDENTIALS is set

#### **"Index not found"**
- ✅ Verify the index exists: `gcloud ai vector-search indexes list`
- ✅ Check that the index is deployed: `gcloud ai vector-search indexes describe`
- ✅ Ensure the index name matches exactly

#### **"API not enabled"**
- ✅ Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com`
- ✅ Wait a few minutes for API activation

### **Debug Commands**

#### **Check Index Status**
```bash
# List all indexes
gcloud ai vector-search indexes list --region=us-central1

# Describe specific index
gcloud ai vector-search indexes describe INDEX_ID --region=us-central1

# Check deployment status
gcloud ai vector-search indexes describe INDEX_ID --region=us-central1 --format="value(deployedIndexes)"
```

#### **Check Permissions**
```bash
# Test Vertex AI access
gcloud ai models list --region=us-central1

# Test Vector Search access
gcloud ai vector-search indexes list --region=us-central1
```

#### **Check Service Logs**
```bash
# Backend logs
gcloud run services logs read penny-assistant-backend --region=us-central1 --limit=50

# Filter for Vector Search
gcloud run services logs read penny-assistant-backend --region=us-central1 | grep -i "vector\|search\|embedding"
```

## 📊 Monitoring and Costs

### **Cost Considerations**
- **Vector Search**: Pay per query and storage
- **Vertex AI**: Pay per embedding generation
- **Storage**: Pay for index storage

### **Monitoring**
```bash
# Monitor Vector Search usage
gcloud ai vector-search indexes describe INDEX_ID --region=us-central1

# Check Vertex AI quotas
gcloud ai operations list --region=us-central1
```

## 🎉 Success Indicators

### **Configuration Success**
- ✅ Vector Search shows as "configured" in web interface
- ✅ Storage method shows "Vertex AI Vector Search (index-name)"
- ✅ Embedding method shows "Vertex AI (textembedding-gecko@001)"

### **Operation Success**
- ✅ PDF uploads store embeddings in Vector Search
- ✅ Queries return results from Vector Search
- ✅ No placeholder responses
- ✅ Real similarity search working

### **Performance Indicators**
- ✅ Embedding generation working
- ✅ Vector storage successful
- ✅ Query response times reasonable
- ✅ No authentication errors

## 🚀 Next Steps

1. **Test with Multiple PDFs**: Upload several documents and test cross-document search
2. **Optimize Index**: Adjust index parameters for better performance
3. **Monitor Usage**: Track costs and performance
4. **Scale as Needed**: Add more indexes or adjust capacity

---

**Happy Vector Searching! 🔍**

With Vector Search properly configured, Penny Assistant will now use real vector-based document search and retrieval, providing much more accurate and relevant results for your PDF queries. 