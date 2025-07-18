#!/bin/bash
set -e

# Get port from environment variable (Cloud Run requirement)
PORT=${PORT:-8080}

echo "Starting Penny Assistant API on port $PORT"

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port $PORT 