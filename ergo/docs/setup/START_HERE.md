#  Start Here - Ergo Quick Setup

**Local-first AI assistant for developers**

## What is Ergo?

Ergo monitors your work activity, understands your code context, and provides AI-powered assistance—all running locally on your machine.

## ⚡ Quick Start (5 Minutes)

### NixOS Users (Recommended)

```bash
# 1. Enter Nix environment (provides all dependencies)
nix-shell

# 2. Build (if not already built)
cargo build --release

# 3. Run everything
./run-all.sh
```

See **[NIXOS_SETUP.md](NIXOS_SETUP.md)** for full NixOS guide.

### Other Linux

```bash
# 1. Build
cargo build --release

# 2. Install Python dependencies
cd orchestrator && pip install -r requirements.txt && cd ..

# 3. Run everything
./run-all.sh
```

**Then open:** http://localhost:3000

##  Documentation Guide

- **[START_HERE.md](START_HERE.md)** ← You are here
- **[RUNNING.md](RUNNING.md)** - How to start/stop services
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed walkthrough
- **[README.md](README.md)** - Complete user guide
- **[INSTALL.md](INSTALL.md)** - Installation options
- **[BUILD_STATUS.md](BUILD_STATUS.md)** - What's implemented
- **[ROADMAP.md](ROADMAP.md)** - Future plans

##  What Works Right Now

 **Daemon** - Monitors windows, tracks activity, respects privacy
 **Chat** - Talk to Gemini with full context awareness
 **Code Review** - Get Opus to review your code
 **Memory** - Remembers your workflows and preferences
 **Neovim Plugin** - Deep editor integration with 5 commands
 **Web UI** - Beautiful chat interface with activity dashboard

## ️ Three Ways to Run

### Option 1: All-in-One (Easiest)
```bash
./run-all.sh
```
Requires tmux. Starts everything in one session.

### Option 2: Separate Terminals
```bash
# Terminal 1
./target/release/ergo

# Terminal 2
./run-orchestrator.sh

# Terminal 3
./run-ui.sh
```

### Option 3: Just the Daemon
```bash
./target/release/ergo
```
Activity tracking only, no AI features.

## 🔍 Verify It's Working

### Check Daemon
```bash
./target/release/ergo stats
```
Should show today's activity.

### Check API
```bash
curl http://127.0.0.1:8765/health | jq
```
Should return `{"status": "healthy"}`.

### Check UI
Open browser: http://localhost:3000

Type: "What am I working on?"

## [X] Quick Tips

**Neovim Commands:**
- `:ErgoExplainContext` - What am I working on?
- `:ErgoJudgeThisCode` - Review this code
- `:ErgoCommitReview` - Review my git changes

**Privacy:**
Password managers and sensitive apps are automatically ignored. Check `.env` to customize patterns.

**Stats:**
```bash
./target/release/ergo stats
```
Shows today's activity summary.

## 🐛 Common Issues

**"Address already in use"**
```bash
lsof -i :8765  # Find what's using the port
kill -9 <PID>
```

**"ModuleNotFoundError: No module named 'fastapi'"**
```bash
cd orchestrator
pip install -r requirements.txt
```

**"Database error"**
```bash
mkdir -p ~/.local/share/ergo
```

## [X] Next Steps

1. **Try the chat** - http://localhost:3000
2. **Install Neovim plugin** - See [README.md](README.md#neovim-plugin-installation)
3. **Customize settings** - Edit `.env`
4. **Set up auto-start** - See [RUNNING.md](RUNNING.md#background-services)

## 🏗️ Project Status

**Phase 0-1:** 90% Complete 
- All core services working
- Database architecture complete
- Model routing functional
- Neovim integration ready

**What's Next:**
- Git integration (planned)
- Shell command tracking (planned)
- Active interventions (infrastructure ready)

##  Project Structure

```
ergo/
├── target/release/ergo       # Built daemon
├── run-all.sh                 # Start everything
├── run-orchestrator.sh        # Start API server
├── run-ui.sh                  # Start web UI
├── .env                       # Your configuration
└── docs/                      # All documentation
```

## 🎓 Learn More

**Architecture:** Read [proj_ergo_arch.md](proj_ergo_arch.md) for the design philosophy

**Development:** See [BUILD_STATUS.md](BUILD_STATUS.md) for implementation details

**Contributing:** Check [ROADMAP.md](ROADMAP.md) for areas needing work

##  You're Ready!

Your system is built and configured. Run `./run-all.sh` and start using Ergo!

**Questions?** Check the documentation or the troubleshooting sections.

---

Built following a practical, local-first architecture. No over-engineering, no fake sentience—just useful developer assistance.
