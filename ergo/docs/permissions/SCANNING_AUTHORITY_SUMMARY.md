# Ergo Scanning Authority - Summary

## Problem
Ergo needs explicit authority to scan and identify various system resources that it currently cannot access.

## Solution Implemented

We've created a comprehensive permission system with three configuration layers:

### 1. **Environment Configuration** (`.env` file)

Added explicit permission flags in your `.env` file:

```bash
# System scanning permissions
ALLOW_PROC_SCAN=true              # Read process info from /proc
ALLOW_WINDOW_MONITORING=true      # Track active windows via xdotool
ALLOW_SHELL_HISTORY_READ=true     # Access shell command history
ALLOW_GIT_SCAN=true               # Scan git repositories
ALLOW_FILE_METADATA_SCAN=true     # Read file metadata (not contents)

# Allowed/forbidden paths
ALLOWED_SCAN_PATHS=~/Documents,~/Projects,~/code,~/Documents/Github
FORBIDDEN_SCAN_PATHS=~/Documents/secrets,~/.ssh,~/.gnupg,~/.password-store

# Process monitoring
MONITOR_PROCESSES=nvim,code,firefox,chrome,terminal,kitty,alacritty
MAX_SCAN_DEPTH=5
```

### 2. **System-Level Permissions** (Already Working)

Your diagnostic check shows these are functional:
-  `/proc` filesystem access (381 processes visible)
-  Git access (git version 2.51.2)
-  Shell history (bash: 500 lines, zsh: 14,233 lines)
-  Ergo data directories created and writable
-  Socket communication ready

### 3. **Neovim Integration** (Setup Guide Created)

For your NixOS Neovim config at `/etc/nixos/neovimConfig/`:
- Plugin installation via `plugins.nix`
- Lua configuration in `config/lua/nvim-ergo.lua`
- Keybindings for explicit commands
- Automatic context reporting every 5 seconds

## What Ergo Can Now Scan

### System Level:
- **Active window titles** - Via xdotool (needs X11 session)
- **Process names** - Via /proc filesystem (working)
- **Command history** - ~/.bash_history and ~/.zsh_history (working)
- **Git repositories** - Status, branches, commits in allowed paths (working)
- **File metadata** - Paths, modification times in allowed directories (working)

### Neovim Integration:
- **Current file** - Path and language
- **Cursor position** - Line and column
- **Diagnostics** - LSP error/warning counts
- **Visual selections** - When you select code
- **Git status** - From within editor

### Privacy Protected:
-  Files matching: password, token, secret, .env, bitwarden, keepass, vault, credentials
-  Directories: ~/.ssh, ~/.gnupg, ~/.password-store, ~/Documents/secrets
-  Screenshots (disabled by default)
-  Browser tracking (disabled by default)
-  Voice recording (disabled by default)

## Files Created

1. **`PERMISSIONS.md`** - Comprehensive permission documentation
2. **`SETUP_PERMISSIONS.md`** - Quick setup and verification guide
3. **`NEOVIM_SETUP.md`** - Neovim plugin integration for NixOS
4. **`scripts/check-permissions.sh`** - Diagnostic tool (executable)
5. **`.env`** - Updated with permission flags
6. **`.env.template`** - Updated template for future reference

## Current Status

###  Working:
- Process monitoring (/proc)
- Git repository scanning
- Shell history access
- Data directory permissions
- Socket communication paths
- Rust toolchain ready

### ️ Needs Attention:
1. **X11 window monitoring** - xdotool can't read active window
   - **Cause:** Likely not in X11 session or DISPLAY not set
   - **Fix:** Run `export DISPLAY=:0` or ensure running in X11 session

2. **Python dependencies** - Not installed yet
   - **Fix:** `pip install -r orchestrator/requirements.txt`

3. **Neovim plugin** - Not installed yet
   - **Fix:** Follow `NEOVIM_SETUP.md` to add to your NixOS config

## Quick Start

### 1. Run Diagnostic
```bash
cd ~/Documents/Github/Ergo/ergo
./scripts/check-permissions.sh
```

### 2. Install Python Dependencies
```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator
pip install -r requirements.txt
```

### 3. Fix X11 Access (if needed)
```bash
export DISPLAY=:0
xdotool getactivewindow  # Should return a number
```

### 4. Install Neovim Plugin
Follow the guide in `NEOVIM_SETUP.md` to add Ergo plugin to `/etc/nixos/neovimConfig/`

### 5. Start Ergo Services
```bash
# Terminal 1: Start daemon
cargo run --bin ergo-daemon

# Terminal 2: Start orchestrator
cd orchestrator
python3 src/main.py

# Terminal 3: Watch logs
tail -f ~/.local/share/ergo/ergo.log
```

## Testing Permissions

