#!/bin/bash
set -e

# Local Development Script for Penny Assistant
# This script runs both backend and frontend locally

echo "🏠 Starting Penny Assistant Locally"
echo "=================================="
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

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "streamlit/app.py" ]; then
    print_error "Please run this script from the penny_assistant directory"
    echo "Current directory: $(pwd)"
    echo "Expected files:"
    echo "  - backend/main.py"
    echo "  - streamlit/app.py"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."

# Install backend dependencies
print_status "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd streamlit
pip install -r requirements.txt
cd ..

print_success "Dependencies installed"

# Check if backend is already running
BACKEND_URL="http://localhost:8080"
if curl -s "$BACKEND_URL/healthz" > /dev/null 2>&1; then
    print_warning "Backend is already running on $BACKEND_URL"
    read -p "Do you want to restart it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping existing backend..."
        pkill -f "uvicorn main:app" || true
        sleep 2
    else
        print_status "Using existing backend"
        BACKEND_RUNNING=true
    fi
fi

# Start backend if not running
if [ "$BACKEND_RUNNING" != "true" ]; then
    print_status "Starting backend server..."
    cd backend
    
    # Set environment variables for local development
    export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-"demo-project"}
    export USER_ID=${USER_ID:-"demo-user"}
    
    # Start backend in background
    python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s "$BACKEND_URL/healthz" > /dev/null 2>&1; then
            print_success "Backend started successfully"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
fi

# Start frontend
print_status "Starting Streamlit frontend..."
cd streamlit

# Set environment variables for local development
export BACKEND_URL=$BACKEND_URL
export USER_ID=${USER_ID:-"demo-user"}
export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=false
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

print_success "Starting Penny Assistant..."
echo ""
echo "🌐 Frontend: http://localhost:$STREAMLIT_SERVER_PORT"
echo "🔧 Backend:  $BACKEND_URL"
echo "📊 Health:   $BACKEND_URL/healthz"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "streamlit run" 2>/dev/null || true
    print_success "Services stopped"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start Streamlit
streamlit run app.py

# This should not be reached unless Streamlit exits unexpectedly
cleanup 