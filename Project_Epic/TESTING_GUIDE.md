# Project Epic - Testing Guide

**How to test the system standalone (without Ergo)**

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd ~/Documents/Github/Ergo/Project_Epic

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set API Keys

```bash
# Required for Claude agents
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional (for Gemini agents)
export GOOGLE_AI_API_KEY="AIza..."
```

### Step 3: Run Tests

#### Option A: Command-Line Tests (No AI calls)

```bash
python test_standalone.py
```

This runs 5 test suites:
1. Quest creation with difficulty-scaled sprints
2. Party assembly with 4 members
3. Campfire business checkpoint
4. Sprint difficulty scaling
5. Complete quest flow simulation

**Expected output:**
- ASCII quest boards
- Sprint details (D→C→B→A→S→SSS)
- Party roster with permissions
- Campfire reports
- Progress tracking

**No API calls are made** - this tests the system structure only.

#### Option B: Web Interface (Full Experience)

```bash
# Start the server
python -m epic.api.server

# Or with uvicorn directly
uvicorn epic.api.server:app --host 127.0.0.1 --port 8766 --reload
```

Then open your browser:
```
http://localhost:8766
```

---

## 🎮 Using the Web Interface

### The Octopath Traveler-Style UI

**1. Party Selection (Top Section)**
   - You see 6 party members: Planner, Mage, Rogue, Tank, Support, Healer
   - Click to select **up to 4 members**
   - Selected members glow green
   - Each shows their icon, role, and class

**2. Quest Input (Middle Section)**
   - Enter your goal: "Build a banking app", "Create JWT auth", etc.
   - Click "BEGIN THE QUEST" button

**3. Quest Display (Bottom Section)**
   - Shows your goal and the randomly-generated Demon King
   - Lists all 6 sprints with difficulty badges (D, C, B, A, S, SSS)
   - Progress bar shows quest completion
   - Two buttons:
     - "⚔️ EXECUTE SPRINT" - Run the current sprint
     - "🏕️ CAMPFIRE" - Trigger business checkpoint

### Example Flow:

```
1. Select party: Planner, Mage, Rogue, Tank
2. Enter goal: "Build a banking app"
3. Click "BEGIN THE QUEST"
4. See quest board with 6 sprints:
   - D-RANK: Stave Away the Crocodiles
   - C-RANK: Clear the Goblin Den
   - B-RANK: Slay the Dragon Fafnir
   - A-RANK: Defeat the Elder Vampire
   - S-RANK: Conquer the Fortress
   - SSS-RANK: SLAY THE VOID LORD

5. Click "EXECUTE SPRINT" to run Sprint 1
6. Click "CAMPFIRE" to get status report
7. Repeat for each sprint
```

---

## 🧪 Testing Without Real AI Calls

The current implementation has **simulation mode** for testing without burning API credits:

### In `epic/api/server.py`:

```python
# This line simulates sprint execution:
await asyncio.sleep(1)  # Simulate work

# For testing, we assume success:
quest.complete_sprint(success=True, cost=sprint_cost, tokens=sprint_tokens)
```

### To Enable Real AI:

Replace the simulation with actual party coordination:

```python
# In execute_sprint endpoint:
current_sprint = quest.get_current_sprint()

# Coordinate party to execute sprint
result = await party.coordinate_action(
    primary_role="rogue",
    action=current_sprint.description,
    context={"sprint": current_sprint.to_dict()},
    supporting_roles=["planner", "mage"]
)

# Extract cost from real execution
sprint_cost = sum(r["cost"] for r in result["supporting"]) + result["primary"]["cost"]
sprint_tokens = result["primary"]["tokens"]["input"] + result["primary"]["tokens"]["output"]
```

---

## 📊 What Each Test Does

### Test 1: Quest Creation
```python
quest = Quest("Build a banking app", budget=10.0)
```

**Tests:**
- Quest type auto-detection
- 6 sprint generation with progressive difficulty
- Demon King naming
- Cost estimation per sprint
- ASCII quest board rendering

**Expected output:**
```
╔══════════════════════════════════════════════════════════════╗
║                     📜 QUEST BOARD 📜                        ║
╠══════════════════════════════════════════════════════════════╣
║  Goal: Build a banking app                                  ║
║  Demon King: VOID LORD OF FINANCES                          ║
║  Status: CREATED                                            ║
╠══════════════════════════════════════════════════════════════╣
║  SPRINTS:                                                    ║
╟──────────────────────────────────────────────────────────────╢
║  → [  D ] Stave Away the Crocodiles                         ║
║  ○ [  C ] Clear the Goblin Den                              ║
║  ○ [  B ] Slay the Dragon Fafnir                            ║
...
```

### Test 2: Party Assembly
```python
party = Party.assemble(roles=["planner", "mage", "rogue", "tank"])
```

