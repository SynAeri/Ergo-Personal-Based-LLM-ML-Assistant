# Ergo Quick Start Guide

Get Ergo running in 5 minutes.

## Prerequisites

- NixOS or Nix with flakes enabled
- API keys for Anthropic (Opus) and/or Google AI (Gemini)

## Step 1: Setup

```bash
cd /path/to/Ergo/ergo
./scripts/setup.sh
```

This creates data directories and a `.env` file from the template.

## Step 2: Configure API Keys

Edit `.env` and add your API keys:

```bash
nvim .env  # or your preferred editor
```

Minimum required:
```env
GOOGLE_AI_API_KEY=your_google_ai_key_here    # For general chat
ANTHROPIC_API_KEY=your_anthropic_key_here     # For code review
```

## Step 3: Enter Nix Environment

```bash
nix develop
```

This provides all dependencies (Rust, Python, libraries).

## Step 4: Build the Daemon

```bash
cargo build --release
```

## Step 5: Install Python Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
cd ..
```

## Step 6: Run Ergo

You need 3 terminal windows (or use tmux/screen):

### Terminal 1: Daemon
```bash
cargo run --release
```

You should see:
```
Ergo Observer starting...
Database: /home/you/.local/share/ergo/activity.db
Database initialized
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monitoring active window every 5 seconds...
📊 Run with 'stats' arg for statistics
Press Ctrl+C to stop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Terminal 2: Orchestrator
```bash
cd orchestrator
python src/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8765
```

### Terminal 3: UI Server
```bash
cd ui
python src/server.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:3000
```

## Step 7: Open the UI

Open your browser to:
```
http://localhost:3000
```

You should see the Ergo chat interface with activity panels.

## Step 8: Test It

Type in the chat:
```
What am I working on right now?
```

Ergo will use your recent activity context to respond.

## Step 9: Install Neovim Plugin (Optional)

If you use Neovim, add to your config:

```lua
-- lazy.nvim
{
  dir = "/path/to/Ergo/ergo/nvim-plugin",
  config = function()
    require('ergo').setup()
  end
}
```

Then try:
```vim
:ErgoExplainContext
```

## Verifying Everything Works

### Check Daemon
The daemon should be logging window changes in Terminal 1.

### Check Orchestrator Health
```bash
curl http://127.0.0.1:8765/health | jq
```

Should return:
```json
{
  "status": "healthy",
  "anthropic_configured": true,
  "gemini_configured": true,
  "database_type": "sqlite"
}
```

### Check Recent Context
```bash
curl http://127.0.0.1:8765/context/recent?minutes=10 | jq
```

Should return recent activity.

### Test Chat API
```bash
curl -X POST http://127.0.0.1:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "include_context": false}' | jq
```

Should return a response from Gemini.

## Common Issues

### "Database error"
The daemon couldn't create `~/.local/share/ergo/`. Run `./scripts/setup.sh` again.

### "Anthropic client not initialized"
Check your `ANTHROPIC_API_KEY` in `.env`. Make sure the orchestrator is reading the `.env` file (should be in the same directory).

### "Connection refused" in UI
Make sure the orchestrator is running on port 8765.

### Neovim plugin does nothing
The plugin writes to `~/.local/share/ergo/nvim_context.json`. Check if that file is being updated. Make sure the orchestrator is running first.

## What's Next?

- Read the [full README](../README.md) for detailed configuration
- Review [proj_ergo_arch.md](proj_ergo_arch.md) for architecture details
- Customize `.env` settings for your workflow
- Set up systemd services for auto-start (see below)

## Running as a Service (Optional)

Create `~/.config/systemd/user/ergo-daemon.service`:

```ini
[Unit]
Description=Ergo Activity Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/Ergo/ergo/target/release/ergo
Restart=on-failure
Environment="RUST_LOG=info"

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable ergo-daemon
systemctl --user start ergo-daemon
```

Create similar services for orchestrator and UI if desired.

## Testing Model Routing

### General Chat (Gemini)
Open UI and ask general questions. These route to Gemini.

### Code Review (Opus)
In Neovim, run `:ErgoJudgeThisCode` on some code. This routes to Opus for deep analysis.

## Privacy Check

1. Open Bitwarden or a password manager
2. Check Terminal 1 - you should see `[IGNORED] Privacy filter triggered`
3. This confirms privacy filters are working

## Next Steps

Now that Ergo is running:

1. **Use it naturally** - let it observe your work for a day
2. **Check activity stats** - run `cargo run --release -- stats`
3. **Ask context questions** - "What was I working on before lunch?"
4. **Get code reviews** - use `:ErgoJudgeThisCode` in Neovim
5. **Review commits** - use `:ErgoCommitReview` before committing

## Getting Help

- Check logs in Terminal windows
- Review `.env` configuration
- Read [Troubleshooting](README.md#troubleshooting) in main README
- Check `~/.local/share/ergo/ergo.log` for detailed logs

## Stopping Ergo

Press `Ctrl+C` in each terminal window, or:

```bash
# If running as systemd services
systemctl --user stop ergo-daemon
systemctl --user stop ergo-orchestrator
systemctl --user stop ergo-ui
```

Your data is preserved in `~/.local/share/ergo/`.

---

**You're now running Ergo!** The daemon is observing your activity, the orchestrator is ready to route model requests, and the UI provides a chat interface with full context awareness.
