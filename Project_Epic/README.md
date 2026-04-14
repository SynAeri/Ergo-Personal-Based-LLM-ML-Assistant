# Project Epic - Fantasy Quest Agent System

**"Kill the Demon Lord" - Where Software Development Meets High Fantasy**

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)

---

## ✨ New: HD-2D Frontend with Mouse Parallax!

**Octopath Traveler-inspired UI with mouse-based parallax forest layers!**

```bash
# Start both backend and frontend
./start-epic.sh

# Or start separately:
python -m epic.api.server          # Backend at :8766
cd frontend && npm run dev         # Frontend at :3000
```

**Open http://localhost:3000** to see the magic! ✨

---

## 🎮 What is Project Epic?

Project Epic transforms software development into an epic fantasy quest. Multiple Claude instances become party members (Planner, Mage, Rogue, Tank, Support, Healer), each with unique personalities and abilities, working together to defeat "Demon Lords" (your coding goals).

### What's New:
- 🎨 **HD-2D Frontend** - Octopath Traveler aesthetic with Next.js + TypeScript
- 🖱️ **Mouse Parallax** - 4-layer forest background that moves with your mouse
- ⚔️ **Working UI** - Full quest creation, sprint execution, and progress tracking
- 📊 **Real-Time Updates** - WebSocket integration for live quest status
- 🎭 **Party Selection** - Click to select up to 4 party members

### Key Concepts

- **Quest** = Your coding goal (e.g., "Implement JWT Auth")
- **Demon Lord** = The main challenge to overcome
- **Party** = 6 Claude instances with different roles and personalities
- **Sprints** = Thematically named based on quest type
- **Campfires** = Synchronization points where party discusses progress
- **Skills** = File operations presented as magical abilities
- **HUD** = Real-time display of HP (budget), MP (tokens), party status

---

## 🏰 Quest Aesthetics by Type

Each quest type has unique thematic sprint names:

### Web App Quests
**Demon Lord:** Elder Vampire Lord
**Sprints:**
1. 🏰 Save the Holy City
2. ⚔️ Vanquish the Vampire Horde
3. 🌅 Restore the Light

### API Service Quests
**Demon Lord:** Chaos Dragon
**Sprints:**
1. ⚒️ Forge the Sacred Weapon
2. 🔥 Temper in Dragon Fire
3. ✨ Imbue with Ancient Magic

### Database Quests
**Demon Lord:** Lich King
**Sprints:**
1. 🕯️ Delve into the Catacombs
2. 💀 Face the Undead Guardians
3. 📜 Claim the Forbidden Knowledge

### Authentication Quests
**Demon Lord:** Shadow Thief
**Sprints:**
1. 🔐 Protect the Royal Seal
2. 🛡️ Fortify the Gate
3. 👁️ Set the Watchers

### Refactor Quests
**Demon Lord:** Corruption Demon
**Sprints:**
1. 🧹 Purify the Corrupted Temple
2. ⚡ Exorcise the Evil Spirits
3. 🕊️ Consecrate the Sacred Ground

### Bug Fix Quests
**Demon Lord:** Shadow Beast
**Sprints:**
1. 🔍 Track the Beast
2. ⚔️ Slay the Shadow Beast
3. 🔦 Light the Torches

---

## 🎭 The Party

### Planner (Scout/Ranger) 🗺️
- **Role:** Task decomposition and strategy
- **Personality:** Cautious, thorough, detail-oriented
- **Skills:** Plan Mission, Analyze Dependencies
- **Permissions:** Read-only
- **Model:** Gemini Flash (fast planning)

### Mage (Wizard/Sage) 🧙
- **Role:** Architecture and deep reasoning
- **Personality:** Thoughtful, principled, long-term thinker
- **Skills:** Analyze Architecture, Suggest Patterns
- **Permissions:** Read, suggest (no write)
- **Model:** Claude Opus (when deep thought needed)

### Rogue (Thief/Assassin) ⚔️
- **Role:** Code execution
- **Personality:** Bold, pragmatic, action-oriented
- **Skills:** Code Strike, Run Command, Git Operations
- **Permissions:** Full file write, shell execution
- **Model:** Claude Sonnet (balanced power/cost)

### Tank (Paladin/Guardian) 🛡️
- **Role:** Verification and testing
- **Personality:** Rigorous, uncompromising, protective
- **Skills:** Alchemical Test, Security Scan
- **Permissions:** Read, run tests
- **Model:** Claude Sonnet

### Support (Cleric/Librarian) 📚
- **Role:** Memory and context retrieval
- **Personality:** Helpful, organized, encyclopedic
- **Skills:** Memory Recall, Scrying Search
- **Permissions:** Memory/vault read
- **Model:** Gemini Flash (cheap lookups)

### Healer (Medic/Chronicler) 🕊️
- **Role:** Summarization and documentation
- **Personality:** Reflective, learning-focused
- **Skills:** Create Summary, Export Knowledge
- **Permissions:** Read, write summaries
- **Model:** Gemini Flash

---

## ⚔️ Skills as Spells

