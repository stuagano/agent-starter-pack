#!/bin/bash
set -e

# Get port from environment variable (Cloud Run requirement)
PORT=${PORT:-8501}

echo "Starting Penny Assistant Streamlit App on port $PORT"

# Start the Streamlit application
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false 