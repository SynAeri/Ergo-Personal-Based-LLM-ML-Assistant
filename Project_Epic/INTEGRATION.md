# Project Epic ↔ Ergo Integration

**How Ergo Work Mode Uses Project Epic**

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   ERGO SYSTEM                        │
│  ┌──────────────────────────────────────────────┐   │
│  │  Neovim Plugin                               │   │
│  │  User: "let's get a job done - impl JWT"    │   │
│  └───────────────────┬──────────────────────────┘   │
│                      │                               │
│  ┌───────────────────▼──────────────────────────┐   │
│  │  Orchestrator (FastAPI)                      │   │
│  │  - Detects work mode activation              │   │
│  │  - Routes to Project Epic                    │   │
│  └───────────────────┬──────────────────────────┘   │
│                      │                               │
│                      │ HTTP/WebSocket                │
└──────────────────────┼───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│              PROJECT EPIC SYSTEM                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Epic Server (localhost:8766)                │   │
│  │  - Receives quest from Ergo                  │   │
│  │  - Assembles party of Claude agents          │   │
│  └───────────────────┬──────────────────────────┘   │
│                      │                               │
│  ┌───────────────────▼──────────────────────────┐   │
│  │  Heroes Journey Coordinator                  │   │
│  │  - Manages phases (campfires + sprints)      │   │
│  │  - Coordinates party members                 │   │
│  └───────────────────┬──────────────────────────┘   │
│                      │                               │
│  ┌───────────────────▼──────────────────────────┐   │
│  │  Party (6 Claude Agents)                     │   │
│  │  Planner → Mage → Rogue → Tank → Support     │   │
│  │                                              │   │
│  └───────────────────┬──────────────────────────┘   │
│                      │                               │
│                      │ Results, Events, Stats        │
└──────────────────────┼───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│                ERGO INFRASTRUCTURE                   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Mission Manager                             │   │
│  │  - Tracks quest as mission                   │   │
│  │  - Records state transitions                 │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Memory Service                              │   │
│  │  - Stores episodic memories                  │   │
│  │  - Learns from quest outcomes                │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Obsidian Bridge                             │   │
│  │  - Exports quest summary to ~/Obsidian       │   │
│  │  - Creates quest journal entry               │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Work Mode Activation

**Location:** `ergo/orchestrator/src/services/supervisor.py`

```python
from Project_Epic.epic import Party, Quest, HeroesJourney
from Project_Epic.epic.hud import HUDDisplay

class Supervisor:
    def __init__(self):
        # ... existing init ...
        self.epic_enabled = os.getenv("EPIC_MODE_ENABLED", "true") == "true"

    async def handle_work_mode(self, user_goal: str) -> Dict[str, Any]:
        """
        When user says "let's get a job done", route to Project Epic
        """
        if not self.epic_enabled:
            # Fall back to classic work mode
            return self.create_mission_from_user_input(user_goal)

        # Create Epic quest
        quest = Quest(
            goal=user_goal,
            budget=self.config.get("default_budget_limit", 10.0),
            max_tokens=self.config.get("default_token_limit", 100_000)
        )

        # Track in Ergo's mission system
        mission_id = self.mission_manager.create_mission(
            title=quest.title,
            goal=user_goal,
            mode="epic_quest",
            budget_limit=quest.budget
        )

        # Assemble party and begin journey
        party = Party.assemble()
        journey = HeroesJourney(party, quest)

        # Stream quest updates to user
        hud = HUDDisplay()

        async for phase_result in journey.embark():
            # Update Ergo mission tracking
            self.mission_manager.log_mission_event(
                mission_id,
                "epic_system",
                phase_result.phase_name,
                phase_result.to_dict()
            )

            # Show HUD to user
            hud.update(phase_result)

            # If campfire, send discussion to user
            if phase_result.is_campfire:
                yield {
                    "type": "campfire",
                    "discussion": phase_result.campfire_log
                }

        # Quest complete - store in Ergo systems
        self._store_quest_results(mission_id, quest, journey)

        return {
            "mission_id": mission_id,
            "quest_id": quest.id,
            "status": "completed",
            "cost": quest.total_cost,
            "demon_lord_defeated": True
        }

    def _store_quest_results(self, mission_id: str, quest: Quest, journey: HeroesJourney):
        """Store quest results in Ergo infrastructure"""
        # Mark mission complete
        self.mission_manager.transition_state(mission_id, "completed")

        # Store episodic memory
        self.memory_service.store_memory(
            memory_type="episodic",
            scope="session",
            title=f"Epic Quest: {quest.title}",
            content=f"Defeated {quest.demon_lord_name}. Party composition: {quest.party_roles}. Cost: ${quest.total_cost:.2f}",
            confidence=1.0
        )

        # Export to Obsidian
        quest_summary = journey.generate_summary()
        vault_path = self.obsidian_bridge.export_epic_quest(mission_id, quest_summary)

        return vault_path
```