Each file operation is a magical skill:

| Skill | Incantation | MP Cost | Effect |
|-------|-------------|---------|--------|
| ⚔️ Code Strike | `write_file` | ~2K tokens | Write or modify code |
| 🔍 Scrying Search | `grep_search` | ~500 tokens | Search for patterns |
| 🧪 Alchemical Test | `run_tests` | ~1K tokens | Run test suite |
| 📚 Memory Recall | `search_memory` | ~300 tokens | Query knowledge base |
| 🎨 Refactor Ritual | `refactor_code` | ~3K tokens | Restructure code |
| 🔮 Git Divination | `git_operations` | ~800 tokens | Git commands |
| 📝 Scribe Scroll | `write_docs` | ~1.5K tokens | Write documentation |
| 🗡️ Delete Curse | `delete_file` | ~200 tokens | Remove files |

---

## 🏕️ Campfire System

Campfires are synchronization points where the party gathers:

```
🏕️ ═══════════════════════════════════════════════
        CAMPFIRE - Quest Progress Review
═══════════════════════════════════════════════ 🏕️

Quest: Implement JWT Authentication
Phase: Trials (Sprint 2)
Budget: 💰 $6.20 / $10.00 | Tokens: 🔮 38K / 100K

───────────────────────────────────────────────────
PLANNER speaks:
"We've completed steps 1-3. Token validation is blocked."

TANK speaks:
"3 tests failing in auth/token.rs. All validation-related."

MAGE speaks:
"Architectural issue. We need to decode before validating."

ROGUE speaks:
"I can fix that in 15 minutes. Awaiting Mage's pattern."
───────────────────────────────────────────────────
DECISION: Mage designs → Rogue implements → Tank verifies
───────────────────────────────────────────────────
```

---

## 📊 HUD Display

Real-time party status:

```
╔═══════════════════════════════════════════════════════════╗
║  QUEST: Implement JWT Authentication                     ║
║  DEMON LORD: Shadow Thief JWT                            ║
║  PHASE: ⚔️ Fortify the Gate (Sprint 2)                   ║
╠═══════════════════════════════════════════════════════════╣
║  HP (Budget):  💰💰💰💰💰💰○○○○  $6.50 / $10.00         ║
║  MP (Tokens):  🔮🔮🔮🔮○○○○○○  42K / 100K              ║
║  XP (Progress): ▓▓▓▓▓▓░░░░ 60%                           ║
╠═══════════════════════════════════════════════════════════╣
║  PARTY STATUS:                                            ║
║    🗺️  Planner:  💤 Resting                              ║
║    🧙 Mage:     ✨ Casting "Analyze Architecture"        ║
║    ⚔️  Rogue:    ⚡ Casting "Code Strike"                ║
║    🛡️  Tank:     👁️ Watching                             ║
║    📚 Support:   💤 Resting                               ║
║    🕊️  Healer:   💤 Resting                              ║
╠═══════════════════════════════════════════════════════════╣
║  RECENT ACTIONS:                                          ║
║  [12:34] Rogue casts Code Strike on src/auth.rs          ║
║  [12:32] Mage suggests using jsonwebtoken crate          ║
║  [12:30] Tank reports test failures                      ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🚀 Quick Start

### Installation

```bash
cd /home/jordanm/Documents/Github/Ergo/Project_Epic
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_AI_API_KEY="AIza..."
```

### Start the Epic Server

```bash
python -m epic.server
# Server starts at http://localhost:8766
```

### Submit a Quest

```bash
curl -X POST http://localhost:8766/quest/create \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Implement JWT authentication for the API",
    "budget": 10.0,
    "max_tokens": 100000
  }'
```

### Watch the Adventure

```bash
# Terminal HUD
python -m epic.hud.watch QUEST_ID

# Or via WebSocket
wscat -c ws://localhost:8766/quest/QUEST_ID/watch
```

---

## 📁 Project Structure

```
Project_Epic/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── epic/                          # Main package
│   ├── __init__.py
│   ├── core/                      # Core agent system
│   │   ├── claude_agent.py       # Base Claude agent
│   │   ├── party.py              # Party coordination
│   │   └── quest.py              # Quest representation
│   ├── agents/                    # Party member implementations
│   │   ├── planner.py
│   │   ├── mage.py
│   │   ├── rogue.py
│   │   ├── tank.py
│   │   ├── support.py
│   │   └── healer.py
│   ├── coordination/              # Journey management
│   │   ├── heroes_journey.py     # Phase management
│   │   ├── campfire.py           # Discussion system
│   │   └── turn_coordinator.py   # Action sequencing
│   ├── optimization/              # Token optimization
│   │   ├── token_manager.py      # Usage tracking
│   │   ├── context_compression.py
│   │   └── caching_strategy.py
│   ├── hud/                       # Display system
│   │   ├── stats_tracker.py      # HP/MP/XP tracking
│   │   ├── skill_system.py       # Skill catalog
│   │   └── terminal_display.py   # ASCII art HUD
│   ├── api/                       # API server
│   │   ├── server.py             # FastAPI app
│   │   ├── websocket.py          # Real-time updates
│   │   └── routes.py             # Endpoints
│   └── config/                    # Configuration
│       ├── party_config.toml     # Party settings
│       └── quest_themes.toml     # Quest aesthetics
├── personalities/                 # Agent personality files
│   ├── planner.md
│   ├── mage.md
│   ├── rogue.md
│   ├── tank.md
│   ├── support.md
│   └── healer.md
├── tests/                         # Test suite
├── examples/                      # Example quests
└── docs/                          # Documentation
```

---

## 🎯 Usage Examples

### Example 1: JWT Authentication Quest

```python
from epic import Party, Quest, HeroesJourney

