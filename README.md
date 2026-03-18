# Ergo

Local-first AI assistant for NixOS developers.

## Quick Start

```bash
cd ergo
# See QUICKSTART.md for setup
```

**[→ Full Quick Start Guide](ergo/QUICKSTART.md)**

## Structure

```
ergo/
├── orchestrator/     # Python FastAPI service (AI routing)
├── src/             # Rust daemon (window monitoring)
├── nvim-plugin/     # Neovim integration
├── ui/              # Web interface (optional)
├── QUICKSTART.md    # Start here
└── docs/journal/    # Detailed docs
```

## Status

- ✅ Orchestrator running
- ✅ Neovim plugin ready
- ⚠️  Daemon needs build
- ⚠️  UI optional

See [ergo/README.md](ergo/README.md) for details.
