# Quick Start: Setting Up Ergo Scanning Permissions

## Overview
Your Ergo permissions diagnostic shows that **most permissions are already working correctly!**

Here's what we found:

 **Working:**
- /proc filesystem access (can read process info)
- Git repository scanning
- Shell history access (bash & zsh)
- Data directories created and writable
- Socket communication ready
- Rust toolchain installed

️ **Needs attention:**
- X11 window monitoring (xdotool can't detect active window - may need DISPLAY set)
- Python packages not installed (fastapi, anthropic, etc.)

## Quick Fix Steps

### 1. Install Python Dependencies
```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator
pip install -r requirements.txt

# Or if using nix-shell:
nix-shell
```

### 2. Fix X11 Window Monitoring (if needed)
If you're running Ergo from a terminal, ensure DISPLAY is set:

```bash
# Check if DISPLAY is set
echo $DISPLAY

# If empty, set it (typically :0 or :1)
export DISPLAY=:0

# Test xdotool
xdotool getactivewindow
```

For permanent fix in NixOS, ensure your X11/Wayland session sets DISPLAY automatically.

### 3. Verify Permissions Are Working
Run the diagnostic again:
```bash
cd ~/Documents/Github/Ergo/ergo
./scripts/check-permissions.sh
```

## What Ergo Can Now Scan

Based on your `.env` configuration, Ergo has authority to:

###  Enabled by Default:
- **Process monitoring** - Active window titles and process names via xdotool
- **Git tracking** - Repository status, branches, commits in:
  - `~/Documents/`
  - `~/Documents/Github/`
- **Shell history** - Command patterns from:
  - `~/.bash_history` (500 commands tracked)
  - `~/.zsh_history` (14,233 commands tracked)
- **File metadata** - File paths, modification times (not contents) in allowed directories
- **Neovim context** - Via Unix socket when nvim plugin is active

###  Protected by Default:
- **No screenshot scanning** - `ENABLE_SCREENSHOTS=false`
- **No browser tracking** - `ENABLE_BROWSER_TRACKING=false`
- **No voice recording** - `ENABLE_VOICE=false`
- **Privacy filters active** - Ignores: passwords, tokens, secrets, .env files, bitwarden, keepass, vaults

### 🚫 Explicitly Forbidden:
These paths are blocked even if they're in allowed directories:
- `~/.ssh/` - SSH keys
- `~/.gnupg/` - GPG keys
- `~/.password-store/` - Pass password manager
- `~/Documents/secrets/` - Custom secrets directory

## How Permissions Are Enforced

Ergo uses a **layered permission system**:

```
1. System-level (Linux/NixOS)
   └─> File permissions, /proc access, X11 socket access

2. Application-level (.env configuration)
   └─> ALLOW_* flags, ALLOWED_SCAN_PATHS, FORBIDDEN_SCAN_PATHS

3. Privacy filters (.env configuration)
   └─> PRIVACY_IGNORE_PATTERNS, PRIVACY_IGNORE_APPS

4. Runtime kill switches (daemon API)
   └─> Pause, privacy mode, emergency stop
```

### Example Permission Flow:

**Scenario:** Ergo tries to scan `~/Documents/Github/myproject/.env`

1.  Linux filesystem: Can read (user owns file)
2.  Application: `~/Documents/Github` is in `ALLOWED_SCAN_PATHS`
3.  **BLOCKED** by privacy filter: filename contains `.env`
4. **Result:** File is ignored, never sent to daemon or LLM

## Testing Your Permissions

### Test 1: Window Monitoring
```bash
# Should return a window ID number
xdotool getactivewindow

# Should return the window title
xdotool getactivewindow getwindowname
```

### Test 2: Process Reading
```bash
# Should show your shell's name
cat /proc/$$/comm

# Should list visible processes
ls /proc/ | grep -E '^[0-9]+$' | wc -l
```

### Test 3: Git Scanning
```bash
cd ~/Documents/Github/Ergo
git status  # Ergo needs this to work
```

### Test 4: Shell History
```bash
# Should show your command history
tail -n 5 ~/.zsh_history
```

### Test 5: Directory Access
```bash
# Should be able to list files in allowed paths
ls ~/Documents/Github/

# Should be denied or show nothing for forbidden paths
ls ~/.ssh/ 2>&1
```

## Adjusting Permissions

### To Grant More Access:
Edit `~/Documents/Github/Ergo/ergo/.env`:

```bash
# Add more paths (comma-separated)
ALLOWED_SCAN_PATHS=~/Documents,~/Projects,~/code,~/work

# Enable browser tracking if needed
ENABLE_BROWSER_TRACKING=true

# Enable screenshots in manual mode
ENABLE_SCREENSHOTS=true
SCREENSHOT_MODE=manual
```

### To Restrict Access:
```bash
# Disable features
ENABLE_GIT_TRACKING=false
ENABLE_SHELL_TRACKING=false

# Add forbidden paths
FORBIDDEN_SCAN_PATHS=~/Documents/secrets,~/.ssh,~/private

# Add privacy patterns
PRIVACY_IGNORE_PATTERNS=password,token,secret,api_key,credential
```

### To Pause All Scanning:
```bash
# Stop the daemon
pkill -f ergo-daemon

# Or use the API (when implemented)
curl -X POST http://127.0.0.1:8765/daemon/pause
```

## Running Ergo with Permissions

### Start the Daemon:
```bash
cd ~/Documents/Github/Ergo/ergo

# Make sure you're in nix-shell if using Nix
nix-shell

# Run the daemon
cargo run --bin ergo-daemon
```

### Start the Orchestrator:
```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator

# Activate Python environment if needed
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run orchestrator
python3 src/main.py
```

### Check Logs:
```bash
# Watch daemon activity
tail -f ~/.local/share/ergo/ergo.log

# Check for permission errors
grep -i "permission\|denied\|forbidden" ~/.local/share/ergo/ergo.log
```

## Troubleshooting Permissions

### "Permission denied" errors

**Check file permissions:**
```bash
ls -la ~/.local/share/ergo/
```

**Fix ownership:**
```bash
sudo chown -R $USER:$USER ~/.local/share/ergo/
chmod -R u+rwX ~/.local/share/ergo/
```

### "xdotool: command not found"

**Check if xdotool is in PATH:**
```bash
which xdotool

# If not found, ensure you're in nix-shell
nix-shell
```

**Or add to system packages in NixOS:**
```nix
# /etc/nixos/configuration.nix
environment.systemPackages = with pkgs; [
  xdotool
  # ... other packages
];
```

### "Cannot read active window"

**Check X11 session:**
```bash
echo $DISPLAY  # Should show :0 or :1
echo $WAYLAND_DISPLAY  # May show wayland-0 if using Wayland

# Test manually
xdotool getactivewindow
```

**If using Wayland:** xdotool may not work. Consider:
- Using X11 session instead
- Or implementing Wayland support (requires different tools like `swaymsg`)

### "Database locked"

**Kill any running instances:**
```bash
pkill -f ergo
rm /tmp/ergo-daemon.sock
rm /tmp/ergo-nvim.sock
```

## Security Best Practices

1. **Review your `.env` file regularly** - Ensure no sensitive paths are in `ALLOWED_SCAN_PATHS`

2. **Keep privacy filters updated** - Add patterns for any new tools you use:
   ```bash
   PRIVACY_IGNORE_PATTERNS=password,token,secret,keepass,1password,lastpass
   ```

3. **Monitor the logs** - Check for unexpected file access:
   ```bash
   tail -f ~/.local/share/ergo/ergo.log | grep -E "scan|read|access"
   ```

4. **Use project-specific rules** - Create `CLAUDE.md` in sensitive projects:
   ```markdown
   # .env files must never be scanned
   # Only scan src/ and docs/ directories
   ```

5. **Backup your Ergo database** - It contains your work patterns:
   ```bash
   cp ~/.local/share/ergo/activity.db ~/.local/share/ergo/backups/activity-$(date +%F).db
   ```

## Next Steps

1.  Run `./scripts/check-permissions.sh` to verify everything
2.  Install Python dependencies: `pip install -r orchestrator/requirements.txt`
3.  Fix X11 access if needed: `export DISPLAY=:0`
4.  Start the daemon: `cargo run --bin ergo-daemon`
5.  Start the orchestrator: `python3 orchestrator/src/main.py`
6.  Test basic scanning: Check logs for window/process events

For detailed technical information, see `PERMISSIONS.md`.

For running the full system, see `RUNNING.md` or `QUICKSTART.md`.