### 2. Real-time HUD Display

**Location:** `ergo/nvim-plugin/lua/ergo-epic.lua`

```lua
-- Show Epic HUD in floating window
local function show_epic_hud()
  local buf = vim.api.nvim_create_buf(false, true)
  local width = 60
  local height = 20

  local win = vim.api.nvim_open_win(buf, true, {
    relative = 'editor',
    width = width,
    height = height,
    col = vim.o.columns - width - 2,
    row = 2,
    style = 'minimal',
    border = 'rounded',
    title = ' 🎮 EPIC QUEST ',
  })

  -- WebSocket connection to Epic server
  local ws = require('ergo.websocket').connect('ws://localhost:8766/quest/' .. quest_id .. '/watch')

  ws:on('message', function(data)
    local lines = vim.fn.split(data.hud_display, '\n')
    vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
  end)
end

-- Command to start epic quest
vim.api.nvim_create_user_command('ErgoEpicQuest', function()
  show_epic_hud()
  -- Send goal to orchestrator
  local goal = vim.fn.input('Quest Goal: ')
  require('ergo.api').start_epic_quest(goal)
end, {})
```

### 3. Obsidian Export Integration

**Location:** `ergo/orchestrator/src/services/obsidian_bridge.py`

```python
def export_epic_quest(self, mission_id: str, quest_summary: Dict) -> Path:
    """Export Epic quest to Obsidian with fantasy formatting"""
    quest_name = quest_summary['title']
    demon_lord = quest_summary['demon_lord']

    md = f"""# 🎮 Epic Quest: {quest_name}

**Demon Lord:** {demon_lord}
**Status:** Defeated ✓
**Party:** {', '.join(quest_summary['party_roles'])}
**Date:** {quest_summary['completed_at']}

---

## The Quest

{quest_summary['goal']}

## The Journey

"""

    # Add each phase
    for phase in quest_summary['phases']:
        md += f"""### {phase['name']}
**Type:** {phase['phase_type']}
**Theme:** {phase['theme']}

{phase['summary']}

"""

        if phase['phase_type'] == 'campfire':
            md += "#### Campfire Discussion\n\n"
            for msg in phase.get('discussion', []):
                md += f"**{msg['agent']}:** {msg['content']}\n\n"

    # Add statistics
    md += f"""---

## Battle Statistics

- **Total Cost:** ${quest_summary['total_cost']:.2f}
- **Tokens Used:** {quest_summary['total_tokens']:,}
- **Tokens Saved (Caching):** {quest_summary['tokens_saved']:,}
- **Duration:** {quest_summary['duration_minutes']} minutes
- **Party Efficiency:** {quest_summary['efficiency_rating']}/10

## Loot Acquired (Lessons Learned)

"""

    for lesson in quest_summary.get('lessons_learned', []):
        md += f"- {lesson}\n"

    md += f"""

---

#epic-quest #quest-completed #{quest_summary['quest_type']}
"""

    # Write to vault
    quests_dir = self.vault_path / "epic-quests"
    quests_dir.mkdir(exist_ok=True)

    file_path = quests_dir / f"quest-{quest_summary['id'][:8]}.md"
    file_path.write_text(md)

    return file_path
```

### 4. Configuration

**Location:** `ergo/config/ergo.toml`

```toml
[epic_mode]
enabled = true
server_url = "http://localhost:8766"
show_hud = true
hud_position = "top_right"  # top_right, bottom_right, floating
enable_animations = true
theme = "fantasy"  # fantasy, cyberpunk, minimal

[epic_mode.party]
default_composition = ["planner", "mage", "rogue", "tank", "support", "healer"]
enable_parallel_execution = true
max_concurrent_agents = 3

[epic_mode.optimization]
enable_prompt_caching = true
compress_context_after_turns = 10
agent_context_filtering = true  # Only send relevant context to each agent

[epic_mode.campfire]
auto_campfire_interval_minutes = 20  # Force campfire every 20 min
min_discussion_turns = 2
enable_party_voting = true
```

