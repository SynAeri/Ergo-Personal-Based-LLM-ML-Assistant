# Run Ergo Right Now

Your daemon is already running! Here's how to complete the setup.

## Current Status

 **Daemon:** Running and monitoring windows
 **API Keys:** Configured in .env
 **Build:** Complete

## Next Steps

### 1. Open a New Terminal

Press `Ctrl+Shift+T` or open a new terminal tab.

### 2. Enter Nix Environment

```bash
cd /path/to/ergo/ergo
nix-shell
```

You'll see the environment loaded with all Python packages.

### 3. Start Orchestrator

```bash
./run-orchestrator.sh
```

You should see:
```
Starting Ergo Orchestrator...
API will be available at: http://127.0.0.1:8765

INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8765
```

### 4. Open Another Terminal for UI

Press `Ctrl+Shift+T` again.

```bash
cd /path/to/ergo/ergo
nix-shell
./run-ui.sh
```

You should see:
```
Starting Ergo UI...
Interface will be available at: http://localhost:3000

INFO:     Uvicorn running on http://127.0.0.1:3000
```

### 5. Open Your Browser

Navigate to: **http://localhost:3000**

You should see the Ergo chat interface!

## Quick Test

In the chat box, type:
```
What am I working on right now?
```

Ergo will use your recent window activity to respond with context.

## Alternative: Use tmux

If you prefer everything in one terminal:

1. Stop the daemon (Ctrl+C in that terminal)
2. Run:
```bash
cd /path/to/ergo/ergo
nix-shell
./run-all.sh
```

This starts all three services in tmux windows:
- `Ctrl+b` then `0` - Daemon
- `Ctrl+b` then `1` - Orchestrator
- `Ctrl+b` then `2` - UI

## Verify Everything

### Check Daemon
```bash
./target/release/ergo stats
```

### Check Orchestrator
```bash
curl http://127.0.0.1:8765/health | jq
```

### Check UI
Open: http://localhost:3000

## What You Can Do

**In the Web UI:**
- Chat with full context awareness
- View recent activity
- See today's stats
- Get interventions (when implemented)

**On Command Line:**
```bash
# View stats
./target/release/ergo stats

# Test API
curl http://127.0.0.1:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}' | jq .response

# Get recent context
curl http://127.0.0.1:8765/context/recent?minutes=30 | jq
```

**In Neovim (after installing plugin):**
- `:ErgoExplainContext`
- `:ErgoJudgeThisCode`
- `:ErgoCommitReview`

## Troubleshooting

### "uvicorn: command not found"

Make sure you're in nix-shell:
```bash
nix-shell
which uvicorn  # Should show a path
```

### Port Already in Use

```bash
# Find what's using port 8765
lsof -i :8765

# Kill it
kill -9 <PID>
```

### UI Can't Connect to Orchestrator

Make sure orchestrator is running:
```bash
curl http://127.0.0.1:8765/health
```

If not, start it:
```bash
nix-shell
./run-orchestrator.sh
```

## Stop Everything

**If using tmux:**
```bash
tmux kill-session -t ergo
```

**If using separate terminals:**
Press `Ctrl+C` in each terminal window.

## Next Steps

1. **Install Neovim plugin** - See README.md
2. **Customize .env** - Adjust settings
3. **Try code review** - Use `:ErgoJudgeThisCode` in Neovim
4. **Set up auto-start** - See NIXOS_SETUP.md for systemd services

## Your System is Ready!

The daemon is collecting activity, the orchestrator can route to AI models, and the UI provides a chat interface.

Start chatting at http://localhost:3000!
