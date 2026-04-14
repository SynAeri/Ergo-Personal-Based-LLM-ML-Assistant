# Project Epic — Full Vision Document

> Single source of truth for architecture, features, and design decisions.
> Written 2026-04-14. Covers everything discussed in design sessions.

---

## 1. What This Is

**Ergo** is a local-first AI work operator for NixOS/Hyprland that monitors your system,
builds persistent memory, and provides contextual assistance through your editor and beyond.

**Project Epic** is the RPG quest execution engine that sits on top of Ergo. It transforms
coding tasks into coordinated multi-agent adventures with a living 2D world visualization.

Together they form one system: Ergo is the city, Project Epic is the quest board inside it.

---

## 2. Current State (What Actually Works)

### Ergo — Working
- Neovim plugin (async, floating windows, live judge, chat terminal)
- Orchestrator (FastAPI, model routing between Gemini Flash + Claude Opus)
- Rust daemon — **now fixed for Hyprland/Wayland** using `hyprctl activewindow`
  - Previously used xdotool which returned "Unknown Window" on Wayland
  - Now captures: title, process, class, workspace correctly
- SQLite activity logging (`~/.local/share/ergo/activity.db`)
- Personality layer (quiet / standard / verbose tsundere mode)

### Ergo — Built But Not Wired
- `database_v2.rs` schema: events, sessions, memories, interventions, summaries, projects
  - All tables exist and are empty — nothing writes to them yet
- `event_emitter.rs` — emits events via in-process channel, never HTTP posts to orchestrator
- The daemon and orchestrator are completely disconnected
  - Daemon logs to `activity_log` (v1)
  - Orchestrator reads from v2 tables
  - They never talk

### Project Epic — Built But Not Wired
- `zones.json` — 10 world locations fully defined
- `dialogue_engine.py` — blacksmith pattern (technical events → fantasy narrative)
- `heroes_journey.py` — quest phase management with campfire checkpoints
- `base_agent.py` — multi-model agent with permission system
- `FullProposal.md` — complete PhaserJS living world architecture spec
- Party system design docs (planner, mage, rogue, tank, support, healer)
- None of the agents actually call the API yet — `process_step` is abstract with no implementations

### NixOS Integration — Friction Point
- Plugin update workflow: edit code → push to GitHub → update SHA in `/etc/nixos/neovimConfig` → nixos-rebuild
- This is the current bottleneck for iteration speed on the Neovim side

---

## 3. The Full Architecture Stack

