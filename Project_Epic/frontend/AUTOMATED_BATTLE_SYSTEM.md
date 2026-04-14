# Automated Battle System - Complete

## Overview

The battle system now runs fully automated with characters performing actions, animations playing, and progress tracking automatically.

---

## Battle Phases

### 1. **Running Phase** (3 seconds)
```
When: Quest starts or new sprint begins
Actions:
  - All characters play "run" animation
  - Characters log "advancing to battle position"
  - Messages staggered by 500ms per character
Duration: 3 seconds
Next: Automatically transitions to Fighting Phase
```

### 2. **Fighting Phase** (Until 100% progress)
```
When: After running phase
Actions:
  - Characters take turns performing actions
  - Each character acts every 2 seconds
  - Actions chosen randomly with weights:
    * 50% Attack (uses MP, plays attack animation)
    * 30% Defend (defensive stance)
    * 20% Item (restores MP)
  - Progress increments 1% every 300ms (30 seconds total)
Duration: Until progress reaches 100%
Next: Back to idle, then new sprint
```

### 3. **Idle Phase**
```
When: Sprint complete
Actions:
  - System message: "Sprint complete! Enemy defeated!"
  - 3 second pause
  - Reset progress to 0%
  - Start next sprint (running phase)
```

---

## Automated Actions

### Attack ⚔️ (50% chance)
```typescript
- Chat: "ROGUE used git status"
- Animation: 'attack' for 1.2 seconds
- Effect: MP -2
- Type: combat
```

### Defend 🛡️ (30% chance)
```typescript
- Chat: "TANK takes defensive stance"
- Animation: brief pause, return to idle
- Effect: None
- Type: action
```

### Item 📦 (20% chance)
```typescript
- Chat: "MAGE searches for tools"
- Animation: None
- Effect: MP +3 (restore)
- Type: action
```

### Escape 🏃 (Not used in auto mode)
```typescript
- Only available for manual actions
- Not used in automated combat
```

---

## Progress System

### Automatic Increment
```
Speed: 1% every 300ms
Total: 100% in 30 seconds
Visual: Smooth horizontal bar at bottom
Display: "{progress}% COMPLETE • {PHASE}"
```

### Phase Indicator
```
🏃 - Running phase (animated pulse)
⚔️ - Fighting phase (animated pulse)
✓ - Idle/Complete
```

---

## Action Rotation

### Turn Order
```
Characters act in order: 0 → 1 → 2 → 3 → 0 → 1...
Interval: 2 seconds per action
Example:
  [0s]  Planner attacks
  [2s]  Mage defends
  [4s]  Rogue attacks
  [6s]  Tank uses item
  [8s]  Planner attacks (cycle repeats)
```

### Staggered Running Messages
```
Example with 4 party members:
  [0s]    PLANNER advancing to battle position
  [0.5s]  MAGE advancing to battle position
  [1s]    ROGUE advancing to battle position
  [1.5s]  TANK advancing to battle position
  [3s]    SYSTEM Engaging enemy!
```

---

## Resource Management

### MP (Mana Points)
```
Starting: 50 MP
Attack: -2 MP
Item: +3 MP
Max: 50 MP
Min: 0 MP
```

### HP (Health Points)
```
Starting: 100 HP
Currently: Not affected (future: take damage)
```

---

## Chat Log Messages

### Format
```
[Icon] AGENT_NAME message
```

### Message Types

**Combat** ⚔️
```
ROGUE used git status
MAGE used npm install
TANK used cargo build
```

**Action** ⚙️
```
PLANNER takes defensive stance
SUPPORT searches for tools
```

**Movement** 🚶
```
HEALER advancing to battle position
ROGUE advancing to battle position
```

**System** 📢
```
SYSTEM Quest initiated! Party assembled.
SYSTEM Engaging enemy!
SYSTEM Sprint complete! Enemy defeated!
```

---

## Visual Feedback

### Animations
```
run:    Character moves forward (3 seconds at start)
attack: Character performs attack motion (1.2 seconds)
idle:   Default standing animation
```

### Progress Bar
```
Color: Gold gradient (from-[#735c00] to-[#e9c349])
Height: 3 pixels (h-3)
Position: Bottom center
Updates: Every 300ms
Smooth: transition-all duration-300
```

### Phase Display
```
Text: "{progress}% COMPLETE • {RUNNING/FIGHTING/IDLE}"
Size: 10px
Color: #8e928c (muted)
Opacity: 60%
```