quest = Quest(
    goal="Implement JWT authentication",
    budget=10.0
)

party = Party.assemble()
journey = HeroesJourney(party, quest)

async for phase in journey.embark():
    print(f"📍 {phase.name}: {phase.theme}")

    if phase.is_campfire:
        # Party discusses at campfire
        discussion = await phase.campfire.gather_party()
        print(discussion)

    if phase.is_sprint:
        # Party works on sprint
        result = await phase.execute()
        print(f"✓ Sprint complete: {result.summary}")

print("🎉 Quest Complete!")
```

### Example 2: Auto-detect Quest Type

```python
goal = "Build a user dashboard with real-time WebSocket updates"
quest_type = HeroesJourney.detect_quest_type(goal)
# Returns: QuestType.WEB_APP

# Automatically uses appropriate aesthetic:
# - Demon Lord: "Elder Vampire Lord UserDashboard"
# - Sprint 1: "Save the Holy City"
# - Sprint 2: "Vanquish the Vampire Horde"
# - Sprint 3: "Restore the Light"
```

---

## 🎨 Customization

### Add New Quest Types

```python
# In epic/coordination/heroes_journey.py

QUEST_THEMES[QuestType.YOUR_TYPE] = {
    "demon_lord": "Your Demon Lord {feature}",
    "sprints": [
        {
            "name": "🌟 Your Sprint Name",
            "description": "What this sprint accomplishes",
            "aesthetic": "Thematic description"
        }
    ]
}
```

### Custom Party Composition

```python
# Use only specific party members
party = Party.assemble(roles=["planner", "rogue", "tank"])

# Or create custom roles
party.add_member(CustomAgent("architect", "architect.md"))
```

---

## 🔧 Token Optimization

Project Epic includes aggressive token optimization:

### Prompt Caching
- Caches personality prompts (90% savings on repeated calls)
- Caches codebase context
- ~$2-4 saved per quest

### Context Compression
- Summarizes old campfire discussions
- Keeps only recent action history
- ~30% token reduction

### Smart Routing
- Agents only receive relevant context
- Planner doesn't get implementation details
- Rogue doesn't get architectural rationale
- ~20% token reduction

### Expected Savings

```
Without optimization: $12-15 per quest
With optimization:    $6-8 per quest
Savings:             ~45-50%
```

---

## 🌐 API Endpoints

### Quest Management

```
POST   /quest/create          Create new quest
GET    /quest/{id}            Get quest status
GET    /quest/{id}/hud        Get HUD data
DELETE /quest/{id}            Cancel quest
```

### Real-time Updates

```
WS     /quest/{id}/watch      Stream quest updates
WS     /quest/{id}/campfire   Listen to campfire discussions
```

### Party Management

```
GET    /party/status          Get all party member status
POST   /party/campfire        Force a campfire discussion
GET    /party/stats           Get token/cost statistics
```

---

## 🎓 Philosophy

### Why Fantasy RPG Metaphor?

1. **Intuitive** - Everyone understands party roles and quests
2. **Engaging** - Makes development feel like an adventure
3. **Observable** - Clear what each "character" is doing
4. **Memorable** - Easier to understand agent coordination
5. **Fun** - Software development should be enjoyable

### Design Principles

1. **Ergo is the DM** - The system orchestrates, Claude instances execute
2. **Token Efficiency** - Every optimization strategy implemented
3. **Self-Contained** - Can be extracted as standalone tool
4. **Observable** - Full transparency via HUD and logs
5. **Flexible** - Easy to customize and extend

---

## 🤝 Integration with Ergo

Project Epic is designed to work standalone OR integrate with Ergo:

```python
# In Ergo orchestrator
from Project_Epic.epic import Party, Quest, HeroesJourney

@app.post("/work_mode/epic_quest")
async def epic_quest(goal: str):
    quest = Quest(goal=goal)
    party = Party.assemble()
    journey = HeroesJourney(party, quest)

    result = await journey.embark()

    # Store in Ergo's systems
    mission_manager.create_mission(...)
    memory_service.store_memory(...)
    obsidian_bridge.export_mission_summary(...)

    return result
```

---

## 📜 License

MIT License - Use freely, credit appreciated

---

## 🎉 Credits

**Created by:** Jordan M
**Inspired by:** D&D, Final Fantasy, and the dream of making coding feel epic

---

**"The party gathers at the tavern. A new contract appears on the quest board. Who will answer the call?"**
