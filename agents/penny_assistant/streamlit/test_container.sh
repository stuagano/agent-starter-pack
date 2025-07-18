#!/bin/bash
set -e

echo "🧪 Testing Penny Assistant Streamlit Frontend container locally..."

# Build the container
echo "📦 Building container..."
docker build -t penny-assistant-frontend .

# Test the container locally
echo "🚀 Starting container locally..."
docker run -d --name penny-frontend-test -p 8501:8501 penny-assistant-frontend

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Test health endpoint
echo "🏥 Testing health endpoint..."
curl -f "http://localhost:8501/?health=check" || {
    echo "❌ Health check failed"
    docker logs penny-frontend-test
    docker stop penny-frontend-test
    docker rm penny-frontend-test
    exit 1
}

echo "✅ Health check passed!"

# Test with different port (simulating Cloud Run)
echo "🔧 Testing with PORT environment variable..."
docker stop penny-frontend-test
docker rm penny-frontend-test

docker run -d --name penny-frontend-test-port -p 9000:9000 -e PORT=9000 penny-assistant-frontend

sleep 10

curl -f "http://localhost:9000/?health=check" || {
    echo "❌ Port test failed"
    docker logs penny-frontend-test-port
    docker stop penny-frontend-test-port
    docker rm penny-frontend-test-port
    exit 1
}

echo "✅ Port test passed!"

# Test with backend URL environment variable
echo "🔗 Testing with BACKEND_URL environment variable..."
docker stop penny-frontend-test-port
docker rm penny-frontend-test-port

docker run -d --name penny-frontend-test-backend -p 8501:8501 \
    -e BACKEND_URL="http://test-backend:8080" \
    -e USER_ID="test-user" \
    penny-assistant-frontend

sleep 10

curl -f "http://localhost:8501/?health=check" || {
    echo "❌ Backend URL test failed"
    docker logs penny-frontend-test-backend
    docker stop penny-frontend-test-backend
    docker rm penny-frontend-test-backend
    exit 1
}

echo "✅ Backend URL test passed!"

# Cleanup
echo "🧹 Cleaning up..."
docker stop penny-frontend-test-backend
docker rm penny-frontend-test-backend

echo "🎉 All tests passed! Streamlit frontend container is ready for Cloud Run deployment." 