**Tests:**
- Agent creation with personalities
- Model assignment per role
- Permission system
- Party roster

**Expected output:**
```
🎭 Party Assembled!

Roster:
  PLANNER      - gemini-2.0-flash
  MAGE         - claude-sonnet-3.5
  ROGUE        - claude-sonnet-3.5
  TANK         - claude-sonnet-3.5

Permissions Check:
  Rogue can write files: True
  Rogue can run commands: True
  Tank can write files: False
  Tank can run tests: True
```

### Test 3: Campfire
```python
report = await campfire.gather_party(...)
```

**Tests:**
- Agent status assessment (HP/MP/morale)
- Progress calculation
- On-track determination
- Pivot recommendation logic
- Strategy change generation

**Expected output:**
```
🏕️  ═══════════════════════════════════════════════════
              CAMPFIRE - BUSINESS CHECKPOINT
   ═══════════════════════════════════════════════════ 🏕️

Quest: Build a banking app
Agenda: Sprint Review
Sprint 2: ✓ SUCCESS

─────────────────────────────────────────────────────
PROGRESS ASSESSMENT
─────────────────────────────────────────────────────
Goal Progress: 33%
On Track: YES ✓
Pivot Needed: NO

─────────────────────────────────────────────────────
PARTY RECON
─────────────────────────────────────────────────────
Overall Morale: Good

PLANNER:
  HP: 75% | MP: 75%
  Morale: Good
  Achievements: Used 3 skills successfully
...
```

### Test 4: Sprint Difficulty
```python
sprints = SprintGenerator.generate_sprints(...)
```

**Tests:**
- Different quest types (web_app, api, database, auth)
- Unique sprint names per type
- Progressive difficulty scaling
- Enemy randomization

**Expected output:**
```
WEB_APP Quest:
──────────────────────────────────────────────────────────────────
  D    | 🦎 Stave Away the Crocodiles
  C    | ⚔️ Clear the Goblin Den
  B    | 🐉 Slay the Dragon Fafnir
  A    | 🧛 Defeat the Elder Vampire
  S    | 🏰 Conquer the Ancient Fortress
  SSS  | 👹 SLAY THE DEMON KING

API_SERVICE Quest:
──────────────────────────────────────────────────────────────────
  D    | 🦎 Ward Off the Slimes
  C    | ⚔️ Drive Back the Bandits
...
```

### Test 5: Full Quest Flow
```python
# Complete simulation of quest → sprints → campfires → completion
```

**Tests:**
- End-to-end quest lifecycle
- Sprint execution
- Campfire checkpoints between sprints
- Budget tracking
- Progress updates
- Final quest completion

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'epic'"

**Solution:**
```bash
# Make sure you're in the Project_Epic directory
cd ~/Documents/Github/Ergo/Project_Epic

# Run tests from this directory
python test_standalone.py
```

### "Personality file not found"

**Solution:**
```bash
# Check that personality files exist
ls personalities/

# Should show:
# planner.md  mage.md  rogue.md  tank.md  support.md  healer.md
```

If missing, they're in the repository but may need to be created.

### Web Interface Not Loading

**Solution:**
```bash
# Check server is running
curl http://localhost:8766/health

# Should return: {"status":"healthy","active_quests":0,...}

# Check static files exist
ls epic/api/static/index.html
```

### API Keys Not Working

**Solution:**
```bash
# Verify keys are set
echo $ANTHROPIC_API_KEY

# Should print your key (sk-ant-...)

# If not set:
export ANTHROPIC_API_KEY="your-key-here"
```

---

## 📈 Next Steps After Testing

Once standalone tests work:

1. **Integrate with Ergo**
   - See `INTEGRATION.md`
   - Connect Ergo work mode → Project Epic
   - Add Neovim HUD integration

2. **Add Real AI Execution**
   - Replace simulation with actual Claude calls
   - Implement party coordination
   - Test with real coding tasks

3. **Enhance Web UI**
   - Add animations
   - Real-time party member animations
   - Better progress visualization
   - Campfire modal dialog

4. **Production Hardening**
   - Error handling
   - Database persistence (SQLite/PostgreSQL)
   - Authentication
   - Rate limiting

---

## 💡 Tips

- **Start with command-line tests** - Fastest way to verify system works
- **Use web interface for visual confirmation** - See the Octopath aesthetic
- **Check browser console** - WebSocket messages show real-time updates
- **Test with small budgets first** - $1-2 to avoid unexpected costs
- **Use simulation mode** - Test flow without API calls

---

**Questions? Check:**
- `README.md` - Project overview
- `INTEGRATION.md` - Ergo integration
- `STATUS.md` - Implementation status
- `IMPLEMENTATION_COMPLETE.md` - Technical details

**"The testing grounds await. Prove your mettle before facing the demon lords."**