```
┌─────────────────────────────────────────────────────────────┐
│  INTERFACES                                                  │
│  Neovim plugin · Web UI (localhost:3000) · Phone (Obsidian) │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  PROJECT EPIC — Quest Engine                                 │
│  agent-swarm (MCP worker coordination)                      │
│  + crewAI (role-based task DAGs)                            │
│  + Living World (PhaserJS zones + dialogue engine)          │
│  + Obsidian MCP bridge (knowledge dungeons)                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  ERGO — Runtime                                             │
│  Orchestrator (FastAPI :8765) · Model Router                │
│  Memory Manager · Context Builder                           │
│  SQLite (activity, events, sessions, memories)              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM LAYER                                               │
│  Rust daemon (Hyprland window monitoring via hyprctl)       │
│  Obsidian Sync ← vault on disk ← MCP plugin                │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Agent Framework Decision

### Engine: agent-swarm + crewAI
The `inspirations/` folder contains full clones of the frameworks we evaluated:

| Repo | Role in stack |
|---|---|
| **agent-swarm** | MCP-based worker coordination — Claude Code instances as agents, SQLite state, lead/worker architecture. This is the agent engine. |
| **crewAI** | Python role-based task DAGs — handles quest execution flow, agent handoffs, task sequencing |
| **swarm** | Lightweight fallback for simple agent routing |
| **generative_agents** | NPC idle behavior patterns (borrowed for ambient party dialogue) |

**Why not hand-roll:** `base_agent.py` and `party.py` exist but `process_step` is abstract
with no implementations. agent-swarm is battle-tested for exactly this pattern.
The RPG world layer stays as the skin on top — agent-swarm replaces the coordination guts.

### Party Composition
| Character | Model | Role |
|---|---|---|
| Planner | Gemini Flash | Task breakdown, risk assessment, dependency mapping |
| Mage | Claude Opus | Architecture decisions, code review, design patterns |
| Rogue | Claude Sonnet | Implementation, refactoring, hotfixes |
| Tank | Claude Sonnet | Testing, validation, verification |
| Support | Gemini Flash | Context retrieval, memory lookup, file search |
| Healer | Gemini Flash | Documentation, summaries, changelogs |

---

## 5. The Living World

The world is a **reactive visualization of quest state**, not an independent simulation.
Agents don't decide to walk to the blacksmith — the orchestrator detects test failures
and emits an event that the visual layer interprets as a blacksmith visit.

### Current Zones (zones.json)
| Zone | Trigger | Mood |
|---|---|---|
| The Campfire | Planning, review phases | Focused |
| The Forge | Debugging, error fixing | Tense |
| The Proving Grounds | Testing, verification | Vigilant |
| The Grand Archive | Documenting, recording | Calm |
| The Guild Hall | Quest selection, idle | Organized |
| The Rusty Compile (Tavern) | Idle, celebration | Celebratory |
| The Stack Overflow Inn | Agents resting | Peaceful |
| The Dungeon Gate | Active sprints | Intense |
| The Deprecated Grounds | Failed quests | Somber |
| The Package Bazaar | Dependency installation | Busy |

### Dialogue Engine (blacksmith pattern)
Technical events translate to fantasy narrative via `dialogue_engine.py`:
- Tests failing → Tank: *"These weapons aren't holding up. To the forge!"*
- Dependencies needed → Support: *"The merchant at the bazaar has what we need."*
- Architecture review → Mage: *"Something doesn't feel right. Let me consult the archives."*
- Sprint complete → Rogue: *"Another one down. Who's buying ale?"*
- Budget warning → Support: *"Our supplies are running low..."*

Ambient dialogue fires probabilistically (30% idle, 20% after 60s, 40% at sprint midpoint).
Event-driven dialogue always fires.

### Confidence Palettes
World color shifts based on quest health:
- High (>0.8) — Sunny, warm, optimistic
- Normal (>0.5) — Overcast, neutral
- Low (>0.3) — Foggy, muted
- Critical — Stormy, dark

---

## 6. The Obsidian Knowledge System

### Vault Decision
**Do NOT put Ergo/Epic knowledge in your root Obsidian vault.**

You have two vaults:
- `Vault For everything/` — personal life, study, people, events. Keep this separate.
- `allStuff/` — already has study notes, daily stuff, mixed content.

**Create a dedicated vault: `Obsidian/Ergo/`**

Reasons:
- MCP plugin scopes to a single vault — you don't want Ergo reading your personal notes
- Obsidian Sync works per-vault — you control what syncs to phone separately
- The knowledge base will grow large and structured differently from personal notes
- Privacy: project code context, window titles, shell history shouldn't mix with personal vault
- Clean graph view — Ergo's knowledge graph stays coherent, not polluted by daily notes

### Vault Structure
```
~/Obsidian/Ergo/
├── CLAUDE.md              ← MCP operating manual (auto-loaded, keep under 100 lines)
├── index.md               ← Page catalog, Claude reads this first
│
├── quests/                ← Completed quest journals (exported from Project Epic)
│   ├── 2026-04-14-jwt-auth.md
│   └── ...
│
├── dungeons/              ← Knowledge dungeons (docs, study notes as explorable nodes)
│   ├── rust-lifetimes.md          ← "Dungeon: Rust Lifetimes"
│   ├── nixos-flakes.md            ← "Dungeon: NixOS Flakes"
│   └── hyprland-config.md
│
├── world/                 ← Project state, architecture decisions
│   ├── ergo-architecture.md
│   ├── project-epic-vision.md
│   └── decisions/
│
├── party/                 ← Party member memory, learned preferences
│   ├── coding-style.md
│   ├── project-patterns.md
│   └── recurring-issues.md
│
└── sessions/              ← Daily session summaries from Ergo daemon
    ├── 2026-04-14.md
    └── ...
```

### Obsidian Dungeon System — The Core Idea

Obsidian notes are **knowledge dungeons**. Opening a note = entering a dungeon.
Following links = moving between dungeon rooms. The world map shows which dungeons
exist, which are cleared, and which you fled from.

```
Obsidian graph view     →  The World Map (overworld)
A note                  →  A dungeon
Links between notes     →  Paths/corridors between dungeons
Note tags               →  Region/biome of the world
Unlinked notes          →  Undiscovered dungeons (fog of war)
Backlinks               →  "You came here from..."
```

**Dungeon states:**
- **Undiscovered** — note exists, never opened
- **Entered** — opened but not finished reading/working
- **Fled** (low HP) — closed quickly, came back → *"Fleeing skeletons on the way out"*
- **In progress** — feature is being built, docs incomplete
- **Cleared** — feature done, docs complete, tests passing

**Narrative examples from the dialogue engine:**

When you open a half-read note on Rust lifetimes that you previously closed quickly:
> *Rogue: "Back to the Rust Catacombs. Last time we barely made it out."*
> *Support: "I have notes from our previous expedition. The skeletons were in section 3."*

When you finish a feature that was documented:
> *"Dungeon Cleared: Rust Lifetimes. The party emerges victorious."*
> *(World map updates, dungeon shows as cleared, party moves to Tavern)*

When the Mage notices you've been in the same dungeon for 30 minutes:
> *"The mage senses something. We've been in these tunnels a long time."*
> *(Intervention triggered — same as stuck pattern detection)*

**Horizontal timeline view (the toon/sprite idea):**
A scrolling timeline in the web UI shows sprites moving left to right as work progresses:
```
[Campfire] ──► [Dungeon Gate] ──► [Floor 1] ──► [Floor 2] ──► [Boss] ──► [Tavern]
  🗺️💬           ⚔️🛡️              💀💀           ⚔️              👑          🍺🎉
