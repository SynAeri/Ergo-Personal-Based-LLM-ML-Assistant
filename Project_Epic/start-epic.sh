#!/bin/bash
# Project Epic - Start Both Backend and Frontend
# This script connects to the FastAPI backend and Next.js frontend for Project Epic

echo "🎮 PROJECT EPIC - STARTING..."
echo "═══════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -f "test_standalone.py" ]; then
    echo "❌ Error: Run this script from Project_Epic directory"
    echo "   cd ~/Documents/Github/Ergo/Project_Epic"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js not found"
    echo "   Install Node.js from https://nodejs.org"
    exit 1
fi

# Check Python venv
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Run: python3 -m venv venv"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Error: Frontend directory not found"
    echo "   Frontend should be at: ./frontend"
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✓ Frontend dependencies installed"
fi

echo "🚀 Starting Project Epic..."
echo ""
echo "Backend will run at:  http://localhost:8766"
echo "Frontend will run at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
source venv/bin/activate
python -m epic.api.server &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both servers
echo ""
echo "✓ Both servers are starting!"
echo ""
echo "═══════════════════════════════════════"
echo "🌐 Open in browser: http://localhost:3000"
echo "═══════════════════════════════════════"
echo ""

# Keep script running
wait
