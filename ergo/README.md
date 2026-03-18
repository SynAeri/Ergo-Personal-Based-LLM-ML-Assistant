# Ergo

Local AI assistant for NixOS with code context and memory.

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) - Get running in 6 steps.

## What It Does

- Monitors your work context (files, git, shell)
- Remembers across sessions
- Integrates with Neovim with non-blocking async UI
- Routes to Gemini (chat) or Opus (code review)
- Passive monitoring with personality-based insights
- Interactive chat interface in Neovim
- Runs locally, SQLite database

## Status

**Working:**
- Orchestrator API (FastAPI)
- Chat with Gemini 2.5 Flash
- Context building and memory
- Database schema
- Neovim plugin foundation

**In Progress:**
- Non-blocking async commands
- Floating window UI
- Passive monitoring system
- Personality layer
- Rust daemon
- Web UI

## Folder Structure

```
ergo/
├── src/                          # Rust daemon (monitoring)
│   ├── main.rs                  # Main daemon entry
│   ├── database_v2.rs           # SQLite schema & operations
│   ├── event_emitter.rs         # Event emission system
│   ├── window_monitor.rs        # Active window tracking
│   ├── context.rs               # Context gathering
│   └── models.rs                # Data models
│
├── orchestrator/                 # Python orchestrator (AI routing)
│   ├── src/
│   │   ├── main.py              # FastAPI server
│   │   ├── config.py            # Environment config
│   │   ├── model_router.py      # AI model routing (Gemini/Opus)
│   │   ├── context_builder.py   # Memory context assembly
│   │   └── memory_manager.py    # Long-term memory
│   ├── init_db.py               # Database initialization
│   └── venv/                    # Python virtual environment
│
├── nvim-plugin/                  # Neovim integration
│   ├── lua/ergo/
│   │   ├── init.lua             # Main plugin code
│   │   ├── ui.lua               # Floating windows (planned)
│   │   ├── async.lua            # Async API calls (planned)
│   │   └── passive.lua          # Passive monitoring (planned)
│   └── plugin/ergo.vim          # Vim plugin loader
│
├── ui/                           # Web UI (future)
│   ├── src/server.py
│   └── templates/index.html
│
├── run-orchestrator.sh           # Startup script
├── QUICKSTART.md                 # Setup guide
├── BUILD_STATUS.md              # Build notes
└── ROADMAP.md                   # Feature roadmap
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get running in 6 steps
- [ROADMAP.md](ROADMAP.md) - Planned features
- [BUILD_STATUS.md](BUILD_STATUS.md) - Current build status
- [docs/journal/](docs/journal/) - Detailed documentation

## Development Workflow

### Updating NixOS Plugin After Changes

After making changes to the nvim-plugin, you need to update NixOS:

1. **Commit and push to GitHub:**
   ```bash
   cd ~/Documents/Github/Ergo/ergo
   git add .
   git commit -m "your message"
   git push origin main
   ```

2. **Get new commit hash:**
   ```bash
   git rev-parse HEAD
   ```

3. **Get correct sha256 for NixOS:**
   ```bash
   # Step 1: Get the base32 hash
   nix-prefetch-url --unpack https://github.com/SynAeri/Ergo-Personal-Based-LLM-ML-Assistant/archive/$(git rev-parse HEAD).tar.gz

   # Step 2: Convert to SRI format (required for modern Nix)
   # Replace <hash> with the output from step 1
   nix-hash --to-sri --type sha256 <hash>

   # Example:
   # nix-prefetch-url output: 198agan9kh3cylv57654wm75jz3r67ajj74l6h9x9h6hy4fyymf0
   # nix-hash --to-sri output: sha256-wFXvHfHQwNQTNJQcKdUxeXxZTuWkmFM29WzAmax6CqU=
   # Use the SRI format in plugins.nix
   ```

4. **Update `/etc/nixos/neovimConfig/plugins.nix`:**
   ```bash
   sudo nvim /etc/nixos/neovimConfig/plugins.nix
   # Update the rev and sha256 lines in the ergo-nvim section
   ```

5. **Rebuild NixOS:**
   ```bash
   sudo nixos-rebuild switch --flake /etc/nixos#nixos
   ```

### Quick Reference: Current Plugin Location

```nix
# In /etc/nixos/neovimConfig/plugins.nix
(pkgs.vimUtils.buildVimPlugin {
  pname = "ergo-nvim";
  version = "unstable-2026-03-18";
  src = pkgs.fetchFromGitHub {
    owner = "SynAeri";
    repo = "Ergo-Personal-Based-LLM-ML-Assistant";
    rev = "COMMIT_HASH_HERE";  # Update this
    sha256 = "sha256-HASH_HERE";  # Update this
  };
  postUnpack = ''
    sourceRoot="$sourceRoot/ergo/nvim-plugin"
  '';
})
```

## Running

```bash
cd /path/to/ergo
./run-orchestrator.sh
```

Then in Neovim: `:ErgoExplainContext`

## Architecture

### Three-Layer System

1. **Daemon Layer (Rust)** - System monitoring
   - Window/process tracking
   - Git repository monitoring
   - Shell history integration
   - Event emission to database

2. **Orchestrator Layer (Python/FastAPI)** - AI routing & memory
   - FastAPI REST API (port 8765)
   - Model routing (Gemini for chat, Opus for code review)
   - Context assembly from events
   - Long-term memory management
   - Personality system

3. **Interface Layer (Neovim)** - User interaction
   - Non-blocking async commands
   - Floating window UI
   - Passive monitoring with insights
   - Interactive chat buffer
   - Real-time context reporting

### Data Flow

```
[Neovim Buffer] → [Plugin] → [Orchestrator API] → [AI Model]
                       ↓              ↓
                [Context File]  [Database]
                                     ↑
                              [Rust Daemon]
                                     ↑
                         [System Events: Windows, Git, Shell]
```

## License

See LICENSE
