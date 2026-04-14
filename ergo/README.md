# Ergo

**Local AI assistant for NixOS with code context and memory**

---

## Quick Start

See **[docs/setup/QUICKSTART.md](docs/setup/QUICKSTART.md)** - Get running in 6 steps.

---

## What It Does

- Monitors your work context (files, git, shell, window activity)
- Remembers patterns and preferences across sessions
- Integrates with Neovim via non-blocking async UI
- Routes to Gemini (general chat) or Opus (code review)
- Passive monitoring with personality-based insights
- **Live code commentary** - Optional real-time remarks as you code
- Interactive chat interface in Neovim
- Runs locally with SQLite database

---

## Documentation

📚 **[Complete Documentation](docs/)** - All guides organized by category

### Quick Links

- **[Architecture](docs/ARCHITECTURE.md)** - Complete system architecture
- **[Quick Start](docs/setup/QUICKSTART.md)** - 6-step setup guide
- **[Documentation Map](docs/DOCUMENTATION_MAP.md)** - Visual guide to all docs

### By Task

| I want to... | Read this |
|--------------|-----------|
| Install Ergo | [START_HERE.md](docs/setup/START_HERE.md) → [INSTALL.md](docs/setup/INSTALL.md) |
| Set up on NixOS | [NIXOS_SETUP.md](docs/setup/NIXOS_SETUP.md) |
| Configure Neovim plugin | [NEOVIM_SETUP.md](docs/setup/NEOVIM_SETUP.md) |
| Understand permissions | [SCANNING_AUTHORITY_SUMMARY.md](docs/permissions/SCANNING_AUTHORITY_SUMMARY.md) |
| Run Ergo | [RUNNING.md](docs/setup/RUNNING.md) |
| Understand architecture | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| See what's planned | [ROADMAP.md](docs/reference/ROADMAP.md) |

---

## Status

### ✅ Working
- Orchestrator API (FastAPI on port 8765)
- Chat with Gemini 2.5 Flash
- Context building and memory layers
- Database schema (SQLite)
- Neovim plugin with async commands
- Floating window UI
- Passive monitoring system
- Floating terminal integration

### 🚧 In Progress
- Session summaries and daily reviews
- Personality layer enhancements
- Web UI refinement
- Rust daemon completion

### 📋 Future
- Git integration enhancements
- Embeddings and vector retrieval
- Voice mode (push-to-talk)
- Remote access via Tailscale
- Autonomous interventions

---

## Folder Structure

```
ergo/
├── src/                          # Rust daemon (system monitoring)
│   ├── main.rs                  # Main daemon entry point
│   ├── database.rs               # SQLite operations
│   ├── window_monitor.rs         # Window tracking
│   ├── privacy.rs                # Privacy filtering
│   └── ...
│
├── orchestrator/                 # Python orchestrator (AI routing)
│   ├── src/
│   │   ├── main.py              # FastAPI server (port 8765)
│   │   ├── config.py            # Configuration
│   │   ├── model_router.py      # AI model routing
│   │   ├── context_builder.py   # Memory context assembly
│   │   └── memory_manager.py    # Long-term memory
│   ├── requirements.txt
│   └── venv/
│
├── nvim-plugin/                  # Neovim integration
│   ├── lua/ergo/
│   │   ├── init.lua             # Main plugin
│   │   ├── ui.lua               # Floating windows
│   │   ├── async.lua            # Async API calls
│   │   ├── passive.lua          # Passive monitoring
│   │   ├── live_judge.lua       # Real-time code commentary
│   │   └── terminal.lua         # Floating terminal
│   └── plugin/ergo.vim
│
├── ui/                           # Web UI
│   ├── src/server.py            # FastAPI server (port 3000)
│   └── templates/
│
├── docs/                         # Documentation
│   ├── setup/                    # Installation guides
│   ├── permissions/              # Security docs
│   ├── reference/                # Technical reference
│   ├── ARCHITECTURE.md           # System architecture
│   └── DOCUMENTATION_MAP.md      # Doc guide
│
├── run-all.sh                    # Start all services in tmux
├── run-orchestrator.sh           # Start orchestrator only
├── run-ui.sh                     # Start UI only
│
├── flake.nix                     # Nix flake configuration
├── shell.nix                     # Development shell
├── Cargo.toml                    # Rust dependencies
└── .env.template                 # Configuration template
```

---

## Architecture

### Three-Layer System

