#!/bin/bash
set -e

# Configuration
SERVICE_NAME="penny-assistant-backend"
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project)

echo "🚀 Deploying Penny Assistant Backend to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Validate configuration first
echo "🔍 Validating configuration..."
python validate_config.py

if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed. Please fix the issues above."
    exit 1
fi

echo "✅ Configuration validated successfully!"

# Check if gcloud is configured
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ No active gcloud account found. Please run 'gcloud auth login'"
    exit 1
fi

# Check if project is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project ID set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "✅ Using project: $PROJECT_ID"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Deploy to Cloud Run
echo "📦 Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --timeout 300

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📋 Service URL:"
    gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
    echo ""
    echo "🔗 Health check:"
    gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"/healthz
    echo ""
    echo "📊 View logs:"
    echo "gcloud run services logs read $SERVICE_NAME --region=$REGION"
    echo ""
    echo "⚙️  Update environment variables:"
    echo "gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars KEY=VALUE"
else
    echo "❌ Deployment failed. Check the logs above for details."
    exit 1
fi 