---

## Timing Breakdown

### Full Sprint Cycle
```
Running Phase:          3 seconds
Fighting Phase:        30 seconds (100% progress)
Idle Phase:             3 seconds
Total per Sprint:      36 seconds
```

### Action Timing
```
Action Interval:        2 seconds
Actions per Sprint:    15 actions (30s / 2s)
Characters (4):         ~4 actions each per sprint
```

### Progress Timing
```
Increment:              1% every 300ms
Total Increments:      100
Duration:              30 seconds (100 × 300ms)
```

---

## Random Commands Pool

```typescript
const commands = [
  'ls -la',
  'grep -r "function"',
  'npm install',
  'git status',
  'python test.py',
  'cargo build',
  'vim config.json',
  'cd src/',
  'cat README.md',
  'pytest tests/',
  'write src/auth.rs',
  'edit config.json',
  'run tests',
  'check logs',
];
```

---

## State Management

### Battle State
```typescript
battlePhase: 'idle' | 'running' | 'fighting'
autoProgress: 0-100 (percentage)
partyAnimations: Record<string, 'idle' | 'run' | 'attack'>
partyStats: Record<string, { hp, maxHp, mp, maxMp }>
chatMessages: Array<ChatMessage>
```

### Transitions
```
quest created → battlePhase = 'running'
running (3s)  → battlePhase = 'fighting'
progress=100% → battlePhase = 'idle'
idle (3s)     → battlePhase = 'running' (next sprint)
```

---

## How It Works (Code Flow)

### 1. Quest Creation
```typescript
createQuest()
  ↓
Quest data received
  ↓
Initialize party stats (HP: 100, MP: 50)
  ↓
Add system message
  ↓
useEffect detects quest → setBattlePhase('running')
```

### 2. Running Phase Start
```typescript
battlePhase = 'running'
  ↓
Set all characters to 'run' animation
  ↓
Add "advancing" messages (staggered 500ms)
  ↓
setTimeout 3s → setBattlePhase('fighting')
  ↓
Add "Engaging enemy!" message
```

### 3. Fighting Phase
```typescript
battlePhase = 'fighting'
  ↓
Start action interval (every 2s)
  ↓
  Character selects random action
    ↓
    Execute action (animation, chat, MP update)
  ↓
Start progress interval (every 300ms)
  ↓
  Increment autoProgress by 1%
  ↓
  If progress >= 100%:
    ↓
    Add "Sprint complete!" message
    ↓
    setBattlePhase('idle')
    ↓
    setTimeout 3s → reset and restart
```

---

## User Experience

### What The User Sees

1. **Quest Start**
   - Characters suddenly run forward
   - Battle log fills with movement messages
   - Progress bar appears at bottom

2. **Combat**
   - Characters take turns acting
   - Animations play (attacks, etc.)
   - Chat log shows what each character does
   - MP bars decrease/increase
   - Progress bar fills steadily

3. **Sprint Complete**
   - "Sprint complete!" message
   - Brief pause (3 seconds)
   - Characters run forward again (new sprint)
   - Cycle repeats

### Fully Observable
```
✓ See which character is acting
✓ See what action they chose
✓ See animations in real-time
✓ See MP resource management
✓ See progress filling
✓ See phase transitions
```

---

## Future Enhancements

### Ready for Real Agent Integration

When real agents are connected, replace:

```typescript
// Current: Random actions
const action = getRandomAction();

// Future: Agent decision
const action = await agent.decideAction(context);
```

```typescript
// Current: Random commands
const command = getRandomCommand();

// Future: Real agent execution
const command = agent.lastExecutedCommand;
```

```typescript
// Current: Simulated progress
setAutoProgress(prev => prev + 1);

// Future: Real task completion
setAutoProgress(agent.completionPercentage);
```

---

## Benefits

✅ **Fully Automated**
- No manual clicking required
- Characters act independently
- Progress happens automatically

✅ **Visually Engaging**
- Constant movement and action
- Real animations tied to actions
- Smooth progress feedback

✅ **Observable AI**
- See every decision
- See every action
- See resource usage

✅ **Educational**
- Shows how multi-agent systems work
- Demonstrates task allocation
- Shows resource management

✅ **Ready for Real Agents**
- Drop-in replacement for random actions
- Same interface for real AI decisions
- Seamless transition

---

The automated battle system makes Project Epic come alive with constant activity, clear feedback, and full observability of the "party" working together to complete the quest!
