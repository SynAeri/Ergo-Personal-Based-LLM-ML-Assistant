# Installation Guide

## Current Build Status

The daemon builds successfully with minimal dependencies. The full Nix environment setup is ready but optional for the daemon.

## Quick Install (Just the Daemon)

If you only want to run the activity monitoring daemon:

```bash
cd ergo
cargo build --release
./target/release/ergo
```

That's it! The daemon will:
- Monitor active windows
- Store events in SQLite (`~/.local/share/ergo/activity.db`)
- Apply privacy filters

View stats:
```bash
./target/release/ergo stats
```

## Full Installation (All Components)

For the complete system with orchestrator, UI, and Neovim plugin:

### 1. Prerequisites

You'll need API keys:
- **Anthropic** (for Claude Opus) - https://console.anthropic.com/
- **Google AI** (for Gemini) - https://aistudio.google.com/app/apikey

### 2. Setup

```bash
cd ergo
./scripts/setup.sh
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
```

### 3. Build Daemon

```bash
cargo build --release
```

### 4. Install Python Dependencies

```bash
cd orchestrator
pip install -r requirements.txt
```

Or use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run Services

You need 3 terminals:

**Terminal 1 - Daemon:**
```bash
./target/release/ergo
```

**Terminal 2 - Orchestrator:**
```bash
cd orchestrator
python src/main.py
```

**Terminal 3 - UI:**
```bash
cd ui
python src/server.py
```

### 6. Access UI

Open browser to: http://localhost:3000

## NixOS Installation (Recommended)

If you're on NixOS or have Nix with flakes:

```bash
# Add flake to git first
git add flake.nix
git commit -m "Add flake"

# Enter development environment
nix develop

# Everything is now available
cargo build --release
cd orchestrator && python src/main.py
```

The flake provides:
- Rust toolchain
- Python 3.11 with all dependencies
- X11 libraries
- All system dependencies

## Neovim Plugin Installation

### With lazy.nvim

```lua
{
  dir = "/path/to/ergo/nvim-plugin",
  config = function()
    require('ergo').setup({
      enabled = true,
      auto_report_interval = 5000,
    })
  end
}
```

### With packer.nvim

```lua
use {
  '/path/to/ergo/nvim-plugin',
  config = function()
    require('ergo').setup()
  end
}
```

### Manual (Neovim package)

```bash
mkdir -p ~/.local/share/nvim/site/pack/ergo/start
ln -s /path/to/ergo/nvim-plugin ~/.local/share/nvim/site/pack/ergo/start/ergo
```

## Verification

### Check Daemon
```bash
./target/release/ergo stats
```

Should show:
```
Ergo Statistics - Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total tracked: Xh Ym
Context switches: N
Most used: your-app
```

### Check Orchestrator
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

### Check UI
Open http://localhost:3000 - you should see the chat interface.

### Check Neovim Plugin

In Neovim:
```vim
:ErgoExplainContext
```

## Troubleshooting

### Cargo build fails with OpenSSL errors

The simplified build removes OpenSSL dependencies. If you see OpenSSL errors:

1. Make sure you're using the latest Cargo.toml
2. Run `cargo clean && cargo build --release`
3. If still failing, use `nix develop` for the full environment

### Python dependencies fail to install

Use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Orchestrator won't start

Check your `.env` file exists and has API keys:
```bash
cat .env | grep API_KEY
```

### Database errors

Ensure directories exist:
```bash
mkdir -p ~/.local/share/ergo
```

### Neovim commands don't work

1. Make sure orchestrator is running first
2. Check `~/.local/share/ergo/nvim_context.json` is being created
3. Verify curl is installed: `which curl`

## Running as a Service

Create `~/.config/systemd/user/ergo-daemon.service`:

```ini
[Unit]
Description=Ergo Activity Daemon
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=/path/to/ergo
ExecStart=/path/to/ergo/target/release/ergo
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable:
```bash
systemctl --user enable ergo-daemon
systemctl --user start ergo-daemon
```

View logs:
```bash
journalctl --user -u ergo-daemon -f
```

Create similar services for orchestrator and UI if desired.

## Next Steps

- See [QUICKSTART.md](QUICKSTART.md) for a guided walkthrough
- Read [README.md](README.md) for full documentation
- Check [BUILD_STATUS.md](BUILD_STATUS.md) for what's implemented
- Review [ROADMAP.md](ROADMAP.md) for future plans

## Getting Help

1. Check the logs in each terminal window
2. Verify `.env` configuration
3. Read the troubleshooting sections
4. Check GitHub issues

The daemon alone is useful for activity tracking. The full system provides AI-powered context awareness and code assistance.
