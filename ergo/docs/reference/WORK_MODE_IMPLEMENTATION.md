# Ergo Work Mode Implementation Plan

**Date:** 2026-03-25
**Status:** Ready to Begin
**Architecture:** See `WORK_MODE_ARCHITECTURE.md`

---

## Implementation Summary

Based on `ergo_work_mode_architecture.txt`, I have created:

1. ✅ **Comprehensive architecture documentation** (`WORK_MODE_ARCHITECTURE.md`)
2. ✅ **Complete database schema** (`orchestrator/src/db/work_mode_schema.sql`)
3. 📋 **Directory structure design** (to be created in `~/ergo/`)
4. 📋 **Initial role templates** (to be created)
5. 📋 **Personality system files** (to be created)

---

## What Has Been Created

### 1. Documentation

**File:** `docs/reference/WORK_MODE_ARCHITECTURE.md`

Comprehensive architecture document covering:
- Six-layer system design
- Mission state machine
- Role-based subagents (Planner, Mage, Rogue, Tank, Support, Healer)
- Memory architecture (Episodic, Semantic, Procedural, Personality)
- Obsidian vault structure
- Personality layering system
- Coding style memory system
- Database schema
- Service architecture
- NixOS integration strategy
- Build phases

### 2. Database Schema

**File:** `orchestrator/src/db/work_mode_schema.sql`

Complete SQLite schema with:
- **missions** - Mission tracking with state machine
- **mission_steps** - Individual agent actions
- **memories** - Four-category memory system
- **coding_style_preferences** - Learned coding preferences
- **personality_profiles** - Layered personality system
- **mission_events** - Detailed event logging
- **vault_exports** - Obsidian sync tracking
- **role_definitions** - Agent role configurations
- **projects** - Project metadata
- Triggers for automatic timestamps
- Initial data for roles and personality modes
- Views for common queries

---

## Directory Structure to Create

The work mode system requires a new directory structure at `~/ergo/`:

```
~/ergo/
├── config/                    # System configuration
│   ├── ergo.toml
│   ├── routes.toml
│   └── permissions.toml
│
├── runtime/                   # Live runtime data
│   ├── activity.db           # Current activity database
│   ├── missions.db           # Work mode missions database
│   ├── logs/
│   ├── cache/
│   └── artifacts/
│
├── vault/                     # Obsidian vault
│   ├── personality/
│   ├── general/
│   ├── procedures/
│   ├── coding/
│   ├── projects/
│   ├── sessions/
│   └── missions/
│
├── models/                    # Prompts and policies
│   ├── prompts/
│   ├── policies/
│   └── role_templates/
│
└── ui/                        # UI exports
    └── exports/
```

---

## Phase 1: Foundation (Immediate Next Steps)

### 1.1 Database Setup

**Task:** Initialize work mode database

```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator
sqlite3 ~/ergo/runtime/missions.db < src/db/work_mode_schema.sql
```

**Verify:**
```bash
sqlite3 ~/ergo/runtime/missions.db "SELECT role_name FROM role_definitions;"
```

Should show: planner, mage, rogue, tank, support, healer

### 1.2 Create Directory Structure

**Task:** Set up `~/ergo/` directory tree

```bash
cd ~
mkdir -p ergo/{config,runtime/{logs,cache,artifacts},vault/{personality,general,procedures,coding/language_profiles,projects/ergo,sessions,missions},models/{prompts,policies,role_templates},ui/exports}
```

**Verify:**
```bash
tree ~/ergo -L 2
```

### 1.3 Create Core Configuration Files

**Files to create:**
- `~/ergo/config/ergo.toml` - Main configuration
- `~/ergo/config/routes.toml` - Model routing rules
- `~/ergo/config/permissions.toml` - Agent permissions

**Example `ergo.toml`:**
```toml
[system]
version = "2.0.0-workmode"
mode = "chat" # Default mode: chat, deliberation, work

[paths]
vault = "~/ergo/vault"
runtime = "~/ergo/runtime"
models = "~/ergo/models"

[supervisor]
max_concurrent_agents = 3
default_budget_limit = 10.0 # USD
default_token_limit = 100000
default_max_iterations = 10

[memory]
ephemeral_window_minutes = 90
working_memory_hours = 24
confidence_threshold = 0.7

[obsidian]
enabled = true
auto_export = true
vault_path = "~/ergo/vault"
```

### 1.4 Create Initial Personality Files

**Create in `~/ergo/vault/personality/`:**

