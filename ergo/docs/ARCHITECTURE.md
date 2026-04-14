# Ergo System Architecture

**Last Updated:** 2026-03-25
**System:** NixOS
**Version:** v2.0+

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Technology Stack](#technology-stack)
6. [Data Flow](#data-flow)
7. [Memory Architecture](#memory-architecture)
8. [Configuration](#configuration)
9. [Design Principles](#design-principles)
10. [NixOS Integration](#nixos-integration)

---

## Executive Summary

**Ergo** is a local-first AI assistant for NixOS developers that monitors work context, builds persistent memory across sessions, and provides intelligent assistance through multiple interfaces.

### Key Principles

- **Local-first**: All core functionality works without cloud services
- **Privacy-conscious**: Built-in privacy filters and kill switches
- **Developer-focused**: Deep integration with code editors and dev tools
- **Memory-based**: Understands patterns, recurring issues, and user preferences
- **Model-agnostic**: Routes to different AI models based on task type

### Core Value Proposition

Ergo is not just another AI chatbot. It's a **work operator with memory and intervention** that:
- Remembers your coding patterns and preferences
- Sees your working context (files, git, shell)
- Intervenes at the right time with contextual insights
- Routes complex tasks to appropriate AI models

---

## System Overview

Ergo is a **modular three-layer system** separated into distinct services:

```
┌─────────────────────────────────────────────────────────────┐
│ INTERFACE LAYER                                             │
│ • Neovim Plugin (Lua)                                       │
│ • Web UI (FastAPI)                                          │
│ • Terminal Chat                                             │
└────────────┬──────────────────────────────────────┬──────────┘
             │                                      │
             ▼                                      ▼
┌────────────────────────────────┐  ┌──────────────────────────────┐
│ ORCHESTRATOR (Python/FastAPI)  │  │ DAEMON (Rust)                │
│ Port: 8765                     │  │ System Monitoring            │
│ • Model Routing               │  │ • Window Tracking            │
│ • Context Assembly            │◄─┤ • Event Emission             │
│ • Memory Management           │  │ • Privacy Filtering          │
│ • Intervention Logic          │  │                              │
└─────────────┬──────────────────┘  └──────────────────────────────┘
              │                              │
              │                              ▼
              │                  ┌──────────────────────────┐
              │                  │ SQLite Database          │
              │                  │ ~/.local/share/ergo/    │
              │                  │ • activity_log           │
              │                  │ • patterns               │
              └──────────────────► • events                 │
                                 │ • memories               │
                                 │ • summaries              │
                                 └──────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│ AI MODEL SERVICES                                           │
│ • Gemini 2.5 Flash (General Chat)                           │
│ • Claude Opus (Code Review/Deep Reasoning)                  │
│ • Local Models (Optional)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Layers

| Layer | Purpose | Technology | Notes |
|-------|---------|------------|-------|
| **Capture** | Collect system, editor, shell, repo signals | Rust | Long-running daemon |
| **Index** | Normalize events and store memory | SQLite/Postgres | Structured first |
| **Reason** | Assemble context, route models, detect patterns | Python | Model-agnostic |
| **Act** | Notifications, interventions, tool execution | Rust + Python | Policy boundaries |
| **Interact** | Chat UI, voice (optional), web interface | FastAPI/Lua | Persona layer |

---

## Directory Structure

```
ergo/
├── src/                          # Rust daemon (system monitoring)
│   ├── main.rs                  # Main daemon entry point
│   ├── database.rs               # SQLite operations
│   ├── window_monitor.rs         # X11/Wayland window tracking
│   ├── privacy.rs                # Privacy filtering
│   ├── context.rs                # Context gathering
│   ├── event_emitter.rs          # Event emission system
│   └── models.rs                 # Data models
│
├── orchestrator/                 # Python FastAPI service
│   ├── src/
│   │   ├── main.py               # FastAPI server (port 8765)
│   │   ├── config.py             # Configuration management
│   │   ├── model_router.py       # AI model routing logic
│   │   ├── context_builder.py    # Memory context assembly
│   │   └── memory_manager.py     # Long-term memory management
│   ├── requirements.txt          # Python dependencies
│   └── venv/                     # Virtual environment
│
├── nvim-plugin/                  # Neovim integration (Lua)
│   ├── lua/ergo/
│   │   ├── init.lua              # Main plugin entry
│   │   ├── ui.lua                # Floating window UI
│   │   ├── async.lua             # Non-blocking async calls
│   │   ├── passive.lua           # Passive monitoring
│   │   ├── live_judge.lua        # Real-time code commentary
│   │   └── terminal.lua          # Floating terminal
│   └── plugin/ergo.vim           # Vim plugin loader
│
├── ui/                           # Web UI
│   ├── src/server.py             # FastAPI web server (port 3000)
│   └── templates/
│
├── flake.nix                     # Nix flake configuration
├── shell.nix                     # Development shell
├── Cargo.toml                    # Rust dependencies
│
├── run-all.sh                    # Start all services in tmux
├── run-orchestrator.sh           # Start orchestrator only
├── run-ui.sh                     # Start UI only
│
├── .env.template                 # Configuration template
└── docs/                         # Documentation
    ├── setup/                    # Installation guides
    ├── permissions/              # Security documentation
    └── reference/                # Technical reference
```

### Data Directories

```
~/.local/share/ergo/
├── activity.db                # Main SQLite database
├── events/                    # Raw event files
├── session_summaries/         # Generated summaries
├── screenshots/               # Captured screenshots (opt-in)
├── audio/                     # Voice recordings (opt-in)
├── repo_snapshots/            # Git snapshot backups
├── models/                    # Local model cache
├── nvim_context.json          # Current Neovim context
└── backups/                   # Database backups

~/.config/ergo/                # Config files
└── .env                       # API keys and settings
```

---

## Core Components

### 1. Rust Daemon (`ergo-daemon`)

**Location:** `src/`
**Purpose:** System Monitoring Layer

#### Responsibilities

- Monitors active window every 5 seconds using `xdotool`
- Tracks process names, window titles, and focus time
- Detects patterns (e.g., stuck on same window >30 min)
- Enforces privacy filtering (ignores password managers, .env files, etc.)
- Stores events in local SQLite database
- Low-level system observation without screenshots

#### Key Files

- `main.rs` - Main loop for window polling and activity logging (src/main.rs:1)
- `window_monitor.rs` - Uses xdotool to get active window info (src/window_monitor.rs:1)
- `database.rs` - SQLite operations (activity_log, patterns tables) (src/database.rs:1)
- `privacy.rs` - Privacy filter patterns and rules (src/privacy.rs:1)

#### Database Schema

```sql
CREATE TABLE activity_log (
  id INTEGER PRIMARY KEY,
  timestamp INTEGER,
  window_title TEXT,
  process_name TEXT,
  duration INTEGER,
  ignored BOOLEAN
);

CREATE TABLE patterns (
  id INTEGER PRIMARY KEY,
  timestamp INTEGER,
  pattern_type TEXT,
  description TEXT,
  window_title TEXT,
  process_name TEXT
);
```

**Storage:** `~/.local/share/ergo/activity.db`

---

### 2. Python Orchestrator (`ergo-orchestrator`)

**Location:** `orchestrator/`
**Purpose:** AI Routing & Memory Layer

#### Responsibilities

- FastAPI server on port `8765` (127.0.0.1)
- Routes requests to appropriate AI models (Gemini, Opus, local)
- Builds context from ephemeral/working/long-term memory
- Manages persistent memory (events, summaries, patterns)
- Handles intervention logic and pattern detection
- Coordinates with daemon for event processing

#### Key Files

- `main.py` - FastAPI server with endpoints (orchestrator/src/main.py:1)
- `config.py` - Configuration management from `.env` (orchestrator/src/config.py:1)
- `model_router.py` - Routes tasks to correct AI model (orchestrator/src/model_router.py:1)
- `context_builder.py` - Assembles context from memory layers (orchestrator/src/context_builder.py:1)
- `memory_manager.py` - Manages event storage and retrieval (orchestrator/src/memory_manager.py:1)

#### Model Routing Strategy

| Task | Model | Reason |
|------|-------|--------|
| General Chat | Gemini 2.5 Flash | Cost-effective, covered by plan |
| Code Review/Debug | Claude Opus | Deep reasoning for expensive tasks |
| Event Tagging | Local/Rules | Cheap, frequent |
| Session Summaries | Local/Gemini | Quick summaries |
| Embeddings | Cheap hosted/Local | Indexing only |

#### API Endpoints

```
GET  /                           # Health check
GET  /health                     # Detailed health (models, DB status)
POST /chat                       # Chat with context
POST /code-review                # Code review endpoint
POST /events                     # Receive events from daemon
POST /summary                    # Generate session summary
GET  /context/recent?minutes=N   # Get recent context
GET  /memory/{type}/{key}        # Retrieve memory
POST /memory/{type}/{key}        # Store memory
GET  /interventions              # Get pending interventions
```

#### Dependencies

```
fastapi, uvicorn, pydantic
anthropic, google-generativeai, openai
sqlalchemy, psycopg2
httpx, python-dotenv
```

---

### 3. Neovim Plugin (`ergo-nvim`)

**Location:** `nvim-plugin/`
**Purpose:** Editor Integration Layer

#### Responsibilities

- Non-blocking async integration with Orchestrator API
- Provides real-time code context to Ergo system
- Floating window UI for responses
- Passive monitoring with insight notifications
- Live code commentary (optional, expensive)
- Interactive chat buffer

#### Key Files

- `init.lua` - Main plugin setup and command definitions (nvim-plugin/lua/ergo/init.lua:1)
- `async.lua` - Non-blocking API calls using curl + jobstart (nvim-plugin/lua/ergo/async.lua:1)
- `ui.lua` - Floating window creation and management (nvim-plugin/lua/ergo/ui.lua:1)
- `passive.lua` - Background monitoring and insights (nvim-plugin/lua/ergo/passive.lua:1)
- `live_judge.lua` - Real-time code commentary (nvim-plugin/lua/ergo/live_judge.lua:1)
- `terminal.lua` - Floating terminal integration (nvim-plugin/lua/ergo/terminal.lua:1)

#### User Commands

```vim
:ErgoExplainContext          # Explain current context
:ErgoExplainContext {range}  # Explain selection
:ErgoSummarizeWork           # Get recent work summary
:ErgoJudgeCode               # Review visible code
:ErgoJudgeCode {range}       # Review selection
:ErgoCommitReview            # Review staged git changes
:ErgoChat                    # Open interactive chat
:ErgoInsight                 # Request contextual insight
:ErgoLiveJudgeToggle         # Toggle live commentary
:ErgoTerminal                # Toggle floating terminal (<leader>ef)
:ErgoToggle                  # Toggle monitoring on/off
:ErgoPassiveToggle           # Toggle passive monitoring
:ErgoPersonality {mode}      # Set personality (quiet/standard/verbose)
```

#### Context Sent to Orchestrator

```json
{
  "event_type": "nvim.buffer.context",
  "timestamp": 1234567890,
  "file_path": "/path/to/file.py",
  "language": "python",
  "cursor": {"line": 42, "col": 10},
  "total_lines": 1000,
  "diagnostics": {
    "error_count": 0,
    "warning_count": 2,
    "total_count": 2
  }
}
```

**Auto-reporting:** Every 5 seconds, plugin writes context to `~/.local/share/ergo/nvim_context.json`

---

### 4. Web UI (`ergo-ui`)

**Location:** `ui/`
**Purpose:** Web Interface

#### Responsibilities

- Simple FastAPI web server on port `3000`
- Chat interface with activity panels
- Proxies requests to Orchestrator API
- Displays context, summaries, interventions
- Health monitoring of all services

#### Main Endpoints

```
GET  /                          # Main UI page
GET  /api/health                # Health check (UI + Orchestrator)
POST /api/chat                  # Chat proxy
GET  /api/context/recent        # Recent context proxy
```

---

## Technology Stack

### Backend

- **Rust**: System daemon, window monitoring, database operations
- **Python 3.11+**: FastAPI orchestrator, AI routing, memory management
- **SQLite**: Primary database (PostgreSQL optional for scale)

### Frontend

- **Lua**: Neovim plugin (async, UI, passive monitoring)
- **Python/FastAPI**: Web UI server
- **HTML/CSS/JavaScript**: Web interface templates

### AI/ML

- **Anthropic**: Claude Opus/Sonnet (code reasoning)
- **Google AI**: Gemini 2.5 Flash (general chat)
- **OpenAI**: Optional GPT support
- **Local Models**: Support for llama.cpp models (future)

### NixOS Integration

- **Nix Flakes**: Declarative dependencies
- **rust-overlay**: Rust toolchain management
- **Development Shell**: Auto-setup with all dependencies

### System Integration

- **xdotool**: Window monitoring on X11/Wayland
- **proc filesystem**: Process information
- **git**: Repository context
- **systemd** (optional): Service management

---

## Data Flow

### Complete Flow

1. **Daemon** continuously polls active window and logs to SQLite
2. **Neovim plugin** periodically sends buffer context to file
3. **User** triggers command (e.g., `:ErgoExplainContext`)
4. **Plugin** makes async API call to Orchestrator
5. **Orchestrator** builds context from:
   - Recent activities (ephemeral)
   - Current session info (working)
   - Relevant memories (long-term)
   - Nvim context file
6. **Orchestrator** routes to appropriate model (Gemini/Opus/Local)
7. **Response** returned to Neovim plugin via async callback
8. **UI** displays response in floating window
9. **Interactions** logged back to memory/database

### Event Model

Ergo uses an event-based memory system. Event families:

```
window.focus.changed
browser.tab.changed
browser.page.visited
shell.command.finished
git.status.changed
build.failed / build.succeeded
nvim.buffer.enter
nvim.selection.changed
nvim.diagnostics.updated
session.summary.created
voice.session.started / ended
```

#### Event Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| event_id | UUID | Unique identity | 550e8400-e29b |
| timestamp | datetime | Ordering and retrieval | 2026-03-25T09:14 |
| source | enum | Emitter service | nvim, browser, shell |
| project_id | text | Repo/task grouping | project-ergo |
| privacy_tag | enum | Retention control | public, private, ignore |
| payload_json | json | Raw normalized content | {...} |
| confidence | float | Signal reliability | 0.92 |

---

## Memory Architecture

Memory is split into **layers** rather than one blended context pool:

### Memory Layers

| Layer | Purpose | Typical Content |
|-------|---------|-----------------|
| **Ephemeral Context** | Last 30-90 minutes of actions | Open files, active window, current shell output, latest diagnostics |
| **Working Memory** | Current day or task block | Open goals, blockers, current branch, recent changes, unresolved issues |
| **Long-term Structured** | Stable, queryable user and project facts | Coding style preferences, common commands, repo metadata, recurring schedules |
| **Long-term Semantic** | Compressed fuzzy-retrieval (future) | Session summaries, solved-problem summaries, decision records, retrospectives |

### Storage Strategy

1. **Start with local storage** - SQLite is sufficient for single-user
2. **Use relational database first** - Most early-value memory is structured
3. **Filesystem for heavy assets** - Screenshots, voice transcripts, archived logs
4. **Add vector layer only when needed** - After memory patterns are stable

### Progression

- **v1**: SQLite or Postgres only
- **v2**: Add embeddings for summaries, notes, selected code chunks
- **v3**: If needed, use pgvector or dedicated vector engine (Qdrant)

---

## Configuration

### Configuration File

**File:** `.env` (created from `.env.template`)

### Key Config Areas

1. **API Credentials**
   - `ANTHROPIC_API_KEY` - For Claude Opus/Sonnet
   - `GOOGLE_AI_API_KEY` - For Gemini 2.5 Flash
   - `OPENAI_API_KEY` - Optional

2. **Database**
   - SQLite path or Postgres connection
   - Default: `~/.local/share/ergo/activity.db`

3. **Storage Paths**
   - Events, summaries, screenshots, audio
   - Default: `~/.local/share/ergo/`

4. **Memory Settings**
   - Context windows (30-90 min ephemeral)
   - Retention periods

5. **Model Routing**
   - Which model for which task
   - Fallback strategies

6. **Intervention Engine**
   - Stuck detection threshold (30+ min same window)
   - Context switch thresholds
   - Quiet hours

7. **Privacy Settings**
   - Patterns to ignore (password managers, .env files)
   - Apps to exclude (Bitwarden, KeePassXC)

8. **Voice Settings**
   - Disabled by default
   - Push-to-talk when enabled

9. **API Server**
   - Host: 127.0.0.1
   - Orchestrator port: 8765
   - UI port: 3000

---

## Design Principles

### 1. Modularity

Three independent layers can fail/update independently:
- Daemon crash doesn't kill orchestrator
- UI restart doesn't affect backend processing
- Plugin updates don't require system restart

### 2. Local-First

Works entirely offline except AI API calls:
- All core data in local SQLite
- No cloud storage for activities
- Private information stays private

### 3. Privacy-by-Design

- Built-in privacy filters (password, token, secret patterns)
- Configurable ignored apps/domains
- Privacy tags on all events
- Screenshot capture is opt-in and manual

### 4. Personality Separation

UI presentation separated from core logic:
- Cognition/reasoning layer stays neutral
- Persona applied only at output layer
- Switchable modes (quiet, standard, verbose)

### 5. Memory Layering

Different retention/retrieval strategies:
- **Ephemeral** (minutes) - Instant context
- **Working** (hours) - Current session
- **Long-term** (persistent) - Facts and patterns
- **Semantic** (future) - Vector embeddings

### 6. Intervention Over Chatting

The key proactive feature is **timely intervention**:
- Excessive context switching
- Repeated occurrence of known error
- Divergence from stated objective
- Build/test avoidance after multiple edits
- Browser drift after work block

Interventions include severity, confidence, quiet-hours handling, and per-project rules.

---

## NixOS Integration

### Nix Flake

**File:** `flake.nix`

**Provides:**
- `packages.ergo-daemon` - Compiled Rust daemon
- `packages.ergo-orchestrator` - Python orchestrator wrapper
- `packages.ergo-ui` - Python UI server wrapper
- `devShells.default` - Complete dev environment

### Dev Environment Includes

- Rust toolchain (with rust-analyzer)
- Python 3.11 with all dependencies
- X11 libraries (for window monitoring)
- Development tools (ripgrep, fd, jq)

### Build Dependencies

- Rust (stable)
- Python 3.11
- pkg-config
- SQLite, PostgreSQL client libs
- X11 development libraries

### Neovim Plugin Integration

For NixOS users with declarative Neovim config at `/etc/nixos/neovimConfig/`:

**In `/etc/nixos/neovimConfig/plugins.nix`:**

```nix
(pkgs.vimUtils.buildVimPlugin {
  pname = "ergo-nvim";
  version = "unstable-2026-03-25";
  src = pkgs.fetchFromGitHub {
    owner = "YourUsername";
    repo = "Ergo";
    rev = "YOUR_COMMIT_HASH";
    sha256 = "sha256-YOUR_HASH_HERE";
  };
  postUnpack = ''
    sourceRoot="$sourceRoot/ergo/nvim-plugin"
  '';
})
```

**In `/etc/nixos/neovimConfig/config/lua/ergo-config.lua`:**

```lua
require('ergo').setup({
  api_url = "http://127.0.0.1:8765",
  enabled = true,
  personality = "standard",
  passive_monitoring = true,
  passive_check_interval = 60000,
  auto_report_interval = 5000,
})
```

### Running Services

**Three-service architecture:**

```bash
# Start all in tmux
./run-all.sh

# Or individual startup:
# Terminal 1: Daemon
cargo run --release

# Terminal 2: Orchestrator
./run-orchestrator.sh

# Terminal 3: UI
./run-ui.sh
```

**Service Ports:**
- Orchestrator API: `http://127.0.0.1:8765`
- Web UI: `http://localhost:3000`
- Daemon: Internal (SQLite database only)

---

## Current Status

### Working

- ✅ Rust daemon (window monitoring, activity logging)
- ✅ Orchestrator API (FastAPI, model routing, context assembly)
- ✅ Chat with Gemini 2.5 Flash
- ✅ Database schema and operations
- ✅ Neovim plugin foundation
- ✅ Floating terminal integration
- ✅ Async non-blocking commands
- ✅ Floating window UI
- ✅ Passive monitoring system

### In Progress

- 🚧 Session summaries and daily reviews
- 🚧 Personality layer improvements
- 🚧 Web UI refinement
- 🚧 Git integration enhancements

### Future

- 📋 Embeddings and vector retrieval
- 📋 Voice mode (push-to-talk)
- 📋 Remote access via Tailscale
- 📋 Autonomous interventions
- 📋 Build/test event tracking

---

## Additional Resources

- **[QUICKSTART.md](setup/QUICKSTART.md)** - Get running in 6 steps
- **[ROADMAP.md](reference/ROADMAP.md)** - Development roadmap
- **[DOCUMENTATION_MAP.md](journal/DOCUMENTATION_MAP.md)** - Full doc guide
- **[PERMISSIONS.md](permissions/PERMISSIONS.md)** - Security and access control

---

**This architecture provides a robust, modular system for local-first AI assistance with developer context awareness, persistent memory, and intelligent model routing—all designed to work seamlessly on NixOS with privacy controls built in.**
