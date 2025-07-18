# Penny Assistant Backend Deployment Guide

## Cloud Run Requirements

This backend is configured to meet all Cloud Run container runtime requirements:

### ✅ Port Configuration
- **Dynamic Port Binding**: Uses `PORT` environment variable (Cloud Run requirement)
- **All Interfaces**: Listens on `0.0.0.0` (not just localhost)
- **Fallback**: Defaults to port 8080 if `PORT` not set

### ✅ Container Configuration
- **64-bit Linux**: Uses `python:3.10-slim` base image
- **Stateless**: No persistent storage dependencies
- **Health Check**: `/healthz` endpoint for Cloud Run health monitoring

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
2. Test on default port (8080)
3. Test with custom PORT environment variable
4. Verify health endpoint responses
5. Clean up test containers

## Manual Testing

You can also test manually:

```bash
# Build container
docker build -t penny-assistant-backend .

# Test with default port
docker run -d --name penny-test -p 8080:8080 penny-assistant-backend
curl http://localhost:8080/healthz

# Test with custom port (simulates Cloud Run)
docker run -d --name penny-test-port -p 9000:9000 -e PORT=9000 penny-assistant-backend
curl http://localhost:9000/healthz

# Cleanup
docker stop penny-test penny-test-port
docker rm penny-test penny-test-port
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

### Deploy Command

```bash
# Build and deploy to Cloud Run
gcloud run deploy penny-assistant-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

### Environment Variables

Set these in Cloud Run console or via gcloud:

```bash
# Required for Google Cloud services
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Customize behavior
LOG_LEVEL=INFO
```

### Health Check Configuration

Cloud Run will automatically use the `/healthz` endpoint for health checks.

## Troubleshooting

### Common Issues

1. **Container won't start**
   - Check logs: `gcloud run services logs read penny-assistant-backend`
   - Verify PORT environment variable is being read
   - Ensure container listens on 0.0.0.0

2. **Health check failures**
   - Verify `/healthz` endpoint returns 200 OK
   - Check application startup logs
   - Ensure no blocking operations during startup

3. **Permission errors**
   - Verify service account has required permissions
   - Check Google Cloud project configuration

### Debug Commands

```bash
# View service logs
gcloud run services logs read penny-assistant-backend

# Describe service configuration
gcloud run services describe penny-assistant-backend

# Update service with new configuration
gcloud run services update penny-assistant-backend --update-env-vars KEY=VALUE
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   FastAPI App    │    │   Google Cloud  │
│                 │    │                  │    │   Services      │
│ • PORT env var  │───▶│ • Dynamic port   │───▶│ • Firestore     │
│ • Health checks │    │ • 0.0.0.0 host   │    │ • Vertex AI     │
│ • Auto-scaling  │    │ • /healthz       │    │ • Calendar API  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Performance Optimization

- **Memory**: 1Gi recommended for PDF processing
- **CPU**: 1 vCPU for most workloads
- **Concurrency**: 80 requests per instance (default)
- **Max Instances**: 10 to control costs

## Security Best Practices

- Use service accounts with minimal required permissions
- Enable Cloud Audit Logs
- Regularly update base image and dependencies
- Use private container registry for production
- Enable VPC connector if needed for private services 