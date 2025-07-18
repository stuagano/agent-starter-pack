#!/bin/bash
set -e

# Enhanced deployment script for Penny Assistant
# This script deploys both services with placeholder implementations
# Users can configure Google Cloud services later through the web interface

echo "🚀 Deploying Penny Assistant (Enhanced Mode)"
echo "============================================"
echo ""
echo "This deployment uses placeholder implementations for all services."
echo "You can configure Google Cloud services later through the web interface."
echo ""

# Configuration
BACKEND_SERVICE_NAME="penny-assistant-backend"
FRONTEND_SERVICE_NAME="penny-assistant-frontend"
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project)

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate prerequisites
validate_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command_exists gcloud; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if project is set
    if [ -z "$PROJECT_ID" ]; then
        print_error "No Google Cloud project set"
        echo "Please run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud"
        echo "Please run: gcloud auth login"
        exit 1
    fi
    
    # Check if billing is enabled
    if ! gcloud billing projects describe $PROJECT_ID --format="value(billingEnabled)" | grep -q "True"; then
        print_warning "Billing is not enabled for project $PROJECT_ID"
        echo "Please enable billing at: https://console.cloud.google.com/billing/projects/$PROJECT_ID"
        echo "This is required for Cloud Run deployment."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Prerequisites validated"
}

# Function to enable APIs
enable_apis() {
    print_status "Enabling required APIs..."
    
    # Enable Cloud Run API
    gcloud services enable run.googleapis.com --quiet || {
        print_error "Failed to enable Cloud Run API"
        exit 1
    }
    
    # Enable Cloud Build API
    gcloud services enable cloudbuild.googleapis.com --quiet || {
        print_error "Failed to enable Cloud Build API"
        exit 1
    }
    
    # Enable Artifact Registry API (for container images)
    gcloud services enable artifactregistry.googleapis.com --quiet || {
        print_error "Failed to enable Artifact Registry API"
        exit 1
    }
    
    print_success "APIs enabled successfully"
}

# Function to validate service files
validate_service_files() {
    print_status "Validating service files..."
    
    # Check backend files
    if [ ! -f "backend/main.py" ]; then
        print_error "backend/main.py not found"
        exit 1
    fi
    
    if [ ! -f "backend/requirements.txt" ]; then
        print_error "backend/requirements.txt not found"
        exit 1
    fi
    
    if [ ! -f "backend/Dockerfile" ]; then
        print_error "backend/Dockerfile not found"
        exit 1
    fi
    
    if [ ! -f "backend/start.sh" ]; then
        print_error "backend/start.sh not found"
        exit 1
    fi
    
    # Check frontend files
    if [ ! -f "streamlit/app.py" ]; then
        print_error "streamlit/app.py not found"
        exit 1
    fi
    
    if [ ! -f "streamlit/requirements.txt" ]; then
        print_error "streamlit/requirements.txt not found"
        exit 1
    fi
    
    if [ ! -f "streamlit/Dockerfile" ]; then
        print_error "streamlit/Dockerfile not found"
        exit 1
    fi
    
    if [ ! -f "streamlit/start.sh" ]; then
        print_error "streamlit/start.sh not found"
        exit 1
    fi
    
    print_success "Service files validated"
}

# Function to deploy backend
deploy_backend() {
    print_status "Deploying Backend Service..."
    cd backend
    
    # Create setup_status.json for placeholder mode
    cat > setup_status.json << EOF
{
  "firestore": {"configured": false, "collection": "user_lists"},
  "calendar": {"configured": false, "credentials_file": null},
  "vertex_ai": {"configured": false, "embedding_model": "textembedding-gecko@001"},
  "vector_search": {"configured": false, "index_name": "penny-assistant-index"},
  "project_id": "$PROJECT_ID",
  "region": "$REGION"
}
EOF
    
    print_status "Building and deploying backend..."
    
    # Deploy with retry logic
    for attempt in 1 2 3; do
        if gcloud run deploy $BACKEND_SERVICE_NAME \
            --source . \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated \
            --port 8080 \
            --memory 1Gi \
            --cpu 1 \
            --max-instances 10 \
            --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
            --timeout 600 \
            --quiet; then
            break
        else
            if [ $attempt -eq 3 ]; then
                print_error "Backend deployment failed after 3 attempts"
                exit 1
            fi
            print_warning "Backend deployment attempt $attempt failed, retrying..."
            sleep 10
        fi
    done
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region=$REGION --format="value(status.url)" --quiet)
    
    if [ -z "$BACKEND_URL" ]; then
        print_error "Failed to get backend URL"
        exit 1
    fi
    
    print_success "Backend deployed successfully"
    echo "📋 Backend URL: $BACKEND_URL"
    
    # Test backend health
    print_status "Testing backend health..."
    sleep 10  # Wait for service to be ready
    
    if curl -f -s "$BACKEND_URL/healthz" > /dev/null; then
        print_success "Backend health check passed"
    else
        print_warning "Backend health check failed (service may still be starting)"
    fi
    
    cd ..
}

