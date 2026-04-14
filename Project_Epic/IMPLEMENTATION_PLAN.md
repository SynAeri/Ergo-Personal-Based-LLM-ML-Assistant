# Project Epic - Living World Implementation Plan

**Based on:** FullProposal.md sections 1187-1221
**Date:** 2026-03-30
**Status:** Ready to Execute

---

## Overview

This plan implements the **Living World visualization layer** for Project Epic by integrating patterns from 4 inspiration repos into a cohesive 2D pixel RPG world that visualizes multi-agent coding coordination.

---

## Key Patterns to Steal

### 1. OpenAI Swarm → Agent Handoff Pattern
**File:** `inspirations/swarm/swarm/core.py`

**What to take:**
- `Result` class with `value`, `agent`, `context_variables`
- Agent handoff via function returns (return Agent → switch active agent)
- Context variables passed through tool calls
- `run()` loop that switches agents based on tool results

**Implementation:**
```python
# epic/core/handoff.py
class HandoffResult:
    """Result of an agent action that may trigger handoff"""
    value: str
    next_agent: Optional[str]  # Agent ID to hand off to
    context_updates: dict

def execute_with_handoff(agent, task, shared_context):
    """Execute agent action and handle handoffs"""
    result = agent.invoke(task, shared_context)
    if result.next_agent:
        return execute_with_handoff(
            party.get_agent(result.next_agent),
            result.value,
            {**shared_context, **result.context_updates}
        )
    return result
```

### 2. Stanford Generative Agents → Memory Stream & World System
**File:** `inspirations/generative_agents/reverie/backend_server/persona/persona.py`

**What to take:**
- `AssociativeMemory` - memory stream with observations → reflections
- `Scratch` - short-term working memory per agent
- Memory retrieval based on recency, importance, relevance
- Phaser-based tilemap world (in frontend_server/)
- Agents walking between locations on pathfinding

**Implementation:**
```python
# epic/memory/agent_memory.py
class AgentMemory:
    """Memory stream for a single agent"""
    observations: List[Observation]  # Raw events
    reflections: List[Reflection]    # Higher-level insights
    scratch: dict                     # Current working memory

    def add_observation(self, event, importance):
        """Add event to memory stream"""

    def reflect(self):
        """Generate reflections from recent observations"""
        # Use cheap LLM to synthesize memories

    def retrieve(self, query, k=5):
        """Retrieve relevant memories"""
        # Score by recency + importance + relevance
```

### 3. CrewAI → Role/Goal/Backstory Schema
**File:** `inspirations/crewAI/lib/crewai/src/crewai/agent.py`

**What to take:**
- Agent definition with `role`, `goal`, `backstory`
- Task delegation pattern
- Sequential and hierarchical execution

**Implementation:**
```python
# Update personalities/*.md to match CrewAI schema
# Each agent personality file gets:
---
role: "Code Execution Specialist"
goal: "Write production-quality code that implements the architecture"
backstory: |
  A bold thief who got tired of stealing code and decided to write it.
  Pragmatic, action-oriented, ships fast and fixes later.
---
```

### 4. Desplega Agent Swarm → Persistent Identity System
**File:** `inspirations/agent-swarm/plugin/agents/`

**What to take:**
- `SOUL.md`, `IDENTITY.md`, `TOOLS.md` per agent
- Memory backed by embeddings (searchable)
- Identity files evolve over time
- Session summaries → automatic memory creation

**Implementation:**
```python
# epic/memory/persistent_identity.py
class PersistentIdentity:
    """Evolving identity for an agent"""
    soul_file: Path          # Core personality (immutable)
    identity_file: Path      # Learned identity (evolves)
    tools_file: Path         # Available skills
    memories: VectorStore    # Searchable memory

    def update_identity(self, learnings):
        """Update identity file with new learnings"""

    def search_memory(self, query):
        """Semantic search over past experiences"""
```

---

## Implementation Order

### Phase 1: Agent Coordination (Week 1)
✅ Already have: `epic/core/claude_agent.py`, `epic/core/party.py`

**New files:**
```
epic/core/handoff.py              # Swarm-style handoff
epic/memory/agent_memory.py       # Memory stream per agent
epic/memory/persistent_identity.py # Evolving identity
```

**Tasks:**
1. Implement HandoffResult and execute_with_handoff
2. Add memory stream to each agent
3. Update personality files with role/goal/backstory
4. Wire memory retrieval into agent context

**Test:** Planner → Mage → Rogue handoff with memory

### Phase 2: World Backend (Week 1-2)
**New files:**
```
epic/world/
├── event_emitter.py         # Emit world events from orchestrator
├── zones.json               # Zone definitions from FullProposal
├── agents_sprites.json      # Agent sprite configs
└── dialogue_engine.py       # LLM-generated ambient dialogue
```

