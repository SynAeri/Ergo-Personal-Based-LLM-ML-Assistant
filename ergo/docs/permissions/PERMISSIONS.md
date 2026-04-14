# Ergo System Permissions Configuration
# This file documents the system-level permissions Ergo needs and how to grant them

## Overview
Ergo requires various system-level permissions to scan and monitor your workstation activity.
This document explains what permissions are needed and how to grant them safely on NixOS.

## Required System Access

### 1. X11 Window Information (via xdotool)
**What it does:** Monitors active window titles and process names
**Required for:** Activity tracking, context switching detection, focus monitoring

**NixOS Configuration:**
Ensure xdotool is available in your shell environment or system packages:
```nix
# In your shell.nix or system configuration
buildInputs = [
  xdotool
  # ... other packages
];
```

**Permission check:**
```bash
xdotool --version  # Should return version info
xdotool getactivewindow  # Should return window ID
```

### 2. Process Information (/proc filesystem)
**What it does:** Reads process names, command lines, and metadata
**Required for:** Process identification, command tracking, shell history

**Automatic on Linux:** No special configuration needed - /proc is readable by default

**Permission check:**
```bash
ls -la /proc/self/comm  # Should show readable file
cat /proc/self/comm     # Should show current process name
```

### 3. Git Repository Access
**What it does:** Reads git status, branch info, recent commits
**Required for:** Project context, commit pattern tracking, repository awareness

**Configuration in .env:**
```bash
ENABLE_GIT_TRACKING=true
```

**Permission requirements:**
- Read access to .git directories in monitored projects
- Ability to run `git` commands in working directories

### 4. Shell History Access
**What it does:** Reads command history for pattern detection
**Required for:** Command recall, workflow pattern identification

**Configuration in .env:**
```bash
ENABLE_SHELL_TRACKING=true
```

**Files accessed:**
- `~/.bash_history`
- `~/.zsh_history`
- `~/.local/share/fish/fish_history`

**Permission check:**
```bash
ls -la ~/.bash_history  # Should be readable by user
```

### 5. Browser Information (Optional)
**What it does:** Reads browser tab titles and URLs (if enabled)
**Required for:** Web context tracking, research pattern detection

**Configuration in .env:**
```bash
ENABLE_BROWSER_TRACKING=false  # Disabled by default for privacy
```

**When enabled, may need access to:**
- Firefox: `~/.mozilla/firefox/*/sessionstore.jsonlz4`
- Chrome: `~/.config/google-chrome/Default/History`

### 6. Neovim Integration (via Unix Socket)
**What it does:** Receives editor context from Neovim plugin
**Required for:** Code context, diagnostics, file tracking

**Configuration in .env:**
```bash
ENABLE_NVIM_PLUGIN=true
NVIM_SOCKET_PATH=/tmp/ergo-nvim.sock
```

**Permission requirements:**
- Ability to create/bind Unix sockets in /tmp
- Socket permissions should be 0600 (user-only)

## Privacy Controls

### Privacy Filters
Configure patterns to ignore in `.env`:
```bash
# Ignore windows/apps containing these terms
PRIVACY_IGNORE_PATTERNS=password,token,secret,.env,bitwarden,keepass,vault,credentials

# Ignore specific applications completely
PRIVACY_IGNORE_APPS=bitwarden,keepassxc

# Ignore specific website domains
PRIVACY_IGNORE_DOMAINS=bank.com,healthcare.example
```

### Kill Switches
The daemon respects these immediate privacy controls:

1. **Pause Collection:** Stop all monitoring temporarily
   ```bash
   # Future API endpoint
   curl -X POST http://127.0.0.1:8765/daemon/pause
   ```

2. **Privacy Mode:** Continue running but don't store events
   ```bash
   # Set in .env
   PRIVACY_MODE=true
   ```

3. **Kill Daemon:** Emergency stop
   ```bash
   pkill -f ergo-daemon
   ```

## NixOS-Specific Configuration

### System-Level Permissions (if running as system service)
If you want to run Ergo as a systemd service, you'll need additional NixOS configuration:

