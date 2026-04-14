# Ergo Work Mode Architecture

**Date:** 2026-03-25
**Status:** Design Phase
**Based on:** `ergo_work_mode_architecture.txt`

---

## Executive Summary

Ergo Work Mode transforms Ergo from a context-aware model router into a **local-first multi-agent work system** with:

- Supervisor-driven subagent workflow
- Persistent structured memory + Obsidian knowledge layer
- Layered personality system (output shaping only)
- Strong NixOS integration
- Role-based agents with defined permissions

**Core Positioning:**

> "A local-first NixOS-native work supervisor with layered memory, role-based subagents, and a curated personality system."

---

## Architecture Shift

### Current Ergo
```
chat → context assembly → choose best model → answer
```

### Target Ergo Work Mode
```
goal → task state machine → supervisor → role agents →
tool execution → review → memory writeback → curated summaries
```

---

## Six-Layer System

### A. Capture Layer
- Rust daemon
- Neovim integration
- Shell / git / build / diagnostics / browser / terminal context

### B. Memory Layer
- **SQLite/Postgres** - Structured truth (source of truth)
- **File storage** - Large artifacts
- **Obsidian vault** - Curated readable memory
- **Embeddings** - Optional, later

### C. Supervisor Layer
- Work mode controller
- Mission state machine
- Subagent planner/dispatcher
- Budget / permission / iteration control

### D. Agent Layer
Role-based subagents:
- **Planner** - Task decomposition
- **Mage (Architect)** - Deep reasoning, system design
- **Rogue (Coder)** - Code execution, file edits
- **Tank (Verifier)** - Constraint checking, testing
- **Support (Retriever)** - Memory gathering, context assembly
- **Healer (Summarizer)** - Session compression, recovery

### E. Personality Layer
- Stable persona files
- Mode overlays (chat / work / code review / quiet / mission)
- Coding-style overlays
- **Output shaping only** - does not corrupt reasoning

### F. Interface Layer
- Neovim commands
- Terminal chat
- Localhost web UI
- Optional storyboard / party UI

---

## Work Mode Activation

### Detection
User says: *"let's get a job done"* or similar activation phrase

### Flow
1. Detect mode activation phrase
2. Create mission object
3. Identify task type
4. Assemble relevant context
5. Decide: single-agent vs multi-agent execution
6. Create task graph
7. Assign role agents
8. Enforce permissions and cost limits
9. Stream progress to localhost UI
10. Write outputs and learning back into memory
11. Generate readable mission summary in Obsidian

### Execution Policy

**Normal Chat Mode:**
- One model, one response, lightweight memory use

**Deliberation Mode:**
- Draft → Critique → Synthesize
- Good for: code review, architecture, tricky debugging

**Work Mode:**
- Supervisor + selected role agents + tool access + progress tracking
- Used for multi-step jobs

---

## Mission State Machine

### States
```
created → scoping → decomposed → waiting_for_approval →
running → review → completed
           ↓
       blocked / awaiting_input / failed → archived
```