1. `core_persona.md`
2. `chat_mode.md`
3. `work_mode.md`
4. `code_review_mode.md`
5. `quiet_mode.md`
6. `mission_mode.md`

### 1.5 Create Role Prompt Templates

**Create in `~/ergo/models/prompts/`:**

1. `supervisor.md` - Main supervisor prompt
2. `planner.md` - Task decomposition agent
3. `mage.md` - Architecture/reasoning agent
4. `rogue.md` - Code execution agent
5. `tank.md` - Verification agent
6. `support.md` - Retrieval agent
7. `healer.md` - Summarization agent

### 1.6 Create Policy Files

**Create in `~/ergo/models/policies/`:**

1. `mission_state_machine.toml`
2. `routing_policy.toml`
3. `permissions_policy.toml`
4. `memory_writeback_policy.toml`
5. `intervention_policy.toml`
6. `coding_style_learning.toml`

---

## Phase 2: Memory Service

### 2.1 Implement Memory Manager

**File:** `orchestrator/src/memory_service.py`

**Functions:**
- `store_memory(memory_type, scope, title, content, confidence)`
- `retrieve_memory(memory_type, scope, project_id=None, limit=10)`
- `update_memory_confidence(memory_id, new_confidence)`
- `export_to_obsidian(memory_id, vault_path)`

### 2.2 Implement Coding Style Extractor

**File:** `orchestrator/src/coding_style_learner.py`

**Functions:**
- `analyze_codebase(repo_path, language)`
- `extract_style_preferences(file_path, language)`
- `update_preference(language, key, value, evidence_weight)`
- `get_style_profile(language)`
- `export_style_to_obsidian(language, vault_path)`

### 2.3 Obsidian Export Bridge

**File:** `orchestrator/src/obsidian_bridge.py`

**Functions:**
- `export_mission_summary(mission_id, vault_path)`
- `export_session_summary(session_data, vault_path)`
- `export_memory(memory_id, vault_path)`
- `export_style_profile(language, vault_path)`
- `sync_vault_exports()`

---

## Phase 3: Supervisor Service

### 3.1 Mission State Machine

**File:** `orchestrator/src/mission_manager.py`

**Functions:**
- `create_mission(goal, mode, project_id=None)`
- `transition_state(mission_id, new_state)`
- `get_mission_status(mission_id)`
- `add_mission_step(mission_id, role, objective)`
- `complete_mission_step(step_id, output, cost)`
- `log_mission_event(mission_id, source, event_type, payload)`

### 3.2 Supervisor Controller

**File:** `orchestrator/src/supervisor.py`

**Functions:**
- `detect_work_mode_activation(user_message)`
- `create_task_graph(mission_id, goal)`
- `select_agents(task_graph)`
- `dispatch_agent(role_name, objective, context)`
- `synthesize_results(mission_id)`
- `enforce_budget_limits(mission_id)`
- `handle_escalation(mission_id, reason)`

### 3.3 Deliberation Mode

**File:** `orchestrator/src/deliberation.py`

**Functions:**
- `draft_solution(problem, context)`
- `critique_solution(draft, criteria)`
- `synthesize_final(draft, critique)`

---

## Phase 4: Role-Based Agents

### 4.1 Base Agent Class

**File:** `orchestrator/src/agents/base_agent.py`

**Class:** `BaseAgent`

**Methods:**
- `execute(objective, context)`
- `check_permissions(tool_name)`
- `call_tool(tool_name, params)`
- `report_progress(status, output)`

### 4.2 Specific Agent Implementations

**Files:**
- `orchestrator/src/agents/planner.py` - `PlannerAgent`
- `orchestrator/src/agents/mage.py` - `MageAgent`
- `orchestrator/src/agents/rogue.py` - `RogueAgent`
- `orchestrator/src/agents/tank.py` - `TankAgent`
- `orchestrator/src/agents/support.py` - `SupportAgent`
- `orchestrator/src/agents/healer.py` - `HealerAgent`

---

## Phase 5: UI Dashboard

### 5.1 Mission Dashboard

**File:** `ui/src/mission_dashboard.py`

**Panels:**
- Mission Overview
- Party Roster (active agents)
- Current Objective
- Active Step Timeline
- Tool Calls Log
- Memory Usage
- Risk/Budget Meter
- Final Deliverables

### 5.2 Real-time Updates

**Technology:** WebSocket or Server-Sent Events (SSE)