```nix
# /etc/nixos/configuration.nix or a module
systemd.user.services.ergo-daemon = {
  description = "Ergo Activity Monitoring Daemon";
  wantedBy = [ "default.target" ];

  serviceConfig = {
    ExecStart = "${pkgs.ergo}/bin/ergo-daemon";
    Restart = "on-failure";

    # Filesystem access
    ReadOnlyPaths = [ "/proc" ];
    ReadWritePaths = [ "%h/.local/share/ergo" ];

    # Privacy: No network access needed for local-only mode
    PrivateNetwork = false;  # Set to true for complete isolation

    # Process restrictions
    NoNewPrivileges = true;
    PrivateTmp = false;  # Need /tmp for sockets
  };

  environment = {
    ERGO_CONFIG = "%h/.config/ergo/.env";
  };
};
```

### File Descriptor Limits
Ensure sufficient file descriptors for monitoring:
```nix
# In your user configuration
security.pam.loginLimits = [{
  domain = "*";
  type = "soft";
  item = "nofile";
  value = "4096";
}];
```

## Testing Permissions

Run this diagnostic script to check all permissions:

```bash
#!/usr/bin/env bash
# ergo-permissions-check.sh

echo "=== Ergo Permissions Diagnostic ==="
echo ""

# Check xdotool
echo "[1] Checking xdotool..."
if command -v xdotool &> /dev/null; then
  echo "    [X] xdotool found: $(xdotool --version 2>&1 | head -1)"
  if xdotool getactivewindow &> /dev/null; then
    echo "    [X] Can read active window"
  else
    echo "    ✗ Cannot read active window (not in X11 session?)"
  fi
else
  echo "    ✗ xdotool not found - install via nix-shell"
fi

# Check /proc access
echo ""
echo "[2] Checking /proc filesystem..."
if [ -r /proc/self/comm ]; then
  echo "    [X] Can read /proc/self/comm: $(cat /proc/self/comm)"
else
  echo "    ✗ Cannot read /proc filesystem"
fi

# Check git
echo ""
echo "[3] Checking git access..."
if command -v git &> /dev/null; then
  echo "    [X] git found: $(git --version)"
else
  echo "    ✗ git not found"
fi

# Check shell history
echo ""
echo "[4] Checking shell history..."
for hist in ~/.bash_history ~/.zsh_history; do
  if [ -f "$hist" ]; then
    echo "    [X] Found $hist ($(wc -l < "$hist") lines)"
  fi
done

# Check Ergo directories
echo ""
echo "[5] Checking Ergo data directories..."
ERGO_DIR="${HOME}/.local/share/ergo"
if [ -d "$ERGO_DIR" ]; then
  echo "    [X] Data directory exists: $ERGO_DIR"
  echo "    [X] Writable: $([ -w "$ERGO_DIR" ] && echo "yes" || echo "no")"
else
  echo "    ✗ Data directory missing: $ERGO_DIR"
  echo "      Run: mkdir -p $ERGO_DIR"
fi

# Check socket path
echo ""
echo "[6] Checking socket permissions..."
SOCK_DIR="/tmp"
if [ -w "$SOCK_DIR" ]; then
  echo "    [X] Can write to $SOCK_DIR for Unix sockets"
else
  echo "    ✗ Cannot write to $SOCK_DIR"
fi

echo ""
echo "=== Diagnostic Complete ==="
```

Save this as `ergo/scripts/check-permissions.sh` and run it:
```bash
chmod +x ergo/scripts/check-permissions.sh
./ergo/scripts/check-permissions.sh
```

## Security Recommendations

1. **Run as user, not root** - Ergo should never need root privileges
2. **Use privacy filters liberally** - Better to over-filter than leak sensitive data
3. **Review logs regularly** - Check `~/.local/share/ergo/ergo.log` for unexpected access
4. **Enable only what you need** - Disable browser/screenshot tracking if not used
5. **Backup your data** - Ergo's database contains valuable context
6. **Use secure remote access** - Only expose via Tailscale, not public internet

## Troubleshooting

### "xdotool not found"
**Solution:** Activate the nix-shell or add xdotool to your system packages

### "Permission denied" reading /proc
**Solution:** Should never happen on Linux - check if running in container/sandbox

### "Cannot bind to socket"
**Solution:** Check if socket already exists: `rm /tmp/ergo-daemon.sock`

### "Database locked"
**Solution:** Another Ergo instance may be running: `pkill -f ergo`

## Further Configuration

See the main `.env.template` for all available configuration options.

For project-specific permissions, create a `CLAUDE.md` in your project root:
```markdown
# Project: MyProject
# Ergo Scanning Permissions

Allowed:
- Git tracking: yes
- Shell commands: yes
- File monitoring: src/ only

Forbidden:
- .env files
- vendor/ directory
- Any file matching *secret*
```