**Tasks:**
1. Create WorldEvent schema (from FullProposal section 6)
2. Implement event emitter in orchestrator
3. Create dialogue generation with Gemini Flash
4. Define all zones and sprite configs

**Test:** Mock quest → emit phase_change events

### Phase 3: World Frontend (Week 2-3)
**New project:**
```
epic-world/                   # PhaserJS frontend
├── package.json
├── vite.config.js
├── src/
│   ├── main.js              # Phaser init + WebSocket
│   ├── scenes/
│   │   ├── WorldScene.js    # Tilemap, agents, zones
│   │   └── HUDScene.js      # Quest stats overlay
│   ├── entities/
│   │   ├── Agent.js         # Agent sprite with pathfinding
│   │   └── SpeechBubble.js  # Dialogue bubbles
│   ├── systems/
│   │   ├── EventRouter.js   # WebSocket → game actions
│   │   ├── Pathfinder.js    # A* on tilemap
│   │   └── PaletteManager.js # Confidence → colors
│   └── assets/
│       ├── tilesets/world.png
│       └── sprites/[agent].png
```

**Tasks:**
1. Set up Vite + Phaser project
2. Create WorldScene with colored rectangles for zones
3. Create Agent sprites (colored squares initially)
4. Implement A* pathfinding
5. Connect WebSocket to orchestrator
6. Wire events → agent movement

**Test:** Mock events move agents between zones

### Phase 4: Ambient Dialogue (Week 3)
**Tasks:**
1. Implement dialogue triggers (FullProposal section 7)
2. Create contextual dialogue templates
3. Wire "blacksmith" pattern - events → narrative
4. Add speech bubbles to Agent.js
5. Tune dialogue frequency and cooldowns

**Test:** Agents speak in character during quest

### Phase 5: Polish (Week 3-4)
**Tasks:**
1. Create actual pixel art (16x16 tileset)
2. Draw agent sprite sheets (4 states × 4 frames)
3. Implement palette shifting based on confidence
4. Add particle effects (fire, sparks, confetti)
5. Create skill tree overlay UI

**Test:** Full quest with world visualization

### Phase 6: Integration (Week 4)
**Tasks:**
1. Connect to real orchestrator
2. Wire all event types end-to-end
3. Test with real quest
4. Performance optimization
5. Cross-browser testing

**Test:** JWT auth quest → full world visualization

---

## File Cleanup Plan

**Too many docs! Consolidate:**
```
Project_Epic/
├── README.md                    # Keep: main overview
├── docs/
│   ├── FullProposal.md         # Move here (architecture spec)
│   ├── INTEGRATION.md          # Move here
│   ├── TESTING_GUIDE.md        # Move here
│   ├── IMPLEMENTATION_*.md     # Move here
│   └── STATUS.md               # Move here
├── QUICKSTART.md               # Keep: quick start guide
└── requirements.txt            # Keep
```

**Delete or merge:**
- COMPLETE.md → merge into STATUS.md
- BACKEND_FIX_PROGRESS.md → merge into STATUS.md
- SETUP.md → merge into QUICKSTART.md
- FRONTEND_SETUP.md → merge into docs/

---

## Next Immediate Steps

### Step 1: Implement Swarm Handoff (30 min)
File: `epic/core/handoff.py`

### Step 2: Add Memory Stream to Agents (1 hour)
File: `epic/memory/agent_memory.py`

### Step 3: Update Personality Files (30 min)
Add role/goal/backstory to all 6 personalities

### Step 4: Create World Event System (1 hour)
File: `epic/world/event_emitter.py`

### Step 5: Set up PhaserJS Project (1 hour)
Directory: `epic-world/`

---

## Success Criteria

The Living World is complete when:

- ✅ Agents hand off work Swarm-style
- ✅ Each agent has memory stream + persistent identity
- ✅ Orchestrator emits world events on state changes
- ✅ PhaserJS world shows agents moving between zones
- ✅ Agents speak contextual dialogue ("Let's visit the blacksmith")
- ✅ Confidence score shifts world palette
- ✅ Campfire events gather all agents
- ✅ Full end-to-end quest visualized

---

## Cost Estimate

**Ambient dialogue (only new cost):**
- ~30 dialogue lines per quest
- Gemini Flash: $0.0001 per line
- **Total: ~$0.003 per quest (essentially free)**

**Rest is existing quest costs (~$7-8 per quest)**

---

## Questions to Resolve

1. Should we use existing Next.js frontend or new PhaserJS app?
   - **Answer:** New PhaserJS app for world, keep Next.js for quest board

2. Where should epic-world/ live?
   - **Answer:** `Project_Epic/epic-world/` (sibling to frontend/)

3. Integrate generative agents Phaser code directly?
   - **Answer:** Use as reference, but rebuild simpler (we don't need full Sims-like autonomy)

---

**"The foundation is built. Now we bring it to life."**
