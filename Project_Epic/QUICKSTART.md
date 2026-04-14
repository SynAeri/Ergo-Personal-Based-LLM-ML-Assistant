# 🚀 Quick Start - 2 Minutes to Epic Quests

## Step 1: Setup (30 seconds)

```bash
cd ~/Documents/Github/Ergo/Project_Epic

# Create .env file with your API key
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY
```

In `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Step 2: Install (30 seconds)

```bash
pip install -r requirements.txt
```

## Step 3: Test (1 minute)

```bash
# Option A: Run tests (no AI calls, instant)
python test_standalone.py

# Option B: Web interface
python -m epic.api.server
# Open: http://localhost:8766
```

---

## Web Interface Usage

1. **Select 4 party members** (click Planner, Mage, Rogue, Tank)
2. **Enter goal:** "Build a banking app"
3. **Click** "BEGIN THE QUEST"
4. **See** your quest with 6 difficulty-scaled sprints
5. **Click** "EXECUTE SPRINT" to run
6. **Click** "CAMPFIRE" for status report

---

## Without API Keys?

Run in simulation mode (no AI calls):

```bash
python test_standalone.py
```

Works perfectly for testing the system!

---

**Full details:** See SETUP.md or TESTING_GUIDE.md
