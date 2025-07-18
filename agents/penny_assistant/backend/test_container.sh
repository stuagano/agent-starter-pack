#!/bin/bash
set -e

echo "🧪 Testing Penny Assistant container locally..."

# Build the container
echo "📦 Building container..."
docker build -t penny-assistant-backend .

# Test the container locally
echo "🚀 Starting container locally..."
docker run -d --name penny-test -p 8080:8080 penny-assistant-backend

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Test health endpoint
echo "🏥 Testing health endpoint..."
curl -f http://localhost:8080/healthz || {
    echo "❌ Health check failed"
    docker logs penny-test
    docker stop penny-test
    docker rm penny-test
    exit 1
}

echo "✅ Health check passed!"

# Test with different port (simulating Cloud Run)
echo "🔧 Testing with PORT environment variable..."
docker stop penny-test
docker rm penny-test

docker run -d --name penny-test-port -p 9000:9000 -e PORT=9000 penny-assistant-backend

sleep 5

curl -f http://localhost:9000/healthz || {
    echo "❌ Port test failed"
    docker logs penny-test-port
    docker stop penny-test-port
    docker rm penny-test-port
    exit 1
}

echo "✅ Port test passed!"

# Cleanup
echo "🧹 Cleaning up..."
docker stop penny-test-port
docker rm penny-test-port

echo "🎉 All tests passed! Container is ready for Cloud Run deployment." 