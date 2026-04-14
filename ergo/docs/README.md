# Ergo Documentation

Welcome to the Ergo documentation. This directory contains all guides, references, and setup instructions for running Ergo on NixOS.

## Quick Links

###  Getting Started
- **[START_HERE](setup/START_HERE.md)** - Begin here if you're new to Ergo
- **[QUICKSTART](setup/QUICKSTART.md)** - Fast setup guide
- **[INSTALL](setup/INSTALL.md)** - Installation instructions

### [X] Setup Guides
- **[Setup Permissions](setup/SETUP_PERMISSIONS.md)** - Configure system scanning authority
- **[NixOS Setup](setup/NIXOS_SETUP.md)** - NixOS-specific configuration
- **[Neovim Setup](setup/NEOVIM_SETUP.md)** - Integrate Ergo with your Neovim config
- **[Running Ergo](setup/RUNNING.md)** - How to start and run all services

###  Permissions & Security
- **[Permissions Overview](permissions/PERMISSIONS.md)** - Comprehensive permission documentation
- **[Scanning Authority Summary](permissions/SCANNING_AUTHORITY_SUMMARY.md)** - What Ergo can scan and why
- **[Quick Reference](reference/PERMISSIONS_QUICKREF.txt)** - Permission cheat sheet

###  Reference
- **[Architecture](reference/architecture.md)** - System architecture and design
- **[Build Status](reference/BUILD_STATUS.md)** - Current build state
- **[Roadmap](reference/ROADMAP.md)** - Future development plans

## Documentation Structure

```
docs/
├── README.md (this file)
├── setup/
│   ├── START_HERE.md           # Entry point for new users
│   ├── QUICKSTART.md           # Fast setup guide
│   ├── INSTALL.md              # Installation instructions
│   ├── NIXOS_SETUP.md          # NixOS-specific setup
│   ├── NEOVIM_SETUP.md         # Neovim plugin integration
│   ├── SETUP_PERMISSIONS.md    # Permission configuration
│   ├── RUNNING.md              # Running the services
│   └── RUN_NOW.md              # Quick run commands
├── permissions/
│   ├── PERMISSIONS.md          # Full permission docs
│   └── SCANNING_AUTHORITY_SUMMARY.md
└── reference/
    ├── architecture.md         # System architecture
    ├── BUILD_STATUS.md         # Build information
    ├── ROADMAP.md              # Development roadmap
    └── PERMISSIONS_QUICKREF.txt # Quick permission reference
```

## By Topic

### Installation & Setup
1. Read [START_HERE.md](setup/START_HERE.md) for overview
2. Follow [INSTALL.md](setup/INSTALL.md) for installation
3. Configure with [SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)
4. Set up [NEOVIM_SETUP.md](setup/NEOVIM_SETUP.md) (if using Neovim)
5. Start services with [RUNNING.md](setup/RUNNING.md)

### Understanding Permissions
1. Quick overview: [SCANNING_AUTHORITY_SUMMARY.md](permissions/SCANNING_AUTHORITY_SUMMARY.md)
2. Full details: [PERMISSIONS.md](permissions/PERMISSIONS.md)
3. Quick reference: [PERMISSIONS_QUICKREF.txt](reference/PERMISSIONS_QUICKREF.txt)

### NixOS Users
1. [NIXOS_SETUP.md](setup/NIXOS_SETUP.md) - System configuration
2. [NEOVIM_SETUP.md](setup/NEOVIM_SETUP.md) - Declarative Neovim config
3. [SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md) - Permission checks

### Developers
1. [architecture.md](reference/architecture.md) - System design
2. [BUILD_STATUS.md](reference/BUILD_STATUS.md) - Current state
3. [ROADMAP.md](reference/ROADMAP.md) - Planned features

## Common Tasks

### First Time Setup
```bash
# 1. Read the start guide
cat docs/setup/START_HERE.md

# 2. Run permission diagnostic
./scripts/check-permissions.sh

# 3. Install dependencies
cd orchestrator && pip install -r requirements.txt

# 4. Start services (see RUNNING.md)
cargo run --bin ergo-daemon &
python3 orchestrator/src/main.py
```

### Check Permissions
```bash
# Run diagnostic
./scripts/check-permissions.sh

# Read permission docs
cat docs/reference/PERMISSIONS_QUICKREF.txt
```

### Configure Neovim
```bash
# Read setup guide
cat docs/setup/NEOVIM_SETUP.md

# Check your config location
ls -la /etc/nixos/neovimConfig/
```

## Documentation Conventions

### File Naming
- **UPPERCASE.md** - User-facing guides and documentation
- **lowercase.md** - Technical reference and architecture docs
- **PREFIXES**:
  - `SETUP_*` - Setup and configuration guides
  - `RUNNING_*` - Operational guides
  - No prefix - Entry points and overviews

### Document Structure
- All docs include a purpose statement at the top
- Step-by-step guides use numbered lists
- Technical references use sections with headers
- Code examples are in bash/nix/lua blocks

## Getting Help

### Permission Issues
1. Run `./scripts/check-permissions.sh`
2. Check logs: `tail -f ~/.local/share/ergo/ergo.log`
3. Review [SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)

### Installation Issues
1. Check [BUILD_STATUS.md](reference/BUILD_STATUS.md)
2. Review [INSTALL.md](setup/INSTALL.md)
3. For NixOS: see [NIXOS_SETUP.md](setup/NIXOS_SETUP.md)

### Runtime Issues
1. Check services are running: `pgrep -f ergo`
2. Test API: `curl http://127.0.0.1:8765/health`
3. Review [RUNNING.md](setup/RUNNING.md)

## Contributing to Documentation

When adding new documentation:
1. Place in appropriate directory (setup/, permissions/, reference/)
2. Update this README.md with link
3. Follow naming conventions
4. Include purpose statement at top of doc
5. Add entry to relevant section above

---

**Last Updated:** 2026-03-18
**Ergo Version:** 0.1.0 (prototype)
**System:** NixOS
