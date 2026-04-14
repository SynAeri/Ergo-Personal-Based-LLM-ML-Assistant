# Ergo Documentation Map

Visual guide to all documentation organized by user journey.

```
                        ERGO DOCUMENTATION
                               │
                ┌──────────────┼──────────────┐
                │              │              │
           SETUP         PERMISSIONS   [X] REFERENCE
                │              │              │
        ┌───────┴───────┐      │              │
        │               │      │              │
    NEW USER      NIXOS USER   │              │
        │               │      │              │
        ▼               ▼      ▼              ▼
```

##  For New Users

**Start Here → Complete Setup → Configure Permissions**

```
1. START_HERE.md
   └─> Overview of Ergo and what it does
       │
2. INSTALL.md
   └─> Installation prerequisites and steps
       │
3. SETUP_PERMISSIONS.md
   └─> Configure what Ergo can scan
       │
4. RUNNING.md
   └─> Start all services and verify
```

### Path: New User Setup
1. **[START_HERE.md](setup/START_HERE.md)** - Read this first
2. **[INSTALL.md](setup/INSTALL.md)** - Install dependencies
3. **[SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)** - Grant scanning authority
4. **[RUNNING.md](setup/RUNNING.md)** - Start the services

**Quick alternative:** [QUICKSTART.md](setup/QUICKSTART.md) or [RUN_NOW.md](setup/RUN_NOW.md)

---

##  For NixOS Users

**NixOS Setup → Neovim Integration → Permissions**

```
1. NIXOS_SETUP.md
   └─> NixOS-specific configuration
       │
2. NEOVIM_SETUP.md
   └─> Integrate with /etc/nixos/neovimConfig/
       │
3. SETUP_PERMISSIONS.md
   └─> Verify system permissions
       │
4. RUNNING.md
   └─> Start services
```

### Path: NixOS User Setup
1. **[NIXOS_SETUP.md](setup/NIXOS_SETUP.md)** - System configuration
2. **[NEOVIM_SETUP.md](setup/NEOVIM_SETUP.md)** - Plugin installation for declarative config
3. **[SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)** - Run diagnostics
4. **[RUNNING.md](setup/RUNNING.md)** - Start everything

---

##  Understanding Permissions

**Quick Reference → Summary → Full Details**

```
1. PERMISSIONS_QUICKREF.txt
   └─> One-page cheat sheet
       │
2. SCANNING_AUTHORITY_SUMMARY.md
   └─> What Ergo scans and why
       │
3. PERMISSIONS.md
   └─> Comprehensive technical docs
```

### Path: Permission Configuration
1. **[PERMISSIONS_QUICKREF.txt](reference/PERMISSIONS_QUICKREF.txt)** - Quick reference card
2. **[SCANNING_AUTHORITY_SUMMARY.md](permissions/SCANNING_AUTHORITY_SUMMARY.md)** - Summary of scanning authority
3. **[PERMISSIONS.md](permissions/PERMISSIONS.md)** - Full technical documentation

**Diagnostic tool:** `scripts/check-permissions.sh`

---

## [X] Reference Documentation

**Architecture → Current Status → Future Plans**

```
1. architecture.md
   └─> System design and components
       │
2. BUILD_STATUS.md
   └─> Current implementation state
       │
3. ROADMAP.md
   └─> Planned features
```

### Path: Understanding Ergo
1. **[architecture.md](reference/architecture.md)** - System architecture and design philosophy
2. **[BUILD_STATUS.md](reference/BUILD_STATUS.md)** - What's built, what's in progress
3. **[ROADMAP.md](reference/ROADMAP.md)** - Future development plans

---

## Documentation by Task

### "I want to install Ergo"
→ [START_HERE.md](setup/START_HERE.md) → [INSTALL.md](setup/INSTALL.md)

### "I'm on NixOS"
→ [NIXOS_SETUP.md](setup/NIXOS_SETUP.md)

### "I use Neovim with declarative config"
→ [NEOVIM_SETUP.md](setup/NEOVIM_SETUP.md)

### "I want to understand permissions"
→ [PERMISSIONS_QUICKREF.txt](reference/PERMISSIONS_QUICKREF.txt) → [SCANNING_AUTHORITY_SUMMARY.md](permissions/SCANNING_AUTHORITY_SUMMARY.md)

### "How do I run Ergo?"
→ [RUNNING.md](setup/RUNNING.md) or [RUN_NOW.md](setup/RUN_NOW.md)