### Test System Scanning:
```bash
# Process info
cat /proc/self/comm

# Window info (if X11 working)
xdotool getactivewindow getwindowname

# Git scanning
cd ~/Documents/Github/Ergo
git status

# Shell history
tail ~/.zsh_history
```

### Test API Access:
```bash
# Health check
curl http://127.0.0.1:8765/health

# Recent context
curl http://127.0.0.1:8765/context/recent?minutes=30

# Chat (with context)
curl -X POST http://127.0.0.1:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What am I working on?", "include_context": true}'
```

### Test Neovim Integration:
```vim
# In Neovim
:ErgoToggle
:ErgoExplainContext
:ErgoSummarizeWork

# Check context file
:!cat ~/.local/share/ergo/nvim_context.json
```

## Adjusting Permissions

### Grant More Access:
Edit `~/Documents/Github/Ergo/ergo/.env`:
```bash
# Add more paths
ALLOWED_SCAN_PATHS=~/Documents,~/Projects,~/work,~/code

# Enable more features
ENABLE_BROWSER_TRACKING=true
ENABLE_SCREENSHOTS=true
SCREENSHOT_MODE=manual
```

### Restrict Access:
```bash
# Disable features
ALLOW_WINDOW_MONITORING=false
ENABLE_SHELL_TRACKING=false

# Add forbidden paths
FORBIDDEN_SCAN_PATHS=~/Documents/secrets,~/.ssh,~/private,~/work/confidential
```

### Emergency Stop:
```bash
# Kill all Ergo processes
pkill -f ergo

# Remove sockets
rm /tmp/ergo-daemon.sock /tmp/ergo-nvim.sock

# Or set in .env
PRIVACY_MODE=true  # Continue running but don't store events
```

## Security Recommendations

1. **Review logs regularly**
   ```bash
   tail -f ~/.local/share/ergo/ergo.log | grep -E "scan|access|read"
   ```

2. **Audit allowed paths**
   - Only add paths you actively work in
   - Keep forbidden paths up to date

3. **Use privacy filters**
   - Add patterns for any password managers
   - Include API key filenames

4. **Monitor database growth**
   ```bash
   du -h ~/.local/share/ergo/activity.db
   ```

5. **Backup regularly**
   ```bash
   cp ~/.local/share/ergo/activity.db \
      ~/.local/share/ergo/backups/activity-$(date +%F).db
   ```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Permission Layers                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Linux/NixOS System Permissions                         │
│     ├─ File permissions (chmod/chown)                      │
│     ├─ /proc access (always available)                     │
│     └─ X11/socket access (DISPLAY, /tmp)                   │
│                                                             │
│  2. Application Configuration (.env)                       │
│     ├─ ALLOW_* flags (explicit grants)                     │
│     ├─ ALLOWED_SCAN_PATHS (path allowlist)                 │
│     └─ FORBIDDEN_SCAN_PATHS (path blocklist)               │
│                                                             │
│  3. Privacy Filters (.env)                                 │
│     ├─ PRIVACY_IGNORE_PATTERNS (content filters)           │
│     ├─ PRIVACY_IGNORE_APPS (application filters)           │
│     └─ PRIVACY_IGNORE_DOMAINS (website filters)            │
│                                                             │
│  4. Runtime Controls (daemon API)                          │
│     ├─ Pause collection                                    │
│     ├─ Privacy mode                                        │
│     └─ Emergency kill switch                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Data Flow:
1. System event occurs (window change, git commit, etc.)
2. Daemon checks: System permissions → Allow
3. Daemon checks: Allowed paths → Allow
4. Daemon checks: Forbidden paths → Block if match
5. Daemon checks: Privacy patterns → Block if match
6. Event stored in database
7. Orchestrator retrieves context for LLM queries
```

## Documentation Index

- **`PERMISSIONS.md`** - Detailed technical documentation of all permissions
- **`SETUP_PERMISSIONS.md`** - Quick start guide with diagnostic checks
- **`NEOVIM_SETUP.md`** - Neovim plugin installation for NixOS
- **`scripts/check-permissions.sh`** - Automated diagnostic tool
- **`.env`** - Your active configuration
- **`.env.template`** - Template with all options documented

## Next Steps

1.  Permissions configured in `.env`
2. ️ Install Python dependencies
3. ️ Fix X11 window monitoring (if needed)
4. ️ Install Neovim plugin
5. ️ Start Ergo services (daemon + orchestrator)
6. ️ Test with diagnostic script
7. ️ Verify events are being captured

## Support

If you encounter permission issues:

1. Run diagnostic: `./scripts/check-permissions.sh`
2. Check logs: `tail -f ~/.local/share/ergo/ergo.log`
3. Review relevant documentation above
4. Check git status for any uncommitted permission changes

---

**Created:** 2026-03-18
**Your System:** NixOS with declarative Neovim config
**Status:** Permissions configured, awaiting installation of Python deps and Neovim plugin
