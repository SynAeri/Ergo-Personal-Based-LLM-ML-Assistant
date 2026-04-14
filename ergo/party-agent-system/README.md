# Party Agent System - RPG-Style Multi-Agent Coding

**"Kill the Demon Lord" - A Fantasy Quest Approach to Software Development**

## Overview

The Party Agent System treats coding missions as fantasy quests, where multiple Claude instances (party members) work together through a hero's journey to accomplish goals.

## System Architecture

```
Quest: "Implement JWT Authentication" (The Demon Lord)
    ↓
Party Formation: Planner, Mage, Rogue, Tank, Support, Healer
    ↓
Hero's Journey:
  1. 🏕️ Campfire Planning - Strategy discussion
  2. ⚔️ Sprint 1: Departure - Initial implementation
  3. 🏕️ Campfire Check-in - Progress review
  4. ⚔️ Sprint 2: Trials - Refinement & testing
  5. 🏕️ Campfire Check-in - Final review
  6. ⚔️ Sprint 3: Return - Polish & documentation
  7. 🎉 Victory Campfire - Celebration & knowledge capture
    ↓
HUD Display:
  HP (Budget): 💰 $8.50 / $10.00
  MP (Tokens): 🔮 45.2K / 100K
  Skills: ⚔️ Edit Code | 🔍 Grep | 🧪 Test | 📚 Search Memory
```

## Directory Structure

```
party-agent-system/
├── README.md                    # This file
├── core/
│   ├── claude_agent.py         # Base Claude agent with personality
│   ├── party.py                # Party composition and coordination
│   └── quest.py                # Quest/mission representation
├── agents/
│   ├── planner.py              # Scout/Ranger - Planning
│   ├── mage.py                 # Wizard - Architecture
│   ├── rogue.py                # Thief - Code execution
│   ├── tank.py                 # Paladin - Testing/verification
│   ├── support.py              # Cleric - Memory/context
│   └── healer.py               # Medic - Summarization
├── coordination/
│   ├── heroes_journey.py       # Quest phase management
│   ├── campfire.py             # Party discussion system
│   └── turn_coordinator.py     # Action sequencing
├── optimization/
│   ├── token_manager.py        # Token usage optimization
│   ├── context_compression.py  # Compress conversation history
│   └── caching_strategy.py     # Claude prompt caching
├── hud/
│   ├── stats_tracker.py        # HP/MP/XP tracking
│   ├── skill_system.py         # Skills as file ops (grep=spell)
│   └── display.py              # Terminal HUD rendering
├── api/
│   ├── server.py               # FastAPI localhost server
│   ├── websocket.py            # Real-time party updates
│   └── routes.py               # Quest submission endpoints
└── config/
    └── party_config.toml       # Party settings and optimization
```

## Token Optimization Strategies

