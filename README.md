# Ergo

**Local-first AI assistant for NixOS developers**

Ergo monitors your work context, builds persistent memory across sessions, and provides intelligent assistance through deep integration with your development workflow.

---

## Quick Start

```bash
cd ergo
./run-all.sh  # Start all services in tmux
```

**[→ Full Documentation](ergo/docs/)**

---

## Structure

```
ergo/
├── orchestrator/     # Python FastAPI service (AI routing & memory)
├── src/             # Rust daemon (window monitoring & events)
├── nvim-plugin/     # Neovim integration
├── ui/              # Web interface
├── docs/            # Comprehensive documentation
│   ├── setup/       # Installation & configuration guides
│   ├── permissions/ # Security & access control
│   └── reference/   # Architecture & technical docs
├── run-all.sh       # Start all services
└── README.md        # This file
```

---

## Documentation

### Quick Links

- **[Quick Start Guide](ergo/docs/setup/QUICKSTART.md)** - Get running in 6 steps
- **[Architecture](ergo/docs/ARCHITECTURE.md)** - Complete system architecture
- **[Documentation Map](ergo/docs/DOCUMENTATION_MAP.md)** - Visual guide to all docs

### By Category

#### Setup & Installation
- [Start Here](ergo/docs/setup/START_HERE.md) - New user entry point
- [Installation Guide](ergo/docs/setup/INSTALL.md) - Prerequisites and install steps
- [NixOS Setup](ergo/docs/setup/NIXOS_SETUP.md) - NixOS-specific configuration
- [Neovim Setup](ergo/docs/setup/NEOVIM_SETUP.md) - Plugin installation
- [Running Ergo](ergo/docs/setup/RUNNING.md) - How to start services

#### Security & Privacy
- [Permissions Overview](ergo/docs/permissions/SCANNING_AUTHORITY_SUMMARY.md) - What Ergo can scan
- [Permission Configuration](ergo/docs/permissions/PERMISSIONS.md) - Detailed permission docs
- [Quick Reference](ergo/docs/permissions/PERMISSIONS_QUICKREF.txt) - One-page cheat sheet

#### Technical Reference
- [System Architecture](ergo/docs/ARCHITECTURE.md) - Complete technical architecture
- [Build Status](ergo/docs/reference/BUILD_STATUS.md) - Current implementation state
- [Roadmap](ergo/docs/reference/ROADMAP.md) - Planned features

---

## Status

- ✅ Orchestrator running (Python FastAPI)
- ✅ Neovim plugin ready (Lua, async)
- ✅ Model routing (Gemini + Opus)
- ✅ Floating terminal integration
- ⚠️  Daemon in progress (Rust)
- ⚠️  Web UI optional

---

## What Ergo Does

- **Context-aware**: Monitors files, git, shell, and window activity
- **Persistent memory**: Remembers patterns, preferences, and project history
- **Smart routing**: Uses Gemini for chat, Opus for deep code analysis
- **Privacy-first**: Built-in filters, local SQLite database
- **Neovim integration**: Non-blocking async commands, floating windows
- **Passive monitoring**: Optional insights and live code commentary

---

## Quick Commands

In Neovim:
```vim
:ErgoExplainContext          " Explain current context
:ErgoChat                    " Open interactive chat
:ErgoJudgeCode               " Review visible code
:ErgoCommitReview            " Review staged changes
:ErgoTerminal                " Toggle floating terminal
:ErgoLiveJudgeToggle         " Toggle live commentary (opt-in)
```

---

## Development

See [ergo/README.md](ergo/README.md) for detailed development workflow, including:
- Updating the Neovim plugin
- NixOS rebuild process
- Service architecture
- Contributing guidelines

---

## License

See LICENSE
