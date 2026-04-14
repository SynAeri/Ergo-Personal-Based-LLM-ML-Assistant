# Project Epic - Quick Reference

**Last Updated:** 2026-03-30
**Current Phase:** Agent Coordination Complete → World Visualization Next

---

## What Just Got Built

### 1. Agent Handoff System (`epic/core/handoff.py`)
```python
# Agents can now hand off work to each other
return handoff_to("mage", "Plan complete. Design the architecture.")
return complete_task("Implementation finished!", files=["src/auth.rs"])
return trigger_campfire("We need to discuss this approach.")
```

### 2. Memory System (`epic/memory/`)
```python
# Each agent remembers experiences
memory.add_observation("Implemented JWT auth", importance=8)
relevant = memory.retrieve("authentication", k=5)
context = memory.get_context_summary()  # For prompts
```

### 3. Persistent Identity (`epic/memory/persistent_identity.py`)
```python
# Agents learn and evolve
identity.record_quest_completion("quest_123", learnings=[
    "JWT requires jsonwebtoken 8.3+",
    "CORS must come before auth middleware"
])
```

### 4. Updated Personalities (all 6 files)
```yaml
---
role: "Code Execution Specialist"
goal: "Write production code that implements the architecture"
backstory: |
  A skilled thief who learned to forge code...
---
```

---

## File Locations

```
Project_Epic/
├── IMPLEMENTATION_PLAN.md      ← Full roadmap for Living World
├── PROGRESS_SUMMARY.md         ← Detailed session summary
├── QUICK_REFERENCE.md          ← This file
├── FullProposal.md             ← Original architecture spec
│
├── epic/
│   ├── core/
│   │   └── handoff.py          ← NEW: Agent coordination
│   └── memory/
│       ├── agent_memory.py     ← NEW: Memory stream
│       └── persistent_identity.py ← NEW: Evolving identity
│
├── personalities/              ← UPDATED: All 6 agents
│   ├── planner.md
│   ├── mage.md
│   ├── rogue.md
│   ├── tank.md
│   ├── support.md
│   └── healer.md
│
└── inspirations/              ← Reference repos
    ├── swarm/
    ├── generative_agents/
    ├── crewAI/
    └── agent-swarm/
```

---

## Next Tasks (In Order)

### Phase 2: World Backend (3-4 hours)

1. **World Event System**
   - File: `epic/world/event_emitter.py`
   - Events: phase_change, agent_active, campfire_start, etc.
   - WebSocket broadcasting

2. **Ambient Dialogue Engine**
   - File: `epic/world/dialogue_engine.py`
   - Gemini Flash for cheap generation
   - Contextual templates ("Let's visit the blacksmith")

3. **Zone Definitions**
   - File: `epic/world/zones.json`
   - From FullProposal section 4.2

### Phase 3: PhaserJS World (4-5 hours)

1. **Project Setup**
   - Directory: `epic-world/`
   - Vite + PhaserJS + WebSocket

2. **WorldScene**
   - Tilemap with zones (colored rectangles first)
   - Agent sprites (colored squares first)
   - A* pathfinding

3. **Event Integration**
   - EventRouter translates events → actions
   - Agents move between zones
   - Speech bubbles appear

### Phase 4: Polish (2-3 hours)

1. **Pixel Art**
   - 16x16 tileset (2-bit palette)
   - Agent sprite sheets (4 states × 4 frames)

2. **Visual Effects**
   - Confidence-based palette shifting
   - Particle effects (fire, sparks)
   - Ambient animations

---

## How to Use New Features

### In Agent Code:

```python
from epic.core.handoff import handoff_to, complete_task, trigger_campfire
from epic.memory import AgentMemory

class RogueAgent:
    def __init__(self, agent_id):
        self.memory = AgentMemory(agent_id)

    def invoke(self, task, context):
        # Do work
        result = self.write_code(task)

        # Record memory
        self.memory.add_observation(
            f"Implemented {task}",
            importance=7,
            metadata={"files": ["src/auth.rs"]}
        )

        # Check if tests pass
        if not tests_pass:
            return trigger_campfire(
                "Tests failing. Need team input.",
                test_failures=failures
            )

        # Hand off to Tank
        return handoff_to(
            "tank",
            "Code written. Please verify.",
            files_changed=["src/auth.rs"]
        )
```

### In Orchestrator:

```python
from epic.core.handoff import HandoffCoordinator, HandoffContext

coordinator = HandoffCoordinator(party)

result = coordinator.execute_with_handoff(
    starting_agent_id="planner",
    task="Implement JWT authentication",
    context=HandoffContext(
        quest_id="quest_123",
        sprint_name="Protect the Royal Seal",
        current_phase="sprint_1",
        goal="Implement JWT auth",
        files_modified=[],
        tests_status={},
        budget_remaining=10.0,
        tokens_used=0,
        agent_outputs=[],
    )
)

print(coordinator.visualize_handoff_chain())
# Output: Handoff chain: planner → mage → rogue → tank
```

### After Quest Completion:

```python
from epic.memory import PersistentIdentity
from pathlib import Path

# Extract learnings for each agent
for agent_id in ["planner", "mage", "rogue", "tank"]:
    identity = PersistentIdentity(agent_id, Path("identities"))

    learnings = extract_learnings(agent_id, quest_results)

    identity.record_quest_completion(
        quest_id="quest_123",
        learnings=learnings
    )

    # IDENTITY.md now updated with new knowledge
```

---

## Key Files from FullProposal.md

### Section References:

- **2.1:** Agent Definitions → `personalities/*.md`
- **4.2:** Zone Definitions → Will be `epic/world/zones.json`
- **6.2:** Event Types → Will be `epic/world/event_emitter.py`
- **7.1:** Dialogue Generation → Will be `epic/world/dialogue_engine.py`
- **8.2:** Frontend Structure → Will be `epic-world/`
- **10.3:** Unlock Conditions → Future skill tree system

---

## Testing Your New Code

```bash
cd Project_Epic

# Test handoff system
python -c "
from epic.core.handoff import handoff_to, complete_task
result = handoff_to('mage', 'Test message')
print(result)
"

# Test memory system
python -c "
from epic.memory import AgentMemory
mem = AgentMemory('test_agent')
mem.add_observation('Test event', importance=5)
print(f'Observations: {len(mem.observations)}')
"

# Test identity system
python -c "
from epic.memory import PersistentIdentity
from pathlib import Path
identity = PersistentIdentity('rogue', Path('identities'))
print(f'Soul length: {len(identity.soul)} chars')
"
```

---

## Documentation Files

### Read These:
- `README.md` - Project overview
- `FullProposal.md` - Complete Living World architecture
- `IMPLEMENTATION_PLAN.md` - Step-by-step build guide
- `PROGRESS_SUMMARY.md` - What just got done

### Reference:
- `inspirations/swarm/README.md` - Handoff pattern source
- `inspirations/generative_agents/README.md` - Memory system source
- `inspirations/crewAI/README.md` - Personality schema source

---

## Cost Estimates

### Current (Simulation Mode):
- **Cost:** $0 (no real LLM calls yet)

### With Real AI:
- **Agent calls:** ~$7-8 per quest (with optimization)
- **Ambient dialogue:** ~$0.003 per quest (Gemini Flash)
- **Memory reflections:** ~$0.01 per quest (Gemini Flash)
- **Total:** ~$7-8 per quest (dialogue is essentially free)

---

## Questions? Issues?

### Check These Files:
1. `IMPLEMENTATION_PLAN.md` - Detailed build roadmap
2. `PROGRESS_SUMMARY.md` - Session recap with examples
3. Code comments - All files have extensive documentation

### Common Issues:

**Q:** Where do I start building the world visualization?
**A:** See IMPLEMENTATION_PLAN.md Phase 2 tasks

**Q:** How do I test the handoff system?
**A:** See "Testing Your New Code" section above

**Q:** What's the difference between soul and identity?
**A:** Soul = immutable core (from personalities/*.md)
      Identity = evolving learnings (from quest experience)

---

## Status Summary

✅ **COMPLETE:**
- Agent handoff coordination (Swarm pattern)
- Memory stream per agent (Stanford pattern)
- Persistent evolving identity (Desplega pattern)
- Role/goal/backstory personalities (CrewAI pattern)

⏳ **PENDING:**
- World event emitter system
- Ambient dialogue engine
- PhaserJS world frontend
- Pixel art assets
- Full integration testing

📊 **Progress:** Phase 1 of 6 Complete (Agent Coordination)

---

**"The foundation is solid. The agents are alive. Now let's build their world."**
