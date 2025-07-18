#!/bin/bash
set -e

# Streamlit Frontend Runner for Penny Assistant
# This script runs just the Streamlit frontend locally

echo "🎨 Starting Penny Assistant Streamlit Frontend"
echo "=============================================="
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
if [ ! -f "streamlit/app.py" ]; then
    print_error "Please run this script from the penny_assistant directory"
    echo "Current directory: $(pwd)"
    echo "Expected file: streamlit/app.py"
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

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd streamlit
pip install -r requirements.txt
cd ..

print_success "Dependencies installed"

# Set environment variables for local development
export BACKEND_URL=${BACKEND_URL:-"http://localhost:8080"}
export USER_ID=${USER_ID:-"demo-user"}
export STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=false
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Check if backend is running
print_status "Checking backend connection..."
if curl -s "$BACKEND_URL/healthz" > /dev/null 2>&1; then
    print_success "Backend is running at $BACKEND_URL"
else
    print_warning "Backend is not running at $BACKEND_URL"
    echo "You can start the backend with: ./run_local.sh"
    echo "Or set BACKEND_URL to point to your running backend"
    echo ""
fi

print_success "Starting Streamlit frontend..."
echo ""
echo "🌐 Frontend: http://localhost:$STREAMLIT_SERVER_PORT"
echo "🔧 Backend:  $BACKEND_URL"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start Streamlit
cd streamlit
streamlit run app.py 