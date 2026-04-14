# NixOS Setup Guide

Ergo on NixOS using nix-shell for dependencies.

## Quick Start

```bash
# 1. Enter the Nix environment
nix-shell

# 2. Build the daemon (if not already built)
cargo build --release

# 3. Run all services
./run-all.sh
```

That's it! The UI will be at http://localhost:3000

## What's Included

The `shell.nix` provides:
-  Rust toolchain (cargo, rustc)
-  Python 3.11 with all packages pre-installed:
  - FastAPI, Uvicorn
  - Anthropic API client
  - Google Generative AI client
  - OpenAI client
  - Pydantic, python-dotenv
  - Jinja2, aiofiles
-  System libraries (X11, SQLite)
-  Utilities (tmux, jq, curl)

## Step-by-Step

### 1. Configure API Keys

Edit `.env` (already done):
```bash
cat .env | grep API_KEY
```

Should show your Anthropic and Google AI keys.

### 2. Enter Nix Shell

```bash
nix-shell
```

You'll see:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ergo Development Environment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Available:
  [X] Rust toolchain
  [X] Python with FastAPI, Anthropic, Google AI
  [X] All system dependencies
...
```

### 3. Build Daemon (if needed)

```bash
cargo build --release
```

This compiles to `target/release/ergo`.

### 4. Run Services

**Option A: All-in-one (tmux)**
```bash
./run-all.sh
```

This starts:
- Window 0: Daemon
- Window 1: Orchestrator (port 8765)
- Window 2: UI (port 3000)

**Option B: Separate terminals**

Terminal 1:
```bash
nix-shell
./target/release/ergo
```

Terminal 2:
```bash
nix-shell
./run-orchestrator.sh
```

Terminal 3:
```bash
nix-shell
./run-ui.sh
```

### 5. Access UI

Open browser: http://localhost:3000

## Verification

### Check Daemon
```bash
./target/release/ergo stats
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

### Test Chat
```bash
curl -X POST http://127.0.0.1:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "include_context": false}' | jq .response
```

## Permanent Installation (NixOS Configuration)

### Option 1: User Environment

Add to `~/.config/nixpkgs/home.nix`:
```nix
{ pkgs, ... }:

{
  home.packages = with pkgs; [
    (import /path/to/ergo/shell.nix { inherit pkgs; })
  ];
}
```

### Option 2: System Configuration

Add to `/etc/nixos/configuration.nix`:
```nix
{ config, pkgs, ... }:

{
  systemd.user.services.ergo-daemon = {
    description = "Ergo Activity Daemon";
    after = [ "graphical-session.target" ];
    wantedBy = [ "default.target" ];

    serviceConfig = {
      Type = "simple";
      ExecStart = "/path/to/ergo/target/release/ergo";
      Restart = "on-failure";
    };
  };

  systemd.user.services.ergo-orchestrator = {
    description = "Ergo Orchestrator";
    after = [ "network.target" ];
    wantedBy = [ "default.target" ];

    serviceConfig = {
      Type = "simple";
      WorkingDirectory = "/path/to/ergo";
      ExecStart = "/path/to/ergo/run-orchestrator.sh";
      Restart = "on-failure";
    };

    path = with pkgs; [
      (python311.withPackages (ps: with ps; [
        fastapi uvicorn anthropic google-generativeai
      ]))
    ];
  };

  systemd.user.services.ergo-ui = {
    description = "Ergo UI Server";
    after = [ "network.target" "ergo-orchestrator.service" ];
    wantedBy = [ "default.target" ];

    serviceConfig = {
      Type = "simple";
      WorkingDirectory = "/path/to/ergo";
      ExecStart = "/path/to/ergo/run-ui.sh";
      Restart = "on-failure";
    };

    path = with pkgs; [
      (python311.withPackages (ps: with ps; [
        fastapi uvicorn jinja2
      ]))
    ];
  };
}
```

Then:
```bash
sudo nixos-rebuild switch
systemctl --user enable ergo-daemon ergo-orchestrator ergo-ui
systemctl --user start ergo-daemon ergo-orchestrator ergo-ui
```

## Troubleshooting

### "uvicorn not found"

Make sure you're in nix-shell:
```bash
nix-shell
which uvicorn
```

Should show a path like `/nix/store/.../bin/uvicorn`.

### "anthropic module not found"

```bash
nix-shell
python -c "import anthropic; print('OK')"
```

Should print "OK".

### Python version mismatch

The shell.nix uses Python 3.11. If you need a different version:

Edit `shell.nix`:
```nix
pythonEnv = pkgs.python312.withPackages (ps: with ps; [
  # ...
]);
```

### Dependencies not available

If a Python package isn't in nixpkgs, add it to shell.nix or use a virtual environment:

```bash
nix-shell
python -m venv venv
source venv/bin/activate
pip install missing-package
```

## Development

### Hot Reload

In nix-shell:

**Daemon:**
```bash
cargo watch -x run
```

**Orchestrator:**
```bash
./run-orchestrator.sh  # Already has --reload
```

**UI:**
```bash
./run-ui.sh
```

### Testing

```bash
nix-shell
cargo test
```

### Building for Production

```bash
nix-shell
cargo build --release --locked
```

## Why nix-shell?

NixOS doesn't use global pip. Instead:
- `shell.nix` provides a reproducible environment
- All dependencies are declaratively specified
- No conflicts with system packages
- Easy to share with others

## Alternative: nix-shell without entering

Run commands directly:
```bash
nix-shell --run "cargo build --release"
nix-shell --run "./run-all.sh"
```

## Flake Support (Future)

The `flake.nix` is ready but needs git tracking:
```bash
git add flake.nix
git commit -m "Add flake"
nix develop  # Instead of nix-shell
```

Flakes provide better reproducibility and caching.

## Summary

On NixOS:
1. `nix-shell` - Get environment
2. `./run-all.sh` - Start everything
3. http://localhost:3000 - Use Ergo

Everything is declarative and reproducible!
