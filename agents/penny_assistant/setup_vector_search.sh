#!/bin/bash
set -e

# Vector Search Setup Script for Penny Assistant
# This script automates the setup of Vertex AI Vector Search

echo "🔍 Setting up Vertex AI Vector Search for Penny Assistant"
echo "========================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
INDEX_NAME="penny-assistant-index"

if [ -z "$PROJECT_ID" ]; then
    print_error "No Google Cloud project set"
    echo "Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔍 Index Name: $INDEX_NAME"
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with Google Cloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if billing is enabled
if ! gcloud billing projects describe $PROJECT_ID --format="value(billingEnabled)" | grep -q "True"; then
    print_error "Billing is not enabled for project $PROJECT_ID"
    echo "Please enable billing at: https://console.cloud.google.com/billing/projects/$PROJECT_ID"
    exit 1
fi

print_success "Prerequisites validated"

# Enable required APIs
print_status "Enabling required APIs..."

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com --quiet || {
    print_error "Failed to enable Vertex AI API"
    exit 1
}

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com --quiet || {
    print_error "Failed to enable Cloud Storage API"
    exit 1
}

# Enable IAM API
gcloud services enable iam.googleapis.com --quiet || {
    print_error "Failed to enable IAM API"
    exit 1
}

print_success "APIs enabled successfully"

# Create Vector Search index
print_status "Creating Vector Search index..."

# Check if index already exists
if gcloud ai vector-search indexes list --region=$REGION --project=$PROJECT_ID --format="value(displayName)" | grep -q "$INDEX_NAME"; then
    print_warning "Index '$INDEX_NAME' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get index ID and delete it
        INDEX_ID=$(gcloud ai vector-search indexes list --region=$REGION --project=$PROJECT_ID --format="value(name)" | grep "$INDEX_NAME")
        if [ ! -z "$INDEX_ID" ]; then
            print_status "Deleting existing index..."
            gcloud ai vector-search indexes delete $INDEX_ID --region=$REGION --project=$PROJECT_ID --quiet || {
                print_warning "Failed to delete existing index, continuing..."
            }
        fi
    else
        print_status "Using existing index"
        INDEX_ID=$(gcloud ai vector-search indexes list --region=$REGION --project=$PROJECT_ID --format="value(name)" | grep "$INDEX_NAME")
    fi
fi

# Create index if it doesn't exist
if [ -z "$INDEX_ID" ]; then
    print_status "Creating new Vector Search index..."
    
    # Create index using gcloud command
    INDEX_ID=$(gcloud ai vector-search indexes create \
        --display-name="$INDEX_NAME" \
        --description="Index for Penny Assistant PDF embeddings" \
        --region=$REGION \
        --project=$PROJECT_ID \
        --embedding-dimension=768 \
        --distance-measure-type="COSINE_DISTANCE" \
        --format="value(name)" 2>/dev/null || echo "")
    
    if [ -z "$INDEX_ID" ]; then
        print_error "Failed to create Vector Search index"
        exit 1
    fi
    
    print_success "Vector Search index created: $INDEX_ID"
else
    print_success "Using existing index: $INDEX_ID"
fi

# Deploy the index
print_status "Deploying Vector Search index..."

# Check if index is already deployed
DEPLOYMENT_STATUS=$(gcloud ai vector-search indexes describe $INDEX_ID --region=$REGION --project=$PROJECT_ID --format="value(deployedIndexes)" 2>/dev/null || echo "")

if [ -z "$DEPLOYMENT_STATUS" ]; then
    print_status "Deploying index..."
    gcloud ai vector-search indexes deploy \
        --index=$INDEX_ID \
        --region=$REGION \
        --project=$PROJECT_ID --quiet || {
        print_error "Failed to deploy Vector Search index"
        exit 1
    }
    print_success "Vector Search index deployed successfully"
else
    print_success "Index is already deployed"
fi

# Create configuration files
print_status "Creating configuration files..."

# Backend configuration
cat > backend/setup_status.json << EOF
{
  "firestore": {"configured": false, "collection": "user_lists"},
  "calendar": {"configured": false, "credentials_file": null},
  "vertex_ai": {
    "configured": true,
    "embedding_model": "textembedding-gecko@001"
  },
  "vector_search": {
    "configured": true,
    "index_name": "$INDEX_NAME"
  },
  "project_id": "$PROJECT_ID",
  "region": "$REGION"
}
EOF

# Frontend configuration
mkdir -p streamlit/config
cat > streamlit/config/setup_status.json << EOF
{
  "firestore": {"configured": false, "collection": "user_lists"},
  "calendar": {"configured": false, "credentials_file": null},
  "vertex_ai": {
    "configured": true,
    "embedding_model": "textembedding-gecko@001"
  },
  "vector_search": {
    "configured": true,
    "index_name": "$INDEX_NAME"
  },
  "project_id": "$PROJECT_ID",
  "region": "$REGION"
}
EOF

print_success "Configuration files created"

# Test Vector Search access
print_status "Testing Vector Search access..."

# Test if we can list indexes
if gcloud ai vector-search indexes list --region=$REGION --project=$PROJECT_ID --limit=1 > /dev/null 2>&1; then
    print_success "Vector Search access confirmed"
else
    print_warning "Vector Search access test failed - check permissions"
fi

# Summary
echo ""
echo "🎉 Vector Search Setup Complete!"
echo "================================"
echo ""
print_success "Project: $PROJECT_ID"
print_success "Region: $REGION"
print_success "Index Name: $INDEX_NAME"
print_success "Index ID: $INDEX_ID"
echo ""
echo "📋 Configuration Files Created:"
echo "   ✅ backend/setup_status.json"
echo "   ✅ streamlit/config/setup_status.json"
echo ""
echo "🚀 Next Steps:"
echo "1. Redeploy your services to use the new configuration:"
echo "   ./deploy_simple.sh"
echo ""
echo "2. Test Vector Search functionality:"
echo "   - Upload a PDF in the web interface"
echo "   - Verify storage method shows 'Vertex AI Vector Search ($INDEX_NAME)'"
echo "   - Ask questions about your PDF"
echo ""
echo "3. Monitor Vector Search usage:"
echo "   gcloud ai vector-search indexes describe $INDEX_ID --region=$REGION"
echo ""
echo "📚 Documentation:"
echo "   - VECTOR_SEARCH_SETUP.md - Detailed setup guide"
echo "   - README.md - Complete project overview"
echo ""
echo "Happy Vector Searching! 🔍" 