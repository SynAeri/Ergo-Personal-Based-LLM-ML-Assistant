#!/usr/bin/env bash
# Ergo setup script
# Initializes directories, databases, and checks dependencies

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Ergo Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Creating from template..."
    cp .env.template .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your API keys before running Ergo"
    echo
fi

# Create data directories
echo "Creating data directories..."
mkdir -p ~/.local/share/ergo/{events,session_summaries,screenshots,audio,repo_snapshots,models,backups}
mkdir -p ~/.config/ergo
echo "✅ Data directories created"
echo

# Check for required commands
echo "Checking dependencies..."

check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1"
    else
        echo "❌ $1 not found"
        MISSING_DEPS=true
    fi
}

MISSING_DEPS=false

check_command cargo
check_command python3
check_command curl
check_command jq

if [ "$MISSING_DEPS" = true ]; then
    echo
    echo "⚠️  Some dependencies are missing. Please install them or use 'nix develop'"
    exit 1
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run 'nix develop' to enter development environment"
echo "3. Run 'cargo build --release' to build the daemon"
echo "4. Start services (see README.md for details)"
echo