1. **Daemon Layer (Rust)** - System monitoring
   - Window/process tracking (xdotool)
   - Git repository monitoring
   - Shell history integration
   - Event emission to database
   - Privacy filtering

2. **Orchestrator Layer (Python/FastAPI)** - AI routing & memory
   - FastAPI REST API (port 8765)
   - Model routing (Gemini for chat, Opus for code review)
   - Context assembly from memory layers
   - Long-term memory management
   - Personality system

3. **Interface Layer (Neovim + Web)** - User interaction
   - Non-blocking async commands
   - Floating window UI
   - Passive monitoring with insights
   - Interactive chat buffer
   - Real-time context reporting
   - Web UI (optional)

### Data Flow

```
[Neovim Buffer] → [Plugin] → [Orchestrator API] → [AI Model]
                       ↓              ↓
                [Context File]  [SQLite Database]
                                     ↑
                              [Rust Daemon]
                                     ↑
                         [System Events: Windows, Git, Shell]
```

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for complete architecture documentation.

---

## Running

### Start All Services

```bash
./run-all.sh  # Launches in tmux with 3 windows
```

### Individual Services

```bash
# Terminal 1: Daemon
cargo run --release

# Terminal 2: Orchestrator
./run-orchestrator.sh

# Terminal 3: UI (optional)
./run-ui.sh
```

**Service Ports:**
- Orchestrator API: `http://127.0.0.1:8765`
- Web UI: `http://localhost:3000`
- Daemon: Internal (SQLite only)

See **[docs/setup/RUNNING.md](docs/setup/RUNNING.md)** for detailed running instructions.

---

## Neovim Commands

```vim
:ErgoExplainContext          " Explain current context
:ErgoExplainContext {range}  " Explain selection
:ErgoSummarizeWork           " Get recent work summary
:ErgoJudgeCode               " Review visible code
:ErgoJudgeCode {range}       " Review selection
:ErgoCommitReview            " Review staged git changes
:ErgoChat                    " Open interactive chat
:ErgoInsight                 " Request contextual insight
:ErgoLiveJudgeToggle         " Toggle live commentary (opt-in)
:ErgoTerminal                " Toggle floating terminal (<leader>ef)
:ErgoToggle                  " Toggle monitoring on/off
:ErgoPassiveToggle           " Toggle passive monitoring
:ErgoPersonality {mode}      " Set personality (quiet/standard/verbose)
```

---

## Development Workflow

### Updating NixOS Plugin After Changes

After making changes to the nvim-plugin:

1. **Commit and push to GitHub:**
   ```bash
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
   nix-prefetch-url --unpack https://github.com/YourUsername/Ergo/archive/$(git rev-parse HEAD).tar.gz

   # Step 2: Convert to SRI format
   nix-hash --to-sri --type sha256 <hash>
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

### Plugin Location in NixOS Config

```nix
# In /etc/nixos/neovimConfig/plugins.nix
(pkgs.vimUtils.buildVimPlugin {
  pname = "ergo-nvim";
  version = "unstable-2026-03-25";
  src = pkgs.fetchFromGitHub {
    owner = "YourUsername";
    repo = "Ergo";
    rev = "COMMIT_HASH_HERE";  # Update this
    sha256 = "sha256-HASH_HERE";  # Update this
  };
  postUnpack = ''
    sourceRoot="$sourceRoot/ergo/nvim-plugin"
  '';
})
```

---

## Live Judge Feature

The Live Judge provides optional real-time code commentary as you write:

**Triggers:**
- Function definition completion
- Import statement addition
- Hovering on a line for 3+ seconds

**Examples:**
- *"url maker with 2 variables? ehhh are you sure about that, I'd use 3 imo..."*
- *"importing pandas again? another statistics thing? you're so predictable..."*

**Enable:** `:ErgoLiveJudgeToggle` (disabled by default to save API calls)

**Note:** Makes frequent API calls. Use sparingly during active coding.

---

## Configuration

**File:** `.env` (created from `.env.template`)

**Required:**
- `GOOGLE_AI_API_KEY` - For Gemini 2.5 Flash
- `ANTHROPIC_API_KEY` - For Claude Opus

**Storage:**
- Database: `~/.local/share/ergo/activity.db`
- Events: `~/.local/share/ergo/events/`
- Summaries: `~/.local/share/ergo/session_summaries/`

See **[docs/setup/QUICKSTART.md](docs/setup/QUICKSTART.md)** for configuration details.

---

## License

See LICENSE
