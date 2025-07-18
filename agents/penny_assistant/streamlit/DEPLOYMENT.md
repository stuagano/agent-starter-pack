# Penny Assistant Streamlit Frontend Deployment Guide

## Cloud Run Requirements

This Streamlit frontend is configured to meet all Cloud Run container runtime requirements:

### ✅ Port Configuration
- **Dynamic Port Binding**: Uses `PORT` environment variable (Cloud Run requirement)
- **All Interfaces**: Listens on `0.0.0.0` (not just localhost)
- **Fallback**: Defaults to port 8501 if `PORT` not set

### ✅ Container Configuration
- **64-bit Linux**: Uses `python:3.10-slim` base image
- **Stateless**: No persistent storage dependencies
- **Health Check**: `/?health=check` endpoint for Cloud Run health monitoring

### ✅ Streamlit-Specific Configuration
- **Headless Mode**: Runs without browser dependencies
- **CORS Disabled**: Optimized for Cloud Run environment
- **XSRF Protection Disabled**: Not needed in Cloud Run context

### ✅ Security & Performance
- **Non-root**: Runs as non-root user
- **Optimized**: Multi-stage build with proper caching
- **Minimal**: Only necessary dependencies included

## Local Testing

Before deploying to Cloud Run, test your container locally:

```bash
# Make test script executable
chmod +x test_container.sh

# Run comprehensive local tests
./test_container.sh
```

This will:
1. Build the container
2. Test on default port (8501)
3. Test with custom PORT environment variable
4. Test with BACKEND_URL environment variable
5. Verify health endpoint responses
6. Clean up test containers

## Manual Testing

You can also test manually:

```bash
# Build container
docker build -t penny-assistant-frontend .

# Test with default port
docker run -d --name penny-frontend-test -p 8501:8501 penny-assistant-frontend
curl "http://localhost:8501/?health=check"

# Test with custom port (simulates Cloud Run)
docker run -d --name penny-frontend-test-port -p 9000:9000 -e PORT=9000 penny-assistant-frontend
curl "http://localhost:9000/?health=check"

# Test with backend URL
docker run -d --name penny-frontend-test-backend -p 8501:8501 \
    -e BACKEND_URL="http://test-backend:8080" \
    penny-assistant-frontend

# Cleanup
docker stop penny-frontend-test penny-frontend-test-port penny-frontend-test-backend
docker rm penny-frontend-test penny-frontend-test-port penny-frontend-test-backend
```

## Cloud Run Deployment

### Prerequisites
1. Google Cloud Project with required APIs enabled:
   - Cloud Run API
   - Container Registry API
   - Cloud Build API

2. Service account with permissions:
   - Cloud Run Admin
   - Storage Admin (for container registry)

3. Backend service deployed and accessible

### Deploy Command

```bash
# Build and deploy to Cloud Run
gcloud run deploy penny-assistant-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars "BACKEND_URL=YOUR_BACKEND_URL,USER_ID=demo-user"
```

### Environment Variables

Set these in Cloud Run console or via gcloud:

```bash
# Required: Backend service URL
BACKEND_URL=https://your-backend-service-url

# Optional: Default user ID
USER_ID=demo-user

# Automatically set by Cloud Run
PORT=8501
```

### Health Check Configuration

Cloud Run will automatically use the `/?health=check` endpoint for health checks.

## Frontend-Backend Integration

### Configuration
The frontend communicates with the backend via HTTP requests. Ensure:

1. **Backend URL**: Set `BACKEND_URL` environment variable to your backend service URL
2. **CORS**: Backend should allow requests from frontend domain
3. **Authentication**: Configure proper authentication if needed

### Environment Setup
```bash
# Local development
BACKEND_URL=http://localhost:8080

# Production (after backend deployment)
BACKEND_URL=https://penny-assistant-backend-xxxxx-uc.a.run.app
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   - Check logs: `gcloud run services logs read penny-assistant-frontend`
   - Verify PORT environment variable is being read
   - Ensure container listens on 0.0.0.0

2. **Health check failures**
   - Verify `/?health=check` endpoint returns 200 OK
   - Check application startup logs
   - Ensure no blocking operations during startup

3. **Backend connection issues**
   - Verify BACKEND_URL is correct
   - Check backend service is running
   - Ensure CORS is properly configured

4. **Streamlit-specific issues**
   - Check if running in headless mode
   - Verify all dependencies are installed
   - Check for missing environment variables

### Debug Commands

```bash
# View service logs
gcloud run services logs read penny-assistant-frontend

# Describe service configuration
gcloud run services describe penny-assistant-frontend

# Update environment variables
gcloud run services update penny-assistant-frontend --update-env-vars KEY=VALUE

# Update backend URL
gcloud run services update penny-assistant-frontend --update-env-vars BACKEND_URL=NEW_URL
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Streamlit App  │    │   Backend API   │
│   Frontend      │    │                  │    │   (Cloud Run)   │
│                 │    │                  │    │                 │
│ • PORT env var  │───▶│ • Dynamic port   │───▶│ • FastAPI       │
│ • Health checks │    │ • 0.0.0.0 host   │    │ • PDF/RAG       │
│ • Auto-scaling  │    │ • /?health=check │    │ • Lists         │
│                 │    │ • Headless mode  │    │ • Calendar      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Performance Optimization

- **Memory**: 1Gi recommended for Streamlit operations
- **CPU**: 1 vCPU for most workloads
- **Concurrency**: 80 requests per instance (default)
- **Max Instances**: 10 to control costs
- **Streamlit Config**: Headless mode for better performance

## Security Best Practices

- Use service accounts with minimal required permissions
- Enable Cloud Audit Logs
- Regularly update base image and dependencies
- Use private container registry for production
- Configure proper CORS settings
- Validate all user inputs

## Development Workflow

1. **Local Development**:
   ```bash
   streamlit run app.py --server.port=8501
   ```

2. **Test Locally**:
   ```bash
   ./test_container.sh
   ```

3. **Deploy**:
   ```bash
   ./deploy.sh
   ```

4. **Monitor**:
   ```bash
   gcloud run services logs read penny-assistant-frontend
   ```

## Environment-Specific Configuration

### Local Development
- `BACKEND_URL=http://localhost:8080`
- `USER_ID=demo-user`
- Streamlit runs in development mode

### Production (Cloud Run)
- `BACKEND_URL=https://your-backend-service-url`
- `USER_ID=demo-user` (or user-specific)
- Streamlit runs in headless mode
- Health checks enabled
- Auto-scaling configured 