"Planning..."  "Entering..."    "Skeletons!"   "Pushing on"   "Final boss"  "Victory!"
```

Each zone transition = sprite walks to next location on the timeline.
Progress is shown as a horizontal scroll, not just a static HUD.

---

## 7. MCP Integration

### How the Obsidian MCP works
Install `obsidian-claude-code-mcp` plugin in Obsidian.
Configure Claude Code / Ergo orchestrator:
```bash
claude mcp add obsidian-vault --transport sse http://localhost:27123/sse
```

The MCP exposes 7 vault operations as tools:
- View files
- String replacement
- Create new files
- Insert content
- Workspace context (active file + vault structure)
- Direct Obsidian API access
- Search

With Obsidian Sync (membership), vault syncs to phone automatically.
Phone → Obsidian app → see quest journals, dungeon maps, session summaries live.

### CLAUDE.md in the vault root
Keep under 100 lines. Documents:
- Vault structure and naming conventions
- What Ergo is allowed to write vs read-only areas
- Privacy rules (no personal vault, no credentials)
- How dungeon states work

---

## 8. Ergo — Missing Wiring (Priority Order)

These are the gaps between what's built and what needs connecting:

### 8.1 Daemon → Orchestrator (Highest Priority)
The daemon monitors windows but the orchestrator never sees it.
Fix: daemon HTTP posts to `POST /events` on state changes.
```rust
// In main.rs after window change detected:
// HTTP POST to http://127.0.0.1:8765/events
// Payload: window title, process, class, workspace, duration
```
This unlocks: YouTube commentary, stuck detection, context-aware interventions.

### 8.2 Daemon writes to v2 events table
Currently writes to legacy `activity_log`. Should write normalized events to `events` table.
The `event_emitter.rs` is built for this — just needs wiring into `main.rs`.

### 8.3 Party agents implement process_step
`base_agent.py` has the abstract method. Need concrete implementations per role.
agent-swarm replaces most of this — adopt its worker pattern.

### 8.4 Obsidian MCP connection
Install plugin, configure MCP endpoint, create Ergo vault with CLAUDE.md.
Healer agent writes quest journals. Support agent reads knowledge dungeons.

### 8.5 Remote access (phone)
Orchestrator binds to 127.0.0.1 only. Tailscale + bind to 0.0.0.0 with auth.
Obsidian Sync handles the knowledge layer automatically once vault is set up.

---

## 9. Tech Stack Summary

| Layer | Technology | Status |
|---|---|---|
| System monitoring | Rust daemon + hyprctl (Hyprland native) | Fixed, working |
| Orchestrator | Python FastAPI :8765 | Working |
| Model routing | Gemini Flash (chat) + Claude Opus (code) | Working |
| Memory | SQLite v1 (active) + v2 schema (empty) | Partial |
| Neovim plugin | Lua, async, floating windows | Working |
| Agent engine | agent-swarm + crewAI | To integrate |
| Quest world | PhaserJS + zones.json + dialogue_engine | Built, not rendered |
| Knowledge layer | Obsidian MCP + dedicated Ergo vault | To set up |
| Phone access | Obsidian Sync (membership) | Ready once vault exists |
| NixOS deploy | Nix flake, sha update workflow | Working but slow |

---

## 10. Next Steps (Ordered)

1. **Wire daemon → orchestrator** — HTTP post events on window change
2. **Create Ergo Obsidian vault** — `~/Obsidian/Ergo/`, CLAUDE.md, install MCP plugin
3. **Adopt agent-swarm as engine** — replace hand-rolled `claude_agent.py`/`party.py`
4. **Implement dungeon zone triggers** — Obsidian open/close events → zone transitions
5. **Horizontal timeline UI** — sprite scroll view in web UI
6. **Tailscale remote access** — expose orchestrator beyond localhost

---

## 11. Design Principles

- **The world is a projection of state** — visualization reacts, doesn't simulate independently
- **Two modes, one metaphor** — Active quest (hero's journey) + Passive exploration (world map dungeons)
- **Ergo is the DM** — orchestrates, tracks state, provides context. Agents are the players.
- **Obsidian Sync = the phone bridge** — no custom mobile app needed, vault syncs everywhere
- **Separate vaults** — personal life and project knowledge never mix
- **agent-swarm as engine** — don't hand-roll what's already production-tested
- **Personality at synthesis** — Ergo speaks with opinion when aggregating agent results, not just relay

---

*Last updated: 2026-04-14*
*Session: architecture design + Obsidian integration planning*
