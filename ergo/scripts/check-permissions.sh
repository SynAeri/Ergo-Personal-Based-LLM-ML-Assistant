#!/usr/bin/env bash
# Ergo permissions diagnostic script
# Checks if the daemon has authority to scan required system resources

echo "=== Ergo Permissions Diagnostic ==="
echo ""

# Check xdotool
echo "[1] Checking xdotool (X11 window monitoring)..."
if command -v xdotool &> /dev/null; then
  echo "    ✓ xdotool found: $(xdotool --version 2>&1 | head -1)"
  if xdotool getactivewindow &> /dev/null; then
    echo "    ✓ Can read active window"
  else
    echo "    ✗ Cannot read active window (not in X11 session?)"
  fi
else
  echo "    ✗ xdotool not found"
  echo "      Fix: Add xdotool to your nix-shell or system packages"
fi

# Check /proc access
echo ""
echo "[2] Checking /proc filesystem (process monitoring)..."
if [ -r /proc/self/comm ]; then
  echo "    ✓ Can read /proc/self/comm: $(cat /proc/self/comm)"
  echo "    ✓ Can read process list: $(ls /proc/ | grep -E '^[0-9]+$' | wc -l) processes visible"
else
  echo "    ✗ Cannot read /proc filesystem"
  echo "      This should never happen on standard Linux - check permissions"
fi

# Check git
echo ""
echo "[3] Checking git access (repository tracking)..."
if command -v git &> /dev/null; then
  echo "    ✓ git found: $(git --version)"
  # Check if we're in a git repo
  if git rev-parse --git-dir &> /dev/null 2>&1; then
    echo "    ✓ Currently in git repository: $(basename $(git rev-parse --show-toplevel))"
    if git status &> /dev/null; then
      echo "    ✓ Can read git status"
    else
      echo "    ✗ Cannot read git status (permissions issue?)"
    fi
  else
    echo "    ℹ Not in a git repository (this is fine)"
  fi
else
  echo "    ✗ git not found"
  echo "      Fix: Add git to your environment"
fi

# Check shell history
echo ""
echo "[4] Checking shell history files..."
FOUND_HISTORY=false
for hist in ~/.bash_history ~/.zsh_history ~/.local/share/fish/fish_history; do
  if [ -f "$hist" ]; then
    LINES=$(wc -l < "$hist" 2>/dev/null || echo "0")
    echo "    ✓ Found $hist ($LINES lines)"
    if [ -r "$hist" ]; then
      echo "      ✓ Readable"
    else
      echo "      ✗ Not readable - check permissions"
    fi
    FOUND_HISTORY=true
  fi
done
if [ "$FOUND_HISTORY" = false ]; then
  echo "    ℹ No shell history files found (check your shell configuration)"
fi

# Check Ergo directories
echo ""
echo "[5] Checking Ergo data directories..."
ERGO_DIR="${HOME}/.local/share/ergo"
if [ -d "$ERGO_DIR" ]; then
  echo "    ✓ Data directory exists: $ERGO_DIR"
  if [ -w "$ERGO_DIR" ]; then
    echo "    ✓ Writable"
  else
    echo "    ✗ Not writable - fix with: chmod u+w $ERGO_DIR"
  fi

  # Check subdirectories
  for subdir in events session_summaries screenshots audio repo_snapshots models backups; do
    if [ -d "$ERGO_DIR/$subdir" ]; then
      echo "    ✓ $subdir/ exists"
    fi
  done
else
  echo "    ✗ Data directory missing: $ERGO_DIR"
  echo "      Fix: mkdir -p $ERGO_DIR/{events,session_summaries,screenshots,audio,repo_snapshots,models,backups}"
fi

# Check config directory
ERGO_CONFIG_DIR="${HOME}/.config/ergo"
if [ -d "$ERGO_CONFIG_DIR" ]; then
  echo "    ✓ Config directory exists: $ERGO_CONFIG_DIR"
else
  echo "    ℹ Config directory not found: $ERGO_CONFIG_DIR (will be created on first run)"
fi

# Check .env file
ERGO_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$ERGO_PROJECT_ROOT/.env" ]; then
  echo "    ✓ .env file found: $ERGO_PROJECT_ROOT/.env"
else
  echo "    ✗ .env file missing"
  echo "      Fix: cp $ERGO_PROJECT_ROOT/.env.template $ERGO_PROJECT_ROOT/.env"
  echo "           Then edit .env with your API keys"
fi

# Check socket path
echo ""
echo "[6] Checking socket permissions (IPC communication)..."
SOCK_DIR="/tmp"
if [ -w "$SOCK_DIR" ]; then
  echo "    ✓ Can write to $SOCK_DIR for Unix sockets"

  # Check for existing socket
  if [ -S "/tmp/ergo-daemon.sock" ]; then
    echo "    ℹ Existing socket found: /tmp/ergo-daemon.sock"
    echo "      (Daemon may already be running, or stale socket)"
  fi
else
  echo "    ✗ Cannot write to $SOCK_DIR"
  echo "      This should never happen - check filesystem permissions"
fi

# Check for running instances
echo ""
echo "[7] Checking for running Ergo processes..."
if pgrep -f ergo-daemon > /dev/null; then
  echo "    ✓ Daemon appears to be running (PID: $(pgrep -f ergo-daemon))"
elif pgrep -f "ergo.*orchestrator" > /dev/null; then
  echo "    ✓ Orchestrator appears to be running (PID: $(pgrep -f 'ergo.*orchestrator'))"
else
  echo "    ℹ No Ergo processes detected (not running)"
fi

# Check Python environment (for orchestrator)
echo ""
echo "[8] Checking Python environment (orchestrator)..."
if command -v python3 &> /dev/null; then
  echo "    ✓ python3 found: $(python3 --version)"

  # Check for required Python packages
  if python3 -c "import fastapi" 2>/dev/null; then
    echo "    ✓ fastapi installed"
  else
    echo "    ✗ fastapi not installed"
    echo "      Fix: pip install -r orchestrator/requirements.txt"
  fi

  if python3 -c "import anthropic" 2>/dev/null; then
    echo "    ✓ anthropic package installed"
  else
    echo "    ✗ anthropic package not installed"
  fi
else
  echo "    ✗ python3 not found"
fi

# Check Rust/Cargo (for daemon)
echo ""
echo "[9] Checking Rust environment (daemon)..."
if command -v cargo &> /dev/null; then
  echo "    ✓ cargo found: $(cargo --version)"
else
  echo "    ✗ cargo not found"
  echo "      Fix: Install Rust or activate nix-shell"
fi

echo ""
echo "=== Diagnostic Complete ==="
echo ""
echo "Summary:"
echo "  - Review any ✗ items above and apply the suggested fixes"
echo "  - Items marked ℹ are informational and may not need action"
echo "  - See PERMISSIONS.md for detailed configuration instructions"