### "What can Ergo scan?"
→ [SCANNING_AUTHORITY_SUMMARY.md](permissions/SCANNING_AUTHORITY_SUMMARY.md)

### "I'm getting permission errors"
→ Run `scripts/check-permissions.sh` → [SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)

### "How does Ergo work internally?"
→ [architecture.md](reference/architecture.md)

### "What features are planned?"
→ [ROADMAP.md](reference/ROADMAP.md)

---

## Documentation Structure

```
docs/
│
├── README.md                   # Main documentation index
├── DOCUMENTATION_MAP.md        # This file - visual guide
│
├── setup/                      # Installation and configuration
│   ├── START_HERE.md          #  Entry point for new users
│   ├── INSTALL.md             # Installation instructions
│   ├── NIXOS_SETUP.md         # NixOS-specific setup
│   ├── NEOVIM_SETUP.md        # Neovim plugin integration
│   ├── SETUP_PERMISSIONS.md   # Permission configuration
│   ├── RUNNING.md             # How to run services
│   ├── RUN_NOW.md             # Quick run commands
│   └── QUICKSTART.md          # Fast setup guide
│
├── permissions/               # Security and access control
│   ├── SCANNING_AUTHORITY_SUMMARY.md  # What Ergo can scan
│   └── PERMISSIONS.md         # Comprehensive permission docs
│
└── reference/                 # Technical reference
    ├── architecture.md        # System design
    ├── BUILD_STATUS.md        # Current build state
    ├── ROADMAP.md             # Development roadmap
    └── PERMISSIONS_QUICKREF.txt  # Quick permission reference
```

---

## Recommended Reading Order

### First Time Users
1. [X] [START_HERE.md](setup/START_HERE.md)
2. [X] [SCANNING_AUTHORITY_SUMMARY.md](permissions/SCANNING_AUTHORITY_SUMMARY.md)
3. [X] [INSTALL.md](setup/INSTALL.md)
4. [X] [SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)
5. [X] [RUNNING.md](setup/RUNNING.md)

### NixOS Users
1. [X] [NIXOS_SETUP.md](setup/NIXOS_SETUP.md)
2. [X] [NEOVIM_SETUP.md](setup/NEOVIM_SETUP.md)
3. [X] [SETUP_PERMISSIONS.md](setup/SETUP_PERMISSIONS.md)
4. [X] [RUNNING.md](setup/RUNNING.md)

### Security-Conscious Users
1. [X] [PERMISSIONS_QUICKREF.txt](reference/PERMISSIONS_QUICKREF.txt)
2. [X] [SCANNING_AUTHORITY_SUMMARY.md](permissions/SCANNING_AUTHORITY_SUMMARY.md)
3. [X] [PERMISSIONS.md](permissions/PERMISSIONS.md)
4. Run `scripts/check-permissions.sh`

### Developers
1. [X] [architecture.md](reference/architecture.md)
2. [X] [BUILD_STATUS.md](reference/BUILD_STATUS.md)
3. [X] [ROADMAP.md](reference/ROADMAP.md)
4. [X] [PERMISSIONS.md](permissions/PERMISSIONS.md)

---

## Quick Commands

### View a document
```bash
# From ergo/ directory
cat docs/setup/START_HERE.md
cat docs/reference/PERMISSIONS_QUICKREF.txt
```

### Search documentation
```bash
grep -r "keyword" docs/
```

### List all docs
```bash
tree docs/ -L 2
```

### Check permissions
```bash
./scripts/check-permissions.sh
```

---

## Document Types

### 📘 Setup Guides (setup/)
- Step-by-step instructions
- Commands to run
- Verification steps
- Troubleshooting

###  Permission Docs (permissions/)
- What Ergo can access
- How to configure access
- Security implications
- Privacy controls

### [X] Reference (reference/)
- Technical architecture
- Design decisions
- Current status
- Future plans

---

## Contributing to Documentation

When adding new docs:

1. **Choose the right directory:**
   - User-facing setup → `setup/`
   - Security/permissions → `permissions/`
   - Technical reference → `reference/`

2. **Follow naming conventions:**
   - UPPERCASE.md for user guides
   - lowercase.md for technical docs

3. **Update indexes:**
   - Add to `docs/README.md`
   - Add to this file (DOCUMENTATION_MAP.md)
   - Update root README.md if major doc

4. **Include:**
   - Purpose statement at top
   - Table of contents for long docs
   - Code examples with language tags
   - Related documentation links

---

**Last Updated:** 2026-03-18
**Total Documents:** 15 files + 1 script
**System:** NixOS