### 1. **Prompt Caching** (Claude's feature)
- Cache personality prompts (they don't change)
- Cache codebase context
- Save ~90% on repeated context

### 2. **Context Compression**
- Summarize old conversation turns
- Keep only recent N messages at full fidelity
- Compress campfire discussions into key decisions

### 3. **Smart Party Coordination**
- Only wake agents when needed (don't send all context to all agents)
- Agents share context through campfire summaries, not full histories
- Use "whispers" (agent-to-agent) instead of full party broadcasts

### 4. **Incremental Context**
- Don't resend unchanged code
- Send diffs instead of full files
- Reference previous tool outputs by ID

## Hero's Journey Phases

### Phase 1: Departure (Planning)
```
🏕️ Campfire: "What's our quest?"
- Planner scouts the territory
- Mage analyzes magical requirements
- Party discusses strategy
- Decide on approach
```

### Phase 2: Initiation (First Sprint)
```
⚔️ Action: Implementation begins
- Rogue writes initial code
- Support provides context/memory
- Tank prepares test suite
```

### Phase 3: Trials (Testing & Refinement)
```
🏕️ Campfire: "How did we do?"
- Tank reports test results
- Mage reviews architecture
- Party discusses issues
⚔️ Action: Fix and improve
- Rogue fixes issues
- Tank re-verifies
```

### Phase 4: Return (Completion)
```
🏕️ Victory Campfire
- Healer documents the journey
- Party reflects on lessons learned
- Export to Obsidian vault
- Celebrate! 🎉
```

## HUD System - Skills as Spells

Each file operation is a "skill" with incantations:

```python
SKILL_CATALOG = {
    "⚔️ Code Strike": {
        "incantation": "write_file",
        "mp_cost": "~2K tokens",
        "description": "Write or modify a code file",
        "animation": "Rogue channels energy into the codebase..."
    },
    "🔍 Scrying Search": {
        "incantation": "grep_search",
        "mp_cost": "~500 tokens",
        "description": "Search for patterns across the realm",
        "animation": "Support gazes into the crystal ball..."
    },
    "🧪 Alchemical Test": {
        "incantation": "run_tests",
        "mp_cost": "~1K tokens",
        "description": "Brew tests to verify correctness",
        "animation": "Tank mixes the testing potion..."
    },
    "📚 Memory Recall": {
        "incantation": "search_memory",
        "mp_cost": "~300 tokens",
        "description": "Recall ancient knowledge",
        "animation": "Support consults the ancient scrolls..."
    },
    "🎨 Refactor Ritual": {
        "incantation": "refactor_code",
        "mp_cost": "~3K tokens",
        "description": "Reshape the code's essence",
        "animation": "Mage weaves arcane patterns..."
    }
}
```

## Campfire System

Campfires are synchronization points where the party discusses:

```python
class Campfire:
    """A safe space for party coordination"""

    async def gather_party(self, agents: List[ClaudeAgent]):
        """All agents share their perspective"""

    async def discuss(self, topic: str):
        """Structured discussion on a topic"""

    async def vote(self, options: List[str]):
        """Party votes on next action"""

    async def compress_to_memory(self):
        """Compress campfire discussion into key decisions"""
```

### Campfire Format

```
🏕️ ═══════════════════════════════════════════════
        CAMPFIRE - Quest Progress Review
═══════════════════════════════════════════════ 🏕️

Quest: Implement JWT Authentication
Phase: Trials (Sprint 2)
Budget: 💰 $6.20 / $10.00 | Tokens: 🔮 38K / 100K

───────────────────────────────────────────────────
PLANNER speaks:
"We've completed steps 1-3. Steps 4-5 are blocked
by test failures. I recommend we focus on the token
validation logic next."

TANK speaks:
"I found 3 failing tests in auth/token.rs:
- test_expired_token FAILED
- test_invalid_signature FAILED
- test_missing_claims FAILED
All related to validation logic."

MAGE speaks:
"The issue is architectural. We're validating before
decoding. I suggest we restructure to decode→validate→use."

ROGUE speaks:
"I can implement that fix in ~15 minutes. Need Mage's
approval on the pattern first."

───────────────────────────────────────────────────
DECISION: Mage designs pattern, Rogue implements, Tank verifies
NEXT PHASE: Sprint continues
───────────────────────────────────────────────────
```

## API - Localhost Server

```python
# Start the party server
uvicorn party_agent_system.api.server:app --host 127.0.0.1 --port 8766

# Submit a quest
POST /quest/create
{
  "title": "Implement JWT Auth",
  "demon_lord": "Add secure authentication to the API",
  "budget": 10.0,
  "max_tokens": 100000
}

# Watch the adventure
WS ws://127.0.0.1:8766/quest/{id}/watch

# Real-time HUD updates
{
  "phase": "campfire_planning",
  "hp": {"current": 8.5, "max": 10.0},
  "mp": {"current": 45200, "max": 100000},
  "party_status": {
    "planner": "thinking",
    "mage": "idle",
    "rogue": "casting",
    "tank": "ready"
  },
  "recent_action": "Rogue casts Code Strike on src/auth.rs"
}
```

## Usage Example

```python
from party_agent_system import Party, Quest, HeroesJourney

# Create a quest
quest = Quest(
    title="Implement JWT Authentication",
    demon_lord="Add JWT-based auth to the API with token validation",
    budget=10.0,
    max_tokens=100_000
)

# Assemble the party
party = Party.assemble(
    roles=["planner", "mage", "rogue", "tank", "support", "healer"]
)

# Begin the hero's journey
journey = HeroesJourney(party, quest)

# Start the adventure
async for phase_result in journey.embark():
    print(f"Phase: {phase_result.phase_name}")
    print(f"Status: {phase_result.status}")
    print(f"HP: ${phase_result.budget_remaining}")
    print(f"MP: {phase_result.tokens_remaining}")

    if phase_result.is_campfire:
        print("🏕️ Campfire Discussion:")
        for message in phase_result.campfire_log:
            print(f"  {message.agent}: {message.content}")

# Quest complete!
print("🎉 Demon Lord Defeated!")
print(f"Final Cost: ${quest.total_cost}")
print(f"Knowledge Gained: {quest.lessons_learned}")
```

## Integration with Ergo

This system plugs into existing Ergo infrastructure:

```python
# In orchestrator/main.py
from party_agent_system import Party, Quest, HeroesJourney

@app.post("/work_mode/quest")
async def start_quest(goal: str):
    # Create quest from work mode goal
    quest = Quest.from_work_mode_goal(goal)

    # Use existing mission_manager for tracking
    mission_id = mission_manager.create_mission(
        title=quest.title,
        goal=quest.demon_lord,
        mode="party_quest"
    )

    # Start the adventure
    party = Party.assemble()
    journey = HeroesJourney(party, quest)

    # Execute and track
    result = await journey.embark()

    # Store in existing memory/obsidian
    memory_service.store_memory(...)
    obsidian_bridge.export_mission_summary(mission_id)

    return result
```

## Configuration

```toml
# party-agent-system/config/party_config.toml

[party]
default_composition = ["planner", "mage", "rogue", "tank", "support", "healer"]
max_concurrent_actions = 3

[optimization]
enable_prompt_caching = true
compress_after_turns = 10
max_context_tokens = 100000
summary_compression_ratio = 0.2

[heroes_journey]
phases = [
    "campfire_planning",
    "sprint_departure",
    "campfire_review",
    "sprint_trials",
    "campfire_review",
    "sprint_return",
    "campfire_victory"
]

[campfire]
min_discussion_turns = 2
max_discussion_turns = 8
enable_voting = true
quorum = 0.6  # 60% agreement to proceed

[hud]
update_interval_ms = 500
show_animations = true
theme = "fantasy"  # or "cyberpunk", "minimal"
```

## Token Optimization Examples

### Before Optimization
```
Total tokens: 85,000
Cost: $12.50
Wasted on repeated context: ~40%
```

### After Optimization
```
Total tokens: 48,000
Cost: $6.80
Saved via:
- Prompt caching: 30K tokens
- Context compression: 5K tokens
- Smart routing: 2K tokens
```

## Why This Works

1. **Engaging Mental Model** - Fantasy RPG is intuitive and fun
2. **Natural Coordination** - Campfires create synchronization points
3. **Token Efficient** - Agents only get context they need
4. **Clear Phases** - Hero's journey provides structure
5. **Observable** - HUD makes the system transparent
6. **Self-Contained** - Can be extracted as separate tool
7. **Ergo Compatible** - Plugs into existing infrastructure

## Next Steps

1. Implement core agent system with token optimization
2. Create hero's journey coordinator
3. Build campfire discussion system
4. Implement HUD display
5. Create localhost API
6. Update role prompts for RPG metaphor
7. Test with real quest

---

**"The party gathers at the tavern. The quest board shows a new contract: 'JWT Authentication Demon Lord'. Who will answer the call?"**
