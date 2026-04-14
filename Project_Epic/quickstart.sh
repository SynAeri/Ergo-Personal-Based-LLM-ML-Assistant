#!/bin/bash
# Project Epic - Quick Start Script

echo "🎮 PROJECT EPIC - QUICK START"
echo "═══════════════════════════════════════"
echo ""

# Check if we're in the right directory
if [ ! -f "test_standalone.py" ]; then
    echo "❌ Error: Run this script from Project_Epic directory"
    echo "   cd ~/Documents/Github/Ergo/Project_Epic"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found"
    exit 1
fi

echo "✓ Python 3 found"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.deps_installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
    touch venv/.deps_installed
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Check API keys
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not set"
    echo "   For real AI execution, set:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
    echo "   For testing without AI, this is fine!"
    echo ""
fi

# Menu
echo "═══════════════════════════════════════"
echo "What would you like to do?"
echo ""
echo "1. Run command-line tests (no AI calls)"
echo "2. Start web interface"
echo "3. Both (tests then web)"
echo "4. Exit"
echo ""
printf "Choice (1-4): "
read choice

case $choice in
    1)
        echo ""
        echo "🧪 Running tests..."
        python test_standalone.py
        ;;
    2)
        echo ""
        echo "🌐 Starting web server..."
        echo "   Open: http://localhost:8766"
        echo ""
        python -m epic.api.server
        ;;
    3)
        echo ""
        echo "🧪 Running tests first..."
        python test_standalone.py
        echo ""
        printf "Press Enter to start web server..."
        read dummy
        echo "🌐 Starting web server..."
        echo "   Open: http://localhost:8766"
        echo ""
        python -m epic.api.server
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