**Events:**
- Mission created
- Step started
- Step completed
- Tool called
- Agent message
- Mission completed

---

## Phase 6: NixOS Integration

### 6.1 Nix Flake Updates

**File:** `flake.nix`

**Add:**
- `ergo-work-mode` package
- Development shell with all dependencies
- Optional Home Manager module
- Optional NixOS service module

### 6.2 Systemd Services

**Create:**
- `~/.config/systemd/user/ergo-daemon.service`
- `~/.config/systemd/user/ergo-orchestrator.service`
- `~/.config/systemd/user/ergo-ui.service`

---

## Testing Strategy

### Unit Tests

**Test coverage:**
- Mission state transitions
- Memory CRUD operations
- Coding style preference updates
- Personality profile loading
- Agent permission checks

### Integration Tests

**Test scenarios:**
- Complete mission flow (chat → work mode → completion)
- Deliberation mode (draft → critique → synthesize)
- Memory writeback to Obsidian
- Coding style learning from repository
- Multi-agent coordination

### End-to-End Tests

**Test workflows:**
1. User requests "let's get a job done"
2. Mission created and decomposed
3. Agents execute in sequence
4. Results synthesized and exported
5. Obsidian vault updated

---

## Migration Path

### From Current Ergo to Work Mode

1. **Backward compatible:** Keep existing chat mode as default
2. **Gradual activation:** Work mode is opt-in initially
3. **Data migration:** Existing memories imported into new schema
4. **UI coexistence:** Old UI continues to work, new dashboard is additional

### Migration Script

**File:** `scripts/migrate_to_work_mode.py`

**Steps:**
1. Create new database from schema
2. Import existing memories
3. Extract coding style from existing repos
4. Create initial Obsidian vault structure
5. Update configuration files

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Database initialized with schema
- ✅ Directory structure created
- ✅ Configuration files in place
- ✅ Personality and role templates created
- ✅ Obsidian vault structure exists

### Phase 2 Complete When:
- ✅ Memories can be stored and retrieved
- ✅ Coding style can be learned from repos
- ✅ Obsidian exports work correctly
- ✅ All memory categories functional

### Phase 3 Complete When:
- ✅ Missions can be created and tracked
- ✅ State machine enforces transitions
- ✅ Supervisor can dispatch agents
- ✅ Deliberation mode works end-to-end

### Phase 4 Complete When:
- ✅ All 6 agent roles implemented
- ✅ Permission enforcement works
- ✅ Tool calls are logged and limited
- ✅ Budget/cost tracking functional

### Phase 5 Complete When:
- ✅ Mission dashboard displays live data
- ✅ Real-time updates work
- ✅ All panels functional
- ✅ User can approve/reject steps

### Phase 6 Complete When:
- ✅ Nix flake builds all components
- ✅ systemd services auto-start
- ✅ Home Manager integration works
- ✅ NixOS-specific features functional

---

## Current Status

- ✅ Architecture designed and documented
- ✅ Database schema created
- ✅ Implementation plan written
- 📋 Directory structure (ready to create)
- 📋 Configuration files (ready to create)
- 📋 Personality templates (ready to create)
- 📋 Role prompts (ready to create)
- 📋 Code implementation (Phase 1-6 pending)

---

## Next Immediate Actions

1. **Create directory structure:**
   ```bash
   mkdir -p ~/ergo/{config,runtime/{logs,cache,artifacts},vault/{personality,general,procedures,coding/language_profiles,projects/ergo,sessions,missions},models/{prompts,policies,role_templates},ui/exports}
   ```

2. **Initialize database:**
   ```bash
   cd ~/Documents/Github/Ergo/ergo/orchestrator
   sqlite3 ~/ergo/runtime/missions.db < src/db/work_mode_schema.sql
   ```

3. **Create core config:**
   ```bash
   touch ~/ergo/config/ergo.toml
   touch ~/ergo/config/routes.toml
   touch ~/ergo/config/permissions.toml
   ```

4. **Create initial personality files** in `~/ergo/vault/personality/`

5. **Create role templates** in `~/ergo/models/role_templates/`

6. **Begin Phase 1 implementation** following this plan

---

## Resources

- **Architecture:** `docs/reference/WORK_MODE_ARCHITECTURE.md`
- **Database Schema:** `orchestrator/src/db/work_mode_schema.sql`
- **Original Spec:** `docs/ergo_work_mode_architecture.txt`
- **Current System Docs:** `docs/ARCHITECTURE.md`

---

**Ready to begin implementation!**
