#!/usr/bin/env bash
# Run all Ergo services in tmux
# Usage: ./run-all.sh

set -e

echo "Starting Ergo services in tmux..."
echo

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is required but not installed"
    echo "Install with: sudo pacman -S tmux (Arch) or sudo apt install tmux (Ubuntu)"
    exit 1
fi

# Kill existing session if it exists
tmux kill-session -t ergo 2>/dev/null || true

# Create new session
tmux new-session -d -s ergo -n daemon

# Window 1: Daemon
tmux send-keys -t ergo:daemon "cd $(pwd) && ./target/release/ergo" C-m

# Window 2: Orchestrator
tmux new-window -t ergo -n orchestrator
tmux send-keys -t ergo:orchestrator "cd $(pwd) && ./run-orchestrator.sh" C-m

# Window 3: UI
tmux new-window -t ergo -n ui
tmux send-keys -t ergo:ui "cd $(pwd) && ./run-ui.sh" C-m

# Select daemon window
tmux select-window -t ergo:daemon

echo "✓ Ergo services started in tmux session 'ergo'"
echo
echo "To attach: tmux attach -t ergo"
echo "To detach: Ctrl+b then d"
echo "To switch windows: Ctrl+b then 0/1/2"
echo "To kill all: tmux kill-session -t ergo"
echo
echo "Services:"
echo "  - Daemon (window 0)"
echo "  - Orchestrator on http://127.0.0.1:8765 (window 1)"
echo "  - UI on http://localhost:3000 (window 2)"
echo

# Auto-attach
tmux attach -t ergo