### Mission Object
```python
{
    "mission_id": UUID,
    "title": str,
    "user_goal": str,
    "task_type": str,
    "project_id": str,
    "priority": int,
    "active_mode": str,
    "budget_limit": float,
    "token_limit": int,
    "max_iterations": int,
    "allowed_tools": list[str],
    "selected_roles": list[str],
    "acceptance_criteria": str,
    "current_state": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Step Object
```python
{
    "step_id": UUID,
    "mission_id": UUID,
    "role": str,
    "objective": str,
    "input_context": dict,
    "output_summary": str,
    "status": str,
    "started_at": datetime,
    "completed_at": datetime,
    "tool_calls": list[dict],
    "cost_estimate": float,
    "review_status": str
}
```

---

## Role-Based Subagents

### 1. Planner
- **Responsibility:** Breaks goal into tasks, identifies missing context, chooses execution sequence
- **Permissions:** Read memory, read repo tree
- **No:** File editing, shell execution
- **Model:** Gemini Flash (cheap planning)

### 2. Mage (Architect)
- **Responsibility:** Deep reasoning, system design, tradeoff analysis, refactor direction
- **Permissions:** Read code, suggest edits
- **No:** Direct shell execution by default
- **Model:** Claude Sonnet/Opus (strongest reasoning)

### 3. Rogue (Coder / Executor)
- **Responsibility:** Writes code, edits files, generates patches
- **Permissions:** Read/write files (scoped), limited shell commands
- **No:** Unrestricted shell/network access
- **Model:** Claude (code-capable)

### 4. Tank (Verifier / Guard)
- **Responsibility:** Checks constraints, tests assumptions, catches violations, ensures acceptance criteria met
- **Permissions:** Run tests, inspect diffs
- **No:** Rewriting code without instruction
- **Model:** Reliable verifier (same family as Mage or strict checker)

### 5. Support (Retriever / Memory Keeper)
- **Responsibility:** Gathers repo context, fetches prior knowledge, assembles memory packets, updates notes
- **Permissions:** Read vault, write summaries
- **No:** Shell access
- **Model:** Cheap model or rules + retrieval pipeline

### 6. Healer (Summarizer / Recovery)
- **Responsibility:** Compresses large sessions, writes post-run summaries, suggests recovery when mission goes off track
- **Permissions:** Read mission state, write summaries
- **No:** Code execution
- **Model:** Cheap summarization model

### Important
**Subagents do not freely debate forever. The supervisor decides when each one is invoked.**

---

## Memory Architecture

### Four Categories

#### A. Episodic Memory
**What happened**
- Session logs
- Missions
- Tool runs
- Debugging trails
- Errors encountered
- Outcomes

#### B. Semantic Memory
**What is generally true**
- User preferences
- Repo facts
- Project decisions
- Stable workflows
- Recurring problems
- Coding conventions

#### C. Procedural Memory
**How Ergo should behave**
- When to interrupt
- How to structure answers
- Preferred review strictness
- Rules for work mode activation
- Permission boundaries

#### D. Personality Memory
**How Ergo presents itself**
- Tone
- Voice constraints
- Mode-specific speech tendencies
- Intimidation, softness, explanation, brevity, sass levels

### Storage Strategy

**Source of Truth:** SQLite or Postgres

**Readable Knowledge Layer:** Obsidian vault

**What goes into Obsidian:**
- Curated summaries
- Personality files
- Project memory summaries
- Working notes
- Mission logs
- Coding style profiles
- Retrospectives

**What stays in DB/runtime storage:**
- Raw events
- Normalized facts
- Mission state
- Tool execution logs
- Confidence scores
- Retrieval metadata
- Indexes

---

## Directory Structure

```
~/ergo/
├── config/
│   ├── ergo.toml
│   ├── routes.toml
│   └── permissions.toml
│
├── runtime/
│   ├── activity.db
│   ├── missions.db
│   ├── logs/
│   ├── cache/
│   └── artifacts/
│
├── vault/                    # Obsidian vault
│   ├── personality/
│   │   ├── core_persona.md
│   │   ├── quiet_mode.md
│   │   ├── standard_mode.md
│   │   ├── work_mode.md
│   │   ├── code_review_mode.md
│   │   └── mission_mode.md
│   ├── general/
│   │   ├── user_profile.md
│   │   ├── preferences.md
│   │   └── communication_preferences.md
│   ├── procedures/
│   │   ├── intervention_policy.md
│   │   ├── review_policy.md
│   │   └── mission_activation_rules.md
│   ├── coding/
│   │   ├── style_profile.md
│   │   ├── language_profiles/
│   │   │   ├── python.md
│   │   │   ├── rust.md
│   │   │   ├── typescript.md
│   │   │   ├── nix.md
│   │   │   └── lua.md
│   │   ├── review_tastes.md
│   │   └── anti_patterns.md
│   ├── projects/
│   │   └── ergo/
│   │       ├── architecture.md
│   │       ├── decisions.md
│   │       └── roadmap.md
│   ├── sessions/
│   │   └── 2026-03-25.md
│   └── missions/
│       ├── mission-0001.md
│       └── mission-0002.md
│
├── models/
│   ├── prompts/
│   │   ├── supervisor.md
│   │   ├── planner.md
│   │   ├── mage.md
│   │   ├── rogue.md
│   │   ├── tank.md
│   │   ├── support.md
│   │   ├── healer.md
│   │   ├── normal_chat.md
│   │   ├── deliberation.md
│   │   └── code_review.md
│   ├── policies/
│   │   ├── mission_state_machine.toml
│   │   ├── routing_policy.toml
│   │   ├── permissions_policy.toml
│   │   ├── memory_writeback_policy.toml
│   │   ├── intervention_policy.toml
│   │   └── coding_style_learning.toml
│   └── role_templates/
│       ├── planner.md
│       ├── mage.md
│       ├── rogue.md
│       ├── tank.md
│       ├── support.md
│       └── healer.md
│
└── ui/
    └── exports/