# Function to deploy frontend
deploy_frontend() {
    print_status "Deploying Frontend Service..."
    cd streamlit
    
    # Create config directory and setup_status.json
    mkdir -p config
    cat > config/setup_status.json << EOF
{
  "firestore": {"configured": false, "collection": "user_lists"},
  "calendar": {"configured": false, "credentials_file": null},
  "vertex_ai": {"configured": false, "embedding_model": "textembedding-gecko@001"},
  "vector_search": {"configured": false, "index_name": "penny-assistant-index"},
  "project_id": "$PROJECT_ID",
  "region": "$REGION"
}
EOF
    
    print_status "Building and deploying frontend..."
    
    # Deploy with retry logic
    for attempt in 1 2 3; do
        if gcloud run deploy $FRONTEND_SERVICE_NAME \
            --source . \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated \
            --port 8501 \
            --memory 1Gi \
            --cpu 1 \
            --max-instances 10 \
            --set-env-vars "BACKEND_URL=$BACKEND_URL,USER_ID=demo-user" \
            --timeout 600 \
            --quiet; then
            break
        else
            if [ $attempt -eq 3 ]; then
                print_error "Frontend deployment failed after 3 attempts"
                exit 1
            fi
            print_warning "Frontend deployment attempt $attempt failed, retrying..."
            sleep 10
        fi
    done
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --format="value(status.url)" --quiet)
    
    if [ -z "$FRONTEND_URL" ]; then
        print_error "Failed to get frontend URL"
        exit 1
    fi
    
    print_success "Frontend deployed successfully"
    echo "📋 Frontend URL: $FRONTEND_URL"
    
    # Test frontend health
    print_status "Testing frontend health..."
    sleep 10  # Wait for service to be ready
    
    if curl -f -s "$FRONTEND_URL/?health=check" > /dev/null; then
        print_success "Frontend health check passed"
    else
        print_warning "Frontend health check failed (service may still be starting)"
    fi
    
    cd ..
}

# Function to display summary
display_summary() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================"
    echo ""
    print_success "Backend Service: $BACKEND_URL"
    print_success "Frontend Service: $FRONTEND_URL"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Open the frontend URL in your browser"
    echo "2. Go to the 'Configuration' page"
    echo "3. Configure Google Cloud services as needed"
    echo "4. All features work with placeholders until configured"
    echo ""
    echo "📊 Service Status:"
    echo "   📝 Lists: Placeholder (Local JSON storage)"
    echo "   📅 Calendar: Placeholder (Demo events)"
    echo "   🤖 RAG: Placeholder (Mock embeddings)"
    echo "   🔍 Vector Search: Placeholder (Mock search)"
    echo ""
    echo "🔄 To upgrade to real services:"
    echo "   1. Go to Configuration page in the web interface"
    echo "   2. Follow the setup instructions for each service"
    echo "   3. Upload credentials and enable APIs"
    echo "   4. Export configuration to backend"
    echo ""
    echo "📚 Documentation:"
    echo "   - README.md - Complete setup guide"
    echo "   - DEPLOYMENT_READY.md - Technical deployment details"
    echo "   - GHERKIN_FEEDBACK_GUIDE.md - Feedback system guide"
    echo ""
    echo "🐛 Debugging:"
    echo "   - Use the 'Debug' tab in the web interface"
    echo "   - Check service logs: gcloud run services logs read"
    echo "   - Test health endpoints: $BACKEND_URL/healthz"
    echo ""
    echo "Happy coding with Penny Assistant! 🤖"
}

# Main execution
main() {
    echo "📋 Project: $PROJECT_ID"
    echo "🌍 Region: $REGION"
    echo ""
    
    # Run validation and deployment steps
    validate_prerequisites
    enable_apis
    validate_service_files
    deploy_backend
    deploy_frontend
    display_summary
}

# Run main function
main "$@" 