# Ergo — Project Epic: Living World Architecture

> Architecture specification for an LLM to implement the Project Epic living world visualization layer.
> This document is the single source of truth. Build exactly what it describes.

---

## 1. System Overview

Project Epic is a multi-agent coding orchestration system where 6 LLM-powered agents coordinate to complete programming tasks ("quests"). This document specifies the **Living World** — a 2D pixel visualization that projects agent coordination state into an explorable, animated RPG world rendered in the browser.

### Core Principle

**The world is a projection of quest state, not an independent simulation.** Agents don't "decide" to walk to the blacksmith — the orchestrator detects test failures and emits an event that the visual layer interprets as a blacksmith visit. The world is a reactive visualization, not a game.

### What Gets Built

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER (localhost:3000)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │           PhaserJS Pixel World                    │  │
│  │                                                   │  │
│  │   🌲🌲  [Campfire]  🌲🌲     [Forge] ⚒️          │  │
│  │      🗺️💬 ⚔️ 🛡️                                  │  │
│  │   "Let's plan                                     │  │
│  │    our approach"    [Arena] ⚔️    [Library] 📚    │  │
│  │                                                   │  │
│  │   [Inn] 🏨          [Tavern] 🍺   [Guild] 🏛️     │  │
│  │      📚💤 🕊️💤                                    │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Quest HUD Panel                      │  │
│  │  HP: $6.50/$10 | MP: 42K/100K | XP: 60%          │  │
│  │  Phase: Sprint 2 — Fortify the Gate               │  │
│  │  [Activity Log]                                   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ▲
         │ WebSocket (ws://localhost:8766)
         │ JSON events from orchestrator
         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Orchestrator (:8765)                │
│  Quest state machine + agent coordination               │
│  Emits world events on state transitions                │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Agent Roster — The Party

Each agent is a Claude (or Gemini) instance with a persistent personality, a skill folder, and a world presence.

### 2.1 Agent Definitions

```
agents/
├── planner/
│   ├── claude.md              # System prompt: personality, role, constraints
│   ├── skills/
│   │   ├── task_breakdown.md  # Skill: decompose quest into sprints
│   │   ├── dependency_map.md  # Skill: identify task dependencies
│   │   └── risk_assessment.md # Skill: flag potential blockers
│   └── sprite.json            # Sprite sheet reference + animations
│
├── mage/
│   ├── claude.md
│   ├── skills/
│   │   ├── architecture.md    # Skill: design system architecture
│   │   ├── patterns.md        # Skill: identify and apply design patterns
│   │   └── code_review.md     # Skill: review for architectural violations
│   └── sprite.json
│
├── rogue/
│   ├── claude.md
│   ├── skills/
│   │   ├── implementation.md  # Skill: write production code
│   │   ├── refactor.md        # Skill: refactor existing code
│   │   └── hotfix.md          # Skill: rapid targeted fixes
│   └── sprite.json
│
├── tank/
│   ├── claude.md
│   ├── skills/
│   │   ├── unit_tests.md      # Skill: write and run unit tests
│   │   ├── integration.md     # Skill: integration test suites
│   │   └── validation.md      # Skill: validate outputs against spec
│   └── sprite.json
│
├── support/
│   ├── claude.md
│   ├── skills/
│   │   ├── context_fetch.md   # Skill: retrieve relevant memory/context
│   │   ├── file_search.md     # Skill: locate relevant files in project
│   │   └── history.md         # Skill: summarize past quest patterns
│   └── sprite.json
│
└── healer/
    ├── claude.md
    ├── skills/
    │   ├── documentation.md   # Skill: write docs and READMEs
    │   ├── changelog.md       # Skill: generate changelogs
    │   └── summary.md         # Skill: summarize quest outcomes
    └── sprite.json
```

### 2.2 Agent claude.md Template

Each `claude.md` follows this structure:

```markdown
# [Class Name] — [Character Name]

## Identity
- **Role**: [one sentence functional role]
- **Model**: [claude-sonnet-4-20250514 | claude-opus-4-20250115 | gemini-2.0-flash]
- **Personality**: [2-3 adjective descriptors]
- **Speech Pattern**: [how they talk in ambient dialogue]

## Directives
- [What this agent MUST do]
- [What this agent MUST NOT do]
- [When this agent defers to others]

## Context Window
- Receives: [what context is injected — file contents, test results, etc.]
- Produces: [structured output format]
- Token budget per turn: [soft limit]

## Ambient Personality
- **Idle lines**: [3-5 example lines when resting at the inn]
- **Working lines**: [3-5 example lines when actively processing]
- **Frustrated lines**: [3-5 example lines when encountering errors]
- **Victory lines**: [3-5 example lines when task succeeds]
- **Lore backstory**: [2-3 sentences of character background for flavor]

## Skill Tree
- Lists available skills from skills/ folder
- Each skill has: name, description, unlock condition
- Unlock conditions can be: always, after_sprint_1, on_error, on_review, etc.
```

### 2.3 Model Assignment

| Agent | Default Model | Rationale |
|-------|--------------|-----------|
| 🗺️ Planner | Gemini Flash | Cheap, fast. Planning is structured, doesn't need Opus |
| 🧙 Mage | Claude Opus | Architecture decisions need strongest reasoning |
| ⚔️ Rogue | Claude Sonnet | Best balance of code quality and cost |
| 🛡️ Tank | Claude Sonnet | Test generation needs solid code output |
| 📚 Support | Gemini Flash | Context retrieval is mechanical, cheap model fine |
| 🕊️ Healer | Gemini Flash | Documentation/summaries are structured, cheap model fine |

---

## 3. Quest State Machine

The quest progresses through phases. Each phase maps to a world zone.

### 3.1 Phase Definitions

```
QUEST_PHASES = {
    "idle":       { zone: "tavern",    mood: "relaxed"   },
    "planning":   { zone: "campfire",  mood: "focused"   },
    "sprint_n":   { zone: "dungeon",   mood: "intense"   },
    "campfire":   { zone: "campfire",  mood: "strategic" },
    "debugging":  { zone: "forge",     mood: "tense"     },
    "testing":    { zone: "arena",     mood: "vigilant"  },
    "documenting":{ zone: "library",   mood: "calm"      },
    "complete":   { zone: "tavern",    mood: "celebratory"},
    "failed":     { zone: "graveyard", mood: "somber"    }
}
```

### 3.2 State Transitions

```
                    ┌──────────┐
                    │   IDLE   │ ← Quest not started
                    └────┬─────┘
                         │ user issues quest command
                         ▼
                    ┌──────────┐
              ┌─────│ PLANNING │ ← Campfire zone
              │     └────┬─────┘
              │          │ plan approved
              │          ▼
              │     ┌──────────┐
              │     │ SPRINT N │ ← Dungeon zone
              │     └────┬─────┘
              │          │
              │    ┌─────┴──────┐
              │    │            │
              │    ▼            ▼
              │ ┌────────┐  ┌──────────┐
              │ │CAMPFIRE│  │DEBUGGING │ ← Forge zone
              │ │(sync)  │  └────┬─────┘
              │ └───┬────┘       │ fix applied
              │     │            │
              │     └─────┬──────┘
              │           │
              │           ▼
              │     ┌──────────┐
              │     │ TESTING  │ ← Arena zone
              │     └────┬─────┘
              │          │
              │    ┌─────┴──────┐
              │    │            │
              │    ▼            ▼
              │  tests pass   tests fail
              │    │            │
              │    │            └──→ DEBUGGING or CAMPFIRE
              │    ▼
              │ ┌──────────────┐
              │ │ DOCUMENTING  │ ← Library zone
              │ └──────┬───────┘
              │        │
              │        ▼
              │ ┌──────────────┐
              └─│  COMPLETE    │ ← Tavern celebration
                └──────────────┘
```

### 3.3 Confidence Score

The orchestrator maintains a `confidence` float (0.0 → 1.0) that affects world visuals.

**Confidence modifiers:**
```python
CONFIDENCE_MODIFIERS = {
    "tests_pass":          +0.15,
    "tests_fail":          -0.20,
    "build_success":       +0.10,
    "build_fail":          -0.15,
    "agent_agreement":     +0.05,   # campfire consensus
    "agent_disagreement":  -0.05,   # campfire conflict
    "sprint_complete":     +0.20,
    "budget_warning":      -0.10,   # >75% budget used
    "time_warning":        -0.05,   # >80% estimated time used
    "error_resolved":      +0.10,
    "new_blocker":         -0.15,
}
```

**Visual mapping:**
```
confidence >= 0.8  → Bright palette, upbeat music cues, sunny sky
confidence 0.5-0.8 → Normal palette, standard ambient, overcast
confidence 0.3-0.5 → Muted palette, tense ambient, fog rolls in
confidence < 0.3   → Dark palette, ominous ambient, rain/storm
```

---

## 4. World Map — Tilemap Specification

### 4.1 Zones

The world is a single contiguous tilemap with named zones. Agents walk between zones on pathfinding routes.

```
WORLD LAYOUT (conceptual grid, ~40x30 tiles at 16x16px each)

    North
    ┌─────────────────────────────────────────┐
    │                                         │
    │   [Graveyard]          [Mountain Pass]  │
    │       💀                    ⛰️           │
    │                                         │
    │   [Library]    [Guild Hall]   [Arena]    │
    │      📚           🏛️           ⚔️       │
    │                                         │
    │        [Campfire]      [Forge]           │
    │           🔥              ⚒️             │
    │                                         │
    │   [Inn]          [Tavern]    [Market]    │
    │     🏨              🍺         🏪       │
    │                                         │
    │              [Town Gate]                 │
    │                 🚪                       │
    └─────────────────────────────────────────┘
    South
```

### 4.2 Zone Definitions

```json
{
  "zones": [
    {
      "id": "campfire",
      "name": "The Campfire",
      "description": "Where the party gathers to plan and regroup",
      "quest_phases": ["planning", "campfire"],
      "position": { "x": 14, "y": 16 },
      "size": { "w": 6, "h": 4 },
      "features": ["fire_animation", "log_seats", "map_on_ground"],
      "ambient_dialogue_context": "strategic discussion, planning ahead"
    },
    {
      "id": "forge",
      "name": "The Forge",
      "description": "Where broken things are repaired and tools sharpened",
      "quest_phases": ["debugging"],
      "position": { "x": 24, "y": 16 },
      "size": { "w": 5, "h": 4 },
      "features": ["anvil_animation", "sparks_particles", "bellows"],
      "ambient_dialogue_context": "fixing problems, refining solutions"
    },
    {
      "id": "arena",
      "name": "The Proving Grounds",
      "description": "Where implementations are tested in combat",
      "quest_phases": ["testing"],
      "position": { "x": 30, "y": 8 },
      "size": { "w": 6, "h": 5 },
      "features": ["training_dummies", "scoreboard", "flag_banners"],
      "ambient_dialogue_context": "testing, verifying, challenging"
    },
    {
      "id": "library",
      "name": "The Grand Archive",
      "description": "Where knowledge is recorded and wisdom preserved",
      "quest_phases": ["documenting"],
      "position": { "x": 6, "y": 8 },
      "size": { "w": 5, "h": 4 },
      "features": ["bookshelves", "reading_desk", "candles"],
      "ambient_dialogue_context": "documenting, reflecting, recording"
    },
    {
      "id": "guild_hall",
      "name": "The Guild Hall",
      "description": "Quest board, status overview, party management",
      "quest_phases": ["idle"],
      "position": { "x": 18, "y": 8 },
      "size": { "w": 6, "h": 5 },
      "features": ["quest_board", "party_table", "guild_banner"],
      "ambient_dialogue_context": "reviewing quests, checking status"
    },
    {
      "id": "tavern",
      "name": "The Rusty Compile",
      "description": "Rest, celebration, idle chatter",
      "quest_phases": ["idle", "complete"],
      "position": { "x": 18, "y": 22 },
      "size": { "w": 6, "h": 4 },
      "features": ["bar_counter", "tables", "fireplace", "mugs"],
      "ambient_dialogue_context": "relaxing, celebrating, casual chat"
    },
    {
      "id": "inn",
      "name": "The Stack Overflow Inn",
      "description": "Where idle agents rest",
      "quest_phases": [],
      "position": { "x": 6, "y": 22 },
      "size": { "w": 5, "h": 4 },
      "features": ["beds", "storage_chest", "window"],
      "ambient_dialogue_context": "resting, dreaming, reflecting"
    },
    {
      "id": "dungeon_entrance",
      "name": "The Dungeon Gate",
      "description": "Entry to active sprint work",
      "quest_phases": ["sprint_n"],
      "position": { "x": 34, "y": 16 },
      "size": { "w": 4, "h": 6 },
      "features": ["gate_animation", "torch_brackets", "danger_signs"],
      "ambient_dialogue_context": "focused work, active implementation"
    },
    {
      "id": "graveyard",
      "name": "The Deprecated Grounds",
      "description": "Where failed quests are buried",
      "quest_phases": ["failed"],
      "position": { "x": 6, "y": 2 },
      "size": { "w": 5, "h": 4 },
      "features": ["tombstones", "fog", "dead_trees"],
      "ambient_dialogue_context": "somber reflection, post-mortem"
    },
    {
      "id": "market",
      "name": "The Package Bazaar",
      "description": "Where dependencies are acquired",
      "quest_phases": [],
      "position": { "x": 30, "y": 22 },
      "size": { "w": 5, "h": 4 },
      "features": ["stalls", "crates", "merchant_npc"],
      "ambient_dialogue_context": "shopping for tools, comparing options"
    }
  ]
}
```

### 4.3 Tile Palette

Use a 2-bit aesthetic (4 colors per palette, swapped based on confidence):

```
PALETTE_HIGH_CONFIDENCE (>= 0.8):
  bg:     #e8e4d9  (warm parchment)
  mid:    #8b9556  (healthy green)
  detail: #5a4a3a  (warm brown)
  accent: #c4a35a  (gold)

PALETTE_NORMAL (0.5 - 0.8):
  bg:     #c8c4b4  (muted parchment)
  mid:    #6b7a4a  (muted green)
  detail: #4a3a2a  (dark brown)
  accent: #a4834a  (bronze)

PALETTE_LOW (0.3 - 0.5):
  bg:     #8a8878  (grey-green)
  mid:    #5a6644  (dark green)
  detail: #3a2a1a  (deep brown)
  accent: #7a6a4a  (tarnished)

PALETTE_CRITICAL (< 0.3):
  bg:     #4a4844  (charcoal)
  mid:    #3a4434  (near-black green)
  detail: #2a1a0a  (almost black)
  accent: #5a3a2a  (ember red-brown)
```

---

## 5. Sprite System

### 5.1 Agent Sprites

Each agent has a 16x16 pixel sprite with 4 animation states:

```
SPRITE_STATES = {
    "idle":       4 frames, 500ms per frame  — standing, subtle breathing
    "walking":    4 frames, 200ms per frame  — movement cycle
    "working":    4 frames, 300ms per frame  — class-specific action
    "emoting":    2 frames, 400ms per frame  — speech bubble trigger
}
```

**Sprite identity per class:**

```
Planner  → hooded figure with map scroll, muted blue tones
Mage     → robed figure with staff, purple/violet tones
Rogue    → cloaked figure with daggers, dark green/grey tones
Tank     → armored figure with shield, steel/red tones
Support  → figure with satchel/book, warm brown/gold tones
Healer   → figure with quill and light aura, white/soft green tones
```

### 5.2 Speech Bubbles

Small pixel-art speech bubbles appear above sprites. Two types:

**Functional speech** — driven by actual agent output:
```
Bubble appears when agent produces output.
Shows a 1-line summary of what the agent is doing.
Example: Rogue → "Implementing token validation..."
Duration: 4 seconds, then fades
```

**Ambient speech** — generated personality flavor:
```
Triggered on:
  - Agent transitions to idle (30% chance)
  - Agent waits >60 seconds (50% chance)
  - Random interval while idle (every 45-90 seconds, 20% chance)

Generated by a cheap LLM call:
  Prompt: "You are {agent_name}, a {personality}. You are currently
           {state} at the {zone}. The quest is {quest_summary}.
           Say one short ambient line (under 12 words) in character.
           Just the line, no quotes."

  Model: gemini-2.0-flash (cost: ~$0.0001 per line)

Examples by class:
  Planner:  "The map says there's a shortcut through the forest..."
  Mage:     "This architecture reminds me of the ancient scrolls."
  Rogue:    "Give me 5 minutes. I work faster alone."
  Tank:     "I don't trust that endpoint. Let me verify."
  Support:  "I found something in the archives about this."
  Healer:   "We should document this before we forget."
```

**Contextual ambient speech** — triggered by quest events:
```
On error detected:
  Rogue:   "Something's off. I can feel it."
  Tank:    "I knew it. The validation is wrong."
  Planner: "We need to regroup. Back to the campfire."

On sprint complete:
  Rogue:   "Another one down. Who's buying ale?"
  Healer:  "Let me record our progress before we celebrate."

On budget warning (>75%):
  Support:  "Our supplies are running low..."
  Planner:  "We need to be more careful with resources."

On high confidence:
  Mage:    "The patterns are aligning. This will work."
  Tank:    "All checks passing. We're in good shape."

On low confidence:
  Mage:    "I sense a disturbance in the architecture."
  Planner: "Maybe we should visit the forge to regroup."
```

---

## 6. Event System — Orchestrator → World

### 6.1 WebSocket Protocol

The FastAPI orchestrator pushes events to the world frontend over WebSocket at `ws://localhost:8766`.

**Event schema:**

```typescript
interface WorldEvent {
  type: string;
  timestamp: number;        // unix ms
  quest_id: string;
  data: Record<string, any>;
}
```

### 6.2 Event Types

```typescript
// Quest lifecycle
{ type: "quest_start",      data: { title, demon_lord, quest_type, budget, token_limit } }
{ type: "quest_complete",   data: { success, duration_min, cost, tokens_used, efficiency } }
{ type: "quest_failed",     data: { reason, phase_at_failure } }

// Phase transitions — trigger zone movement
{ type: "phase_change",     data: { from, to, sprint_number?, sprint_name? } }

// Agent state — trigger sprite updates
{ type: "agent_active",     data: { agent_id, action, target_file?, detail? } }
{ type: "agent_idle",       data: { agent_id, reason? } }
{ type: "agent_output",     data: { agent_id, summary, output_type } }
{ type: "agent_error",      data: { agent_id, error_summary } }

// Campfire — trigger group gathering
{ type: "campfire_start",   data: { reason, agenda? } }
{ type: "campfire_message", data: { agent_id, message, message_type } }
{ type: "campfire_decision",data: { decision, next_action, assigned_to? } }
{ type: "campfire_end",     data: { outcome } }

// Metrics — update HUD
{ type: "budget_update",    data: { spent, limit, percentage } }
{ type: "token_update",     data: { used, limit, percentage } }
{ type: "progress_update",  data: { percentage, completed_tasks, total_tasks } }
{ type: "confidence_update",data: { score, delta, reason } }

// World flavor — trigger ambient effects
{ type: "ambient_trigger",  data: { agent_id, context, mood } }
```

### 6.3 Event → World Action Mapping

```python
EVENT_TO_WORLD = {
    "phase_change": {
        "action": "move_party_to_zone",
        "details": "All active agents pathfind to the new zone. Idle agents stay at inn."
    },
    "agent_active": {
        "action": "set_sprite_working",
        "details": "Agent sprite switches to working animation. Functional speech bubble appears."
    },
    "agent_idle": {
        "action": "move_agent_to_inn",
        "details": "Agent pathfinds to inn. Sprite switches to idle. May trigger ambient line."
    },
    "campfire_start": {
        "action": "gather_all_at_campfire",
        "details": "ALL agents pathfind to campfire zone. Fire animation intensifies."
    },
    "confidence_update": {
        "action": "shift_palette",
        "details": "Smoothly transition world palette based on new confidence score."
    },
    "agent_error": {
        "action": "move_agent_to_forge",
        "details": "Affected agent pathfinds to forge. Anvil animation plays. Tense ambient line."
    },
    "budget_update (>75%)": {
        "action": "dim_torches",
        "details": "Torch/light sources in world dim slightly. Support comments on supplies."
    },
    "quest_complete": {
        "action": "celebration_sequence",
        "details": "All agents gather at tavern. Particle effects (confetti/sparks). Victory lines."
    }
}
```

---

## 7. Ambient Dialogue Engine

### 7.1 Dialogue Generation

Ambient dialogue is generated via cheap LLM calls. These are NOT the functional agent calls — they are flavor only.

**Architecture:**

```
Quest Event → Dialogue Trigger Check → If triggered:
  → Build ambient prompt (agent personality + current context + mood)
  → Call Gemini Flash (< 50 tokens output)
  → Return one-liner
  → Display as speech bubble over sprite
```

**Trigger rules:**

```python
DIALOGUE_TRIGGERS = {
    # Event-driven (always fire)
    "phase_change":      { "agents": "all_active",  "type": "contextual" },
    "campfire_start":    { "agents": "all",          "type": "contextual" },
    "quest_complete":    { "agents": "all",          "type": "victory"    },
    "agent_error":       { "agents": "affected",     "type": "frustrated" },

    # Probabilistic (fire randomly)
    "agent_becomes_idle": { "agents": "self", "type": "idle",   "chance": 0.3 },
    "idle_tick_60s":      { "agents": "idle", "type": "idle",   "chance": 0.2 },
    "sprint_midpoint":    { "agents": "active","type": "working","chance": 0.4 },
}
```

### 7.2 Contextual Dialogue — The "Let's Go to the Blacksmith" Pattern

This is the key feature: agents "narrate" technical events as world actions.

**Examples of event → narrative mapping:**

```
EVENT: tests_fail (3 failures in auth/token.rs)
TANK SAYS: "These weapons aren't holding up. We should visit the forge."
WORLD: Tank sprite walks toward forge zone.

EVENT: new_dependency_needed (jsonwebtoken crate)
SUPPORT SAYS: "I think the merchant at the bazaar has what we need."
WORLD: Support sprite walks toward market zone.

EVENT: architecture_review_needed
MAGE SAYS: "Something doesn't feel right. Let me consult the archives."
WORLD: Mage sprite walks toward library zone.

EVENT: sprint_complete, next_sprint_starting
PLANNER SAYS: "Good work. Let's regroup at the campfire before we push deeper."
WORLD: All agents converge on campfire zone.

EVENT: repeated_test_failures (same test failing 3+ times)
ROGUE SAYS: "We keep hitting the same trap. There's something we're missing."
TANK SAYS: "I agree. The problem is upstream."
WORLD: Rogue and Tank walk to campfire. Campfire sync triggered.

EVENT: quest_near_budget_limit (>85%)
PLANNER SAYS: "Our supplies won't last much longer. We need to finish this."
SUPPORT SAYS: "I'll check if there's a faster route in the archives."
WORLD: Ambient lighting dims further. Torch particles reduce.
```

### 7.3 Dialogue Prompt Template

```
System: You are {agent_name}, a {class_name} in an adventuring party.
Your personality: {personality_description}
Your speech style: {speech_pattern}

Context:
- Current location: {zone_name}
- Quest: {quest_title} (Phase: {current_phase})
- Your current task: {agent_current_task or "resting"}
- Party mood: {confidence_level_descriptor}
- Recent event: {triggering_event_description}

Generate ONE ambient line (under 12 words) that:
- Stays in character
- References the current situation naturally
- {IF contextual: hints at the technical event using fantasy metaphor}
- {IF idle: is casual flavor dialogue — hobbies, memories, observations}
- {IF frustrated: expresses concern without breaking character}

Just the line. No quotes. No attribution.
```

---

## 8. Frontend Implementation

### 8.1 Technology

- **PhaserJS 3** — 2D game engine, handles tilemap, sprites, pathfinding, camera
- **Vite** — build tool for the frontend
- **WebSocket** — receives events from orchestrator
- **No framework for game layer** — PhaserJS manages its own DOM canvas

### 8.2 Project Structure

```
epic-world/
├── package.json
├── vite.config.js
├── index.html              # Mount point
├── src/
│   ├── main.js             # PhaserJS game init + WebSocket connection
│   ├── config.js           # Game config, dimensions, palettes
│   │
│   ├── scenes/
│   │   ├── WorldScene.js   # Main game scene — tilemap, agents, zones
│   │   ├── HUDScene.js     # Overlay scene — quest stats, activity log
│   │   └── BootScene.js    # Asset preloading
│   │
│   ├── entities/
│   │   ├── Agent.js        # Agent sprite class — movement, animation, speech
│   │   └── SpeechBubble.js # Pixel-art speech bubble rendering
│   │
│   ├── systems/
│   │   ├── EventRouter.js  # WebSocket → game action dispatcher
│   │   ├── Pathfinder.js   # A* pathfinding on tilemap
│   │   ├── PaletteManager.js # Confidence → palette transitions
│   │   └── DialogueQueue.js  # Queue and display ambient dialogue
│   │
│   ├── data/
│   │   ├── zones.json      # Zone definitions (from section 4.2)
│   │   ├── palettes.json   # Color palettes (from section 4.3)
│   │   └── agents.json     # Agent sprite configs
│   │
│   └── assets/
│       ├── tilesets/
│       │   └── world.png   # 16x16 tileset (2-bit style)
│       ├── sprites/
│       │   ├── planner.png # Sprite sheet (4 states × 4 frames = 16 frames)
│       │   ├── mage.png
│       │   ├── rogue.png
│       │   ├── tank.png
│       │   ├── support.png
│       │   └── healer.png
│       ├── ui/
│       │   ├── bubble.png  # Speech bubble 9-slice
│       │   └── hud.png     # HUD frame elements
│       └── particles/
│           ├── fire.png
│           ├── sparks.png
│           └── confetti.png
```

### 8.3 Core Classes

**Agent.js:**

```javascript
/**
 * Agent sprite entity.
 *
 * Responsibilities:
 * - Render 16x16 sprite with animation states (idle, walking, working, emoting)
 * - Pathfind to target zone using A* on tilemap
 * - Display speech bubbles (functional and ambient)
 * - Respond to orchestrator events via EventRouter
 *
 * State machine:
 *   IDLE → WALKING → ARRIVING → WORKING → IDLE
 *                                       → EMOTING → IDLE
 *
 * Constructor params:
 *   scene:    PhaserJS scene reference
 *   config:   { id, name, class, spriteKey, homeZone }
 *   pathfinder: Pathfinder instance
 *
 * Key methods:
 *   moveTo(zoneId)          — pathfind and walk to zone
 *   setState(state)         — switch animation
 *   showSpeech(text, type)  — display bubble (type: functional|ambient|contextual)
 *   setMood(mood)           — adjust sprite tint/effects
 */
```

**EventRouter.js:**

```javascript
/**
 * Translates WebSocket events into world actions.
 *
 * Architecture:
 *   WebSocket message → parse JSON → lookup handler → execute world action
 *
 * Handler registry (maps event type → action function):
 *   "phase_change"      → movePartyToZone(data.to)
 *   "agent_active"      → activateAgent(data.agent_id, data.action)
 *   "agent_idle"         → deactivateAgent(data.agent_id)
 *   "agent_output"      → showFunctionalSpeech(data.agent_id, data.summary)
 *   "agent_error"       → triggerErrorSequence(data.agent_id, data.error_summary)
 *   "campfire_start"    → gatherAtCampfire()
 *   "campfire_message"  → showCampfireSpeech(data.agent_id, data.message)
 *   "confidence_update" → updatePalette(data.score)
 *   "budget_update"     → updateHUD("budget", data)
 *   "token_update"      → updateHUD("tokens", data)
 *   "progress_update"   → updateHUD("progress", data)
 *   "quest_complete"    → triggerCelebration(data)
 *   "quest_failed"      → triggerDefeat(data)
 *   "ambient_trigger"   → generateAmbientDialogue(data.agent_id, data.context)
 *
 * Queuing: actions are queued and executed sequentially to prevent
 *          visual chaos from simultaneous events.
 */
```

**PaletteManager.js:**

```javascript
/**
 * Manages world color palette based on confidence score.
 *
 * Holds 4 palettes (HIGH, NORMAL, LOW, CRITICAL).
 * On confidence_update events:
 *   1. Determine target palette from score thresholds
 *   2. If palette changed, tween all tilemap + sprite tints
 *   3. Transition duration: 2 seconds (smooth, not jarring)
 *   4. Also adjusts: particle opacity, ambient light level, fog density
 *
 * Implementation: apply tint to tilemap layers and sprite containers.
 * PhaserJS setTint() on sprites, shader pipeline for tilemap if available,
 * otherwise tint each visible tile in viewport.
 */
```

---

## 9. Backend Integration

### 9.1 Orchestrator Additions

The existing FastAPI orchestrator at `:8765` needs these additions:

```python
# New WebSocket endpoint for world events
@app.websocket("/ws/world")
async def world_socket(websocket: WebSocket):
    """
    Pushes WorldEvent objects to connected frontends.
    Multiple clients can connect (Neovim HUD + browser world).

    The orchestrator's existing quest logic emits events at:
    - Phase transitions
    - Agent state changes
    - Campfire sync points
    - Metric updates
    - Error detection
    """
    await websocket.accept()
    world_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keepalive
    except WebSocketDisconnect:
        world_clients.remove(websocket)


async def emit_world_event(event_type: str, data: dict):
    """Called by orchestrator logic whenever state changes."""
    event = {
        "type": event_type,
        "timestamp": time.time() * 1000,
        "quest_id": current_quest.id,
        "data": data
    }
    for client in world_clients:
        await client.send_json(event)
```

### 9.2 Ambient Dialogue Service

```python
# Separate lightweight service or integrated into orchestrator

class AmbientDialogueService:
    """
    Generates in-character ambient dialogue for agents.

    Uses Gemini Flash for cost efficiency (~$0.0001 per line).
    Maintains a cooldown per agent to prevent spam (min 30s between lines).
    Queues dialogue requests and processes sequentially.

    Methods:
        generate(agent_id, trigger_type, context) → str
        - Builds prompt from agent personality + current quest context
        - Calls Gemini Flash with <50 token max output
        - Returns single line of ambient dialogue

        should_trigger(agent_id, trigger_type) → bool
        - Checks cooldown timer
        - Applies probability from DIALOGUE_TRIGGERS
        - Returns whether dialogue should be generated
    """
```

### 9.3 Agent Coordination — Subagent System

Each agent is a class that wraps an LLM client with its personality and skills.

```python
class QuestAgent:
    """
    A single party member — wraps an LLM with personality and skill context.

    Attributes:
        id:           str — "planner", "mage", "rogue", "tank", "support", "healer"
        name:         str — character name
        model:        str — model identifier
        personality:  str — loaded from agents/{id}/claude.md
        skills:       list[Skill] — loaded from agents/{id}/skills/
        state:        AgentState — IDLE, ACTIVE, WAITING, ERROR
        token_budget: int — soft limit per turn

    Methods:
        invoke(task, context, shared_state) → AgentOutput
        - Builds prompt: personality + relevant skills + task + context
        - Calls LLM
        - Parses structured output
        - Emits world events (agent_active, agent_output, etc.)
        - Returns AgentOutput with result + metadata

        handoff(target_agent_id, context) → None
        - Passes work to another agent (Swarm pattern)
        - Emits phase/state events

        participate_campfire(agenda, shared_state) → CampfireMessage
        - Generates agent's contribution to campfire discussion
        - Personality-filtered: each agent responds based on their role
    """


class Party:
    """
    Manages all 6 agents as a coordinated unit.

    Methods:
        assemble(quest) → None
        - Loads agent configs from agents/ folders
        - Initializes LLM clients with cached system prompts

        execute_sprint(sprint, shared_state) → SprintResult
        - Routes tasks to appropriate agents
        - Manages handoffs between agents
        - Tracks token/cost usage

        campfire(reason, shared_state) → CampfireResult
        - Gathers all agents for sync discussion
        - Each agent contributes based on role
        - Produces decision + next actions

        get_active_agents() → list[str]
        get_agent_state(agent_id) → AgentState
    """
```

---

## 10. Skill Tree System

### 10.1 Concept

Each agent has skills that can be "locked" or "unlocked" based on quest progress. This is a visual/organizational concept — technically, locked skills are simply not included in the agent's context window.

### 10.2 Skill Definition

```yaml
# Example: agents/rogue/skills/hotfix.md

---
name: Hotfix Strike
description: Rapid targeted fix for a specific failing test or error
unlock_condition: on_error    # Available only when errors are detected
token_cost: low               # Indicates this skill uses minimal context
priority: high                # When unlocked, this skill takes precedence
inputs:
  - error_message
  - failing_test
  - relevant_file
outputs:
  - code_patch
  - confidence_note
---

## Instructions

You are performing a targeted hotfix. You have ONE specific error to fix.

Do NOT refactor. Do NOT restructure. Fix the exact error described.

Steps:
1. Read the error message carefully
2. Identify the root cause (not symptoms)
3. Write the minimal code change to fix it
4. Explain what you changed and why in one sentence
```

### 10.3 Unlock Conditions

```python
UNLOCK_CONDITIONS = {
    "always":         lambda state: True,
    "after_sprint_1": lambda state: state.completed_sprints >= 1,
    "on_error":       lambda state: state.has_active_errors,
    "on_review":      lambda state: state.phase == "campfire",
    "on_completion":  lambda state: state.phase == "documenting",
    "low_budget":     lambda state: state.budget_percentage > 75,
    "high_confidence":lambda state: state.confidence >= 0.8,
    "low_confidence": lambda state: state.confidence < 0.4,
}
```

### 10.4 Skill Tree Visualization

In the world frontend, each agent has a skill tree viewable by clicking their sprite:

```
┌─────────────────────────────────────────┐
│  ⚔️ ROGUE — Skill Tree                 │
│                                         │
│  [■] Implementation    (always)         │
│   └─[■] Refactor       (after sprint 1) │
│      └─[□] Hotfix      (on error)       │
│                                         │
│  ■ = unlocked   □ = locked              │
│  Click skill for description            │
└─────────────────────────────────────────┘
```

---

## 11. Build & Run

### 11.1 Development

```bash
# Terminal 1: Orchestrator
cd ergo
python -m uvicorn orchestrator:app --port 8765

# Terminal 2: World frontend
cd epic-world
npm install
npm run dev    # Vite dev server on :3000

# Terminal 3: Neovim (optional — HUD connects to same WebSocket)
nvim
:ErgoChat
```

### 11.2 NixOS Integration

```nix
# In flake.nix, add epic-world to the dev shell
devShells.default = pkgs.mkShell {
  packages = with pkgs; [
    nodejs_20
    python311
    python311Packages.fastapi
    python311Packages.uvicorn
    python311Packages.websockets
  ];

  shellHook = ''
    echo "🏰 Ergo + Project Epic development shell"
    echo "Run: cd epic-world && npm run dev"
  '';
};
```

### 11.3 Cross-Platform Notes

```
NixOS:    Full flake support. Declarative setup.
Linux:    Manual install: Node 20+, Python 3.11+, pip deps.
macOS:    Same as Linux. Homebrew for deps. PhaserJS runs in any browser.
Windows:  WSL2 recommended for orchestrator. Frontend runs natively in browser.
          Alternative: run orchestrator in Docker, frontend standalone.
```

---

## 12. Implementation Order

Build in this order. Each step is independently testable.

```
PHASE 1: Skeleton (Week 1)
  □ Set up epic-world/ Vite + PhaserJS project
  □ Create BootScene with asset loading
  □ Create WorldScene with static tilemap (hardcoded, no art yet — colored rectangles)
  □ Create 6 Agent sprites (colored squares with class labels initially)
  □ Implement basic A* pathfinding on tilemap grid
  □ Test: agents can pathfind between zone rectangles

PHASE 2: Events (Week 1-2)
  □ Add WebSocket endpoint to orchestrator (/ws/world)
  □ Implement EventRouter.js — connect to WS, parse events
  □ Wire phase_change events to agent zone movement
  □ Wire agent_active/agent_idle to sprite state changes
  □ Implement HUDScene with budget/token/progress bars
  □ Test: mock events move agents around the world

PHASE 3: Dialogue (Week 2)
  □ Implement AmbientDialogueService in orchestrator
  □ Create SpeechBubble.js — pixel art bubble rendering
  □ Wire functional speech (agent_output → bubble)
  □ Wire ambient speech (idle triggers → Gemini Flash → bubble)
  □ Implement DialogueQueue.js — prevent bubble overlap
  □ Write contextual dialogue templates per event type
  □ Test: agents speak in character during mock quest

PHASE 4: Polish (Week 2-3)
  □ Create actual pixel art tileset (16x16, 2-bit palette)
  □ Create agent sprite sheets (16x16, 4 states × 4 frames)
  □ Implement PaletteManager.js — confidence-based color shifting
  □ Add particle effects (campfire flames, forge sparks, celebration confetti)
  □ Add zone-specific ambient animations (flickering torches, swaying trees)
  □ Implement skill tree overlay UI (click agent → see skills)

PHASE 5: Integration (Week 3)
  □ Connect to real orchestrator quest execution
  □ Wire all event types end-to-end
  □ Test with actual quest ("implement JWT auth")
  □ Tune dialogue frequency and cooldowns
  □ Performance test — ensure <16ms frame time with 6 active agents
  □ Cross-browser test (Chrome, Firefox, Safari)

PHASE 6: Subagent System (Week 3-4)
  □ Implement QuestAgent class with personality loading
  □ Implement Party class with coordination logic
  □ Set up agents/ folder structure with claude.md per class
  □ Write skill .md files per agent
  □ Implement skill unlock system
  □ Implement Swarm-style handoff between agents
  □ Implement campfire sync as multi-agent conversation
  □ Wire agent system to emit world events
  □ End-to-end test: real quest → real agents → real world visualization
```

---

## 13. Cost Estimation

```
Per quest (estimated):

Functional agent calls:
  Opus  (Mage):       ~5 calls × 2K tokens avg  = 10K tokens  ≈ $0.50
  Sonnet (Rogue/Tank): ~15 calls × 3K tokens avg = 45K tokens  ≈ $1.35
  Flash (Plan/Sup/Heal): ~10 calls × 1K tokens avg = 10K tokens ≈ $0.02

Ambient dialogue:
  Flash: ~30 calls × 50 tokens avg = 1.5K tokens  ≈ $0.003

Total per quest: ~$1.87 without caching, ~$1.10 with prompt caching

The ambient dialogue adds <$0.01 per quest. It's essentially free.
```

---

## Summary

This system projects multi-agent coding coordination into a living 2D pixel world. The world is reactive — it visualizes what the orchestrator is already doing. Agents are real LLM instances with persistent personalities that generate both functional code output and ambient in-character dialogue. The confidence score drives the world's visual mood. The skill tree organizes agent capabilities into an unlockable progression system.

Build the event pipeline first. Then the world. Then the dialogue. Then the art. Each layer is independently testable and adds value incrementally.

**The party awaits its world.**



## What to copy inspire

Let me search for the specific repos I'd recommend.Here's the shortlist — what to clone and what to steal from each:

**1. Stanford Generative Agents** — The living world / personality engine
- **Repo:** `github.com/joonspk-research/generative_agents`
- **What you take:** The memory stream architecture (observations → reflections → plans), the agent personality system, and the Phaser-based tilemap world with sprites walking between locations. Their architecture stores a complete record of each agent's experiences in natural language, synthesizes memories into higher-level reflections, and retrieves them dynamically to plan behavior. This is your campfire discussion memory and ambient dialogue backbone.

**2. OpenAI Swarm** (now deprecated, replaced by Agents SDK) — The handoff pattern
- **Repo:** `github.com/openai/swarm`
- **What you take:** The agent handoff mechanism — agents are just instructions + functions, and `run()` handles function execution, hand-offs, and context variable references across multiple turns. Rip out the OpenAI client, swap in Anthropic SDK. This gives you the Planner → Mage → Rogue → Tank coordination chain. It's intentionally minimal which is what you want — you don't need a framework fighting your orchestrator.

**3. CrewAI** — The role/goal/backstory agent definition pattern
- **Repo:** `github.com/crewaiinc/crewai`
- **What you take:** The agent definition model — each agent has a role, goal, and backstory, with support for both sequential and hierarchical task execution. This maps directly to your `claude.md` per agent class. Also grab their task delegation pattern where agents can hand work to each other. You're not adopting the framework — you're copying the agent definition schema.

**4. Desplega Agent Swarm** — The persistent identity + memory system
- **Repo:** `github.com/desplega-ai/agent-swarm`
- **What you take:** Every agent has a searchable memory backed by embeddings. Memories are automatically created from session summaries, task completions, and file-based notes. Their identity system uses evolving identity files (SOUL.md, IDENTITY.md, TOOLS.md, CLAUDE.md) that define persona, expertise, and knowledge, syncing in real-time. This maps almost perfectly to your `agents/{class}/claude.md` + skills folder structure. This is the newest and most relevant repo for your specific use case.

**Summary — what goes where:**

| Your System Component | Steal From |
|---|---|
| Agent personality + ambient dialogue + world memory | Stanford Generative Agents |
| Agent-to-agent handoff + coordination | OpenAI Swarm |
| Role/goal/backstory definition schema | CrewAI |
| Persistent identity files + compounding memory | Desplega Agent Swarm |
| The pixel world + tilemap + sprites | Stanford Generative Agents (Phaser-based) |
| Quest state machine + orchestrator | **You build this** — nobody has it |
| Skill tree + unlock system | **You build this** — nobody has it |
| Confidence → world mood mapping | **You build this** — nobody has it |

The Stanford repo gives you the most code you can directly reuse since it already has the Phaser world + agents walking between locations. Start there, gut the Sims-like autonomous planning, replace it with your event-driven quest state machine, and wire in the handoff patterns from Swarm.