```

---

## Personality System

### Layered Personality Stack

**Layer 1: Core Persona**
- Stable identity
- Overall tone
- Boundaries
- Default assistant behavior

**Layer 2: Mode Overlay**
- Chat mode
- Work mode
- Code review mode
- Quiet mode
- Mission mode

**Layer 3: Situational Output Style**
- Concise
- Expanded
- Blunt
- Mentoring
- Severe
- Calm

**Layer 4: Coding Expression Overlay**
- How comments are written
- How suggestions are phrased
- Strictness in review
- Style preferences in generated code

### Key Rule
**Personality shapes output and judgement framing, not factual reasoning.**

### Personality in Code Work

#### A. Review Tone
- More severe about sloppy code
- More direct about bad abstractions
- More assertive on anti-patterns

#### B. Suggestion Preference
- Prefers explicitness over magic
- Prefers maintainable structure over clever hacks
- Prefers naming clarity over shortness
- Prefers strong comments only when useful

#### C. Code Generation Style
- Favors readability
- Favors consistent spacing and naming
- Prefers clear error handling
- Prefers fewer but meaningful abstractions

### Separation
- **Outward explanation:** Can carry personality
- **Code artifacts:** Obey project style guides first
- **Personal taste:** Applies only where project doesn't decide

---

## Coding Style Memory

### Learned From
- Existing repositories
- Accepted vs rejected suggestions
- Manual edits after generated code
- Code review preferences
- Repeated patterns in naming and structure

### Stored as Structured Preferences

```python
style_profile = {
    "prefer_explicit_types": True,
    "prefer_small_functions": True,
    "prefer_guard_clauses": True,
    "preferred_comment_density": "low",
    "prefer_functional_style": False,
    "prefer_descriptive_names": "high",
    "tolerate_magic_numbers": "low",
    "test_strictness": "medium",
    "refactor_aggressiveness": "medium"
}
```

### Per-Language Profiles
- `python_style_profile`
- `rust_style_profile`
- `typescript_style_profile`
- `nix_style_profile`
- `lua_style_profile`

### Readable Mirror
Maintain markdown representation in Obsidian vault under `coding/language_profiles/`

---

## Database Schema

### missions
```sql
CREATE TABLE missions (
    mission_id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    goal TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    project_id TEXT,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    budget_limit REAL,
    total_cost REAL DEFAULT 0,
    token_limit INTEGER,
    max_iterations INTEGER,
    allowed_tools TEXT, -- JSON array
    selected_roles TEXT, -- JSON array
    acceptance_criteria TEXT
);
```

### mission_steps
```sql
CREATE TABLE mission_steps (
    step_id UUID PRIMARY KEY,
    mission_id UUID NOT NULL REFERENCES missions(mission_id),
    role_name TEXT NOT NULL,
    objective TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    input_context TEXT, -- JSON
    output_summary TEXT,
    tool_calls TEXT, -- JSON array
    cost_estimate REAL,
    review_status TEXT
);
```

### memories
```sql
CREATE TABLE memories (
    memory_id UUID PRIMARY KEY,
    memory_type TEXT NOT NULL, -- episodic, semantic, procedural, personality
    scope TEXT NOT NULL, -- user, project, session
    project_id TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### coding_style_preferences
```sql
CREATE TABLE coding_style_preferences (
    pref_id UUID PRIMARY KEY,
    language TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    evidence_count INTEGER DEFAULT 1,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(language, preference_key)
);
```

### personality_profiles
```sql
CREATE TABLE personality_profiles (
    profile_id UUID PRIMARY KEY,
    mode_name TEXT NOT NULL UNIQUE,
    prompt_fragment TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE
);
```

### mission_events
```sql
CREATE TABLE mission_events (
    event_id UUID PRIMARY KEY,
    mission_id UUID REFERENCES missions(mission_id),
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
```

### vault_exports
```sql
CREATE TABLE vault_exports (
    export_id UUID PRIMARY KEY,
    mission_id UUID REFERENCES missions(mission_id),
    path TEXT NOT NULL,
    export_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

---

## Service Architecture

### Service 1: ergo-daemon (Rust)
**Purpose:**
- Collect activity
- Observe processes/windows/editor state
- Emit normalized events
- Privacy filtering

### Service 2: ergo-core (Python)
**Purpose:**
- Mission state machine
- Supervisor logic
- Memory management
- Model routing
- Subagent invocation
- Writeback

### Service 3: ergo-ui (Web)
**Purpose:**
- Localhost dashboard
- Mission timeline
- Role status cards
- Memory browsing
- Intervention display

### Service 4: ergo-nvim (Lua plugin)
**Purpose:**
- Editor interface
- Context push
- Command surface
- Local code review hooks

### Service 5: ergo-voice (Optional)
**Purpose:**
- Push-to-talk voice interaction
- Disabled by default

---

## NixOS Integration

### A. Declarative Setup
- `flake.nix` controls full dev and runtime environment
- Packages for daemon, orchestrator, UI, helper tools
- Shell and service reproducibility

### B. Home-Manager / NixOS Module Integration
- Optional NixOS module for enabling Ergo services
- Optional Home Manager module for user config
- Declarative Neovim integration
- Declarative systemd user services

### C. Native Tool Awareness
- Nix flake structure awareness
- `nix develop / nix run / rebuild` context understanding
- Shell output parsing for Nix build failures
- Repo-specific Nix hints

### D. Local Service Mesh
- Daemon, orchestrator, and UI run through local services
- Predictable paths under `~/.local/share/ergo` or `~/ergo`
- Low-friction startup and restart

**Result:** NixOS becomes a first-class habitat, not just "supported"

---

## Build Phases

### Phase 1: Foundation
- Formal memory service
- Structured coding style memory
- Personality layering
- Obsidian export bridge

### Phase 2: Supervision
- Mission state machine
- Supervisor layer
- Deliberation mode (draft → critique → synthesize)

### Phase 3: Multi-Agent
- Role-based subagents
- Localhost mission dashboard
- Tool permissions and budget enforcement

### Phase 4: Polish
- Full Work Mode UX polish
- Party/storyboard presentation
- Optional voice and deeper Nix integration

---

## Permissions and Safety

### Per-Role Permissions

**Planner:**
- ✅ Read memory, read repo tree
- ❌ No file edits, no shell

**Mage:**
- ✅ Read code, suggest edits
- ❌ No direct file writes unless escalated

**Rogue:**
- ✅ Read/write file scope limited to mission
- ✅ Shell access limited to allowlist
- ❌ No network by default unless enabled

**Tank:**
- ✅ Run tests, inspect diffs
- ❌ No editing unless explicitly allowed

**Support:**
- ✅ Read vault, write summaries
- ❌ No shell

### Global Mission Controls
- Max cost
- Max iterations per role
- Human approval on destructive actions
- Pause / kill switch

---

## Memory Writeback Pipeline

### After Each Session

**Runtime Writeback:**
- Structured DB entries
- Updated style profile counters
- Mission outcome fields
- New recurring issue links
- Preference updates

**Vault Writeback:**
- Concise session summary
- Project note updates
- Mission note
- Coding-style evolution notes (if relevant)

**Writeback Rules:**
- Not every tiny event becomes a note
- Only meaningful, compressed summaries go to Obsidian
- Raw noise stays in DB/log layer

---

## Key Architectural Principles

### ✅ DO

- **Ergo = Supervisor** - Ergo controls the mission
- **Memory DB = Truth** - SQLite/Postgres is source of truth
- **Obsidian = Curated Mind Palace** - Human-readable knowledge
- **Personality = Layered Output System** - Shapes presentation, not facts
- **Coding Style = Structured Learned Preferences** - Not prose dumps
- **NixOS = Native Habitat** - First-class integration
- **Subagents = Role Workers** - Under supervisor control

### ❌ DON'T

- **Claude = Hidden Boss** - Models are workers, not owners
- **Obsidian = Entire Database** - Only for curated knowledge
- **Personality = Giant Emotional Blob** - Must be layered and scoped
- **Agents = Free-Roaming Improv Troupe** - Supervisor controls invocation

---

## Summary

**Ergo Work Mode should be a NixOS-native supervisor system that uses structured memory, curated Obsidian knowledge, layered personality, and role-based subagents to execute real work while keeping the user in control.**

---

**Status:** Ready for Phase 1 implementation
**Next Steps:** See `docs/reference/WORK_MODE_IMPLEMENTATION.md` (to be created)