---

## Usage Flow

### Standard Epic Quest

1. User opens Neovim
2. User types: `:ErgoChat`
3. User says: "let's get a job done - implement JWT authentication"
4. Ergo detects work mode activation
5. Ergo calls Project Epic server
6. HUD appears in Neovim floating window
7. Party assembles, quest begins
8. User watches HUD in real-time:
   - Budget bar decreasing
   - Token usage climbing
   - Party members taking actions
   - Campfire discussions
9. Quest completes
10. Summary exported to ~/Obsidian/epic-quests/
11. Ergo stores learnings in memory

### Alternative: Direct Epic Mode

```vim
:ErgoEpicQuest
" Prompts: Quest Goal: implement JWT authentication
" HUD appears, quest begins immediately
```

---

## Data Flow

### Quest Start

```
Neovim → Orchestrator → Epic Server
  { "goal": "implement JWT auth" }
       ↓
Epic Server → Heroes Journey
  Creates quest, assembles party, starts first phase
       ↓
Epic Server → Neovim (WebSocket)
  { "phase": "campfire_planning", "hud": {...} }
```

### During Quest

```
Epic Server (continuous WebSocket stream)
  ↓
Neovim HUD (updates every 500ms)
  {
    "hp": {"current": 7.50, "max": 10.00},
    "mp": {"current": 42000, "max": 100000},
    "party_status": {
      "rogue": "casting_code_strike"
    },
    "recent_action": "Rogue modified src/auth.rs"
  }
```

### Quest Complete

```
Epic Server → Orchestrator
  {
    "quest_id": "abc123",
    "status": "completed",
    "summary": {...},
    "lessons": [...]
  }
       ↓
Orchestrator → Mission Manager (track completion)
Orchestrator → Memory Service (store learnings)
Orchestrator → Obsidian Bridge (export quest)
       ↓
Neovim (final notification)
  "🎉 Demon Lord Defeated! Quest exported to Obsidian."
```

---

## Environment Setup

### Start Both Systems

```bash
# Terminal 1: Ergo Orchestrator
cd ~/Documents/Github/Ergo/ergo
./run-orchestrator.sh

# Terminal 2: Project Epic Server
cd ~/Documents/Github/Ergo/Project_Epic
python -m epic.server

# Both running, ready for quests!
```

### Or use the combined launcher:

```bash
cd ~/Documents/Github/Ergo
./run-epic-mode.sh  # Starts both orchestrator and Epic server
```

---

## Benefits of Integration

1. **Seamless UX** - User says "let's get a job done", everything else is automatic
2. **Full Tracking** - Ergo tracks the mission, Project Epic executes it
3. **Memory Integration** - Learnings stored in Ergo's memory system
4. **Obsidian Export** - Quest journals exported to user's vault
5. **Observable** - Real-time HUD shows exactly what's happening
6. **Flexible** - Can disable Epic mode and use classic work mode

---

## Fallback Strategy

If Project Epic server is unavailable, Ergo falls back to classic work mode:

```python
async def handle_work_mode(self, user_goal: str):
    if self.epic_enabled:
        try:
            return await self._epic_quest(user_goal)
        except ConnectionError:
            print("⚠️  Epic server unavailable, using classic work mode")
            return self._classic_work_mode(user_goal)
    else:
        return self._classic_work_mode(user_goal)
```

---

## Configuration Options

### Disable Epic Mode

```toml
# ergo/config/ergo.toml
[epic_mode]
enabled = false  # Use classic work mode instead
```

### Custom Party Composition

```toml
[epic_mode.party]
default_composition = ["planner", "rogue", "tank"]  # Smaller party
```

### Change HUD Theme

```toml
[epic_mode]
theme = "cyberpunk"  # Different aesthetic (future feature)
```

---

## Why This Architecture?

1. **Separation of Concerns**
   - Ergo: Infrastructure, tracking, memory, Obsidian
   - Epic: Party coordination, quest execution, HUD

2. **Modularity**
   - Project Epic can run standalone
   - Ergo can use classic mode or Epic mode
   - Easy to swap implementations

3. **Scalability**
   - Epic server can handle multiple concurrent quests
   - Multiple Ergo instances can share one Epic server

4. **Development**
   - Can develop/test Epic independently
   - Can update Epic without touching Ergo core
   - Clear boundaries

---

**"Ergo calls upon the heroes. The quest begins."**
